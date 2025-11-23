import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging
from database.db_manager import DBManager
from backend.session_manager import session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Directory setup
UPLOAD_DIR = "."
WEB_DIR = "web"

# Ensure web directory exists
os.makedirs(WEB_DIR, exist_ok=True)

# Mount static files (for serving the PWA)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

# Database Instance
db = DBManager()

# We will use a simple callback mechanism if running in the same process
on_upload_callback = None

def set_upload_callback(callback):
    global on_upload_callback
    on_upload_callback = callback

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
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File uploaded from mobile: {file_path} by user {user_id}")
        
        # Trigger callback in main app to process the note
        # We need to pass user_id to the callback now
        if on_upload_callback:
            on_upload_callback(file_path, user_id)
            
        return {"status": "success", "filename": filename, "message": "Image uploaded and processing started."}
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes")
async def get_notes(user_id: str = Depends(verify_user_and_pin)):
    """Returns a list of all notes for the authenticated user."""
    try:
        notes = db.get_all_notes(user_id=user_id)
        return notes
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
        return note
    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    return {"status": "running", "service": "PaperToPlan AI Companion"}
