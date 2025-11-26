import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from backend.server import app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tauri_server")

# Add CORS middleware for Tauri
# This allows the frontend (tauri://localhost or http://localhost:1420) to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    logger.info("Starting Tauri Backend Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
