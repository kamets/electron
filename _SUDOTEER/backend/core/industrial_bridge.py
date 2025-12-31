import logging
import asyncio
from typing import Dict, Any, List, Optional
from .bus import bus
from .hardware.safety import safety_watchdog
from .hardware.modbus_driver import modbus_driver
from .hardware.sensory_engine import sensory_engine

logger = logging.getLogger("_SUDOTEER")

class IndustrialBridge:
	"""
	Universal Industrial Bridge.
	The physical link between the Agentic Brain and the Concrete Hardware.
	Integrates with SensoryEngine for 10Hz Latent Variable telemetry.
	"""
	def __init__(self, mode: str = "hardware"):
		self.mode = mode # 'simulation' or 'hardware'
		self.connected = False
		self.is_streaming = False

	async def connect(self):
		"""Initialize hardware connection and sensory engine."""
		logger.info(f"Connecting Industrial Bridge [Mode: {self.mode}]...")

		# 1. Connect to Modbus PLC
		if self.mode == "hardware":
			self.connected = await modbus_driver.connect()
			if not self.connected:
				logger.warning("FAILED TO CONNECT TO HARDWARE. Reverting to Simulation Mode.")
				self.mode = "simulation"
				self.connected = True
		else:
			self.connected = True
			logger.info("Industrial Bridge initiated in Simulation Mode.")

		# 2. Start the High-Freq Sensory Engine (10Hz)
		await sensory_engine.start()

		# 3. Start the UI/A2A Streaming Loop
		self.is_streaming = True
		asyncio.create_task(self._stream_telemetry())

		logger.info("✓ Industrial Bridge fully operational.")

	async def _stream_telemetry(self):
		"""
		Continuously broadcasts both Raw and Inferred (Latent) signals to the A2A bus.
		Broadcast rate: 2Hz for UI/Agent awareness (Filtered from 10Hz Sensory Engine).
		"""
		while self.is_streaming:
			try:
				# Combine raw signals and latent insights
				payload = {
					"timestamp": asyncio.get_event_loop().time(),
					"mode": self.mode,
					"latent": sensory_engine.latent_states,
					"raw": sensory_engine.raw_buffer
				}

				# Publish for all Agents and the UI Dashboard
				await bus.publish("telemetry/industrial", payload)

				await asyncio.sleep(0.5) # 2Hz Awareness Stream
			except Exception as e:
				logger.error(f"Telemetry Stream Error: {e}")
				await asyncio.sleep(1)

	async def write_setpoint(self, actuator_id: str, value: Any) -> bool:
		"""
		Validated hardware write.
		Follows the 'Trust but Verify' protocol by checking against the Safety Watchdog.
		"""
		if not self.connected:
			logger.error(f"Bridge not connected. Refusing command: {actuator_id}")
			return False

		# 1. SAFETY VALIDATION (Non-negotiable)
		if not safety_watchdog.validate_actuator_request(actuator_id, value):
			logger.error(f"⚠ SAFETY VIOLATION: Command rejected for {actuator_id}")
			return False

		# 2. PHYSICAL EXECUTION
		if self.mode == "hardware":
			success = await modbus_driver.write_actuator(actuator_id, value)
			if success:
				logger.info(f"✓ Hardware Write: {actuator_id} = {value}")
			else:
				logger.error(f"✖ Hardware Write FAILED: {actuator_id}")
			return success
		else:
			# Simulation logic
			logger.info(f"Simulated Write: {actuator_id} = {value}")
			return True

	async def disconnect(self):
		self.is_streaming = False
		await sensory_engine.stop()
		await modbus_driver.disconnect()
		self.connected = False
		logger.info("Industrial Bridge disconnected.")

# Global bridge instance
industrial_bridge = IndustrialBridge()
