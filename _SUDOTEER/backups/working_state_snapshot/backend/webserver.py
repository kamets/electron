import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

# Configure Logger
logger = logging.getLogger("_SUDOTEER")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("⚡ WebServer Lifespan: Startup")
    yield
    # Shutdown logic
    logger.info("⚡ WebServer Lifespan: Shutdown")

app = FastAPI(title="_SUDOTEER Engine", lifespan=lifespan)

# Allow CORS for Electron (file:// or localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---

@app.get("/health")
async def health_check():
    return {"status": "online", "system": "_SUDOTEER"}

@app.post("/api/actuator")
async def handle_actuator(data: dict):
    """
    Handle HMI button clicks (Lights, Pumps).
    For now, just log and acknowledge.
    """
    logger.info(f"API Actuator Recv: {data}")
    return {"status": "success", "action": data.get("action")}

@app.post("/api/settings")
async def handle_settings(data: dict):
    """
    Handle Autosave from Modals.
    """
    logger.info(f"API Settings Recv: {data}")
    # Return a mock 'BCC' hash to satisfy the frontend
    import hashlib
    bcc = hashlib.md5(str(data).encode()).hexdigest()[:8].upper()
    return {"status": "success", "bcc": bcc}

# --- WebSocket for Voice (Placeholder for Week 1) ---
@app.websocket("/ws/voice")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Voice Client Connected")
    try:
        while True:
            # Receive binary (audio) or text (control)
            data = await websocket.receive_text()
            logger.info(f"WS Recv: {data}")
            # Mock Feedback Loop
            await websocket.send_json({"status": "processing", "message": "Echo"})
    except WebSocketDisconnect:
        logger.info("Voice Client Disconnected")

def start_webserver(host="127.0.0.1", port=8000):
    """Entry point to run the server programmatically."""
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    # We use a custom runner if needed, or just .run()
    # But since we run alongside agency.py, we might run this in a thread.
    server.run()

if __name__ == "__main__":
    start_webserver()
