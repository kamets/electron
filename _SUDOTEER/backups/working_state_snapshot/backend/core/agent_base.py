import os
import json
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import dspy

# Delayed imports to avoid circular dependency
# These will be imported inside methods or after class definition

logger = logging.getLogger("_SUDOTEER")

class DVRModule(dspy.Module):
	"""Standardized DURABLE reasoning module for all agents."""
	def __init__(self, role: str):
		super().__init__()
		from .memory.dspy_signatures import DecomposeTask, ValidateResult, RecomposeResults
		self.role = role
		self.decomposer = dspy.ChainOfThought(DecomposeTask)
		self.validator = dspy.ChainOfThought(ValidateResult)
		self.recomposer = dspy.ChainOfThought(RecomposeResults)

class BaseAgent(dspy.Module):
	"""
	Lean & Durable Base class for all _SUDOTEER agents.
	Enforces workstation isolation and standardizes communication/memory.
	"""
	def __init__(self, agent_id: str, role: str):
		super().__init__()
		self.agent_id = agent_id
		self.role = role
		self.dvr = DVRModule(role)

		# Workstation Isolation
		self.workstation_path = f"sandbox/workstations/{agent_id}"
		os.makedirs(self.workstation_path, exist_ok=True)

	def log_interaction(self, message: str, event_type: str = "thought"):
		"""Standardized logging and monologue recording."""
		from .monologue import recorder
		logger.info(f"[{self.agent_id}]: {message}")
		recorder.record_event(self.agent_id, self.role, event_type, message)

		# Durable Memory Heuristic
		if event_type in ["result", "decision", "error"]:
			asyncio.create_task(self.remember(message, {"type": event_type}))

	async def remember(self, content: str, metadata: Optional[Dict[str, Any]] = None):
		"""Store to long-term hybrid memory."""
		from .memory.manager import memory_manager
		return await memory_manager.remember(self.agent_id, content, metadata)

	async def recall(self, query: str) -> Dict[str, Any]:
		"""Semantic & relational retrieval."""
		from .memory.manager import memory_manager
		return await memory_manager.recall(query)

	async def get_context(self, query: str, extra_context: Optional[str] = None) -> str:
		"""Fetch the premium 'Context Sandwich' for reasoning."""
		from .memory.manager import memory_manager
		return await memory_manager.get_context_sandwich(self.agent_id, query, extra_context)

	def gain_xp(self, amount: int, reason: str):
		"""Strategic Mastery Loop."""
		from .gamification import matryoshka_engine
		matryoshka_engine.add_xp(self.agent_id, amount)
		self.log_interaction(f"XP Gain: +{amount} ({reason})", "thought")

	async def read_documentation(self, file_path: str):
		if not os.path.exists(file_path):
			self.log_interaction(f"Failed to read doc: {file_path} not found.", "error")
			return

		with open(file_path, "r", encoding="utf-8") as f:
			content = f.read()

		title = os.path.basename(file_path)
		from .memory.manager import memory_manager
		result = await memory_manager.ingest_document(self.agent_id, title, content, protocol="beta")

		xp_gain = result["chunks_ingested"] * 5
		self.gain_xp(xp_gain, f"Read documentation: {title}")
		return result

	async def decompose(self, task: str) -> List[str]:
		context = await self.get_context(task)
		result = await asyncio.to_thread(self.dvr.decomposer, task=task, role=self.role, context=context)
		self.log_interaction(f"Decomposed task into {len(result.subtasks)} steps", "thought")
		return result.subtasks

	async def validate(self, requirements: str, result: Any) -> bool:
		val = await asyncio.to_thread(self.dvr.validator, requirements=requirements, result=str(result))
		if not val.is_valid:
			self.log_interaction(f"Validation failed: {val.feedback}", "error")
		return val.is_valid

	async def recompose(self, original_task: str, subtask_results: List[Dict]) -> str:
		output = await asyncio.to_thread(self.dvr.recomposer, original_task=original_task, subtask_results=subtask_results)
		return output.final_output

	async def send_a2a(self, to_agent: str, content: Any, message_type: str = "request") -> Any:
		from .bus import bus
		from .protocol import A2AMessage
		msg = A2AMessage(from_agent=self.agent_id, to_agent=to_agent, content=content, message_type=message_type)
		return await bus.send_request(msg)

	@abstractmethod
	async def handle_request(self, message: Any) -> Any:
		pass

	@abstractmethod
	async def forward(self, *args, **kwargs):
		pass

	async def assimilate_wisdom(self):
		self.log_interaction("Initiating self-reflection and wisdom assimilation...", "thought")
		from .memory.manager import memory_manager
		await memory_manager.sifter_session_end(self.agent_id)
		self.gain_xp(50, "Completed self-reflection session")
		self.log_interaction("Wisdom assimilation complete.", "result")

# Global Alias
SudoAgent = BaseAgent
