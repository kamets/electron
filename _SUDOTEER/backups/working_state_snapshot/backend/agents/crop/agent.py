import logging
import dspy
from typing import Dict, Any, Union, Optional
from backend.core.agent_base import BaseAgent
from backend.core.memory.dspy_signatures import ManageCropCycle

logger = logging.getLogger("_SUDOTEER")

class CropAgent(BaseAgent):
	"""
	Tier 2: Crop Agent.
	Manages the overall crop lifecycle and milestones.
	Uses DSPy to track progress and predict harvest.
	"""
	def __init__(self, agent_id: str = "crop_01", role: str = "Crop Cycle Manager"):
		super().__init__(agent_id, role)

		# DSPy Modules
		self.cycle_manager = dspy.ChainOfThought(ManageCropCycle)

	async def forward(self, crop_data: Dict[str, Any], env_history: str = "") -> Dict[str, Any]:
		"""
		Reasoning path for crop management.
		"""
		self.log_interaction(f"Analyzing crop lifecycle for: {crop_data.get('type')}", event_type="thought")

		# 1. Manage crop cycle
		result = self.cycle_manager(
			crop_data=str(crop_data),
			environmental_history=env_history
		)

		self.log_interaction(f"Current Phase: {result.current_phase}. Next Milestone: {result.next_milestone}", event_type="result")
		self.log_interaction(f"Health Score: {result.health_score}", event_type="action")

		return {
			"status": "monitored",
			"current_phase": result.current_phase,
			"next_milestone": result.next_milestone,
			"estimated_harvest": result.estimated_harvest_date,
			"health_score": result.health_score
		}

	async def handle_request(self, message: 'A2AMessage') -> Any:
		"""Handle crop lifecycle requests."""
		self.log_interaction(f"Received crop request from {message.from_agent}", event_type="thought")
		content = message.content
		if isinstance(content, dict):
			return await self.forward(content.get("crop_data", {}), content.get("env_history", ""))
		return await self.forward({"data": content})
