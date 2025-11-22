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
                        raw_text TEXT,
                        ai_analysis TEXT,
                        status TEXT DEFAULT 'pending',
                        implementation_time TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")

    def add_note(self, raw_text: str, status: str = 'pending') -> int:
        """Add a new note with raw text. Returns the new note ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notes (raw_text, status, created_at)
                    VALUES (?, ?, ?)
                """, (raw_text, status, datetime.now()))
                conn.commit()
                logger.info(f"Note added with ID: {cursor.lastrowid}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding note: {e}")
            return -1

    def update_note_text(self, note_id: int, text: str):
        """Update the raw text of a note."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET raw_text = ? WHERE id = ?", (text, note_id))
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

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Retrieve all notes ordered by creation date (newest first)."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
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

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single note by ID."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()
                if row:
                    note = dict(row)
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
