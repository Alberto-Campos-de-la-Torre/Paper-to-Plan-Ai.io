import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging

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

# Global reference to the main app's DB and AI (injected at runtime if needed, 
# but for simplicity we might just use the DB directly or share the instance)
# Ideally, we'd pass the controller, but for a simple companion, we can just save the file 
# and let the main app pick it up or trigger a callback if we run in the same process.
# Since we run this in a thread from main.py, we can access shared state if we are careful.
# For now, let's just save the file and let the user "Refresh" or we can trigger an event.

# We will use a simple callback mechanism if running in the same process
on_upload_callback = None

def set_upload_callback(callback):
    global on_upload_callback
    on_upload_callback = callback

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open(os.path.join(WEB_DIR, "mobile_index.html"), "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: mobile_index.html not found</h1>"

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Generate a unique filename
        timestamp = int(datetime.now().timestamp())
        filename = f"mobile_capture_{timestamp}.jpg"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File uploaded from mobile: {file_path}")
        
        # Trigger callback in main app to process the note
        if on_upload_callback:
            # We pass the path to the main thread logic
            # Note: This runs in the server thread, so the callback must be thread-safe 
            # or schedule the work on the main UI thread.
            on_upload_callback(file_path)
            
        return {"status": "success", "filename": filename, "message": "Image uploaded and processing started."}
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    return {"status": "running", "service": "PaperToPlan AI Companion"}
