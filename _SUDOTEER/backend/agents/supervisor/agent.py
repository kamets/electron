import logging
import json
import dspy
from typing import Any, Dict, List, Optional
from backend.core.agent_base import SudoAgent
from backend.core.protocol import A2AMessage
from backend.core.memory.dspy_signatures import (
	DecomposeUserGoal,
	RouteToAgent,
	NarrateResults,
	RiskAssessment
)
from backend.core.agent_challenges import trigger_level_up

logger = logging.getLogger("_SUDOTEER")

class SupervisorAgent(SudoAgent):
	"""
	Tier 1: The Supervisor (The Front Man).
	User's single point of contact.
	Processes goals → delegates tasks → explains results.
	Acts as the narrator and central router for all operations.

	USES DSPY: ChainOfThought with typed signatures for reasoning.
	"""
	def __init__(self, agent_id: str = "supervisor_01", role: str = "Supervisor"):
		super().__init__(agent_id, role)
		self.active_delegations: Dict[str, Any] = {}

		# DSPy Modules - ChainOfThought for multi-step reasoning
		self.decomposer = dspy.ChainOfThought(DecomposeUserGoal)
		self.router = dspy.ChainOfThought(RouteToAgent)
		self.narrator = dspy.ChainOfThought(NarrateResults)
		self.risk_assessor = dspy.ChainOfThought(RiskAssessment)

	async def perform_risk_assessment(self, action: str) -> Dict[str, Any]:
		"""Mechanical Humility: Hard check before high-stakes actions."""
		if not matryoshka_engine.check_unlocked("risk_assessment", self.agent_id):
			return {"recommendation": "PROCEED", "risk_score": 0.0}

		context = self._get_system_context()
		result = self.risk_assessor(proposed_action=action, context=context)

		score = float(result.risk_score)
		recommendation = result.recommendation

		self.log_interaction(f"Risk Assessment for '{action}': {score} ({recommendation})", "thought")

		if recommendation == "PAUSE_EXECUTION" or score > 0.8:
			self.log_interaction("🛑 HIGH RISK DETECTED. Execution Paused. Requiring User ACK.", "escalation")
			return {"recommendation": "PAUSE", "score": score, "factor": result.risk_factor}

		return {"recommendation": "PROCEED", "score": score}

	async def forward(self, user_goal: str) -> Dict[str, Any]:
		"""
		Main reasoning path for the Supervisor using DSPy.
		1. Risk Assessment (Human Gavel)
		2. Calibration (Ambiguity Check)
		3. Decompose & Route
		"""
		self.log_interaction(f"Supervisor starting mission: {user_goal}", event_type="thought")

		# 1. Risk Assessment (Level 2+)
		assessment = await self.perform_risk_assessment(user_goal)
		if assessment["recommendation"] == "PAUSE":
			return {
				"status": "paused",
				"reason": "HIGH_RISK",
				"details": assessment["factor"],
				"score": assessment["score"]
			}

		# 2. Confidence Calibration (Level 3+)
		if matryoshka_engine.check_unlocked("confidence_calibration", self.agent_id):
			# For Level 3 agents, we verify the plan before decomposition
			# First, we need a draft plan to verify
			context = self._get_system_context()
			draft = self.decomposer(user_goal=user_goal, context=context)

			calibration = await confidence_monitor.verify_plan(user_goal, str(draft.subtasks))
			if not calibration["is_confident"]:
				self.log_interaction(f"Hubris Detected! Ambiguity: {calibration['ambiguity_score']}", "thought")
				return {
					"status": "clarification_required",
					"question": calibration["clarification"],
					"assumptions": calibration["assumptions"]
				}

		# 3. Standard DSPy Decomposition
		context = self._get_system_context()
		# Prepend Constitution if unlocked (Level 2+)
		tenets = await self.get_constitution_tenets()
		if tenets:
			context = f"CRITICAL CONSTITUTIONAL TENETS:\n" + "\n".join(tenets) + "\n\n" + context

		decompose_result = self.decomposer(
			user_goal=user_goal,
			context=context
		)

		subtasks = decompose_result.subtasks if isinstance(decompose_result.subtasks, list) else [decompose_result.subtasks]
		self.log_interaction(
			f"DSPy Decomposed: {len(subtasks)} subtasks",
			event_type="thought"
		)

		# Step 4: DSPy Routing
		delegation_plan = await self._dspy_route_tasks(subtasks)

		# Step 5: Execute delegations
		results = {}
		for agent_id, task_data in delegation_plan.items():
			self.log_interaction(f"Delegating to {agent_id}", event_type="action")
			result = await self.send_a2a(agent_id, task_data, message_type="request")
			results[agent_id] = result

		# Step 6: DSPy Narration
		narrative_result = self.narrator(
			original_goal=user_goal,
			agent_results=json.dumps(results, indent=2)
		)

		self.log_interaction(f"Supervision complete.", event_type="observation")

		# HANDBOOK: The Learning Loop [Phase 3]
		# Call the Sifter to archive this mission into episodic memory
		from backend.core.memory.manager import memory_manager
		await memory_manager.sifter_session_end(self.agent_id)

		# Mastery Loop: Trigger Level Up challenge if mission complete
		final_status = "complete"
		await trigger_level_up(self.agent_id)

		return {
			"status": final_status,
			"goal": user_goal,
			"narrative": narrative_result.narrative,
			"key_insights": narrative_result.key_insights,
			"raw_results": results
		}

	def _get_system_context(self) -> str:
		"""Get current system state for DSPy decomposition."""
		available_agents = {
			"tier_1": ["supervisor_01"],
			"tier_2_operational": [
				"climate_agent (temperature, heating, cooling)",
				"nutrient_agent (water, pH, EC, irrigation)",
				"photoperiod_agent (lights, day/night cycles)",
				"predictive_agent (growth forecasting)",
				"anomaly_agent (sensor drift detection)"
			],
			"tier_3_development": [
				"architect_01 (system design, planning)",
				"coder_01 (code generation)",
				"tester_01 (testing, validation)",
				"documenter_01 (documentation)",
				"validator_01 (audit, quality assurance)"
			]
		}

		return json.dumps({
			"available_agents": available_agents,
			"system_status": "online",
			"current_focus": "greenhouse seed production and development workflow"
		}, indent=2)

	async def _dspy_route_tasks(self, subtasks: List[str]) -> Dict[str, Any]:
		"""
		Use DSPy to intelligently route subtasks to agents.
		This replaces the hardcoded keyword matching with LLM reasoning.
		"""
		plan = {}
		available_agents_json = self._get_system_context()

		for subtask in subtasks:
			# DSPy decides the routing
			route_result = self.router(
				subtask=subtask,
				available_agents=available_agents_json
			)

			agent_id = route_result.agent_id
			self.log_interaction(
				f"Routed '{subtask}' -> {agent_id}\nReasoning: {route_result.reasoning}",
				event_type="thought"
			)

			# Store in delegation plan
			if agent_id not in plan:
				plan[agent_id] = {"goals": []}
			plan[agent_id]["goals"].append(subtask)

		return plan

	async def handle_request(self, message: A2AMessage) -> Any:
		"""
		Handle peer-to-peer requests from other agents.
		The Supervisor can receive status updates or escalations.
		"""
		self.log_interaction(f"Supervisor received request from {message.from_agent}", event_type="thought")

		content = message.content
		if isinstance(content, dict):
			if "escalation" in content:
				# Handle escalations from lower-tier agents
				return await self._handle_escalation(content["escalation"], message.from_agent)
			elif "status_update" in content:
				# Log status updates
				self.log_interaction(f"Status from {message.from_agent}: {content['status_update']}", event_type="observation")
				return {"acknowledged": True}

		return {"response": "Supervisor acknowledges your message."}

	async def _handle_escalation(self, escalation_data: Dict, from_agent: str) -> Dict:
		"""
		Handle escalations from Tier 2/3 agents.
		E.g., when an agent hits an issue or needs human-in-the-loop approval.
		"""
		logger.warning(f"ESCALATION from {from_agent}: {escalation_data}")

		# In production, this would trigger a UI notification or voice alert
		self.log_interaction(
			f"Escalation received: {escalation_data.get('reason', 'Unknown')}",
			event_type="escalation"
		)

		return {
			"escalation_acknowledged": True,
			"action": "Flagged for human review",
			"from_agent": from_agent
		}
