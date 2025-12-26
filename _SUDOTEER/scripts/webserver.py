# _SUDOTEER Web Server - Python-Only UI
# No Node.js, no npm, no dependency hell!

"""
FastAPI-based web server for _SUDOTEER UI.

Serves:
- Static HTML/CSS/JS (existing frontend files)
- WebSocket for real-time telemetry
- REST API for commands

Replaces: Electron (avoids 60k+ npm files)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Setup logging immediately
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("_SUDOTEER.WebServer")

# Import existing backend
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.ui_bridge import ui_bridge
from backend.core.memory.artifact_manager import artifact_manager
from backend.core.memory.task_queue import task_queue
from backend.sandbox.simulations.greenhouse import GreenhouseSimulation
from backend.agents.supervisor import SupervisorAgent
from backend.core.factory import agent_factory
from backend.core.dspy_config import initialize_dspy

logger = logging.getLogger("_SUDOTEER.WebServer")

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
	title="_SUDOTEER Agency",
	description="Premium Forensic Intelligence Platform",
	version="1.0.0"
)

# Serve static files (HTML/CSS/JS)
frontend_path = Path(__file__).parent / "frontend" / "views"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Active WebSocket connections
active_connections: list[WebSocket] = []

# Greenhouse simulation instance
greenhouse = GreenhouseSimulation()

# Supervisor agent instance (Tier 1: User's single point of contact)
supervisor = None

# ============================================
# WEBSOCKET ENDPOINT (Real-time telemetry)
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	"""
	WebSocket connection for real-time updates.

	Replaces: stdout parsing in Electron
	Benefits: Native browser support, no parsing needed
	"""
	await websocket.accept()
	active_connections.append(websocket)

	logger.info(f"WebSocket connected. Total connections: {len(active_connections)}")

	try:
		# Send initial state
		await websocket.send_json({
			"type": "INITIAL_STATE",
			"data": {
				"agents": ["architect", "coder", "tester", "documenter", "validator"],
				"status": "online",
				"timestamp": datetime.now().isoformat()
			}
		})

		# Listen for commands from UI
		while True:
			data = await websocket.receive_text()
			command = json.loads(data)

			# Handle command
			await handle_command(command, websocket)

	except WebSocketDisconnect:
		active_connections.remove(websocket)
		logger.info(f"WebSocket disconnected. Remaining: {len(active_connections)}")

# ============================================
# BROADCAST TELEMETRY
# ============================================

async def broadcast_telemetry():
	"""
	Background task to broadcast telemetry to all connected clients.

	Replaces: stdout with ::SUDO:: delimiter
	Benefits: Native JSON, no parsing errors
	"""
	while True:
		if active_connections:
			# Get greenhouse state
			state = greenhouse.get_state()

			# Create telemetry packet
			telemetry = {
				"type": "GREENHOUSE_TELEMETRY",
				"event": "GREENHOUSE_TELEMETRY",
				"agent_id": "greenhouse_sim",
				"data": state,
				"timestamp": datetime.now().isoformat()
			}

			# Broadcast to all clients
			disconnected = []
			for connection in active_connections:
				try:
					await connection.send_json(telemetry)
				except Exception as e:
					logger.error(f"Failed to send telemetry: {e}")
					disconnected.append(connection)

			# Remove disconnected clients
			for conn in disconnected:
				active_connections.remove(conn)

		# Update greenhouse physics
		# greenhouse.update(delta_time=1.0)  # TODO: fix later

		# Wait 1 second
		await asyncio.sleep(1.0)

# ============================================
# COMMAND HANDLER
# ============================================

async def handle_command(command: dict, websocket: WebSocket):
	"""
	Handle commands from UI.

	Examples:
	- START_PUMP
	- STOP_PUMP
	- SPAWN_AGENT
	- etc.
	"""
	cmd_type = command.get("command")
	payload = command.get("payload", {})

	logger.info(f"Command received: {cmd_type}")

	if cmd_type == "AGENT_MSG":
		target = payload.get("target")
		action = payload.get("action")

		if target == "greenhouse_sim":
			# Greenhouse control
			if action == "START_PUMP":
				greenhouse.set_actuator("pump_active", True)
				await websocket.send_json({
					"type": "COMMAND_ACK",
					"command": "START_PUMP",
					"status": "success"
				})

			elif action == "STOP_PUMP":
				greenhouse.set_actuator("pump_active", False)
				await websocket.send_json({
					"type": "COMMAND_ACK",
					"command": "STOP_PUMP",
					"status": "success"
				})

	elif cmd_type == "PING":
		await websocket.send_json({
			"type": "PONG",
			"timestamp": datetime.now().isoformat()
		})

# ============================================
# REST API ENDPOINTS
# ============================================

# Serve static files (HTML/CSS/JS)
frontend_path = Path(__file__).parent / "frontend" / "views"

# REST API ENDPOINTS (Must come BEFORE mounting static root)
@app.get("/api/status")
async def get_status():
	"""Get system status"""
	return {
		"status": "online",
		"agents": 5,
		"connections": len(active_connections),
		"uptime": ui_bridge.get_uptime()
	}

@app.get("/api/tasks")
async def get_tasks():
	"""Get task queue"""
	return task_queue.get_progress_summary()

# Serve main UI
@app.get("/", response_class=HTMLResponse)
async def root():
	"""Serve main UI"""
	index_file = frontend_path / "index.html"
	if index_file.exists():
		return index_file.read_text(encoding="utf-8")
	return "<h1>_SUDOTEER Agency</h1><p>Frontend not found</p>"

@app.post("/api/command")
async def post_command(command: dict):
	"""Send command to backend"""
	logger.info(f"REST command: {command}")
	return {"status": "received"}

@app.post("/api/goal")
async def post_goal(request: dict):
	"""User goal endpoint - Tier 1 Supervisor interaction."""
	user_goal = request.get("goal", "")
	if not user_goal:
		return {"error": "No goal provided"}

	logger.info(f"User Goal Received: {user_goal}")

	# Forward to Supervisor (Tier 1) - Calling module directly as per DSPy best practices
	if supervisor:
		result = await supervisor(user_goal)
		return {"status": "success", "result": result}
	else:
		return {"error": "Supervisor agent not initialized"}

# Mount the entire views directory at root last
app.mount("/", StaticFiles(directory=str(frontend_path)), name="static")

# ============================================
# STARTUP EVENT
# ============================================

@app.on_event("startup")
async def startup_event():
	"""Start background tasks"""
	global supervisor

	logger.info("[START] Starting _SUDOTEER Web Server")

	# CRITICAL: Initialize DSPy backend for agents
	logger.info("[DSPy] Initializing LM backend...")
	dspy_ready = initialize_dspy(auto=True)
	if not dspy_ready:
		logger.error("[DSPy] ❌ Failed to initialize LM backend. Agents will be offline.")

	# Initialize Supervisor agent (Tier 1)
	supervisor = SupervisorAgent("supervisor_01", "Supervisor")
	logger.info("[AGENT] Tier 1 Supervisor initialized")

	# Start telemetry broadcast
	asyncio.create_task(broadcast_telemetry())

	logger.info("? Background tasks started")

# ============================================
# MAIN (Run Server)
# ============================================

def main():
	"""
	Run the web server.

	Access at: http://localhost:8000
	"""
	print("\n" + "="*60)
	print("  _SUDOTEER Web Server")
	print("="*60)
	print(f"\n[SERVER] Server starting at: http://localhost:8888")
	print(f"[FILES] Serving frontend from: {frontend_path}")
	print(f"\n[OPEN] Open in browser: http://localhost:8888")
	print("\nPress Ctrl+C to stop\n")

	uvicorn.run(
		app,
		host="0.0.0.0",
		port=8888,
		log_level="info",
		access_log=True
	)

if __name__ == "__main__":
	main()
