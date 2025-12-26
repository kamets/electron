import logging
from typing import Dict, Any, List, Optional
from .sandbox import ToolSandbox

logger = logging.getLogger("_SUDOTEER")

class IntelligentToolSelector:
	"""
	_SUDOTEER Intelligent Tool Selector.
	Selects the most effective tools for an agent's task based on capability and performance history.
	"""
	def __init__(self):
		self.sandbox = ToolSandbox()
		self.tool_usage_history = {} # Tracks tool success rates

	def select_tools(self, role: str, task: str) -> List[str]:
		"""
		Selects a subset of tools from the whitelist suitable for the task.
		"""
		whitelist = self.sandbox.get_whitelist()
		recommended = []

		task_lower = task.lower()

		# Heuristics for tool selection
		if role == "Coder":
			recommended.extend(["os", "json", "ast", "re"])
		if "api" in task_lower or "request" in task_lower:
			recommended.append("aiohttp")
		if "math" in task_lower or "calculate" in task_lower:
			recommended.append("math")

		# Ensure we only recommend what's in the whitelist
		final_selection = [tool for tool in recommended if tool in whitelist]

		# Default fallback
		if not final_selection:
			final_selection = ["json"]

		logger.info(f"ToolSelector: Recommended {final_selection} for role {role}")
		return final_selection

	def record_tool_performance(self, tool_name: str, success: bool):
		"""Log how a tool performed to improve future selection."""
		if tool_name not in self.tool_usage_history:
			self.tool_usage_history[tool_name] = {"success": 0, "total": 0}

		self.tool_usage_history[tool_name]["total"] += 1
		if success:
			self.tool_usage_history[tool_name]["success"] += 1

# Global tool selector
tool_selector = IntelligentToolSelector()
