import logging
import dspy
from typing import Dict, Any, Union, Optional
from backend.core.agent_base import SudoAgent
from backend.core.protocol import A2AMessage
from backend.core.dspy_signatures import AuditCodeBundle

from .scanner import SecurityScanner
from .enforcer import StandardsEnforcer

logger = logging.getLogger("_SUDOTEER")

class ValidatorAgent(SudoAgent):
	"""
	Tier 3: Validator Agent.
	The Final Audit. Ensures the entire bundle is compliant and secure.

	USES DSPY: ChainOfThought with AuditCodeBundle signature for the final quality gate.
	"""
	def __init__(self, agent_id: str = "validator_01", role: str = "Validator"):
		super().__init__(agent_id, role)
		self.scanner = SecurityScanner()
		self.enforcer = StandardsEnforcer()

		# DSPy Module
		self.auditor = dspy.ChainOfThought(AuditCodeBundle)

	async def forward(self, bundle: Dict[str, Any], quality_standards: str = None) -> Dict[str, Any]:
		"""
		Perform comprehensive final audit of the implementation package.
		"""
		self.log_interaction("Initiating final multi-stage audit...", event_type="thought")

		# Extract components
		code = bundle.get("code", "")
		tests = bundle.get("tests", bundle.get("test_code", ""))
		docs = bundle.get("docs", bundle.get("markdown", ""))

		if not quality_standards:
			quality_standards = "JSDoc compliance, 100% test passing, no high-severity security findings."

		# 1. Local Security Scan (Deterministic)
		findings = self.scanner.scan(str(code))

		# 2. Local Standards Verification (Deterministic)
		violations = self.enforcer.verify(str(code))

		# 3. DSPy Cognitive Audit (The Brain)
		audit_result = self.auditor(
			code=str(code),
			tests=str(tests),
			documentation=str(docs),
			quality_standards=quality_standards
		)

		# Combined Decision Logic
		critical_blockers = findings + violations + audit_result.critical_issues
		is_fully_valid = audit_result.is_valid and len(critical_blockers) == 0

		if is_fully_valid:
			self.log_interaction("Audit PASSED: All security and quality gates cleared.", event_type="result")
		else:
			self.log_interaction(f"Audit FAILED: {len(critical_blockers)} issues identified.", event_type="error")

		return {
			"is_valid": is_fully_valid,
			"audit_report": audit_result.audit_report,
			"critical_issues": critical_blockers,
			"recommendations": audit_result.recommendations,
			"status": "cleared" if is_fully_valid else "flagged"
		}

	async def handle_request(self, message: A2AMessage) -> Any:
		"""Handle requests from the Orchestrator."""
		self.log_interaction(f"Handling audit request from {message.from_agent}", event_type="thought")
		content = message.content
		return await self.forward(content)
