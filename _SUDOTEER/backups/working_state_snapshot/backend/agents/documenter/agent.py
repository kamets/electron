import logging
import dspy
import asyncio
from typing import Dict, Any, Union, Optional
from backend.core.agent_base import BaseAgent
from backend.core.protocol import A2AMessage
from backend.core.memory.dspy_signatures import GenerateDocumentation

from .generator import DocGenerator

logger = logging.getLogger("_SUDOTEER")

class DocumenterAgent(BaseAgent):
	"""
	Tier 3: Documenter Agent.
	Generates clean, professional documentation for the system.

	USES DSPY: ChainOfThought with GenerateDocumentation signature.
	"""
	def __init__(self, agent_id: str = "documenter_01", role: str = "Documenter"):
		super().__init__(agent_id, role)
		self.generator = DocGenerator()

		# DSPy Module
		self.doc_generator = dspy.ChainOfThought(GenerateDocumentation)

	async def forward(self, bundle: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
		"""
		Reasoning path for documentation generation.
		"""
		# Extract components from bundle
		if isinstance(bundle, dict):
			code = bundle.get("code", "")
			architecture = bundle.get("architecture", "Unknown architecture")
			test_results = str(bundle.get("test_results", "Not tested"))
		else:
			code = str(bundle)
			architecture = "Standard implementation"
			test_results = "N/A"

		self.log_interaction("Analyzing code and architecture context for documentation", event_type="thought")

		# 1. DSPy Documentation Generation
		result = await asyncio.to_thread(
			self.doc_generator,
			code=code,
			architecture=architecture,
			test_results=test_results
		)

		# 2. Apply JSDoc standards using local utility
		enriched_code = self.generator.apply_jsdoc(code)
		self.log_interaction("Applied JSDoc and project documentation standards", event_type="action")

		self.log_interaction("High-quality documentation bundle produced", event_type="result")

		return {
			"status": "completed",
			"markdown": result.documentation,
			"api_docs": result.api_reference,
			"enriched_code": enriched_code
		}

	async def handle_request(self, message: A2AMessage) -> Any:
		"""Handle documentation requests from Tester or Orchestrator."""
		self.log_interaction(f"Handling doc request from {message.from_agent}", event_type="thought")
		content = message.content
		return await self.forward(content)
