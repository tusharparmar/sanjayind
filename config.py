import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Voice Configuration
    TTS_ENGINE = os.environ.get('TTS_ENGINE', 'gtts')  # 'gtts' or 'pyttsx3'
    VOICE_GENDER = 'female'
    VOICE_LANGUAGE = 'en'
    
    # WebRTC Configuration
    STUN_SERVERS = [
        'stun:stun.l.google.com:19302',
        'stun:stun1.l.google.com:19302'
    ]
    
    # TURN Servers (optional - add your own)
    TURN_SERVERS = []
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_PATH = 'knowledge_base.json'
    
    # Widget Configuration
    WIDGET_TITLE = 'AI Voice Assistant'
    WIDGET_THEME = 'modern'
    
    # CORS Configuration
    CORS_ORIGINS = ["*"]  # In production, specify allowed origins
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    @staticmethod
    def validate_config():
        """Validate required configuration"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True

