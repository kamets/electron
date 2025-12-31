import logging
import dspy
import asyncio
from typing import Dict, Any, Union, Optional
from backend.core.agent_base import BaseAgent
from backend.core.protocol import A2AMessage
from backend.core.memory.dspy_signatures import GenerateTests, ValidateLogic

from .generator import TestGenerator
from .runner import TestRunner

logger = logging.getLogger("_SUDOTEER")

class TesterAgent(BaseAgent):
	"""
	Tier 3: Tester Agent.
	Responsible for logic validation and quality assurance.

	USES DSPY:
	1. GenerateTests signature to build the test suite.
	2. ValidateLogic signature to check for edge cases and logical consistency.
	"""
	def __init__(self, agent_id: str = "tester_01", role: str = "Tester"):
		super().__init__(agent_id, role)
		self.generator = TestGenerator()
		self.runner = TestRunner()

		# DSPy Modules
		self.test_generator = dspy.ChainOfThought(GenerateTests)
		self.logic_validator = dspy.ChainOfThought(ValidateLogic)

	async def forward(self, code: Union[str, Dict[str, Any]], requirements: str = None) -> Dict[str, Any]:
		"""
		Execute the testing reasoning path.
		"""
		# Normalize input
		if isinstance(code, dict):
			code_str = code.get("code", str(code))
			requirements = code.get("requirements", requirements)
		else:
			code_str = str(code) if code else ""

		if not requirements:
			requirements = "Standard logical correctness, safety, and performance."

		preview = code_str[:50] + "..." if len(code_str) > 50 else code_str
		self.log_interaction(f"Analyzing code for validation: {preview}", event_type="thought")

		# 1. DSPy Test Generation
		test_result = await asyncio.to_thread(self.test_generator, code=code_str, requirements=requirements)
		self.log_interaction("Generated comprehensive test suite with DSPy", event_type="action")

		# 2. Run Tests (Simulated Runner integration)
		# We merge the DSPy generated tests with any local framework requirements
		report = await self.runner.run_suite(test_result.test_code)

		# 3. DSPy Logic Validation (Deep Reasoning)
		validation = await asyncio.to_thread(
			self.logic_validator,
			code=code_str,
			test_results=f"Pass Status: {report['status']}, Coverage: {report['coverage']}%"
		)

		status = "passed" if validation.is_valid and report["status"] == "passed" else "failed"

		# Log result (This triggers automatic self-splitting memory because event_type='result')
		self.log_interaction(
			f"Validation complete. Logic Status: {status}. Reasoning: {validation.recommendations}",
			event_type="result"
		)

		return {
			"status": status,
			"is_valid": validation.is_valid,
			"test_code": test_result.test_code,
			"issues": validation.issues,
			"recommendations": validation.recommendations,
			"report": report
		}

	async def handle_request(self, message: A2AMessage) -> Any:
		"""Handle requests from Coder or Orchestrator."""
		self.log_interaction(f"Handling test request from {message.from_agent}", event_type="thought")
		content = message.content
		if isinstance(content, dict):
			code = content.get("code", "")
			requirements = content.get("architecture", None) # Usually comes from Architect's plan
			return await self.forward(code, requirements)
		else:
			return await self.forward(content)
