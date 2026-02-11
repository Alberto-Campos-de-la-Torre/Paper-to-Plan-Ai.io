import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use absolute path for database to avoid CWD issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_NAME = os.path.join(PROJECT_ROOT, "megirecords.db")

class DBManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize the database with medical tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        pin TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS corrections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_path TEXT NOT NULL,
                        corrected_text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        date_of_birth TEXT,
                        gender TEXT,
                        blood_type TEXT,
                        allergies TEXT,
                        conditions TEXT,
                        cie10_codes TEXT,
                        contact_phone TEXT,
                        contact_email TEXT,
                        emergency_contact TEXT,
                        notes TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS consultations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        user_id TEXT NOT NULL,
                        document_type TEXT DEFAULT 'consultation',
                        raw_text TEXT,
                        ai_analysis TEXT,
                        status TEXT DEFAULT 'pending',
                        image_path TEXT,
                        priority TEXT DEFAULT 'normal',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reviewed_at TIMESTAMP,
                        FOREIGN KEY (patient_id) REFERENCES patients(id)
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prescriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        consultation_id INTEGER,
                        patient_id INTEGER,
                        drug_name TEXT,
                        dose TEXT,
                        frequency TEXT,
                        duration TEXT,
                        instructions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (consultation_id) REFERENCES consultations(id),
                        FOREIGN KEY (patient_id) REFERENCES patients(id)
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lab_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        consultation_id INTEGER,
                        test_name TEXT,
                        value TEXT,
                        unit TEXT,
                        reference_range TEXT,
                        is_abnormal INTEGER DEFAULT 0,
                        test_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (patient_id) REFERENCES patients(id),
                        FOREIGN KEY (consultation_id) REFERENCES consultations(id)
                    )
                """)

                conn.commit()
                logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")

    # ─── User Methods ───────────────────────────────────────────

    def create_user(self, username: str, pin: str) -> bool:
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

    def delete_user(self, username: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def verify_user(self, username: str, pin: str) -> bool:
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
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, pin FROM users ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [{"username": row[0], "pin": row[1]} for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching users: {e}")
            return []

    # ─── Correction Methods ─────────────────────────────────────

    def save_correction(self, image_path: str, corrected_text: str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO corrections (image_path, corrected_text, created_at) VALUES (?, ?, ?)",
                    (image_path, corrected_text, datetime.now())
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving correction: {e}")

    def get_recent_corrections(self, limit: int = 3) -> List[Dict[str, Any]]:
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

    # ─── Patient Methods ────────────────────────────────────────

    def add_patient(self, name: str, date_of_birth: str = None, gender: str = None,
                    blood_type: str = None, allergies: list = None, conditions: list = None,
                    cie10_codes: list = None, contact_phone: str = None, contact_email: str = None,
                    emergency_contact: str = None, notes: str = None, created_by: str = None) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                cursor.execute("""
                    INSERT INTO patients (name, date_of_birth, gender, blood_type, allergies,
                        conditions, cie10_codes, contact_phone, contact_email, emergency_contact,
                        notes, created_by, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, date_of_birth, gender, blood_type,
                    json.dumps(allergies or []),
                    json.dumps(conditions or []),
                    json.dumps(cie10_codes or []),
                    contact_phone, contact_email, emergency_contact,
                    notes, created_by, now, now
                ))
                conn.commit()
                logger.info(f"Patient added: {name} (ID: {cursor.lastrowid})")
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding patient: {e}")
            return -1

    def get_patient_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
                row = cursor.fetchone()
                if row:
                    patient = dict(row)
                    for field in ['allergies', 'conditions', 'cie10_codes']:
                        if patient.get(field):
                            try:
                                patient[field] = json.loads(patient[field])
                            except json.JSONDecodeError:
                                patient[field] = []
                        else:
                            patient[field] = []
                    return patient
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching patient {patient_id}: {e}")
            return None

    def get_all_patients(self) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients ORDER BY updated_at DESC")
                rows = cursor.fetchall()
                patients = []
                for row in rows:
                    patient = dict(row)
                    for field in ['allergies', 'conditions', 'cie10_codes']:
                        if patient.get(field):
                            try:
                                patient[field] = json.loads(patient[field])
                            except json.JSONDecodeError:
                                patient[field] = []
                        else:
                            patient[field] = []
                    patients.append(patient)
                return patients
        except sqlite3.Error as e:
            logger.error(f"Error fetching patients: {e}")
            return []

    def update_patient(self, patient_id: int, **kwargs) -> bool:
        try:
            allowed = ['name', 'date_of_birth', 'gender', 'blood_type', 'allergies',
                        'conditions', 'cie10_codes', 'contact_phone', 'contact_email',
                        'emergency_contact', 'notes']
            updates = []
            values = []
            for key, val in kwargs.items():
                if key in allowed:
                    if key in ['allergies', 'conditions', 'cie10_codes'] and isinstance(val, list):
                        val = json.dumps(val)
                    updates.append(f"{key} = ?")
                    values.append(val)
            if not updates:
                return False
            updates.append("updated_at = ?")
            values.append(datetime.now())
            values.append(patient_id)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE patients SET {', '.join(updates)} WHERE id = ?",
                    values
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating patient {patient_id}: {e}")
            return False

    def search_patients(self, query: str) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                search = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM patients
                    WHERE name LIKE ? OR contact_phone LIKE ? OR contact_email LIKE ?
                    ORDER BY name ASC
                """, (search, search, search))
                rows = cursor.fetchall()
                patients = []
                for row in rows:
                    patient = dict(row)
                    for field in ['allergies', 'conditions', 'cie10_codes']:
                        if patient.get(field):
                            try:
                                patient[field] = json.loads(patient[field])
                            except json.JSONDecodeError:
                                patient[field] = []
                        else:
                            patient[field] = []
                    patients.append(patient)
                return patients
        except sqlite3.Error as e:
            logger.error(f"Error searching patients: {e}")
            return []

    def delete_patient(self, patient_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting patient {patient_id}: {e}")
            return False

    # ─── Consultation Methods ───────────────────────────────────

    def add_consultation(self, user_id: str, patient_id: int = None, image_path: str = "",
                         raw_text: str = "", document_type: str = "consultation") -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO consultations (patient_id, user_id, document_type, image_path,
                        raw_text, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'pending', ?)
                """, (patient_id, user_id, document_type, image_path, raw_text, datetime.now()))
                conn.commit()
                logger.info(f"Consultation added with ID: {cursor.lastrowid}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding consultation: {e}")
            return -1

    def get_consultation_by_id(self, consultation_id: int, user_id: str = None) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM consultations WHERE id = ?", (consultation_id,))
                row = cursor.fetchone()
                if row:
                    consultation = dict(row)
                    if user_id and consultation.get('user_id') != user_id:
                        return None
                    if consultation.get('ai_analysis'):
                        try:
                            consultation['ai_analysis'] = json.loads(consultation['ai_analysis'])
                        except json.JSONDecodeError:
                            consultation['ai_analysis'] = {}
                    return consultation
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching consultation {consultation_id}: {e}")
            return None

    def get_consultations_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM consultations WHERE patient_id = ? ORDER BY created_at DESC",
                    (patient_id,)
                )
                rows = cursor.fetchall()
                consultations = []
                for row in rows:
                    c = dict(row)
                    if c.get('ai_analysis'):
                        try:
                            c['ai_analysis'] = json.loads(c['ai_analysis'])
                        except json.JSONDecodeError:
                            c['ai_analysis'] = {}
                    consultations.append(c)
                return consultations
        except sqlite3.Error as e:
            logger.error(f"Error fetching consultations for patient {patient_id}: {e}")
            return []

    def get_all_consultations(self, user_id: str = None) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if user_id:
                    cursor.execute(
                        "SELECT * FROM consultations WHERE user_id = ? ORDER BY created_at DESC",
                        (user_id,)
                    )
                else:
                    cursor.execute("SELECT * FROM consultations ORDER BY created_at DESC")
                rows = cursor.fetchall()
                consultations = []
                for row in rows:
                    c = dict(row)
                    if c.get('ai_analysis'):
                        try:
                            c['ai_analysis'] = json.loads(c['ai_analysis'])
                        except json.JSONDecodeError:
                            c['ai_analysis'] = {}
                    consultations.append(c)
                return consultations
        except sqlite3.Error as e:
            logger.error(f"Error fetching consultations: {e}")
            return []

    def update_consultation_analysis(self, consultation_id: int, analysis: Dict[str, Any]):
        try:
            doc_type = analysis.get("document_type", "consultation")
            analysis_json = json.dumps(analysis)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE consultations
                    SET ai_analysis = ?, status = 'processed', document_type = ?
                    WHERE id = ?
                """, (analysis_json, doc_type, consultation_id))
                conn.commit()
                logger.info(f"Consultation {consultation_id} updated with analysis.")
        except sqlite3.Error as e:
            logger.error(f"Error updating consultation {consultation_id}: {e}")

    def update_consultation_status(self, consultation_id: int, status: str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE consultations SET status = ? WHERE id = ?",
                    (status, consultation_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating consultation status {consultation_id}: {e}")

    def update_consultation_text(self, consultation_id: int, text: str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE consultations SET raw_text = ? WHERE id = ?",
                    (text, consultation_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating consultation text {consultation_id}: {e}")

    def update_consultation_error(self, consultation_id: int, error_msg: str):
        try:
            error_json = json.dumps({"error": error_msg, "summary": "Error de Procesamiento"})
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE consultations
                    SET ai_analysis = ?, status = 'error'
                    WHERE id = ?
                """, (error_json, consultation_id))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error marking consultation {consultation_id} as error: {e}")

    def mark_as_reviewed(self, consultation_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE consultations SET status = 'reviewed', reviewed_at = ?
                    WHERE id = ?
                """, (datetime.now(), consultation_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error marking consultation {consultation_id} as reviewed: {e}")
            return False

    def link_consultation_patient(self, consultation_id: int, patient_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE consultations SET patient_id = ? WHERE id = ?",
                    (patient_id, consultation_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error linking consultation {consultation_id} to patient {patient_id}: {e}")
            return False

    def delete_consultation(self, consultation_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT image_path FROM consultations WHERE id = ?", (consultation_id,))
                row = cursor.fetchone()
                cursor.execute("DELETE FROM prescriptions WHERE consultation_id = ?", (consultation_id,))
                cursor.execute("DELETE FROM lab_results WHERE consultation_id = ?", (consultation_id,))
                cursor.execute("DELETE FROM consultations WHERE id = ?", (consultation_id,))
                conn.commit()
                if row and row[0]:
                    try:
                        if os.path.exists(row[0]):
                            os.remove(row[0])
                    except OSError:
                        pass
                return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting consultation {consultation_id}: {e}")
            return False

    # ─── Prescription Methods ───────────────────────────────────

    def add_prescription(self, consultation_id: int, patient_id: int, drug_name: str,
                         dose: str = "", frequency: str = "", duration: str = "",
                         instructions: str = "") -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO prescriptions (consultation_id, patient_id, drug_name, dose,
                        frequency, duration, instructions, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (consultation_id, patient_id, drug_name, dose, frequency, duration,
                      instructions, datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding prescription: {e}")
            return -1

    def get_prescriptions_by_consultation(self, consultation_id: int) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM prescriptions WHERE consultation_id = ? ORDER BY created_at DESC",
                    (consultation_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching prescriptions: {e}")
            return []

    def get_prescriptions_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM prescriptions WHERE patient_id = ? ORDER BY created_at DESC",
                    (patient_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching prescriptions for patient {patient_id}: {e}")
            return []

    # ─── Lab Result Methods ─────────────────────────────────────

    def add_lab_result(self, patient_id: int, consultation_id: int = None, test_name: str = "",
                       value: str = "", unit: str = "", reference_range: str = "",
                       is_abnormal: int = 0, test_date: str = None) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lab_results (patient_id, consultation_id, test_name, value,
                        unit, reference_range, is_abnormal, test_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (patient_id, consultation_id, test_name, value, unit,
                      reference_range, is_abnormal, test_date, datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding lab result: {e}")
            return -1

    def get_lab_results_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM lab_results WHERE patient_id = ? ORDER BY created_at DESC",
                    (patient_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching lab results for patient {patient_id}: {e}")
            return []

    # ─── Stats ──────────────────────────────────────────────────

    def get_medical_stats(self, user_id: str = None) -> Dict[str, Any]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Total patients
                cursor.execute("SELECT COUNT(*) FROM patients")
                total_patients = cursor.fetchone()[0]

                # Total consultations
                if user_id:
                    cursor.execute("SELECT COUNT(*) FROM consultations WHERE user_id = ?", (user_id,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM consultations")
                total_consultations = cursor.fetchone()[0]

                # Document type distribution
                if user_id:
                    cursor.execute("""
                        SELECT document_type, COUNT(*) FROM consultations
                        WHERE user_id = ? GROUP BY document_type
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT document_type, COUNT(*) FROM consultations
                        GROUP BY document_type
                    """)
                document_types = {row[0]: row[1] for row in cursor.fetchall()}

                # Consultations by status
                if user_id:
                    cursor.execute("""
                        SELECT status, COUNT(*) FROM consultations
                        WHERE user_id = ? GROUP BY status
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT status, COUNT(*) FROM consultations
                        GROUP BY status
                    """)
                status_counts = {row[0]: row[1] for row in cursor.fetchall()}

                return {
                    "total_patients": total_patients,
                    "total_consultations": total_consultations,
                    "document_types": document_types,
                    "consultations_by_status": status_counts
                }
        except sqlite3.Error as e:
            logger.error(f"Error fetching medical stats: {e}")
            return {
                "total_patients": 0,
                "total_consultations": 0,
                "document_types": {},
                "consultations_by_status": {}
            }
