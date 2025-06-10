from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS
import os
import json
import logging
from config import Config
from ai_assistant import AIAssistant
from knowledge_base import KnowledgeBase
from speech_processor import SpeechProcessor

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app, origins=Config.CORS_ORIGINS)
socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ORIGINS, async_mode='eventlet')

# Initialize components
try:
    Config.validate_config()
    ai_assistant = AIAssistant()
    knowledge_base = KnowledgeBase()
    speech_processor = SpeechProcessor()
except Exception as e:
    logging.error(f"Failed to initialize components: {e}")
    ai_assistant = None
    knowledge_base = None
    speech_processor = None

# Store active rooms and users
active_rooms = {}
user_sessions = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/widget')
def widget():
    """Widget page for embedding"""
    return render_template('widget.html')

@app.route('/widget.js')
def widget_js():
    """Serve the widget JavaScript file"""
    return send_from_directory('static/js', 'widget.js', mimetype='application/javascript')

@app.route('/api/config')
def get_config():
    """Get client configuration"""
    return jsonify({
        'stunServers': Config.STUN_SERVERS,
        'turnServers': Config.TURN_SERVERS,
        'widgetTitle': Config.WIDGET_TITLE,
        'widgetTheme': Config.WIDGET_THEME
    })

@app.route('/api/knowledge-base')
def get_knowledge_base():
    """Get knowledge base entries"""
    if knowledge_base:
        return jsonify(knowledge_base.get_all_entries())
    return jsonify([])

@app.route('/api/ai-query', methods=['POST'])
def ai_query():
    """Process AI query"""
    if not ai_assistant:
        return jsonify({'error': 'AI Assistant not available'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        context = data.get('context', {})
        
        response = ai_assistant.process_query(query, context)
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"AI query error: {e}")
        return jsonify({'error': str(e)}), 500

# Socket.IO Event Handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    session_id = request.sid
    user_sessions[session_id] = {
        'connected_at': None,
        'room': None,
        'user_info': {}
    }
    logger.info(f"Client connected: {session_id}")
    emit('connected', {'sessionId': session_id})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    if session_id in user_sessions:
        room = user_sessions[session_id].get('room')
        if room and room in active_rooms:
            # Remove user from room
            if session_id in active_rooms[room]['users']:
                active_rooms[room]['users'].remove(session_id)
            
            # Notify other users in room
            emit('user_left', {'userId': session_id}, room=room)
            
            # Clean up empty rooms
            if len(active_rooms[room]['users']) == 0:
                del active_rooms[room]
        
        del user_sessions[session_id]
    
    logger.info(f"Client disconnected: {session_id}")

@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a room"""
    session_id = request.sid
    room_id = data.get('roomId', 'default')
    user_info = data.get('userInfo', {})
    
    # Create room if it doesn't exist
    if room_id not in active_rooms:
        active_rooms[room_id] = {
            'users': [],
            'created_at': None
        }
    
    # Add user to room
    join_room(room_id)
    active_rooms[room_id]['users'].append(session_id)
    user_sessions[session_id]['room'] = room_id
    user_sessions[session_id]['user_info'] = user_info
    
    # Notify other users
    emit('user_joined', {
        'userId': session_id,
        'userInfo': user_info,
        'roomUsers': active_rooms[room_id]['users']
    }, room=room_id)
    
    logger.info(f"User {session_id} joined room {room_id}")

@socketio.on('leave_room')
def handle_leave_room():
    """Handle user leaving a room"""
    session_id = request.sid
    if session_id in user_sessions:
        room = user_sessions[session_id].get('room')
        if room:
            leave_room(room)
            if room in active_rooms and session_id in active_rooms[room]['users']:
                active_rooms[room]['users'].remove(session_id)
            
            emit('user_left', {'userId': session_id}, room=room)
            user_sessions[session_id]['room'] = None

# WebRTC Signaling Events
@socketio.on('offer')
def handle_offer(data):
    """Handle WebRTC offer"""
    session_id = request.sid
    target_id = data.get('targetId')
    offer = data.get('offer')
    
    if target_id:
        emit('offer', {
            'fromId': session_id,
            'offer': offer
        }, room=target_id)

@socketio.on('answer')
def handle_answer(data):
    """Handle WebRTC answer"""
    session_id = request.sid
    target_id = data.get('targetId')
    answer = data.get('answer')
    
    if target_id:
        emit('answer', {
            'fromId': session_id,
            'answer': answer
        }, room=target_id)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    """Handle ICE candidate"""
    session_id = request.sid
    target_id = data.get('targetId')
    candidate = data.get('candidate')
    
    if target_id:
        emit('ice_candidate', {
            'fromId': session_id,
            'candidate': candidate
        }, room=target_id)

# AI Assistant Events
@socketio.on('voice_query')
def handle_voice_query(data):
    """Handle voice query from client"""
    if not ai_assistant or not speech_processor:
        emit('error', {'message': 'AI services not available'})
        return
    
    try:
        session_id = request.sid
        audio_data = data.get('audioData')
        context = data.get('context', {})
        
        # Process speech to text
        text_query = speech_processor.speech_to_text(audio_data)
        
        if text_query:
            # Get AI response
            ai_response = ai_assistant.process_query(text_query, context)
            
            # Convert response to speech
            audio_response = speech_processor.text_to_speech(ai_response)
            
            emit('ai_response', {
                'textQuery': text_query,
                'textResponse': ai_response,
                'audioResponse': audio_response
            })
        else:
            emit('error', {'message': 'Could not process voice input'})
            
    except Exception as e:
        logger.error(f"Voice query error: {e}")
        emit('error', {'message': str(e)})

@socketio.on('screen_analysis')
def handle_screen_analysis(data):
    """Handle screen content analysis"""
    try:
        session_id = request.sid
        screen_data = data.get('screenData')
        
        # Process screen content (this would integrate with screen_analyzer.py)
        # For now, we'll just acknowledge the request
        emit('screen_analysis_result', {
            'status': 'received',
            'message': 'Screen analysis feature coming soon'
        })
        
    except Exception as e:
        logger.error(f"Screen analysis error: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Run the application
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )

