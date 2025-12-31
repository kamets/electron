"""
🔋 _SUDOTEER CORE ENGINE 🔋
The master operational brain.
Orchestrates agent tasks, manages state, and enforces the 'Trust but Verify' protocol.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from .bus import bus
from .protocol import A2AMessage
from .hardware.sensory_engine import sensory_engine
from .hardware.modbus_driver import modbus_driver

logger = logging.getLogger("_SUDOTEER")

class SudoteerEngine:
    """
    The central execution engine.
    Links sensory data to agentic actions and enforces the 'Atomic Task' workflow.
    """
    def __init__(self):
        self.active_tasks: Dict[str, Any] = {}
        self.is_running = False

    async def initialize(self):
        """Boot up the sensory and communication layers."""
        logger.info("SudoteerEngine: Initializing...")

        # 1. Start Sensory Engine
        await sensory_engine.start()

        # 2. Connect Hardware
        connected = await modbus_driver.connect()
        if not connected:
            logger.warning("SudoteerEngine: Running in DEGRADED mode (Hardware Offline)")

        # 3. Subscribe to high-freq telemetry
        await bus.subscribe("telemetry/high_freq", self._on_telemetry_receipt)

        self.is_running = True
        logger.info("SudoteerEngine: Fully Operational")

    async def _on_telemetry_receipt(self, data: Any):
        """Process real-time telemetry and check for 'Trust but Verify' violations."""
        # TODO: Implement real-time anomaly detection here
        pass

    async def execute_atomic_task(self, agent_id: str, task_description: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        The core 'Work' unit.
        Dispatches a task to an agent, records the trajectory, and verifies the outcome.
        """
        task_id = f"task_{int(asyncio.get_event_loop().time())}"
        logger.info(f"Engine: Starting Atomic Task {task_id} for {agent_id}: {task_description[:50]}...")

        # 1. Dispatch to Agent via Bus
        req = A2AMessage(
            from_agent="engine",
            to_agent=agent_id,
            content={"task": task_description, "metadata": metadata},
            message_type="request"
        )

        try:
            # 2. Monitor execution (Sandbox handled by agent_base)
            result = await bus.send_request(req)

            # 3. TRUST BUT VERIFY: Hardware state check
            if metadata and metadata.get("requires_hardware_verify"):
                verification = await self._verify_hardware_state(metadata["target_register"], metadata["expected_value"])
                result["hardware_verified"] = verification

            logger.info(f"Engine: Task {task_id} completed. Status: {result.get('status', 'unknown')}")
            return {"task_id": task_id, "result": result}

        except Exception as e:
            logger.error(f"Engine: Task {task_id} FAILED: {e}")
            return {"task_id": task_id, "status": "failed", "error": str(e)}

    async def _verify_hardware_state(self, key: str, expected_val: Any, timeout: float = 5.0) -> bool:
        """Wait for the sensory engine to confirm a physical state change."""
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            current_val = sensory_engine.latent_states.get(key) or \
                         (await modbus_driver.read_sensor(key))

            if current_val == expected_val:
                return True
            await asyncio.sleep(0.5)
        return False

# Global heart of the system
sudoteer_engine = SudoteerEngine()
