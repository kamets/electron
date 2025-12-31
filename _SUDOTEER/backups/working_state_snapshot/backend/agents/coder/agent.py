import logging
import json
import dspy
import asyncio
from typing import Dict, Any, Union, Optional, List
from backend.core.agent_base import BaseAgent
from backend.core.protocol import A2AMessage
from backend.core.memory.dspy_signatures import GenerateCode

from .rules import CodingRulesEngine
from .validator import CodeValidator

logger = logging.getLogger("_SUDOTEER")

class CoderAgent(BaseAgent):
	"""
	Tier 3: Coder Agent.
	Responsible for technical implementation and code generation.

	USES DSPY: ChainOfThought with GenerateCode signature for structured code generation.
	"""
	def __init__(self, agent_id: str = "coder_01", role: str = "Coder"):
		super().__init__(agent_id, role)
		self.rules_engine = CodingRulesEngine()
		self.validator = CodeValidator()

		# DSPy Module - ChainOfThought for code generation
		self.code_generator = dspy.ChainOfThought(GenerateCode)

	async def forward(self, task: Union[str, Dict[str, Any]], architecture_plan: str = None) -> Dict[str, Any]:
		"""
		Generate production-quality code using DSPy with memory-enhanced learning.
		"""
		# Parse task input
		if isinstance(task, dict):
			task_desc = task.get("task", task.get("goal", str(task)))
			architecture_plan = task.get("architecture", architecture_plan)
		else:
			task_desc = str(task)

		self.log_interaction(f"Processing implementation task: {task_desc}", event_type="thought")

		# 1. RETRIEVAL - Recall similar past implementations to 'learn' from history
		past_lessons = await self.recall(f"Code patterns and blocks for {task_desc}")

		# Default architecture if not provided
		if not architecture_plan:
			architecture_plan = "Standard Python module following PEP8, with type hints and docstrings"

		# 2. CONTEXT - Fetch Context Sandwich (Facts + Semantics + History)
		context = await self.get_context(task_desc, extra_context=str(past_lessons))

		# 3. GENERATION - DSPy Code Generation
		code_result = await asyncio.to_thread(
			self.code_generator,
			task_description=task_desc,
			architecture_plan=architecture_plan,
			context=context
		)

		# Log DSPy reasoning
		self.log_interaction(
			f"Code generated with reasoning:\n{code_result.explanation}",
			event_type="thought"
		)

		# 4. VALIDATION - Validate the generated code
		generated_code = code_result.code
		is_valid_syntax = self.validator.check_syntax(generated_code)
		standards_report = self.rules_engine.validate_standards(generated_code)

		# Auto-fix/Correct (Self-Learning from errors)
		if not standards_report["passed"]:
			self.log_interaction("Style violations found, performing self-correction...", event_type="action")
			generated_code = self.rules_engine.auto_fix(generated_code)
			standards_report = self.rules_engine.validate_standards(generated_code)
			self.gain_xp(5, f"Self-correction of {task_desc}")

		# 5. REFLECTION - Active Learning Step
		final_status = "success" if is_valid_syntax and standards_report["passed"] else "needs_review"

		if final_status == "success":
			self.gain_xp(20, f"Successful implementation of {task_desc}")
			# Explicitly remember the successful pattern for future recall
			await self.remember(
				f"Successful implementation pattern for '{task_desc}':\n{code_result.explanation}",
				metadata={"type": "coding_pattern", "task": task_desc}
			)

		self.log_interaction(
			f"Code generation complete. Status: {final_status}",
			event_type="result"
		)

		return {
			"status": final_status,
			"code": generated_code,
			"explanation": code_result.explanation,
			"language": "python",
			"metadata": {
				"syntax_valid": is_valid_syntax,
				"standards_passed": standards_report["passed"],
				"standards_score": standards_report.get("score", 10),
				"issues": standards_report.get("issues", [])
			}
		}

	def recompose(self, results: List[str]) -> str:
		"""Combine generated snippets into a final module."""
		return "\n\n".join(results)

	async def handle_request(self, message: A2AMessage) -> Any:
		"""Handle requests from Architect/Orchestrator."""
		self.log_interaction(f"Received coding request from {message.from_agent}", event_type="thought")

		content = message.content
		if isinstance(content, dict):
			# Extract task and architecture from delegation package
			task = content.get("goal", content.get("task", ""))
			architecture = content.get("architecture", None)

			result = await self.forward(task, architecture)
			return result
		else:
			# Simple string task
			return await self.forward(content)
