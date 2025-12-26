import os
import json
import logging
import importlib.util
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger("_SUDOTEER")

class ADEEngine:
	"""
	Agent Development Environment (ADE) Engine.
	Allows dynamic creation, registration, and assignment of tools to agents.
	"""
	def __init__(self, registry_path: str = "backend/core/tool_registry.json"):
		self.registry_path = registry_path
		self.tools: Dict[str, Dict[str, Any]] = self._load_registry()

	def _load_registry(self) -> Dict[str, Any]:
		"""Load the tool registry from disk."""
		if os.path.exists(self.registry_path):
			try:
				with open(self.registry_path, 'r') as f:
					return json.load(f)
			except Exception as e:
				logger.error(f"Failed to load tool registry: {e}")
		return {}

	def _save_registry(self):
		"""Save the tool registry to disk."""
		with open(self.registry_path, 'w') as f:
			json.dump(self.tools, f, indent='\t')

	def register_tool(self, tool_id: str, code: str, metadata: Dict[str, Any]):
		"""
		Register a new dynamic tool.
		The code is expected to be a valid Python snippet defining a 'run' function.
		"""
		logger.info(f"Registering dynamic tool: {tool_id}")
		tool_entry = {
			"code": code,
			"metadata": metadata, # e.g., {"description": "...", "target_agents": ["coder"]}
			"status": "pending_validation"
		}
		self.tools[tool_id] = tool_entry
		self._save_registry()

	def get_agent_tools(self, agent_id: str) -> Dict[str, Callable]:
		"""Compile and return tools assigned to a specific agent."""
		agent_tools = {}
		for tool_id, info in self.tools.items():
			target_agents = info.get("metadata", {}).get("target_agents", [])
			if agent_id in target_agents or "*" in target_agents:
				try:
					# Dynamically compile the tool code
					spec = importlib.util.spec_from_loader(tool_id, loader=None)
					module = importlib.util.module_from_spec(spec)
					exec(info["code"], module.__dict__)
					if hasattr(module, 'run'):
						agent_tools[tool_id] = module.run
						logger.info(f"Tool {tool_id} compiled and assigned to {agent_id}")
				except Exception as e:
					logger.error(f"Failed to compile tool {tool_id}: {e}")
		return agent_tools

# Global ADE instance
ade_engine = ADEEngine()
