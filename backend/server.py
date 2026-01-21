import os
import shutil
import json
import cv2
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging
import asyncio
from typing import List, Dict
import sys
import time

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

WEB_DIR = os.path.join(BASE_DIR, "web")
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)

from database.db_manager import DBManager
from backend.ai_manager import AIEngine
from backend.session_manager import session_manager
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Instance
db = DBManager()

# FastAPI App
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Engine Instance (Singleton)
_ai_engine = None

def get_ai_engine():
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine

# --- Background Tasks ---

async def process_image_note_background(image_path: str, user_id: str):
    """Background task to process image note: extract text -> analyze -> update DB."""
    try:
        logger.info(f"Starting background processing for image: {image_path}")
        
        # Create initial note entry in DB
        # Create initial note entry in DB
        note_id = db.add_note(
            image_path=image_path,
            raw_text="Procesando...",
            user_id=user_id
        )
        
        if note_id == -1:
            logger.error("Failed to create note in DB")
            return

        engine = get_ai_engine()
        
        # 1. Extract Text
        logger.info(f"Extracting text from {image_path}...")
        extracted_text = engine.extract_text_from_image(image_path)
        
        # Update DB with raw text
        db.update_note_text(note_id, extracted_text)
        
        # 2. Analyze Text
        logger.info(f"Analyzing text for note {note_id}...")
        analysis = engine.analyze_text(extracted_text)
        
        # Update DB with analysis
        db.update_note_analysis(note_id, analysis)
        
        # Notify user via WebSocket
        # Notify user via WebSocket
        await manager.broadcast("processing_complete", user_id)
        logger.info(f"Background processing complete for note {note_id}")
        
    except Exception as e:
        logger.error(f"Error in background processing for note {note_id if 'note_id' in locals() else 'unknown'}: {e}")
        if 'note_id' in locals():
            db.update_note_error(note_id, str(e))

async def process_text_note_background(note_id: int, text: str, user_id: str):
    """Background task to process text note with AI."""
    try:
        logger.info(f"Starting background processing for note {note_id}")
        engine = get_ai_engine()
        analysis = engine.analyze_text(text)
        
        # Update DB with analysis
        db.update_note_analysis(note_id, analysis)
        
        # Notify user via WebSocket
        await manager.broadcast("processing_complete", user_id)
        logger.info(f"Background processing complete for note {note_id}")
        
    except Exception as e:
        logger.error(f"Error in background processing for note {note_id}: {e}")
        db.update_note_error(note_id, str(e))

# ... (existing endpoints)

class CreateUserRequest(BaseModel):
    username: str
    pin: str

