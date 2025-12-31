"""
Nutrient Agent Logic
Implements automated dosing and manual overrides.
"""
import logging
from backend.core.agent_base import BaseAgent
from backend.core.ui_bridge import ui_bridge

logger = logging.getLogger("_SUDOTEER")

class NutrientAgent(BaseAgent):
    def __init__(self, agent_id: str, role: str = "Nutrient"):
        super().__init__(agent_id, role)
        self.target_ph = 6.0
        self.tolerance = 0.2
        self.dosing_enabled = True

    async def execute(self, goal: str):
        """Standard Agent Execution Loop."""
        ui_bridge.broadcast_agent_status(self.agent_id, "active", {"task": goal})

        # Process Logic
        if "ph" in goal.lower():
            await self.adjust_ph()

        ui_bridge.broadcast_agent_status(self.agent_id, "success")

    async def adjust_ph(self):
        # Placeholder for real sensor check + dosing
        logger.info(f"[{self.agent_id}] Checking pH levels...")
        # Simulated reading
        current_ph = 5.8
        if current_ph < (self.target_ph - self.tolerance):
            logger.info(f"[{self.agent_id}] pH Low ({current_ph}). Dosing base...")
            # Trigger hardware
            from backend.core.industrial_bridge import industrial_bridge
            await industrial_bridge.write_actuator("ph_up", True)

    def handle_intent(self, intent_data: dict):
        action = intent_data.get("action")
        value = intent_data.get("value")

        if action == "set_on":
            self.dosing_enabled = True
            logger.info(f"[{self.agent_id}] Automated Dosing ENABLED")
        elif action == "set_off":
            self.dosing_enabled = False
            logger.info(f"[{self.agent_id}] Automated Dosing DISABLED")

        if value > 0:
            self.target_ph = value
            logger.info(f"[{self.agent_id}] Target pH set to {value}")
