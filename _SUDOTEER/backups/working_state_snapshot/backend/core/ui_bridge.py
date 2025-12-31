"""
_SUDOTEER UI Bridge
Connects the internal A2A Agent Bus to the Electron Frontend.
Uses stdout to stream JSON events to the parent Electron process.
Includes Dead Man's Switch stall detection.
"""

import json
import sys
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("_SUDOTEER")

class UIBridge:
	"""
	Real-time bridge between Python agents and Electron UI.
	Broadcasts agent events and system heartbeats to the frontend.
	Includes stall detection via Dead Man's Switch pattern.
	"""
	def __init__(self):
		self._stop_event = threading.Event()
		self._heartbeat_thread: Optional[threading.Thread] = None

		# STALL DETECTION STATE (Dead Man's Switch)
		self._last_tick = time.time()
		self._stall_threshold = 10.0  # Seconds before we consider system "stalled"
		self._lock = threading.Lock()  # Thread safety for timestamp

		self.uptime_start = time.time()

	def get_uptime(self) -> float:
		"""Returns system uptime in seconds."""
		return time.time() - self.uptime_start

	def tick(self):
		"""
		The 'Watchdog' reset.
		Call this method inside your main Agent loop or task processor
		to prove the main thread is still working.

		This prevents false "STALLED" alerts during legitimate long-running tasks.
		Example usage:
			bridge.tick()  # Before starting heavy agent task
			result = agent.execute(task)
			bridge.tick()  # After completing task
		"""
		with self._lock:
			self._last_tick = time.time()

	def start_heartbeat(self, interval_seconds: float = 2.0):
		"""
		Starts a background thread that pings the UI every N seconds.
		The heartbeat monitors for "stalled" agents using Dead Man's Switch.

		Args:
			interval_seconds: How often to send heartbeats (default: 2s)
		"""
		if self._heartbeat_thread is not None:
			logger.warning("UIBridge heartbeat already running")
			return

		def pulse():
			while not self._stop_event.is_set():
				# CHECK FOR STALL (Dead Man's Switch)
				with self._lock:
					time_since_tick = time.time() - self._last_tick

				# DETERMINE STATUS
				if time_since_tick > self._stall_threshold:
					status = "stalled"
					logger.warning(f"⚠️  SYSTEM STALLED! No tick() for {time_since_tick:.1f}s")
				else:
					status = "alive"

				# BROADCAST
				self.broadcast("SYSTEM_HEARTBEAT", "system", {
					"status": status,
					"uptime": time.time() - self.uptime_start,
					"last_tick_delta": round(time_since_tick, 2)
				})
				time.sleep(interval_seconds)

		# Daemon thread dies when main process exits
		self._heartbeat_thread = threading.Thread(target=pulse, daemon=True)
		self._heartbeat_thread.start()
		logger.info(f"UIBridge heartbeat started (interval: {interval_seconds}s, stall threshold: {self._stall_threshold}s)")

	def stop_heartbeat(self):
		"""Gracefully stops the heartbeat thread."""
		self._stop_event.set()
		if self._heartbeat_thread:
			self._heartbeat_thread.join(timeout=5)
			logger.info("UIBridge heartbeat stopped")

	def broadcast(self, event_type: str, agent_id: str, payload: Dict[str, Any]):
		"""
		Sends a JSON event to Electron via stdout.
		Uses ::SUDO:: delimiter to separate from normal logs.

		Args:
			event_type: e.g., "TASK_START", "THINKING", "SUCCESS", "ERROR"
			agent_id: e.g., "coder_01", "system"
			payload: Additional data to send
		"""
		message = {
			"type": "IPC_EVENT",
			"event": event_type,
			"agent_id": agent_id,
			"data": payload,
			"timestamp": datetime.now().isoformat()
		}

		try:
			# Print with delimiter for Electron to parse
			json_str = json.dumps(message)
			print(f"::SUDO::{json_str}", flush=True)
			sys.stdout.flush()
		except BrokenPipeError:
			# Electron closed but Python still running - exit gracefully
			logger.warning("Broken pipe detected - Electron connection lost")
			sys.exit(0)
		except Exception as e:
			logger.error(f"UIBridge broadcast failed: {e}")

	def broadcast_agent_status(self, agent_id: str, status: str, details: Dict[str, Any] = None):
		"""
		Convenience method for agent status updates.
		Automatically calls tick() to reset the watchdog.

		Args:
			agent_id: Agent identifier
			status: "idle", "active", "success", "error"
			details: Additional context
		"""
		self.broadcast(f"AGENT_{status.upper()}", agent_id, details or {})
		self.tick()  # Prove the main thread is alive

	def broadcast_workflow_step(self, workflow_id: str, current_node: str, status: str):
		"""
		Broadcasts workflow progress for real-time visualization.

		Args:
			workflow_id: Unique workflow execution ID
			current_node: Currently executing agent
			status: "processing", "completed", "failed"
		"""
		self.broadcast("WORKFLOW_UPDATE", "orchestrator", {
			"workflow_id": workflow_id,
			"current_node": current_node,
			"status": status
		})
		self.tick()  # Prove the main thread is alive

# Global UIBridge instance
ui_bridge = UIBridge()
