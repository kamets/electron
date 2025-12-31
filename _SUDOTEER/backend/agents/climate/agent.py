"""
Climate Agent
Manages HVAC, Fans, and Humidity based on VPD and Transpiration Potential (TP).
Updated with the 'Golden Variation' discovery.
"""
import logging
import asyncio
from backend.core.agent_base import BaseAgent
from backend.core.bus import bus
from backend.core.protocol import A2AMessage

logger = logging.getLogger("_SUDOTEER")

class ClimateAgent(BaseAgent):
    def __init__(self, agent_id: str = "climate_01", role: str = "Climate"):
        super().__init__(agent_id, role)
        self.target_vpd = 1.2
        self.tp_threshold_high = 15.0 # Fan ON
        self.tp_threshold_low = 10.0  # Fan OFF

    async def initialize(self):
        """Subscribe to real-time industrial telemetry."""
        await bus.subscribe("telemetry/industrial", self._on_telemetry)
        logger.info(f"[{self.agent_id}] Subscribed to high-freq telemetry.")

    async def _on_telemetry(self, data: dict):
        """
        Main Reactive Loop.
        Uses the 'Third Item' (TP) to preemptively manage environment.
        """
        latent = data.get("latent", {})
        vpd = latent.get("vpd", 1.0)

        # Calculate Transpiration Potential (TP)
        # Using mock light if not in raw data (should be in raw from sensory_engine)
        light = data.get("raw", {}).get("lux", [15000])[-1]
        tp = (vpd * light) / 1000.0

        # LOGIC: Preemptive Fan Control (The Discovery Plan)
        from backend.core.industrial_bridge import industrial_bridge

        if tp > self.tp_threshold_high:
            logger.info(f"[{self.agent_id}] High TP Detected ({tp:.2f}). Preemptive Cooling/Airflow: ON")
            await industrial_bridge.write_setpoint("fan", True)
        elif tp < self.tp_threshold_low:
            logger.info(f"[{self.agent_id}] Low TP Detected ({tp:.2f}). Conservation Mode: fan OFF")
            await industrial_bridge.write_setpoint("fan", False)

    async def handle_request(self, message: A2AMessage):
        # Handle manual override requests or goal changes
        pass

    async def forward(self, *args, **kwargs):
        pass
