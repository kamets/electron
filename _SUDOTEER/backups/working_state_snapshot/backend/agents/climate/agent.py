"""
Climate Agent
Manages HVAC, Fans, and Humidity based on VPD targets.
"""
import logging
from backend.core.agent_base import BaseAgent
from backend.core.ui_bridge import ui_bridge
from backend.core.utils.calculations import calculate_vpd

logger = logging.getLogger("_SUDOTEER")

class ClimateAgent(BaseAgent):
    def __init__(self, agent_id: str, role: str = "Climate"):
        super().__init__(agent_id, role)
        self.target_vpd = 1.2  # Ideal for most growth stages
        self.temp_threshold = 28.0

    async def execute(self, goal: str):
        ui_bridge.broadcast_agent_status(self.agent_id, "active", {"task": goal})

        # Determine necessary adjustment
        await self.balance_environment()

        ui_bridge.broadcast_agent_status(self.agent_id, "success")

    async def balance_environment(self):
        """Calculates VPD and adjusts fans/HVAC."""
        from backend.core.industrial_bridge import industrial_bridge
        sensors = industrial_bridge.sensors

        temp = sensors.get("S02_TEMP", 25.0)
        hum = sensors.get("S03_HUM", 60.0)

        current_vpd = calculate_vpd(temp, hum)
        logger.info(f"[{self.agent_id}] Current VPD: {current_vpd} kPa (Target: {self.target_vpd})")

        if current_vpd < (self.target_vpd - 0.2):
            logger.info(f"[{self.agent_id}] VPD Low (Too Humid). Increasing Extraction Fans.")
            await industrial_bridge.write_actuator("A07_FAN_EXTRACT", True)
        elif current_vpd > (self.target_vpd + 0.2):
            logger.info(f"[{self.agent_id}] VPD High (Too Dry). Triggering Misters.")
            await industrial_bridge.write_actuator("A08_MISTERS", True)

        # Emergency Heat Protection
        if temp > self.temp_threshold:
            logger.warning(f"[{self.agent_id}] CRITICAL TEMP: {temp}C. Emergency cooling active.")
            await industrial_bridge.write_actuator("A09_AC_UNIT", True)
