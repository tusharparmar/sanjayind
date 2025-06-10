# AI Voice Assistant - Embeddable Web Application

A comprehensive Python-based web application that enables real-time voice calls, screen sharing, and AI voice assistant integration. This app can be embedded into any website via a simple script tag or iframe.

## 🌟 Features

### Core Functionality
- **Voice Calls**: Real-time voice communication using WebRTC
- **Screen Sharing**: Share and analyze screen content with AI assistance
- **AI Voice Assistant**: Powered by Google's Gemini API with natural female voice
- **Knowledge Base**: Integrated workflows and operational guidance
- **Embeddable Widget**: Easy integration into any website

### AI Capabilities
- **Voice Recognition**: Speech-to-text processing
- **Natural Language Processing**: Powered by Gemini Pro API
- **Text-to-Speech**: Female voice synthesis
- **Screen Content Analysis**: OCR and DOM analysis for context-aware assistance
- **Workflow Guidance**: Step-by-step task assistance

### Technical Features
- **WebRTC**: Peer-to-peer media streaming
- **Socket.IO**: Real-time communication
- **Cross-Origin Support**: Embeddable across different domains
- **Responsive Design**: Works on desktop and mobile devices
- **Customizable Themes**: Light and dark themes available

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Modern web browser with WebRTC support

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-voice-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your configuration:
   ```env
   GEMINI_API_KEY=your-gemini-api-key-here
   SECRET_KEY=your-secret-key
   FLASK_DEBUG=False
   HOST=0.0.0.0
   PORT=5000
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the demo**
   Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `SECRET_KEY` | Flask secret key | auto-generated |
| `FLASK_DEBUG` | Enable debug mode | False |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 5000 |
| `TTS_ENGINE` | Text-to-speech engine (gtts/pyttsx3) | gtts |
| `VOICE_LANGUAGE` | Voice language code | en |

### Widget Configuration

```javascript
new AIVoiceWidget({
    serverUrl: 'http://localhost:5000',
    theme: 'modern',           // 'modern' or 'dark'
    position: 'bottom-right',  // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
    title: 'AI Voice Assistant',
    enableVoice: true,
    enableScreenShare: true,
    enableChat: true,
    autoConnect: true,
    minimized: false
});
```

## 📦 Integration Guide

### Method 1: Script Tag Integration

Add this to your website's HTML:

```html
<script src="http://your-server.com/widget.js"></script>
<script>
    new AIVoiceWidget({
        serverUrl: 'http://your-server.com',
        theme: 'modern',
        position: 'bottom-right'
    });
</script>
```

### Method 2: Auto-initialization

```html
<script>
    window.aiVoiceWidgetConfig = {
        serverUrl: 'http://your-server.com',
        theme: 'modern',
        position: 'bottom-right',
        autoConnect: true
    };
</script>
<script src="http://your-server.com/widget.js"></script>
```

### Method 3: iframe Integration

```html
<iframe 
    src="http://your-server.com/widget?theme=modern&position=bottom-right"
    width="320" 
    height="500"
    frameborder="0">
</iframe>
```

## 🎯 Usage Examples

### Basic Voice Interaction

```javascript
// Initialize widget
const widget = new AIVoiceWidget({
    serverUrl: 'http://localhost:5000'
});

// Listen for responses
widget.voiceAssistant.onResponse((data) => {
    console.log('AI Response:', data.textResponse);
});

// Send text query
widget.voiceAssistant.sendTextQuery('How do I reset my password?');
```

### Screen Sharing with Analysis

```javascript
// Start screen sharing
widget.webrtcClient.startScreenShare()
    .then(stream => {
        console.log('Screen sharing started');
        // AI will automatically analyze shared content
    })
    .catch(error => {
        console.error('Screen sharing failed:', error);
    });
```

### Custom Knowledge Base

Add your own workflows to `knowledge_base.json`:

```json
{
    "workflows": {
        "custom_process": {
            "title": "Custom Process",
            "description": "Step-by-step guide for custom task",
            "steps": [
                {
                    "step": 1,
                    "title": "First Step",
                    "description": "Description of first step",
                    "expected_elements": ["button", "form"],
                    "common_issues": ["Issue 1", "Issue 2"]
                }
            ]
        }
    }
}
```

## 🏗️ Architecture

### Backend Components
- **Flask Application** (`app.py`): Main server with Socket.IO
- **AI Assistant** (`ai_assistant.py`): Gemini API integration
- **Speech Processor** (`speech_processor.py`): Voice processing
- **Knowledge Base** (`knowledge_base.py`): Workflow management
- **Screen Analyzer** (`screen_analyzer.py`): Content analysis

### Frontend Components
- **WebRTC Client** (`webrtc-client.js`): Media streaming
- **Voice Assistant** (`voice-assistant.js`): Voice interaction
- **Widget** (`widget.js`): Embeddable interface

### Communication Flow
1. Client connects via Socket.IO
2. WebRTC establishes peer connection
3. Voice input → Speech-to-text → Gemini API → Text-to-speech
4. Screen content → OCR/Analysis → Context-aware responses

## 🔒 Security Considerations

### CORS Configuration
```python
CORS_ORIGINS = ["https://yourdomain.com", "https://anotherdomain.com"]
```

### API Key Protection
- Store API keys in environment variables
- Use HTTPS in production
- Implement rate limiting

### WebRTC Security
- Use TURN servers for production
- Implement user authentication
- Monitor connection quality

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Production Considerations
- Use a production WSGI server (Gunicorn)
- Set up reverse proxy (Nginx)
- Configure SSL certificates
- Set up monitoring and logging
- Use Redis for session storage

### Example Production Setup

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

## 🧪 Testing

### Manual Testing
1. Open the demo page at `http://localhost:5000`
2. Test voice recognition by clicking the microphone button
3. Test screen sharing functionality
4. Try the chat interface

### Browser Compatibility
- Chrome 60+ (recommended)
- Firefox 55+
- Safari 11+
- Edge 79+

### Required Permissions
- Microphone access for voice features
- Screen capture for screen sharing
- Camera access (optional)

## 🛠️ Troubleshooting

### Common Issues

**Voice recognition not working**
- Check microphone permissions
- Ensure HTTPS in production
- Verify browser compatibility

**Screen sharing fails**
- Check browser permissions
- Ensure secure context (HTTPS)
- Try different browsers

**AI responses are slow**
- Check Gemini API key
- Verify internet connection
- Monitor API rate limits

**Widget not loading**
- Check CORS configuration
- Verify server URL
- Check browser console for errors

### Debug Mode
Enable debug mode for detailed logging:
```bash
export FLASK_DEBUG=True
python app.py
```

## 📚 API Reference

### Socket.IO Events

#### Client → Server
- `join_room`: Join a communication room
- `voice_query`: Send voice query for AI processing
- `offer/answer/ice_candidate`: WebRTC signaling

#### Server → Client
- `ai_response`: AI assistant response
- `user_joined/user_left`: Room management
- `offer/answer/ice_candidate`: WebRTC signaling

### REST API Endpoints

#### GET `/api/config`
Get client configuration

#### POST `/api/ai-query`
Send text query to AI assistant
```json
{
    "query": "How do I reset my password?",
    "context": {
        "url": "https://example.com/login",
        "pageText": "Login page content..."
    }
}
```

#### GET `/api/knowledge-base`
Get knowledge base entries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- WebRTC for real-time communication
- Socket.IO for real-time messaging
- Flask for the web framework
- Tesseract for OCR functionality

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

---

**Note**: This application requires a Google Gemini API key to function. Please ensure you have proper API access and understand the usage costs before deploying to production.

