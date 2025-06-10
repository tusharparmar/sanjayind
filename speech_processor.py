import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import io
import base64
import tempfile
import os
import logging
from config import Config

class SpeechProcessor:
    """Handle speech-to-text and text-to-speech processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize TTS engine based on configuration
        self.tts_engine = Config.TTS_ENGINE
        if self.tts_engine == 'pyttsx3':
            self._init_pyttsx3()
        
        self.logger.info(f"Speech processor initialized with {self.tts_engine} TTS engine")
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 TTS engine"""
        try:
            self.pyttsx3_engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.pyttsx3_engine.getProperty('voices')
            
            # Try to find a female voice
            female_voice = None
            for voice in voices:
                if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                    female_voice = voice
                    break
            
            if female_voice:
                self.pyttsx3_engine.setProperty('voice', female_voice.id)
            elif voices:
                # Use the second voice if available (often female)
                self.pyttsx3_engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            
            # Set speech rate and volume
            self.pyttsx3_engine.setProperty('rate', 180)  # Speed of speech
            self.pyttsx3_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
            self.pyttsx3_engine = None
    
    def speech_to_text(self, audio_data):
        """
        Convert speech audio data to text
        
        Args:
            audio_data (str): Base64 encoded audio data or file path
        
        Returns:
            str: Transcribed text or None if failed
        """
        try:
            # Handle different audio data formats
            if isinstance(audio_data, str) and audio_data.startswith('data:audio'):
                # Handle base64 encoded audio from web
                audio_data = self._decode_base64_audio(audio_data)
            
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                if isinstance(audio_data, bytes):
                    temp_file.write(audio_data)
                else:
                    # Assume it's a file path
                    with open(audio_data, 'rb') as f:
                        temp_file.write(f.read())
                
                temp_file_path = temp_file.name
            
            try:
                # Use speech recognition to convert audio to text
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                # Try Google Speech Recognition first
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.logger.info(f"Speech recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    self.logger.warning("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    self.logger.error(f"Google Speech Recognition error: {e}")
                
                # Fallback to offline recognition
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    self.logger.info(f"Speech recognized (offline): {text}")
                    return text
                except sr.UnknownValueError:
                    self.logger.warning("Sphinx could not understand audio")
                except sr.RequestError as e:
                    self.logger.error(f"Sphinx error: {e}")
                
                return None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            self.logger.error(f"Speech to text error: {e}")
            return None
    
    def text_to_speech(self, text):
        """
        Convert text to speech audio
        
        Args:
            text (str): Text to convert to speech
        
        Returns:
            str: Base64 encoded audio data or None if failed
        """
        try:
            if self.tts_engine == 'gtts':
                return self._gtts_text_to_speech(text)
            elif self.tts_engine == 'pyttsx3':
                return self._pyttsx3_text_to_speech(text)
            else:
                self.logger.error(f"Unknown TTS engine: {self.tts_engine}")
                return None
                
        except Exception as e:
            self.logger.error(f"Text to speech error: {e}")
            return None
    
    def _gtts_text_to_speech(self, text):
        """Convert text to speech using Google TTS"""
        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=Config.VOICE_LANGUAGE,
                slow=False
            )
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Encode to base64
            audio_data = audio_buffer.getvalue()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return f"data:audio/mp3;base64,{audio_base64}"
            
        except Exception as e:
            self.logger.error(f"gTTS error: {e}")
            return None
    
    def _pyttsx3_text_to_speech(self, text):
        """Convert text to speech using pyttsx3"""
        try:
            if not self.pyttsx3_engine:
                return None
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Save speech to file
                self.pyttsx3_engine.save_to_file(text, temp_file_path)
                self.pyttsx3_engine.runAndWait()
                
                # Read the audio file and encode to base64
                with open(temp_file_path, 'rb') as f:
                    audio_data = f.read()
                
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                return f"data:audio/wav;base64,{audio_base64}"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            self.logger.error(f"pyttsx3 error: {e}")
            return None
    
    def _decode_base64_audio(self, base64_audio):
        """Decode base64 audio data"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_audio:
                base64_audio = base64_audio.split(',')[1]
            
            # Decode base64
            audio_data = base64.b64decode(base64_audio)
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Base64 decode error: {e}")
            return None
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            self.logger.info("Microphone calibrated for ambient noise")
            return True
        except Exception as e:
            self.logger.error(f"Microphone calibration error: {e}")
            return False
    
    def listen_for_speech(self, timeout=5, phrase_time_limit=10):
        """
        Listen for speech from microphone
        
        Args:
            timeout (int): Seconds to wait for speech to start
            phrase_time_limit (int): Maximum seconds for phrase
        
        Returns:
            str: Recognized text or None
        """
        try:
            with self.microphone as source:
                self.logger.info("Listening for speech...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Convert audio to text
            try:
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Heard: {text}")
                return text
            except sr.UnknownValueError:
                self.logger.warning("Could not understand speech")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            self.logger.warning("Listening timeout")
            return None
        except Exception as e:
            self.logger.error(f"Listen error: {e}")
            return None

