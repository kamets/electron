import logging
import json
import dspy
import asyncio
from typing import Any, Dict, List, Optional
from backend.core.agent_base import BaseAgent
from backend.core.protocol import A2AMessage
from backend.core.memory.dspy_signatures import ArchitectPlan

logger = logging.getLogger("_SUDOTEER")

class ArchitectAgent(BaseAgent):
	"""
	Tier 3: Architect Agent.
	Responsible for high-level system design and task delegation.

	USES DSPY: ChainOfThought with ArchitectPlan signature for structured planning.
	"""
	def __init__(self, agent_id: str = "architect_01", role: str = "Architect"):
		super().__init__(agent_id, role)

		# DSPy Module - ChainOfThought for architectural planning
		self.planner = dspy.ChainOfThought(ArchitectPlan)

	async def forward(self, goal: str, constraints: str = None) -> Dict[str, Any]:
		"""
		Create architectural plan using DSPy.
		1. Analyze the goal and constraints
		2. Generate architecture with components
		3. Determine delegation order
		4. Delegate to Coder for implementation
		"""
		self.log_interaction(f"Architecting solution for goal: {goal}", event_type="thought")

		# Default constraints if not provided
		if not constraints:
			constraints = "Budget: 2 hours, Tech: Python+DSPy+FastAPI, Quality: Production-ready"

		# DSPy Planning
		plan_result = await asyncio.to_thread(
			self.planner,
			goal=goal,
			constraints=constraints
		)

		# Log the architectural reasoning
		self.log_interaction(
			f"Architecture Plan:\n{plan_result.architecture}\n\n"
			f"Components: {plan_result.components}\n"
			f"Order: {plan_result.delegation_order}",
			event_type="thought"
		)

		# Prepare delegation package
		delegation_package = {
			"goal": goal,
			"architecture": plan_result.architecture,
			"components": plan_result.components,
			"order": plan_result.delegation_order
		}

		# Delegate to Coder via A2A
		self.log_interaction("Delegating implementation to Coder", event_type="action")
		await self.send_a2a("coder_01", delegation_package, message_type="request")

		return {
			"status": "delegated",
			"architecture": plan_result.architecture,
			"components": plan_result.components,
			"delegation_order": plan_result.delegation_order
		}

	async def handle_request(self, message: A2AMessage) -> Any:
		"""Handle P2P requests from other agents."""
		self.log_interaction(f"Handling request from {message.from_agent}", event_type="thought")

		content = message.content
		if isinstance(content, dict):
			# If it has a goal, create a plan
			if "goal" in content:
				goal = content["goal"]
				constraints = content.get("constraints", "Standard constraints")

				result = await self.forward(goal, constraints)
				return result

		# Default response
		return {
			"response": "Refine the logic to focus on industrial safety first.",
			"agent": self.agent_id
		}
