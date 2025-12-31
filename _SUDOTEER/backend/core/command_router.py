"""
_SUDOTEER Command Router
Maps incoming UI commands to specific backend actions.
"""

import logging
from typing import Dict, Any, Callable
from backend.core.factory import agent_factory
from backend.core.ui_bridge import ui_bridge
from backend.sandbox.simulations.greenhouse import greenhouse_sim

logger = logging.getLogger("_SUDOTEER")

class CommandRouter:
	"""Dispatches commands from Electron to the appropriate service handlers."""

	def __init__(self, factory=None):
		self.factory = factory or agent_factory
		self.shutdown_callback = None
		self.handlers: Dict[str, Callable] = {
			"SPAWN_AGENT": self._handle_spawn,
			"KILL_AGENT": self._handle_kill,
			"AGENT_MSG": self._handle_agent_message,
			"SYSTEM_SHUTDOWN": self._handle_shutdown,
			"PING": self._handle_ping,
			"SLASH_COMMAND": self._handle_slash_command
		}

	def _handle_slash_command(self, payload: Dict[str, Any]):
		"""
		The 'Fast Lane' Parser.
		Converts textual slash commands into direct hardware/system actions.
		"""
		cmd = payload.get("cmd", "").lower()
		args = payload.get("args", "").lower()

		logger.info(f"⚡ Slash Command Recv: /{cmd} {args}")

		if cmd == "pump":
			action = "START_PUMP" if "on" in args else "STOP_PUMP"
			self._handle_greenhouse(action, payload)
			ui_bridge.broadcast("COMMAND_SUCCESS", "router", {"msg": f"Pump {'started' if 'on' in args else 'stopped'}"})

		elif cmd == "status":
			# Immediate system health report
			from backend.core.industrial_bridge import industrial_bridge
			sensors = industrial_bridge.sensors
			report = f"System Status: Temp={sensors.get('S02_TEMP', 'N/A')}C, pH={sensors.get('S04_PH', 'N/A')}"
			ui_bridge.broadcast("SYSTEM_REPORT", "router", {"report": report})

		elif cmd == "agent":
			# e.g. /agent spawn climate
			if "spawn" in args:
				role = args.replace("spawn", "").strip()
				self._handle_spawn({"role": role, "name": f"{role}_manual"})

		else:
			logger.warning(f"Unknown slash command: /{cmd}")
			ui_bridge.broadcast("COMMAND_ERROR", "router", {"error": f"Unknown command: /{cmd}"})

	def set_factory(self, factory):
		"""Allow dynamic factory replacement (useful for tests)."""
		self.factory = factory

	def set_shutdown_callback(self, callback: Callable):
		"""Allow the server to be stopped via the router."""
		self.shutdown_callback = callback

	def dispatch(self, command: str, payload: Dict[str, Any]):
		"""Routes a command to its handler."""
		handler = self.handlers.get(command)
		if handler:
			try:
				handler(payload)
			except Exception as e:
				logger.error(f"Handler error for {command}: {e}")
				ui_bridge.broadcast("COMMAND_ERROR", "router", {"error": str(e)})
		else:
			logger.warning(f"No handler registered for command: {command}")
			ui_bridge.broadcast("COMMAND_ERROR", "router", {"error": f"Unknown command: {command}"})

	def _handle_spawn(self, payload: Dict[str, Any]):
		role = payload.get("role")
		name = payload.get("name")
		if role and name:
			self.factory.spawn_agent(role=role, name=name)
		else:
			logger.error("SPAWN_AGENT: Missing role or name")

	def _handle_kill(self, payload: Dict[str, Any]):
		name = payload.get("name")
		if name:
			self.factory.kill_agent(name)

	def _handle_agent_message(self, payload: Dict[str, Any]):
		target = payload.get("target", "")
		action = payload.get("action", "")

		# Specific logic for Greenhouse Simulation
		if target.startswith("greenhouse"):
			self._handle_greenhouse(action, payload)
		else:
			logger.info(f"Routing message to {target}: {action}")

	def _handle_greenhouse(self, action: str, payload: Dict[str, Any]):
		# UI commands use source="user" to trigger manual override (agents locked out)
		mapping = {
			"START_PUMP": lambda: greenhouse_sim.set_actuator("pump_active", True, source="user"),
			"STOP_PUMP": lambda: greenhouse_sim.set_actuator("pump_active", False, source="user"),
			"SET_HEATER": lambda: greenhouse_sim.set_actuator("heater", payload.get("value", False), source="user"),
			"CLEAR_OVERRIDE": lambda: greenhouse_sim.clear_override(payload.get("actuator", "")),
			"CLEAR_ALL_OVERRIDES": lambda: greenhouse_sim.clear_all_overrides()
		}
		if action in mapping:
			mapping[action]()
			logger.info(f"Greenhouse action {action} executed via UI.")

	def _handle_shutdown(self, payload: Dict[str, Any]):
		logger.critical("System shutdown requested via UI.")
		if self.shutdown_callback:
			self.shutdown_callback()

	def _handle_ping(self, payload: Dict[str, Any]):
		import time
		ui_bridge.broadcast("PONG", "router", {"timestamp": time.time()})

# Global router instance
command_router = CommandRouter()
