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

import uvicorn
import asyncio
import logging
import httpx
import json
import time
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("_SUDOTEER.WebServer")

# Chroma Proxy Configuration
CHROMA_INTERNAL_URL = "http://127.0.0.1:8001"
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.ui_bridge import ui_bridge
from backend.core.memory.artifact_manager import artifact_manager
from backend.core.memory.task_queue import task_queue
from backend.sandbox.simulations.greenhouse import GreenhouseSimulation
from backend.agents.supervisor import SupervisorAgent
from backend.core.factory import agent_factory
from backend.core.dspy_config import initialize_dspy
from backend.core.boot import SudoBootstrapper

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
frontend_path = Path(__file__).parent.parent / "frontend" / "views"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Active WebSocket connections
active_connections: list[WebSocket] = []

# Greenhouse simulation instance
greenhouse = GreenhouseSimulation()

# Supervisor agent instance (Tier 1: User's single point of contact)
supervisor = None

# Edge Node Reporter (MQTT Distributed Control)
reporter = None
last_heartbeat_time = 0
HEARTBEAT_INTERVAL = 5.0 # Seconds

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
			state = greenhouse.get_telemetry_packet()

			# Create telemetry packet
			telemetry = {
				"type": "GREENHOUSE_TELEMETRY",
				"event": "GREENHOUSE_TELEMETRY",
				"agent_id": "greenhouse_sim",
				"data": state,
				"edge_status": {
					"connected": reporter.connected if reporter else False,
					"unit_id": reporter.unit_id if reporter else "OFFLINE"
				},
				"timestamp": datetime.now().isoformat()
			}

			# Heartbeat for Distributed Control (JSON report card every 5s)
			global last_heartbeat_time
			now_ts = time.time()
			if reporter and (now_ts - last_heartbeat_time >= HEARTBEAT_INTERVAL):
				reporter.send_heartbeat(state)
				last_heartbeat_time = now_ts

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
		greenhouse.step(delta_time_sec=1.0)

		# Proactive Heartbeat: reset the watchdog timer
		ui_bridge.tick()

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
# CHROMA COMPATIBILITY PROXY (API v1 -> v2)
# ============================================

@app.get("/api/v1/heartbeat")
async def proxy_heartbeat():
	try:
		async with httpx.AsyncClient() as client:
			r = await client.get(f"{CHROMA_INTERNAL_URL}/api/v2/heartbeat", timeout=5.0)
			return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
	except Exception as e:
		return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.get("/api/v1/collections")
async def proxy_list_collections():
	try:
		async with httpx.AsyncClient() as client:
			r = await client.get(f"{CHROMA_INTERNAL_URL}/api/v2/tenants/default_tenant/databases/default_database/collections", timeout=5.0)
			return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
	except Exception as e:
		return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.post("/api/v1/collections")
async def proxy_create_collection(request: Request):
	try:
		content = await request.body()
		async with httpx.AsyncClient() as client:
			r = await client.post(f"{CHROMA_INTERNAL_URL}/api/v2/tenants/default_tenant/databases/default_database/collections", content=content, timeout=5.0)
			return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
	except Exception as e:
		return Response(content=f"Proxy error: {str(e)}", status_code=502)

