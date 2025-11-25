# import whisper
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
                import whisper
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
        # Check file size
        file_size = os.path.getsize(audio_path)
        logger.info(f"Audio file size: {file_size} bytes")
        if file_size == 0:
            logger.error("Audio file is empty!")
            return ""
        try:
            # Debug: Check audio duration with ffprobe
            import subprocess
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                duration = result.stdout.decode('utf-8').strip()
                logger.info(f"Audio duration: {duration} seconds")
            except Exception as e:
                logger.warning(f"Could not check audio duration: {e}")

            result = self.model.transcribe(audio_path)
            text = result["text"].strip()
            logger.info(f"Transcription complete. Length: {len(text)} chars")
            
            if not text:
                logger.warning("Whisper returned empty text.")
                return "No se pudo transcribir el audio. Por favor, intente grabar de nuevo hablando más claro."
                
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise e
