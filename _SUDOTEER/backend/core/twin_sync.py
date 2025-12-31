"""
_SUDOTEER Twin Sync Engine
Synchronizes the Physical Twin (Hardware) with the Digital Twin (Graph/Memory).
Detects drift, verifies operations, and publishes 'Wisdom' upon resolution.
"""
import logging
import asyncio
import time
from typing import Dict, Any
from backend.core.bus import bus
from backend.core.memory.manager import memory_manager
from backend.core.ui_bridge import ui_bridge

logger = logging.getLogger("_SUDOTEER")

class TwinSyncEngine:
    def __init__(self):
        self.expectations: Dict[str, Any] = {}
        self.last_sync_time = time.time()
        self.sync_interval = 5.0 # Seconds
        self.is_running = False

    def start(self):
        """Start the sync monitoring loop."""
        if self.is_running: return
        self.is_running = True
        asyncio.create_task(self._sync_loop())
        logger.info("TwinSyncEngine: Monitoring started.")

    async def _sync_loop(self):
        """Background loop to verify physical vs digital state."""
        while self.is_running:
            try:
                await self.perform_sync_check()
            except Exception as e:
                logger.error(f"TwinSync Error: {e}")
            await asyncio.sleep(self.sync_interval)

    async def perform_sync_check(self):
        """
        The 'Reality Check': Compares physical sensors with digital expectations.
        """
        # 1. Fetch current physical sensors from Industrial Bridge (simulated via bus)
        # In this implementation, we subscribe to topics, but for a global check,
        # we can peek at the industrial_bridge instance.
        from backend.core.industrial_bridge import industrial_bridge
        physical_state = industrial_bridge.sensors

        # 2. Fetch Digital Expectations from Memory Manager (Neo4j/Graph)
        # HANDBOOK: 'How should the greenhouse look right now?'
        digital_expectations = await memory_manager.recall("Current environmental expectations", mode="relational")

        # 3. Detect Drift
        drift_detected = False
        for key, physical_val in physical_state.items():
            expected_val = digital_expectations.get("graph_context", {}).get(key)

            if expected_val is not None:
                # Basic threshold check
                if abs(float(physical_val) - float(expected_val)) > 1.0:
                    drift_detected = True
                    logger.warning(f"TWIN DRIFT: {key} (Physical: {physical_val} != Expected: {expected_val})")
                    ui_bridge.broadcast("TWIN_DRIFT_ALERT", "system", {
                        "key": key,
                        "physical": physical_val,
                        "expected": expected_val
                    })

        # 4. Update Heartbeat
        self.last_sync_time = time.time()

    def set_expectation(self, key: str, value: Any):
        """Agents call this when they perform an action (e.g. 'Turn on Light')."""
        self.expectations[key] = value
        # Also store in Graph for long-term 'Expectation'
        asyncio.create_task(memory_manager.remember("twin_sync", f"Set digital expectation for {key} to {value}", {
            "type": "expectation",
            "key": key,
            "value": value
        }))

# Global Instance
twin_sync = TwinSyncEngine()
