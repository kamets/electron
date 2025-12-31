import logging
import asyncio
import uuid
from typing import Dict, List, Any, Callable, Optional, Union
from .bus import bus
from .protocol import A2AMessage
from .ui_bridge import ui_bridge

logger = logging.getLogger("_SUDOTEER")

class WorkflowState(dict):
	"""Dynamic state passed between workflow nodes."""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if "workflow_id" not in self: self["workflow_id"] = str(uuid.uuid4())
		if "data" not in self: self["data"] = {}
		if "current_step" not in self: self["current_step"] = "init"
		if "agent_statuses" not in self: self["agent_statuses"] = {}
		if "errors" not in self: self["errors"] = []
		if "status" not in self: self["status"] = "running"

class WorkflowNode:
	"""
	A single step in a multi-agent workflow.
	Aligned with LangGraph node patterns.
	"""
	def __init__(
		self,
		name: str,
		agent_id: str,
		function: Callable[[WorkflowState], Union[WorkflowState, Any]],
		next_nodes: List[str] = None,
		condition: Optional[Callable[[WorkflowState], str]] = None
	):
		self.name = name
		self.agent_id = agent_id
		self.function = function
		self.next_nodes = next_nodes or []
		self.condition = condition

class WorkflowDefinition:
	"""Blueprint for a multi-agent process."""
	def __init__(self, name: str, description: str, nodes: List[WorkflowNode], entry_point: str):
		self.name = name
		self.description = description
		self.nodes = {node.name: node for node in nodes}
		self.entry_point = entry_point

	def get_node(self, name: str) -> Optional[WorkflowNode]:
		return self.nodes.get(name)

class WorkflowOrchestrator:
	"""
	Advanced Orchestrator for _SUDOTEER.
	Executes graph-based workflows with A2A communication.
	"""
	def __init__(self):
		self.workflows: Dict[str, WorkflowDefinition] = {}

	def register_workflow(self, workflow: WorkflowDefinition):
		self.workflows[workflow.name] = workflow
		logger.info(f"Workflow '{workflow.name}' registered.")

	async def execute_workflow(self, workflow_name: str, initial_data: Dict[str, Any] = None) -> WorkflowState:
		"""Run the workflow graph from entry point to end."""
		if workflow_name not in self.workflows:
			raise ValueError(f"Workflow '{workflow_name}' not found.")

		workflow = self.workflows[workflow_name]
		state = WorkflowState(data=initial_data or {})
		current_node_name = workflow.entry_point

		logger.info(f"[{state['workflow_id']}] Starting workflow: {workflow_name} at {current_node_name}")

		try:
			while current_node_name:
				node = workflow.get_node(current_node_name)
				if not node:
					logger.error(f"Node {current_node_name} not found in workflow {workflow_name}")
					state["errors"].append(f"Node {current_node_name} not found")
					state["status"] = "failed"
					break

				logger.info(f"[{state['workflow_id']}] Executing Node: {current_node_name} (Agent: {node.agent_id})")

				# TICK: Prove main thread is alive before heavy agent task
				ui_bridge.tick()

				# Execute the node function
				if asyncio.iscoroutinefunction(node.function):
					state = await node.function(state)
				else:
					state = node.function(state)

				# TICK: Prove main thread is alive after completing task
				ui_bridge.tick()

				# Determine next node
				if node.condition:
					current_node_name = node.condition(state)
				elif node.next_nodes:
					# Standard sequential or first of list
					current_node_name = node.next_nodes[0]
				else:
					current_node_name = None

			if state["status"] == "running":
				state["status"] = "completed"

		except Exception as e:
			logger.error(f"Workflow execution failed: {e}")
			state["errors"].append(str(e))
			state["status"] = "failed"

		logger.info(f"[{state['workflow_id']}] Workflow '{workflow_name}' complete. Status: {state['status']}")
		return state

# Global orchestrator instance
workflow_orchestrator = WorkflowOrchestrator()