@app.post("/api/users")
async def create_user(request: CreateUserRequest):
    """Creates a new user."""
    try:
        if session_manager.user_exists(request.username):
             raise HTTPException(status_code=400, detail="User already exists")
        
        success = session_manager.add_user(request.username, request.pin)
        if success:
            return {"status": "success", "message": "User created"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{username}")
async def delete_user(username: str):
    """Deletes a user."""
    try:
        if not session_manager.user_exists(username):
             raise HTTPException(status_code=404, detail="User not found")
        
        success = session_manager.remove_user(username)
        if success:
            return {"status": "success", "message": "User deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ConfigRequest(BaseModel):
    host: str
    logic_model: str
    vision_model: str

@app.get("/api/config")
async def get_config():
    """Get current AI configuration."""
    try:
        from backend.config_manager import config_manager
        config = config_manager.get_all()
        return config
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def update_config(request: ConfigRequest):
    """Update AI configuration."""
    try:
        from backend.config_manager import config_manager
        
        # Save to persistent config
        config_manager.update({
            'host': request.host,
            'logic_model': request.logic_model,
            'vision_model': request.vision_model
        })
        
        # Update current engine instance
        engine = get_ai_engine()
        import ollama
        engine.host = request.host
        engine.client = ollama.Client(host=request.host)
        engine.logic_model = request.logic_model
        engine.vision_model = request.vision_model
        
        logger.info(f"Config updated and saved: Host={request.host}, Logic={request.logic_model}, Vision={request.vision_model}")
        return {"status": "success", "message": "Configuration updated and saved"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/test")
async def test_config():
    """Test connection to Ollama."""
    try:
        engine = get_ai_engine()
        # Simple test: list models or just check if client is reachable
        models = engine.client.list()
        return {"success": True, "message": "Ollama connected", "models": [m.get('model', m.get('name', 'unknown')) for m in models['models']]}
    except Exception as e:
        logger.error(f"Ollama connection test failed: {e}")
        return {"success": False, "errors": [str(e)]}

# ... (rest of the file)

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

# Global callbacks
on_upload_callback = None
on_audio_callback = None

def set_upload_callback(callback):
    global on_upload_callback
    on_upload_callback = callback

def set_audio_callback(callback):
    global on_audio_callback
    on_audio_callback = callback

# ... (existing imports and setup)

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
        else:
            # Standalone mode: trigger background processing directly
            logger.info("Standalone mode: Triggering background processing for image upload.")
            asyncio.create_task(process_image_note_background(abs_file_path, user_id))
            
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
        else:
            # Standalone mode: trigger background processing directly (assuming text processing for now or add audio processing)
            logger.info("Standalone mode: Triggering background processing for audio upload.")
            # TODO: Implement audio processing background task. For now, just log it.
            # asyncio.create_task(process_audio_note_background(abs_file_path, user_id))
            
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
            # Note: on_upload_callback expects image_path, but for regeneration we might need a different flow
            # or the callback handles text-only if image_path is None/empty?
            # Looking at main.py, on_mobile_upload calls process_new_note which calls ai_pipeline.
            # ai_pipeline does OCR then text analysis.
            # For regeneration, we just want text analysis.
            # The main app's regenerate_note (in main.py) calls ai_pipeline_text_only.
            # But here we are in server.py.
            # If we are in standalone mode, we can call process_text_note_background.
            # If we are in desktop app mode, on_upload_callback is set.
            # However, on_upload_callback signature is (file_path, user_id).
            # We can't easily signal "text only" via this callback unless we pass a special flag or path.
            # BUT, the desktop app has its own regenerate logic in UI.
            # If this endpoint is called, it's likely from the React UI (Standalone or Desktop Hybrid).
            # If React UI calls this, we should probably just do the work in background here regardless of callback?
            # OR, if callback is set, we assume the main python app handles it?
            # The main python app DOES NOT have a callback for "regenerate". It has one for "upload".
            # So calling on_upload_callback here is actually WRONG for regeneration because it would re-OCR.
            
            # FIX: Always use background task for regeneration in server.py, 
            # unless we want to add a specific on_regenerate_callback.
            # Given the current architecture, server.py should handle the logic if it can.
            asyncio.create_task(process_text_note_background(note_id, new_text, user_id))
        else:
            # Standalone mode
            asyncio.create_task(process_text_note_background(note_id, new_text, user_id))
        
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
        self.last_frame = None

    def open_camera(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                logger.info("Opening camera...")
                # Try index 0 with V4L2
                self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not self.camera.isOpened():
                     logger.warning("Camera 0 (V4L2) failed, trying Camera 1 (V4L2)")
                     self.camera = cv2.VideoCapture(1, cv2.CAP_V4L2)
                
                if not self.camera.isOpened():
                     logger.warning("V4L2 failed, trying default backend (CAP_ANY) on index 0")
                     self.camera = cv2.VideoCapture(0, cv2.CAP_ANY)

                if not self.camera.isOpened():
                    logger.error("Could not open any camera.")
                    self.camera = None
                else:
                    # Warmup
                    for _ in range(5):
                        self.camera.read()
                    logger.info("Camera opened successfully.")

    def get_frame(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                return None

            success, frame = self.camera.read()
            if not success:
                logger.warning("Failed to read frame from camera")
                return None
            
            # Cache the frame for capture_image
            self.last_frame = frame.copy()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()

    def capture_image(self):
        with self.lock:
            # If we have a recent frame from the stream, use it!
            if self.last_frame is not None:
                logger.info("Capturing image from active stream buffer")
                return self.last_frame.copy()
            
            # If no stream is active, we try to open just for one shot
            logger.info("No active stream, opening camera for single capture")
            cap = cv2.VideoCapture(0, cv2.CAP_ANY)
            if not cap.isOpened():
                cap = cv2.VideoCapture(1, cv2.CAP_ANY)
            
            if not cap.isOpened():
                 raise Exception("Could not open camera device")

            # Read a few frames to let auto-exposure settle
            for _ in range(10):
                cap.read()
                
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise Exception("Could not read frame from camera")
            return frame

    def release(self):
        with self.lock:
            if self.camera:
                logger.info("Releasing camera...")
                self.camera.release()
                self.camera = None

camera_manager = CameraManager()

def generate_frames():
    # Ensure camera is open
    camera_manager.open_camera()
    frame_count = 0
    try:
        while True:
            frame = camera_manager.get_frame()
            if frame is None:
                # If we lose the frame, try to re-open or just wait a bit
                time.sleep(0.1)
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            frame_count += 1
            if frame_count % 30 == 0:
                logger.info(f"Streaming frame {frame_count}, size: {len(frame)} bytes")
            
            time.sleep(0.03) # Limit to ~30fps
    except GeneratorExit:
        logger.info("Client disconnected from video stream.")
    except Exception as e:
        logger.error(f"Error in video stream: {e}")
    finally:
        logger.info("Releasing camera resource.")
        camera_manager.release()

@app.get("/api/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/current_frame")
async def get_current_frame():
    """Returns a single frame for frontend polling."""
    camera_manager.open_camera()
    frame = camera_manager.get_frame()
    if frame is None:
        raise HTTPException(status_code=503, detail="Camera not ready")
    
    return Response(content=frame, media_type="image/jpeg")

class TextNoteRequest(BaseModel):
    text: str

@app.post("/api/notes/text")
async def create_text_note(request: TextNoteRequest, user_id: str = Depends(verify_user_and_pin)):
    """Creates a new note from raw text."""
    try:
        # Create initial note entry
        note_id = db.add_note(
            image_path="", # Empty for text-only notes
            raw_text=request.text,
            user_id=user_id
        )
        
        if note_id == -1:
             raise HTTPException(status_code=500, detail="Failed to create note in DB")

        # Trigger background processing
        asyncio.create_task(process_text_note_background(note_id, request.text, user_id))
        
        return {"status": "success", "message": "Text note created and processing started", "note_id": note_id}
    except Exception as e:
        logger.error(f"Error creating text note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        else:
            # Standalone mode: trigger background processing directly
            logger.info("Standalone mode: Triggering background processing for webcam capture.")
            asyncio.create_task(process_image_note_background(abs_file_path, user_id))
            
        return {"status": "success", "filename": filename, "file_path": abs_file_path, "message": "Image captured and processing started."}
        
    except Exception as e:
        logger.error(f"Webcam capture failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Print existing users to verify persistence
    try:
        users = session_manager.get_all_users()
        logger.info(f"Existing users in DB: {users}")
    except Exception as e:
        logger.error(f"Failed to list users on startup: {e}")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
