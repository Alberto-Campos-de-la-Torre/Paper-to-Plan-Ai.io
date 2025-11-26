import os
import shutil
import json
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging
import asyncio
from typing import List, Dict
from database.db_manager import DBManager
from backend.session_manager import session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import cv2

app = FastAPI()

# ... (existing imports)

# We need a way to pass the loop to the external world or vice versa.
# Let's add a startup event to capture the loop.
global_loop = None

@app.on_event("startup")
async def startup_event():
    global global_loop
    global_loop = asyncio.get_running_loop()

# Directory setup - Use absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
WEB_DIR = os.path.join(BASE_DIR, "web")

# Ensure directories exist
os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"CAPTURES_DIR: {CAPTURES_DIR}")
logger.info(f"WEB_DIR: {WEB_DIR}")

# Mount static files (for serving the PWA)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

# Database Instance
db = DBManager()

# We will use a simple callback mechanism if running in the same process
on_upload_callback = None
on_audio_callback = None

def set_upload_callback(callback):
    global on_upload_callback
    on_upload_callback = callback

def set_audio_callback(callback):
    global on_audio_callback
    on_audio_callback = callback

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        # Map user_id -> List[WebSocket]
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
    """Thread-safe broadcast"""
    if global_loop and manager:
        asyncio.run_coroutine_threadsafe(manager.broadcast(message, user_id), global_loop)


async def verify_user_and_pin(x_auth_user: str = Header(None), x_auth_pin: str = Header(None)):
    logger.info(f"Auth Attempt - User: '{x_auth_user}', PIN: '{x_auth_pin}'")
    if not x_auth_user or not x_auth_pin:
        logger.warning("Auth failed: Missing headers")
        raise HTTPException(status_code=401, detail="Missing Username or PIN")
    
    if not session_manager.verify_user(x_auth_user, x_auth_pin):
        logger.warning(f"Auth failed: Invalid credentials for user '{x_auth_user}'")
        raise HTTPException(status_code=401, detail="Invalid Username or PIN")
    
    return x_auth_user

@app.post("/api/login")
async def login(x_auth_user: str = Header(None), x_auth_pin: str = Header(None)):
    """Validates username and PIN for login."""
    if not x_auth_user or not x_auth_pin:
        raise HTTPException(status_code=400, detail="Username and PIN required")
    
    if session_manager.verify_user(x_auth_user, x_auth_pin):
        return {"status": "success", "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or PIN")

