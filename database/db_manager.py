import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = "papertoplan.db"

class DBManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize the database and create the notes table if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT DEFAULT 'admin',
                        raw_text TEXT,
                        ai_analysis TEXT,
                        status TEXT DEFAULT 'pending',
                        implementation_time TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    corrected_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    pin TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
                conn.commit()
                
                # Migration: Check columns in notes
                cursor.execute("PRAGMA table_info(notes)")
                columns = [info[1] for info in cursor.fetchall()]
                
                if 'image_path' not in columns:
                    logger.info("Migrating DB: Adding image_path column to notes table.")
                    cursor.execute("ALTER TABLE notes ADD COLUMN image_path TEXT")
                    conn.commit()

                if 'user_id' not in columns:
                    logger.info("Migrating DB: Adding user_id column to notes table.")
                    cursor.execute("ALTER TABLE notes ADD COLUMN user_id TEXT DEFAULT 'admin'")
                    conn.commit()

                logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")

    def create_user(self, username: str, pin: str) -> bool:
        """Creates a new user with a PIN. Returns True if successful."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, pin, created_at) VALUES (?, ?, ?)",
                    (username, pin, datetime.now())
                )
                conn.commit()
                logger.info(f"User created: {username}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed: Username {username} already exists.")
            return False
        except sqlite3.Error as e:
            logger.error(f"Error creating user: {e}")
            return False

    def verify_user(self, username: str, pin: str) -> bool:
        """Verifies if the username and PIN match."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT pin FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                if row and row[0] == pin:
                    return True
                return False
        except sqlite3.Error as e:
            logger.error(f"Error verifying user: {e}")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieves all users."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, pin FROM users ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [{"username": row[0], "pin": row[1]} for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching users: {e}")
            return []

    def add_note(self, image_path: str, raw_text: str = "", user_id: str = "admin") -> int:
        """Add a new note with an image path and optional raw text. Returns the new note ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO notes (image_path, raw_text, status, created_at, user_id) VALUES (?, ?, ?, ?, ?)",
                    (image_path, raw_text, 'pending', datetime.now(), user_id)
                )
                conn.commit()
                logger.info(f"Note added with ID: {cursor.lastrowid} for user: {user_id}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding note: {e}")
            return -1

    def save_correction(self, image_path: str, corrected_text: str):
        """Saves a user correction as a learning example."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO corrections (image_path, corrected_text, created_at) VALUES (?, ?, ?)",
                    (image_path, corrected_text, datetime.now())
                )
                conn.commit()
                logger.info(f"Correction saved for {image_path}")
        except sqlite3.Error as e:
            logger.error(f"Error saving correction: {e}")

    def get_recent_corrections(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieves recent corrections to use as few-shot examples."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT image_path, corrected_text FROM corrections ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                return [{"image_path": row[0], "corrected_text": row[1]} for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching corrections: {e}")
            return []

    def update_note_text(self, note_id: int, new_text: str):
        """Update the raw text of a note."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET raw_text = ? WHERE id = ?", (new_text, note_id))
                conn.commit()
                logger.info(f"Note {note_id} text updated.")
        except sqlite3.Error as e:
            logger.error(f"Error updating note text {note_id}: {e}")

    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()
                logger.info(f"Note {note_id} deleted.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting note {note_id}: {e}")
            return False

    def update_note_error(self, note_id: int, error_msg: str):
        """Update a note status to error."""
        try:
            error_json = json.dumps({"error": error_msg, "title": "Error de Procesamiento"})
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notes 
                    SET ai_analysis = ?, status = 'error', implementation_time = 'Error'
                    WHERE id = ?
                """, (error_json, note_id))
                conn.commit()
                logger.info(f"Note {note_id} marked as error.")
        except sqlite3.Error as e:
            logger.error(f"Error marking note {note_id} as error: {e}")

    def flush_db(self) -> bool:
        """Delete all notes from the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes")
                conn.commit()
                logger.info("Database flushed. All notes deleted.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error flushing database: {e}")
            return False

    def update_note_analysis(self, note_id: int, analysis: Dict[str, Any]):
        """Update a note with the AI analysis result."""
        try:
            # Extract implementation time for easier filtering
            impl_time = analysis.get("implementation_time", "Unknown")
            analysis_json = json.dumps(analysis)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notes 
                    SET ai_analysis = ?, status = 'processed', implementation_time = ?
                    WHERE id = ?
                """, (analysis_json, impl_time, note_id))
                conn.commit()
                logger.info(f"Note {note_id} updated with analysis.")
        except sqlite3.Error as e:
            logger.error(f"Error updating note {note_id}: {e}")

    def get_all_notes(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all notes ordered by creation date. Optionally filter by user_id."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if user_id:
                    cursor.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
                else:
                    cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
                    
                rows = cursor.fetchall()
                
                notes = []
                for row in rows:
                    note = dict(row)
                    # Parse JSON string back to dict if it exists
                    if note['ai_analysis']:
                        try:
                            note['ai_analysis'] = json.loads(note['ai_analysis'])
                        except json.JSONDecodeError:
                            note['ai_analysis'] = {}
                    notes.append(note)
                return notes
        except sqlite3.Error as e:
            logger.error(f"Error fetching notes: {e}")
            return []

    def get_note_by_id(self, note_id: int, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve a single note by ID. Optionally verify user ownership."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()
                if row:
                    note = dict(row)
                    
                    # Check ownership if user_id is provided
                    if user_id and note.get('user_id') != user_id:
                        return None
                        
                    if note['ai_analysis']:
                        try:
                            note['ai_analysis'] = json.loads(note['ai_analysis'])
                        except json.JSONDecodeError:
                            note['ai_analysis'] = {}
                    return note
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching note {note_id}: {e}")
            return None
