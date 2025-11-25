import whisper
import os
import logging

logger = logging.getLogger(__name__)

class VoiceManager:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.model = None
        
    def load_model(self):
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}...")
            try:
                self.model = whisper.load_model(self.model_size)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise e

    def transcribe(self, audio_path):
        """
        Transcribes the given audio file to text.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        self.load_model()
        
        logger.info(f"Transcribing audio: {audio_path}")
        try:
            result = self.model.transcribe(audio_path)
            text = result["text"]
            logger.info(f"Transcription complete. Length: {len(text)} chars")
            return text.strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise e
