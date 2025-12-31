import logging
from typing import Dict, Any, Union, Optional
from backend.core.agent_base import BaseAgent
from backend.core.llm.seeker import llm_seeker

logger = logging.getLogger("_SUDOTEER")

class SeekerAgent(BaseAgent):
	"""
	_SUDOTEER Seeker Agent.
	A specialized LOM (Language model Operation Model) that searches for
	available LLMs to ensure a 'human-hassle-free' experience.
	"""
	def __init__(self, agent_id: str = "seeker_01", role: str = "Seeker"):
		super().__init__(agent_id, role)

	async def forward(self, *args, **kwargs):
		"""
		Main seeker logic: Search and Connect.
		"""
		self.log_interaction("Seeking language model nodes...", event_type="thought")

		nodes = await llm_seeker.scan_local_host()

		if nodes:
			self.log_interaction(f"Found {len(nodes)} nodes. Establishing connection...", event_type="result")
			return {
				"status": "connected",
				"nodes": nodes,
				"primary_node": nodes[0]["url"]
			}
		else:
			self.log_interaction("No local nodes found. Searching wider network...", event_type="thought")
			# Wider scan placeholder
			return {"status": "searching", "nodes": []}

	async def handle_request(self, message: 'A2AMessage') -> Any:
		"""Handle requests to find models or verify connection status."""
		return await self.forward()
