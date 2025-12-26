import time
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from .bus import bus
from .protocol import A2AMessage
from .workflow import workflow_orchestrator, WorkflowDefinition, WorkflowNode, WorkflowState
from .ui_bridge import ui_bridge
from backend.utils.finance import finance_tracker

logger = logging.getLogger("_SUDOTEER")

class AgencyOrchestrator:
	"""
	Technical Brain of _SUDOTEER.
	Orchestrates professional multi-agent workflows with A2A protocol.
	Enforces ROI-based guardrails and tracks system health.
	"""
	def __init__(self, budget_limit_hours: float = 2.0):
		self.budget_limit_hours = budget_limit_hours
		self.start_time = None
		self._setup_default_workflows()

	def _setup_default_workflows(self):
		"""Define the core 'Pass-the-Torch' validation chain."""
		nodes = [
			WorkflowNode("coder", "coder", self._step_coder, ["tester"]),
			WorkflowNode("tester", "tester", self._step_tester, ["documenter"]),
			WorkflowNode("documenter", "documenter", self._step_documenter, ["validator"]),
			WorkflowNode("validator", "validator", self._step_validator, [])
		]
		chain = WorkflowDefinition("validation_chain", "Professional Coder-to-Validator flow", nodes, "coder")
		workflow_orchestrator.register_workflow(chain)

	# --- Workflow Step Functions ---

	async def _run_agent_step(self, state: WorkflowState, agent_id: str, task_name: str, payload_key: str, input_payload: Dict[str, Any]) -> WorkflowState:
		"""Generic helper to run a standardized agent step with guardrails."""
		if not self.check_viability():
			return state

		finance_tracker.log_utilization(agent_id)
		ui_bridge.broadcast_agent_status(agent_id, "active", {"task": task_name})

		result = await bus.send_request(A2AMessage(
			from_agent="orchestrator",
			to_agent=agent_id,
			content=input_payload
		))

		state["data"][payload_key] = result
		ui_bridge.broadcast_agent_status(agent_id, "success", {"completed": True})
		return state

	async def _step_coder(self, state: WorkflowState) -> WorkflowState:
		return await self._run_agent_step(
			state, "coder_01", "Coding Phase", "code",
			{"task": state["data"].get("goal")}
		)

	async def _step_tester(self, state: WorkflowState) -> WorkflowState:
		return await self._run_agent_step(
			state, "tester_01", "Testing Phase", "test_report",
			{"code": state["data"].get("code")}
		)

	async def _step_documenter(self, state: WorkflowState) -> WorkflowState:
		return await self._run_agent_step(
			state, "documenter_01", "Documentation Phase", "docs",
			{"code": state["data"].get("code"), "tests": state["data"].get("test_report")}
		)

	async def _step_validator(self, state: WorkflowState) -> WorkflowState:
		state = await self._run_agent_step(
			state, "validator_01", "Final Audit Phase", "validation_result",
			{"bundle": {
				"code": state["data"].get("code"),
				"tests": state["data"].get("test_report"),
				"docs": state["data"].get("docs")
			}}
		)
		# Extraction logic moved here for simplicity
		v_res = state["data"].get("validation_result")
		state["data"]["valid"] = v_res.get("valid") if isinstance(v_res, dict) else False
		return state

	# --- Utilities ---

	def start_timer(self):
		self.start_time = time.time()
		logger.info("Agency workflow timer started.")

	def check_viability(self) -> bool:
		if not self.start_time: return True
		elapsed_hours = (time.time() - self.start_time) / 3600
		if elapsed_hours > self.budget_limit_hours or not finance_tracker.is_stable():
			logger.error("Stop signal triggered: Budget or Financial Stability violation.")
			return False
		return True

	async def execute_validation_chain(self, goal: str):
		self.start_timer()
		logger.info(f"Triggering professional validation chain for goal: {goal}")

		final_state = await workflow_orchestrator.execute_workflow("validation_chain", {"goal": goal})

		success = final_state["data"].get("valid", False)
		finance_tracker.log_effectiveness(goal, 1, success)

		logger.info(f"Orchestration Summary: {json.dumps(finance_tracker.get_summary_metrics(), indent=2)}")
		return final_state["data"] if success else None

# Global orchestrator instance
orchestrator = AgencyOrchestrator()
