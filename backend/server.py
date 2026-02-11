import os
import shutil
import json
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel
from database.db_manager import DBManager
from backend.session_manager import session_manager
from backend.document_generator import MedicalDocumentGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import cv2

app = FastAPI()

# Capture the event loop at startup for thread-safe broadcasts
global_loop = None

@app.on_event("startup")
async def startup_event():
    global global_loop
    global_loop = asyncio.get_running_loop()

# Directory setup - Use absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
WEB_DIR = os.path.join(BASE_DIR, "web")

os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"CAPTURES_DIR: {CAPTURES_DIR}")
logger.info(f"WEB_DIR: {WEB_DIR}")

# Mount static files (for serving the PWA)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

# Database Instance
db = DBManager()

# Document Generator
doc_generator = MedicalDocumentGenerator()

# Callbacks for processing (set by main app)
on_upload_callback = None
on_audio_callback = None

def set_upload_callback(callback):
    global on_upload_callback
    on_upload_callback = callback

def set_audio_callback(callback):
    global on_audio_callback
    on_audio_callback = callback


# ─── Pydantic Models ─────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = []
    conditions: Optional[List[str]] = []
    cie10_codes: Optional[List[str]] = []
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    emergency_contact: Optional[str] = None
    notes: Optional[str] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    cie10_codes: Optional[List[str]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    emergency_contact: Optional[str] = None
    notes: Optional[str] = None

class TextConsultation(BaseModel):
    text: str
    patient_id: Optional[int] = None

class LinkPatient(BaseModel):
    patient_id: int

class RegenerateRequest(BaseModel):
    raw_text: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    pin: str


# ─── WebSocket Manager ───────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def broadcast(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending WS message: {e}")

manager = ConnectionManager()

def broadcast_update_sync(user_id: str, message: str):
    """Thread-safe broadcast."""
    if global_loop and manager:
        asyncio.run_coroutine_threadsafe(manager.broadcast(message, user_id), global_loop)


# ─── Auth ─────────────────────────────────────────────────────

async def verify_user_and_pin(x_auth_user: str = Header(None), x_auth_pin: str = Header(None)):
    if not x_auth_user or not x_auth_pin:
        raise HTTPException(status_code=401, detail="Missing Username or PIN")
    if not session_manager.verify_user(x_auth_user, x_auth_pin):
        raise HTTPException(status_code=401, detail="Invalid Username or PIN")
    return x_auth_user

@app.post("/api/login")
async def login(x_auth_user: str = Header(None), x_auth_pin: str = Header(None)):
    if not x_auth_user or not x_auth_pin:
        raise HTTPException(status_code=400, detail="Username and PIN required")
    if session_manager.verify_user(x_auth_user, x_auth_pin):
        return {"status": "success", "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid username or PIN")


# ─── Users ────────────────────────────────────────────────────

@app.get("/api/users")
async def get_users():
    try:
        users_dict = session_manager.get_all_users()
        return [{"username": k, "pin": v} for k, v in users_dict.items()]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users")
async def create_user(data: UserCreate):
    try:
        if session_manager.user_exists(data.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        success = session_manager.add_user(data.username, data.pin)
        if success:
            return {"status": "success", "username": data.username, "pin": data.pin}
        raise HTTPException(status_code=500, detail="Failed to create user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{username}")
async def delete_user(username: str):
    try:
        success = session_manager.remove_user(username)
        if success:
            return {"status": "success", "message": f"User {username} deleted"}
        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── WebSocket ────────────────────────────────────────────────

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# ─── Mobile Root ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        mobile_index_path = os.path.join(WEB_DIR, "mobile_index.html")
        with open(mobile_index_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: mobile_index.html not found</h1>"


# ─── Patients ─────────────────────────────────────────────────

@app.post("/api/patients")
async def create_patient(patient: PatientCreate, user_id: str = Depends(verify_user_and_pin)):
    try:
        patient_id = db.add_patient(
            name=patient.name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender,
            blood_type=patient.blood_type,
            allergies=patient.allergies,
            conditions=patient.conditions,
            cie10_codes=patient.cie10_codes,
            contact_phone=patient.contact_phone,
            contact_email=patient.contact_email,
            emergency_contact=patient.emergency_contact,
            notes=patient.notes,
            created_by=user_id
        )
        if patient_id < 0:
            raise HTTPException(status_code=500, detail="Failed to create patient")
        return {"status": "success", "patient_id": patient_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients")
async def get_patients(user_id: str = Depends(verify_user_and_pin)):
    try:
        patients = db.get_all_patients()
        return patients
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/search")
async def search_patients(q: str = "", user_id: str = Depends(verify_user_and_pin)):
    try:
        if not q:
            return db.get_all_patients()
        return db.search_patients(q)
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        patient = db.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/patients/{patient_id}")
async def update_patient(patient_id: int, data: PatientUpdate, user_id: str = Depends(verify_user_and_pin)):
    try:
        patient = db.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        success = db.update_patient(patient_id, **update_data)
        if success:
            return {"status": "success", "message": "Patient updated"}
        raise HTTPException(status_code=500, detail="Failed to update patient")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        patient = db.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        success = db.delete_patient(patient_id)
        if success:
            return {"status": "success", "message": "Patient deleted"}
        raise HTTPException(status_code=500, detail="Failed to delete patient")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/{patient_id}/consultations")
async def get_patient_consultations(patient_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        patient = db.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        consultations = db.get_consultations_by_patient(patient_id)
        return _flatten_consultations(consultations)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching consultations for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/{patient_id}/prescriptions")
async def get_patient_prescriptions(patient_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        return db.get_prescriptions_by_patient(patient_id)
    except Exception as e:
        logger.error(f"Error fetching prescriptions for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/{patient_id}/lab-results")
async def get_patient_lab_results(patient_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        return db.get_lab_results_by_patient(patient_id)
    except Exception as e:
        logger.error(f"Error fetching lab results for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Consultations ────────────────────────────────────────────

def _flatten_consultation(c: Dict) -> Dict:
    """Flatten a consultation for API response."""
    analysis = c.get('ai_analysis', {}) or {}
    if isinstance(analysis, str):
        try:
            analysis = json.loads(analysis)
        except Exception:
            analysis = {}
    return {
        "id": c['id'],
        "patient_id": c.get('patient_id'),
        "user_id": c.get('user_id', ''),
        "document_type": c.get('document_type', 'consultation'),
        "status": c.get('status', 'pending'),
        "priority": c.get('priority', 'normal'),
        "summary": analysis.get('summary', ''),
        "confidence_score": analysis.get('confidence_score', 0),
        "created_at": c.get('created_at', ''),
        "reviewed_at": c.get('reviewed_at'),
    }

def _flatten_consultations(consultations: List[Dict]) -> List[Dict]:
    return [_flatten_consultation(c) for c in consultations]

@app.get("/api/consultations")
async def get_consultations(user_id: str = Depends(verify_user_and_pin)):
    try:
        consultations = db.get_all_consultations(user_id=user_id)
        return _flatten_consultations(consultations)
    except Exception as e:
        logger.error(f"Error fetching consultations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultations/{consultation_id}")
async def get_consultation_detail(consultation_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found")

        analysis = c.get('ai_analysis', {}) or {}
        if isinstance(analysis, str):
            try:
                analysis = json.loads(analysis)
            except Exception:
                analysis = {}

        # Get patient info if linked
        patient = None
        if c.get('patient_id'):
            patient = db.get_patient_by_id(c['patient_id'])

        # Get prescriptions for this consultation
        prescriptions = db.get_prescriptions_by_consultation(consultation_id)

        return {
            "id": c['id'],
            "patient_id": c.get('patient_id'),
            "patient": patient,
            "user_id": c.get('user_id', ''),
            "document_type": c.get('document_type', 'consultation'),
            "status": c.get('status', 'pending'),
            "priority": c.get('priority', 'normal'),
            "raw_text": c.get('raw_text', ''),
            "image_path": c.get('image_path', ''),
            "ai_analysis": analysis,
            "prescriptions": prescriptions,
            "created_at": c.get('created_at', ''),
            "reviewed_at": c.get('reviewed_at'),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching consultation {consultation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultations/text")
async def create_text_consultation(data: TextConsultation, user_id: str = Depends(verify_user_and_pin)):
    try:
        consultation_id = db.add_consultation(
            user_id=user_id,
            patient_id=data.patient_id,
            raw_text=data.text
        )
        if consultation_id < 0:
            raise HTTPException(status_code=500, detail="Failed to create consultation")

        # Process in background
        def process():
            _process_text_consultation(consultation_id, data.text, user_id, data.patient_id)

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

        return {"status": "success", "consultation_id": consultation_id, "message": "Consultation created and processing started."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating text consultation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/consultations/{consultation_id}")
async def delete_consultation(consultation_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found or unauthorized")
        success = db.delete_consultation(consultation_id)
        if success:
            return {"status": "success", "message": "Consultation deleted"}
        raise HTTPException(status_code=500, detail="Failed to delete consultation")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting consultation {consultation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultations/{consultation_id}/regenerate")
async def regenerate_consultation(consultation_id: int, data: RegenerateRequest,
                                   user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found or unauthorized")

        raw_text = data.raw_text if data.raw_text else c.get('raw_text', '')
        if not raw_text:
            raise HTTPException(status_code=400, detail="No text available for regeneration")

        if data.raw_text:
            db.update_consultation_text(consultation_id, raw_text)

        db.update_consultation_status(consultation_id, 'processing')

        patient_id = c.get('patient_id')

        def process():
            _process_text_consultation(consultation_id, raw_text, user_id, patient_id, is_regeneration=True)

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

        return {"status": "success", "message": "Consultation queued for regeneration"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating consultation {consultation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultations/{consultation_id}/review")
async def review_consultation(consultation_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found or unauthorized")
        success = db.mark_as_reviewed(consultation_id)
        if success:
            return {"status": "success", "message": "Consultation marked as reviewed"}
        raise HTTPException(status_code=500, detail="Failed to mark as reviewed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing consultation {consultation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultations/{consultation_id}/link-patient")
async def link_consultation_to_patient(consultation_id: int, data: LinkPatient,
                                        user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found or unauthorized")
        patient = db.get_patient_by_id(data.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        success = db.link_consultation_patient(consultation_id, data.patient_id)
        if success:
            return {"status": "success", "message": "Consultation linked to patient"}
        raise HTTPException(status_code=500, detail="Failed to link consultation")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking consultation {consultation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Documents (PDF) ─────────────────────────────────────────

@app.get("/api/documents/medical-note/{consultation_id}")
async def download_medical_note(consultation_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found")

        patient = None
        if c.get('patient_id'):
            patient = db.get_patient_by_id(c['patient_id'])

        pdf_bytes = doc_generator.generate_medical_note(c, patient, doctor=user_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=nota_medica_{consultation_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating medical note PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/prescription/{consultation_id}")
async def download_prescription(consultation_id: int, user_id: str = Depends(verify_user_and_pin)):
    try:
        c = db.get_consultation_by_id(consultation_id, user_id=user_id)
        if not c:
            raise HTTPException(status_code=404, detail="Consultation not found")

        patient = None
        if c.get('patient_id'):
            patient = db.get_patient_by_id(c['patient_id'])

        prescriptions = db.get_prescriptions_by_consultation(consultation_id)
        if not prescriptions:
            # Try extracting from analysis
            analysis = c.get('ai_analysis', {}) or {}
            if isinstance(analysis, str):
                try:
                    analysis = json.loads(analysis)
                except Exception:
                    analysis = {}
            plan = analysis.get('plan', {})
            if isinstance(plan, dict):
                meds = plan.get('medications', [])
                prescriptions = [m for m in meds if isinstance(m, dict) and m.get('drug_name')]

        if not prescriptions:
            raise HTTPException(status_code=404, detail="No prescriptions found for this consultation")

        pdf_bytes = doc_generator.generate_prescription(c, patient, prescriptions, doctor=user_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=receta_{consultation_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prescription PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Upload & Capture ────────────────────────────────────────

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), user_id: str = Depends(verify_user_and_pin)):
    try:
        timestamp = int(datetime.now().timestamp())
        filename = f"mobile_capture_{timestamp}.jpg"
        file_path = os.path.join(CAPTURES_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded from mobile: {file_path} by user {user_id}")

        abs_file_path = os.path.abspath(file_path)
        if on_upload_callback:
            on_upload_callback(abs_file_path, user_id)

        return {"status": "success", "filename": filename, "message": "Image uploaded and processing started."}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload_audio")
async def upload_audio(file: UploadFile = File(...), user_id: str = Depends(verify_user_and_pin)):
    try:
        timestamp = int(datetime.now().timestamp())
        ext = os.path.splitext(file.filename)[1] if file.filename else ".webm"
        if not ext:
            ext = ".webm"
        filename = f"voice_note_{timestamp}{ext}"
        file_path = os.path.join(CAPTURES_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Audio uploaded from mobile: {file_path} by user {user_id}")

        abs_file_path = os.path.abspath(file_path)
        if on_audio_callback:
            on_audio_callback(abs_file_path, user_id)

        return {"status": "success", "filename": filename, "message": "Audio uploaded and processing started."}
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Camera ───────────────────────────────────────────────────

class CameraManager:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()

    def get_frame(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(0)
            success, frame = self.camera.read()
            if not success:
                return None
            ret, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()

    def capture_image(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
            else:
                ret, frame = self.camera.read()
            if not ret:
                raise Exception("Could not read frame")
            return frame

    def release(self):
        with self.lock:
            if self.camera:
                self.camera.release()
                self.camera = None

camera_manager = CameraManager()

def generate_frames():
    while True:
        frame = camera_manager.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/api/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/api/capture_webcam")
async def capture_webcam(user_id: str = Depends(verify_user_and_pin)):
    try:
        frame = camera_manager.capture_image()
        timestamp = int(datetime.now().timestamp())
        filename = f"webcam_capture_{timestamp}.jpg"
        file_path = os.path.join(CAPTURES_DIR, filename)

        cv2.imwrite(file_path, frame)
        logger.info(f"Webcam capture saved: {file_path}")

        abs_file_path = os.path.abspath(file_path)
        if on_upload_callback:
            on_upload_callback(abs_file_path, user_id)

        return {"status": "success", "filename": filename, "file_path": abs_file_path,
                "message": "Image captured and processing started."}
    except Exception as e:
        logger.error(f"Webcam capture failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Stats & Status ──────────────────────────────────────────

@app.get("/api/status")
async def get_status():
    return {"status": "running", "service": "MEGI Records - Expedientes Médicos Digitales"}

@app.get("/api/stats")
async def get_stats(user_id: str = Depends(verify_user_and_pin)):
    try:
        return db.get_medical_stats(user_id=user_id)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Background Processing ───────────────────────────────────

def _process_text_consultation(consultation_id: int, text: str, user_id: str,
                                patient_id: int = None, is_regeneration: bool = False):
    """Process a text consultation with AI analysis in background."""
    try:
        from backend.ai_manager import AIEngine
        ai = AIEngine()

        if not is_regeneration:
            db.update_consultation_status(consultation_id, 'processing')

        broadcast_update_sync(user_id, json.dumps({
            "type": "consultation_update",
            "consultation_id": consultation_id,
            "status": "processing"
        }))

        # Classify document
        classification = ai.classify_document(text)
        doc_type = classification.get('document_type', 'consultation')

        # Full medical analysis
        analysis = ai.analyze_medical_text(text)

        if 'error' in analysis:
            db.update_consultation_error(consultation_id, analysis['error'])
            broadcast_update_sync(user_id, json.dumps({
                "type": "consultation_update",
                "consultation_id": consultation_id,
                "status": "error",
                "error": analysis['error']
            }))
            return

        analysis['document_type'] = doc_type
        db.update_consultation_analysis(consultation_id, analysis)

        # Extract and save prescriptions
        if patient_id:
            prescriptions = ai.extract_prescriptions(analysis)
            for rx in prescriptions:
                db.add_prescription(
                    consultation_id=consultation_id,
                    patient_id=patient_id,
                    drug_name=rx.get('drug_name', ''),
                    dose=rx.get('dose', ''),
                    frequency=rx.get('frequency', ''),
                    duration=rx.get('duration', ''),
                    instructions=rx.get('instructions', '')
                )

            # Extract and save lab results
            lab_results = ai.extract_lab_results(analysis)
            for lab in lab_results:
                db.add_lab_result(
                    patient_id=patient_id,
                    consultation_id=consultation_id,
                    test_name=lab.get('test_name', ''),
                    value=lab.get('value', ''),
                    unit=lab.get('unit', ''),
                    reference_range=lab.get('reference_range', ''),
                    is_abnormal=lab.get('is_abnormal', 0)
                )

        broadcast_update_sync(user_id, json.dumps({
            "type": "consultation_update",
            "consultation_id": consultation_id,
            "status": "processed"
        }))

        logger.info(f"Consultation {consultation_id} processed successfully.")

    except Exception as e:
        logger.error(f"Error processing consultation {consultation_id}: {e}")
        db.update_consultation_error(consultation_id, str(e))
        broadcast_update_sync(user_id, json.dumps({
            "type": "consultation_update",
            "consultation_id": consultation_id,
            "status": "error",
            "error": str(e)
        }))


def process_medical_document_background(image_path: str, user_id: str, patient_id: int = None):
    """Process a medical document image with OCR + AI analysis. Called from callbacks."""
    try:
        from backend.ai_manager import AIEngine
        ai = AIEngine()

        # Create consultation record
        consultation_id = db.add_consultation(
            user_id=user_id,
            patient_id=patient_id,
            image_path=image_path
        )

        if consultation_id < 0:
            logger.error("Failed to create consultation record")
            return

        db.update_consultation_status(consultation_id, 'processing')
        broadcast_update_sync(user_id, json.dumps({
            "type": "consultation_update",
            "consultation_id": consultation_id,
            "status": "processing"
        }))

        # OCR
        examples = db.get_recent_corrections(limit=3)
        raw_text = ai.extract_text_from_image(image_path, examples)

        if raw_text.startswith("Error"):
            db.update_consultation_error(consultation_id, raw_text)
            broadcast_update_sync(user_id, json.dumps({
                "type": "consultation_update",
                "consultation_id": consultation_id,
                "status": "error",
                "error": raw_text
            }))
            return

        db.update_consultation_text(consultation_id, raw_text)

        # Classify
        classification = ai.classify_document(raw_text)
        doc_type = classification.get('document_type', 'consultation')

        # Full analysis
        analysis = ai.analyze_medical_text(raw_text)

        if 'error' in analysis:
            db.update_consultation_error(consultation_id, analysis['error'])
            broadcast_update_sync(user_id, json.dumps({
                "type": "consultation_update",
                "consultation_id": consultation_id,
                "status": "error",
                "error": analysis['error']
            }))
            return

        analysis['document_type'] = doc_type
        db.update_consultation_analysis(consultation_id, analysis)

        # Extract prescriptions and lab results if patient is linked
        if patient_id:
            prescriptions = ai.extract_prescriptions(analysis)
            for rx in prescriptions:
                db.add_prescription(
                    consultation_id=consultation_id,
                    patient_id=patient_id,
                    drug_name=rx.get('drug_name', ''),
                    dose=rx.get('dose', ''),
                    frequency=rx.get('frequency', ''),
                    duration=rx.get('duration', ''),
                    instructions=rx.get('instructions', '')
                )

            lab_results = ai.extract_lab_results(analysis)
            for lab in lab_results:
                db.add_lab_result(
                    patient_id=patient_id,
                    consultation_id=consultation_id,
                    test_name=lab.get('test_name', ''),
                    value=lab.get('value', ''),
                    unit=lab.get('unit', ''),
                    reference_range=lab.get('reference_range', ''),
                    is_abnormal=lab.get('is_abnormal', 0)
                )

        broadcast_update_sync(user_id, json.dumps({
            "type": "consultation_update",
            "consultation_id": consultation_id,
            "status": "processed"
        }))

        logger.info(f"Medical document {consultation_id} processed successfully.")

    except Exception as e:
        logger.error(f"Error processing medical document: {e}")
