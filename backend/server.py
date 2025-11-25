import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
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

app = FastAPI()

# Directory setup
CAPTURES_DIR = "captures"
WEB_DIR = "web"

# Ensure directories exist
os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

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

# We need a way to pass the loop to the external world or vice versa.
# Let's add a startup event to capture the loop.
global_loop = None

@app.on_event("startup")
async def startup_event():
    global global_loop
    global_loop = asyncio.get_running_loop()

def broadcast_update_sync(user_id: str, message: str):
    """Thread-safe broadcast"""
    if global_loop and manager:
        asyncio.run_coroutine_threadsafe(manager.broadcast(message, user_id), global_loop)


async def verify_user_and_pin(x_auth_user: str = Header(None), x_auth_pin: str = Header(None)):
    if not x_auth_user or not x_auth_pin:
        raise HTTPException(status_code=401, detail="Missing Username or PIN")
    
    if not session_manager.verify_user(x_auth_user, x_auth_pin):
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
        with open(os.path.join(WEB_DIR, "mobile_index.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
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
            "created_at": note['created_at'],
            "raw_text": note['raw_text'],
            "title": analysis.get('title', 'Sin Título'),
            "feasibility_score": analysis.get('feasibility_score', 0),
            "summary": analysis.get('summary', ''),
            "technical_considerations": analysis.get('technical_considerations', []),
            "recommended_stack": analysis.get('recommended_stack', [])
        }
        return flat_note
    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {e}")
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
