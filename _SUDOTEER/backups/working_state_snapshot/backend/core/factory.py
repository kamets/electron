import logging
from typing import Dict, Any, Type, Optional
from .agent_base import SudoAgent
from .ade_engine import ade_engine
from .bus import bus

logger = logging.getLogger("_SUDOTEER")

class AgentFactory:
	"""
	Central factory for spawning and configuring agents.
	Handles workstation setup, tool assignment, and bus registration.
	"""
	def __init__(self):
		self.active_agents: Dict[str, SudoAgent] = {}
		self._role_map = {}

	def register_role(self, role: str, agent_class: Type[SudoAgent]):
		"""Map a role name to an agent class."""
		self._role_map[role.lower()] = agent_class

	def spawn_agent(self, role: str, agent_id: str, config: Optional[Dict[str, Any]] = None) -> SudoAgent:
		"""
		Create a new agent instance, configure it, and register it.
		"""
		agent_class = self._role_map.get(role.lower())
		if not agent_class:
			raise ValueError(f"Unknown agent role: {role}")

		logger.info(f"Spawning agent: {agent_id} as {role}")

		# 1. Initialize Instance
		agent_instance = agent_class(agent_id=agent_id, role=role)

		# 2. Assign Custom Tools from ADE
		custom_tools = ade_engine.get_agent_tools(agent_id)
		agent_instance.tools = custom_tools

		# 3. Register on A2A Bus
		bus.register_agent(agent_id, agent_instance)

		self.active_agents[agent_id] = agent_instance
		return agent_instance

	def get_agent(self, agent_id: str) -> Optional[SudoAgent]:
		"""Retrieve an active agent by ID."""
		return self.active_agents.get(agent_id)

# Global factory instance
agent_factory = AgentFactory()
