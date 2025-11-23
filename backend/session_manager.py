import random
import string
from typing import Dict, Optional

class SessionManager:
    def __init__(self):
        # Map PIN -> User ID
        self.sessions: Dict[str, str] = {}
        # Map User ID -> PIN (for reverse lookup if needed)
        self.user_pins: Dict[str, str] = {}
        
        # Create a default admin user
        self.create_user("admin")

    def create_user(self, user_id: str) -> str:
        """Creates a new user session and returns the generated PIN."""
        # Remove existing session for this user if any
        if user_id in self.user_pins:
            old_pin = self.user_pins[user_id]
            if old_pin in self.sessions:
                del self.sessions[old_pin]

        pin = self._generate_unique_pin()
        self.sessions[pin] = user_id
        self.user_pins[user_id] = pin
        return pin

    def get_user_id(self, pin: str) -> Optional[str]:
        """Returns the user_id associated with the PIN, or None if invalid."""
        return self.sessions.get(pin)

    def get_pin(self, user_id: str) -> Optional[str]:
        """Returns the PIN for a given user_id."""
        return self.user_pins.get(user_id)

    def _generate_unique_pin(self) -> str:
        """Generates a unique 4-digit PIN."""
        while True:
            pin = ''.join(random.choices(string.digits, k=4))
            if pin not in self.sessions:
                return pin

    def get_all_users(self) -> Dict[str, str]:
        """Returns a dictionary of user_id -> pin."""
        return self.user_pins

# Global instance
session_manager = SessionManager()