@app.get("/api/users")
async def get_users():
    """Returns a list of all users and their PINs."""
    try:
        users_dict = session_manager.get_all_users()
        # Convert to list of objects for easier frontend handling
        users_list = [{"username": k, "pin": v} for k, v in users_dict.items()]
        return users_list
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep alive / listen for messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        mobile_index_path = os.path.join(WEB_DIR, "mobile_index.html")
        logger.info(f"Attempting to serve mobile_index.html from: {mobile_index_path}")
        with open(mobile_index_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"mobile_index.html not found at: {mobile_index_path}")
        return "<h1>Error: mobile_index.html not found</h1>"

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), user_id: str = Depends(verify_user_and_pin)):
    try:
        # Generate a unique filename
        timestamp = int(datetime.now().timestamp())
        filename = f"mobile_capture_{timestamp}.jpg"
        file_path = os.path.join(CAPTURES_DIR, filename)
        
        # Save the file in captures directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File uploaded from mobile: {file_path} by user {user_id}")
        
        # Trigger callback in main app to process the note
        # Pass absolute path and user_id to the callback
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
        # Generate a unique filename
        timestamp = int(datetime.now().timestamp())
        # Use original extension or default to .webm (common for web recording)
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".webm"
            
        filename = f"voice_note_{timestamp}{ext}"
        # Save in captures dir for simplicity, or a new voice_notes dir
        file_path = os.path.join(CAPTURES_DIR, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Audio uploaded from mobile: {file_path} by user {user_id}")
        
        # Trigger callback
        abs_file_path = os.path.abspath(file_path)
        if on_audio_callback:
            on_audio_callback(abs_file_path, user_id)
            
        return {"status": "success", "filename": filename, "message": "Audio uploaded and processing started."}
        
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes")
async def get_notes(user_id: str = Depends(verify_user_and_pin)):
    """Returns a list of all notes for the authenticated user."""
    try:
        notes = db.get_all_notes(user_id=user_id)
        # Flatten the structure for the mobile app
        flat_notes = []
        for note in notes:
            analysis = note.get('ai_analysis', {}) or {}
            flat_note = {
                "id": note['id'],
                "status": note['status'],
                "implementation_time": note['implementation_time'],
                "title": analysis.get('title', 'Sin Título'),
                "feasibility_score": analysis.get('feasibility_score', 0)
            }
            flat_notes.append(flat_note)
        return flat_notes
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes/{note_id}")
async def get_note_detail(note_id: int, user_id: str = Depends(verify_user_and_pin)):
    """Returns details for a specific note if owned by the user."""
    try:
        note = db.get_note_by_id(note_id, user_id=user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Flatten structure
        analysis = note.get('ai_analysis', {}) or {}
        flat_note = {
            "id": note['id'],
            "status": note['status'],
            "implementation_time": note['implementation_time'],
            "title": analysis.get('title', 'Sin Título'),
            "summary": analysis.get('summary', ''),
            "feasibility_score": analysis.get('feasibility_score', 0),
            "technical_considerations": analysis.get('technical_considerations', []),
            "recommended_stack": analysis.get('recommended_stack', []),
            "raw_text": note.get('raw_text', ''),
            "created_at": note.get('created_at', '')
        }
        return flat_note
    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, user_id: str = Depends(verify_user_and_pin)):
    """Deletes a note if owned by the user."""
    try:
        note = db.get_note_by_id(note_id, user_id=user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found or unauthorized")
        
        success = db.delete_note(note_id)
        if success:
            return {"status": "success", "message": "Note deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete note")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notes/{note_id}/regenerate")
async def regenerate_note(note_id: int, request: dict, user_id: str = Depends(verify_user_and_pin)):
    """Regenerates the AI analysis for a note with new raw text."""
    try:
        note = db.get_note_by_id(note_id, user_id=user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found or unauthorized")
        
        new_text = request.get('raw_text', '')
        if not new_text:
            raise HTTPException(status_code=400, detail="raw_text is required")
        
        # Update the raw text
        db.update_note_text(note_id, new_text)
        
        # Set status to pending for reprocessing
        db.update_note_error(note_id, "Pending regeneration")
        
        # Trigger AI processing callback if available
        if on_upload_callback:
            on_upload_callback(note.get('image_path', ''), user_id)
        
        return {"status": "success", "message": "Note queued for regeneration"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating note {note_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notes/{note_id}/complete")
async def mark_note_completed(note_id: int, user_id: str = Depends(verify_user_and_pin)):
    """Marks a note as completed."""
    try:
        note = db.get_note_by_id(note_id, user_id=user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found or unauthorized")
        
        success = db.mark_as_completed(note_id)
        if success:
            return {"status": "success", "message": "Note marked as completed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark note as completed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking note {note_id} as completed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    return {"status": "running", "service": "PaperToPlan AI Companion"}

@app.get("/api/stats")
async def get_stats(user_id: str = Depends(verify_user_and_pin)):
    """Returns statistics for the user's notes."""
    try:
        notes = db.get_all_notes(user_id=user_id)
        
        # 1. Progress (Completed vs In Progress)
        completed_count = 0
        in_progress_count = 0
        for note in notes:
            if note.get('completed', 0) == 1:
                completed_count += 1
            elif note.get('status') != 'error':
                in_progress_count += 1
                
        # 2. Implementation Time
        time_counts = {"Corto Plazo": 0, "Mediano Plazo": 0, "Largo Plazo": 0}
        for note in notes:
            t = note.get('implementation_time', 'Unknown')
            if not t: t = 'Unknown'
            if "Corto" in t or "Short" in t: time_counts["Corto Plazo"] += 1
            elif "Medio" in t or "Mediano" in t or "Medium" in t: time_counts["Mediano Plazo"] += 1
            elif "Largo" in t or "Long" in t: time_counts["Largo Plazo"] += 1

        # 3. Feasibility Scores
        scores = []
        for note in notes:
            analysis = note.get('ai_analysis', {}) or {}
            try:
                s = int(analysis.get('feasibility_score', 0))
                if s > 0: scores.append(s)
            except: pass
            
        return {
            "progress": {
                "completed": completed_count,
                "in_progress": in_progress_count
            },
            "implementation_time": time_counts,
            "feasibility_scores": scores
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
            
        # Generate filename
        timestamp = int(datetime.now().timestamp())
        filename = f"webcam_capture_{timestamp}.jpg"
        file_path = os.path.join(CAPTURES_DIR, filename)
        
        # Save image
        cv2.imwrite(file_path, frame)
        logger.info(f"Webcam capture saved: {file_path}")
        
        # Trigger processing callback if exists (for original app)
        abs_file_path = os.path.abspath(file_path)
        if on_upload_callback:
            on_upload_callback(abs_file_path, user_id)
            
        return {"status": "success", "filename": filename, "file_path": abs_file_path, "message": "Image captured and processing started."}
        
    except Exception as e:
        logger.error(f"Webcam capture failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

@app.get("/api/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

