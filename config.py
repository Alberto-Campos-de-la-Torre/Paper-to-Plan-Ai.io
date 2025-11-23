import os
import random
import string

class Config:
    def __init__(self):
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
        self.OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.PIN_CODE = self._generate_pin()

    def _generate_pin(self):
        """Generates a random 4-digit PIN."""
        return ''.join(random.choices(string.digits, k=4))

# Global instance
config = Config()
