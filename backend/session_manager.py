import random
import string
from typing import Dict, Optional

class SessionManager:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    @property
    def db(self):
        """Lazy initialization of DBManager."""
        if self._db is None:
            from database.db_manager import DBManager
            self._db = DBManager()
        return self._db

    def create_user(self, username: str) -> str:
        """Creates a new user session and returns the generated PIN."""
        pin = self._generate_unique_pin()
        if self.db.create_user(username, pin):
            return pin
        return "" # Or handle error appropriately

    def verify_user(self, username: str, pin: str) -> bool:
        """Verifies if the username and PIN match."""
        return self.db.verify_user(username, pin)

    def get_user_id(self, pin: str) -> Optional[str]:
        """
        Returns the username associated with the PIN.
        Note: This is a bit ambiguous if multiple users have the same PIN (unlikely but possible with 4 digits).
        For stricter security, we should require username + PIN for every request, 
        or issue a session token. For now, we'll iterate to find the user.
        """
        users = self.db.get_all_users()
        for user in users:
            if user['pin'] == pin:
                return user['username']
        return None

    def _generate_unique_pin(self) -> str:
        """Generates a random 4-digit PIN."""
        return ''.join(random.choices(string.digits, k=4))

    def get_all_users(self) -> Dict[str, str]:
        """Returns a dictionary of username -> pin."""
        users = self.db.get_all_users()
        return {user['username']: user['pin'] for user in users}

    def add_user(self, username: str, pin: str) -> bool:
        return self.db.create_user(username, pin)

    def remove_user(self, username: str) -> bool:
        return self.db.delete_user(username)

    def user_exists(self, username: str) -> bool:
        users = self.get_all_users()
        return username in users

# Global instance - but DB won't be initialized until first use
session_manager = SessionManager()

# Lazy singleton accessor for SessionManager
def get_session_manager() -> SessionManager:
    """Return a singleton SessionManager, creating it on first call.
    This prevents side‑effects during module import (e.g., when Sidebar imports this module)."""
    if not hasattr(get_session_manager, "_instance"):
        get_session_manager._instance = SessionManager()
    return get_session_manager._instance
