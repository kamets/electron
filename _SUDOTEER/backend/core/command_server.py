"""
_SUDOTEER Command Server
Listens to stdin for JSON commands from Electron frontend.
Enables UI → Backend control (dynamic agent spawning, system commands).
"""

import sys
import json
import threading
import logging
from typing import Any, Dict

logger = logging.getLogger("_SUDOTEER")

from .command_router import command_router

class CommandServer:
	"""
	Background thread that listens for JSON commands from Electron via stdin.
	Delegates execution to the CommandRouter.
	"""

	def __init__(self, factory_instance=None):
		self.running = True
		self.listener_thread = None
		self.command_count = 0
		if factory_instance:
			command_router.set_factory(factory_instance)

	def start(self):
		"""Starts the non-blocking listener thread."""
		command_router.set_shutdown_callback(self.stop)
		self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
		self.listener_thread.start()
		logger.info("✅ CommandServer listening on stdin")

	def _listen_loop(self):
		"""Continuously reads single-line JSON strings from Electron."""
		while self.running:
			try:
				line = sys.stdin.readline()
				if not line:
					break
				line = line.strip()
				if line:
					self._process_command(line)
			except Exception as e:
				logger.error(f"CommandServer input error: {e}")

	def _process_command(self, raw_json: str):
		"""Parse and route incoming commands."""
		try:
			cmd_packet = json.loads(raw_json)
			command = cmd_packet.get("command")
			payload = cmd_packet.get("payload", {})

			self.command_count += 1
			logger.info(f"📥 Command #{self.command_count}: {command}")

			# Dispatch to Router
			command_router.dispatch(command, payload)

		except json.JSONDecodeError as e:
			logger.error(f"Invalid JSON received: {raw_json[:100]}... Error: {e}")
		except Exception as e:
			logger.error(f"Command processing error: {e}")

	def stop(self):
		"""Gracefully stop the command server."""
		self.running = False

# Import at bottom to avoid circular dependency
import time
