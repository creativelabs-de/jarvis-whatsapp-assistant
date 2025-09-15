import asyncio
import logging
import tempfile
import os
from typing import Optional
from google.cloud import speech
from google.cloud import texttospeech
import aiohttp
from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        self.speech_client = None
        self.tts_client = None
        self.setup_clients()
    
    def setup_clients(self):
        """Setup Google Cloud Speech clients"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Initialize Google Cloud clients
                self.speech_client = speech.SpeechClient()
                self.tts_client = texttospeech.TextToSpeechClient()
                logger.info("Google Cloud Speech clients initialized")
            else:
                logger.warning("Google Cloud credentials not configured - using mock speech service")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud clients: {e}")
            logger.info("Falling back to mock speech service")
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "ogg") -> Optional[str]:
        """Transcribe audio to text"""
        try:
            if self.speech_client:
                return await self._transcribe_with_google(audio_data, audio_format)
            else:
                return await self._mock_transcribe(audio_data, audio_format)
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def _transcribe_with_google(self, audio_data: bytes, audio_format: str) -> Optional[str]:
        """Transcribe using Google Cloud Speech-to-Text"""
        try:
            # Convert audio format if needed
            if audio_format.lower() == "ogg":
                # WhatsApp sends OGG files, convert to supported format
                audio_data = await self._convert_audio_format(audio_data, "ogg", "wav")
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
            elif audio_format.lower() == "mp3":
                encoding = speech.RecognitionConfig.AudioEncoding.MP3
            else:
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=16000,
                language_code="de-DE",  # German
                alternative_language_codes=["en-US"],  # Fallback to English
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                model="latest_long"
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                # Get the most confident result
                result = response.results[0]
                if result.alternatives:
                    transcript = result.alternatives[0].transcript
                    confidence = result.alternatives[0].confidence
                    
                    logger.info(f"Speech transcription: '{transcript}' (confidence: {confidence:.2f})")
                    return transcript.strip()
            
            logger.warning("No speech recognized in audio")
            return None
            
        except Exception as e:
            logger.error(f"Google Speech-to-Text error: {e}")
            return None
    
    async def _mock_transcribe(self, audio_data: bytes, audio_format: str) -> str:
        """Mock transcription for development"""
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Return a mock transcription
        mock_responses = [
            "Hallo JARVIS, wie geht es dir?",
            "Bestelle meiner Freundin rote Rosen",
            "Wie ist das Wetter heute?",
            "Plane einen Termin für morgen",
            "Sende eine E-Mail an meinen Chef"
        ]
        
        import random
        return random.choice(mock_responses)
    
    async def _convert_audio_format(self, audio_data: bytes, from_format: str, to_format: str) -> bytes:
        """Convert audio format using ffmpeg"""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=f".{from_format}", delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
            
            output_path = input_path.replace(f".{from_format}", f".{to_format}")
            
            # Use ffmpeg to convert
            import subprocess
            result = subprocess.run([
                "ffmpeg", "-i", input_path, 
                "-ar", "16000",  # Sample rate
                "-ac", "1",      # Mono
                "-y",            # Overwrite output
                output_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Read converted file
                with open(output_path, "rb") as f:
                    converted_data = f.read()
                
                # Clean up
                os.unlink(input_path)
                os.unlink(output_path)
                
                return converted_data
            else:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                # Clean up
                os.unlink(input_path)
                if os.path.exists(output_path):
                    os.unlink(output_path)
                
                return audio_data  # Return original if conversion fails
                
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return audio_data
    
    async def text_to_speech(self, text: str, language_code: str = "de-DE") -> Optional[bytes]:
        """Convert text to speech"""
        try:
            if self.tts_client:
                return await self._tts_with_google(text, language_code)
            else:
                return await self._mock_tts(text, language_code)
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return None
    
    async def _tts_with_google(self, text: str, language_code: str) -> Optional[bytes]:
        """Text-to-speech using Google Cloud"""
        try:
            # Set up the synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=f"{language_code}-Wavenet-C" if language_code == "de-DE" else f"{language_code}-Wavenet-D",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.OGG_OPUS,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            logger.info(f"Generated speech for text: '{text[:50]}...'")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google Text-to-Speech error: {e}")
            return None
    
    async def _mock_tts(self, text: str, language_code: str) -> bytes:
        """Mock TTS for development"""
        # Return empty audio data for mock
        logger.info(f"Mock TTS for: '{text[:50]}...'")
        return b""  # Empty audio data
    
    async def detect_language(self, text: str) -> str:
        """Detect language of text"""
        # Simple language detection based on common words
        german_words = ["der", "die", "das", "und", "ist", "ich", "du", "er", "sie", "es", "wir", "ihr", "sie"]
        english_words = ["the", "and", "is", "i", "you", "he", "she", "it", "we", "they", "are"]
        
        text_lower = text.lower()
        german_count = sum(1 for word in german_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if german_count > english_count:
            return "de-DE"
        else:
            return "en-US"

# Global speech service instance
speech_service = SpeechService()
