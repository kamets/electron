import os
import json
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import dspy

from .monologue import recorder
from .memory.manager import memory_manager
from .memory.dspy_signatures import DecomposeTask, ValidateResult, RecomposeResults

from .gamification import matryoshka_engine
from .memory.dspy_modules.calibration import confidence_monitor

logger = logging.getLogger("_SUDOTEER")

class DVRModule(dspy.Module):
	"""Standardized DURABLE reasoning module for all agents."""
	def __init__(self, role: str):
		super().__init__()
		self.role = role
		self.decomposer = dspy.ChainOfThought(DecomposeTask)
		self.validator = dspy.ChainOfThought(ValidateResult)
		self.recomposer = dspy.ChainOfThought(RecomposeResults)

class SudoAgent(dspy.Module):
	"""
	Lean & Durable Base class for all _SUDOTEER agents.
	Enforces workstation isolation and standardizes communication/memory.
	"""
	def __init__(self, agent_id: str, role: str):
		super().__init__()
		self.agent_id = agent_id
		self.role = role
		self.dvr = DVRModule(role)

		# Matryoshka Level Tracking
		self.level = matryoshka_engine.get_level(agent_id)

		# Workstation Isolation
		self.workstation_path = f"sandbox/workstations/{agent_id}"
		os.makedirs(self.workstation_path, exist_ok=True)

	async def get_constitution_tenets(self) -> List[str]:
		"""Fetch tenets from Neo4j :MUST_UPHOLD relationship if unlocked."""
		if not matryoshka_engine.check_unlocked("constitution", self.agent_id):
			return []

		# Fetch from graph store via memory manager
		try:
			context = await self.recall("What are the tenets of the Constitution I must uphold?")
			# Extra logic to extract list of tenets from context if available
			return context.get("graph_context", {}).get("tenets", [])
		except Exception:
			return []

	def log_interaction(self, message: str, event_type: str = "thought"):
		"""Standardized logging and monologue recording."""
		logger.info(f"[{self.agent_id}]: {message}")
		recorder.record_event(self.agent_id, self.role, event_type, message)

		# Durable Memory Heuristic
		if event_type in ["result", "decision", "error"]:
			asyncio.create_task(self.remember(message, {"type": event_type}))

	async def remember(self, content: str, metadata: Optional[Dict[str, Any]] = None):
		"""Store to long-term hybrid memory."""
		return await memory_manager.remember(self.agent_id, content, metadata)

	async def recall(self, query: str) -> Dict[str, Any]:
		"""Semantic & relational retrieval."""
		return await memory_manager.recall(query)

	async def get_context(self, query: str) -> str:
		"""Fetch the premium 'Context Sandwich' for reasoning."""
		return await memory_manager.get_context_sandwich(self.agent_id, query)

	def gain_xp(self, amount: int, reason: str):
		"""Strategic Mastery Loop [Module 3]."""
		matryoshka_engine.add_xp(self.agent_id, amount)
		self.log_interaction(f"XP Gain: +{amount} ({reason})", "thought")

	async def decompose(self, task: str) -> List[str]:
		"""Durable task breakdown with sandwich context."""
		context = await self.get_context(task)
		result = self.dvr.decomposer(task=task, role=self.role, context=context)
		self.log_interaction(f"Decomposed task into {len(result.subtasks)} steps", "thought")
		return result.subtasks

	async def validate(self, requirements: str, result: Any) -> bool:
		"""Validate output quality."""
		val = self.dvr.validator(requirements=requirements, result=str(result))
		if not val.is_valid:
			self.log_interaction(f"Validation failed: {val.feedback}", "error")
		return val.is_valid

	async def recompose(self, original_task: str, subtask_results: List[Dict]) -> str:
		"""Consolidate findings into a durable final report."""
		output = self.dvr.recomposer(original_task=original_task, subtask_results=subtask_results)
		return output.final_output

	@abstractmethod
	async def handle_request(self, message: Any) -> Any:
		pass

	@abstractmethod
	async def forward(self, *args, **kwargs):
		pass