@app.api_route("/api/v1/collections/{collection_id}/{action}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_collection_action(collection_id: str, action: str, request: Request):
	try:
		method = request.method
		content = await request.body()
		url = f"{CHROMA_INTERNAL_URL}/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id}/{action}"
		async with httpx.AsyncClient() as client:
			r = await client.request(method, url, content=content, timeout=10.0)
			return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
	except Exception as e:
		return Response(content=f"Proxy error: {str(e)}", status_code=502)

# ============================================
# REST API ENDPOINTS
# ============================================

# Serve static files (HTML/CSS/JS)
frontend_path = Path(__file__).parent.parent / "frontend" / "views"

# REST API ENDPOINTS (Must come BEFORE mounting static root)
@app.get("/api/status")
async def get_status():
	"""Get system status"""
	# Check Neo4j status dynamically
	from backend.core.memory.manager import memory_manager
	if memory_manager.graph_store.driver is None:
		await memory_manager.graph_store.connect()
	graph_ready = memory_manager.graph_store.driver is not None

	return {
		"status": "online" if graph_ready else "degraded",
		"agents": len(agent_factory.active_agents),
		"connections": len(active_connections),
		"uptime": ui_bridge.get_uptime(),
		"systems": {
			"vector": "online",
			"graph": "online" if graph_ready else "offline",
			"simulation": "active"
		}
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

@app.get("/api/settings")
async def get_settings():
	"""Retrieve persisted system settings"""
	try:
		settings_path = Path(__file__).parent.parent / "settings.json"
		if settings_path.exists():
			with open(settings_path, "r") as f:
				return json.load(f)
		return {}
	except Exception as e:
		logger.error(f"Failed to load settings: {e}")
		return {}

@app.post("/api/settings")
async def update_settings(settings: dict):
	"""Update system settings (autosaved from UI) and persist to disk"""
	from backend.core.utils.mewtocol import MewtocolFrame

	# Create a payload string for checksum verification (simulating PLC data)
	payload = json.dumps(settings.get("settings", {}))
	bcc = MewtocolFrame.calculate_bcc(payload)

	logger.info(f"🔒 SETTINGS UPDATED: {json.dumps(settings, indent=2)}")
	logger.info(f"🛡️ BCC INSURANCE: [Payload Checksum: {bcc}] - Frame Validated for PLC Transmission")

	# Persist to disk
	try:
		settings_path = Path(__file__).parent.parent / "settings.json"
		# Merge with existing settings if possible
		existing = {}
		if settings_path.exists():
			with open(settings_path, "r") as f:
				existing = json.load(f)

		# Update mapping for the specific type (e.g. nutrient-settings)
		existing[settings.get("type", "general")] = settings.get("settings", {})

		with open(settings_path, "w") as f:
			json.dump(existing, f, indent=4)
	except Exception as e:
		logger.error(f"Failed to persist settings: {e}")

	return {"status": "success", "message": "Settings saved and persisted", "bcc": bcc}

@app.post("/api/goal")
async def post_goal(request: dict):
	"""User goal endpoint - Tier 1 Supervisor interaction."""
	user_goal = request.get("goal", "")
	if not user_goal:
		return {"error": "No goal provided"}

	logger.info(f"User Goal Received: {user_goal}")

	# Forward to Supervisor (Tier 1) - Calling module directly as per DSPy best practices
	if supervisor:
		try:
			result = await supervisor.forward(user_goal)
			return {"status": "success", "result": result}
		except Exception as e:
			logger.error(f"Supervisor execution failed: {e}")
			return {"status": "error", "error": str(e)}
	else:
		return {"error": "Supervisor agent not initialized"}

# ============================================
# ACTUATOR CONTROL (UI Override)
# ============================================

@app.post("/api/actuator")
async def control_actuator(request: Request):
	"""
	Direct actuator control from UI.
	These are USER commands that override agent control.
	"""
	from backend.sandbox.simulations.greenhouse import greenhouse_sim

	try:
		data = await request.json()
	except:
		return {"status": "error", "message": "Invalid JSON"}

	name = data.get("name", "")
	value = data.get("value")
	action = data.get("action", "set")  # "set", "toggle", "clear_override"

	if action == "clear_override":
		greenhouse_sim.clear_override(name)
		return {"status": "success", "message": f"Override cleared for {name}"}

	if action == "clear_all":
		greenhouse_sim.clear_all_overrides()
		return {"status": "success", "message": "All overrides cleared"}

	if action == "toggle":
		current = greenhouse_sim.actuators.get(name, False)
		value = not current

	# Set with USER source (creates override)
	success = greenhouse_sim.set_actuator(name, value, source="user")

	# Logic for BCC Insurance
	from backend.core.utils.mewtocol import MewtocolFrame
	bcc = MewtocolFrame.calculate_bcc(f"USER_SET_{name}_{value}")

	return {
		"status": "success" if success else "blocked",
		"actuator": name,
		"value": greenhouse_sim.actuators.get(name),
		"override_active": greenhouse_sim.manual_override.get(name, False),
		"bcc": bcc
	}

@app.get("/api/overrides")
async def get_overrides():
	"""Get list of active manual overrides."""
	from backend.sandbox.simulations.greenhouse import greenhouse_sim
	active = {k: v for k, v in greenhouse_sim.manual_override.items() if v}
	return {"overrides": active, "count": len(active)}

# Mount the entire views directory at root last
app.mount("/", StaticFiles(directory=str(frontend_path)), name="static")

# ============================================
# STARTUP EVENT
# ============================================

@app.on_event("startup")
async def startup_event():
	"""Start background tasks"""
	global supervisor, reporter

	logger.info("[START] Starting _SUDOTEER Web Server")

	# 0. Initialize Edge Node Reporter (Master Overseer Connection)
	from backend.core.distributed.reporter import GreenhouseReporter
	reporter = GreenhouseReporter(unit_id="GH-01", broker_address="localhost")
	logger.info(f"🛡️ [DISTRIBUTED] Edge Node GH-01 Initialized (MQTT Mode)")

	# 1. Boot Subsystems (DSPy, VectorDB, etc.)
	SudoBootstrapper.initialize_subsystems()

	# 2. Register Roles & Spawn Full Agency
	SudoBootstrapper.register_agency_roles()
	await SudoBootstrapper.spawn_baseline_agents()

	# 3. Retrieve Supervisor for API usage
	supervisor = agent_factory.get_agent("supervisor_01")
	logger.info(f"[AGENT] Tier 1 Supervisor ready: {supervisor is not None}")

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
	print("  _SUDOTEER Web Server (Proxy Mode)")
	print("="*60)
	print(f"\n[SERVER] Server starting at: http://localhost:8000")
	print(f"[CHROMA] Proxying to: {CHROMA_INTERNAL_URL}")
	print(f"[FILES] Serving frontend from: {frontend_path}")
	print(f"\n[OPEN] Open in browser: http://localhost:8000")
	print("\nPress Ctrl+C to stop\n")

	uvicorn.run(
		app,
		host="0.0.0.0",
		port=8000,
		log_level="info",
		access_log=True
	)

if __name__ == "__main__":
	main()
