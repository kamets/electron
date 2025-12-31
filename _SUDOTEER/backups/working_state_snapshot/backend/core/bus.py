import logging
import asyncio
from typing import Dict, List, Any, Callable, Optional
from .protocol import A2AMessage
from .monologue import recorder

logger = logging.getLogger("_SUDOTEER")

class A2ABus:
	"""
	Standardized A2A Communication Bus.
	Supports peer-to-peer requests, broadcasting, and state synchronization.
	Every message is logged for forensic auditing and training datasets.
	"""
	def __init__(self):
		self.subscribers: Dict[str, List[Callable]] = {}
		self.agent_registry: Dict[str, Any] = {}

	def register_agent(self, agent_id: str, agent_instance: Any, capabilities: List[str] = None):
		"""Register an agent and its capabilities on the bus."""
		self.agent_registry[agent_id] = {
			"instance": agent_instance,
			"capabilities": capabilities or []
		}
		logger.info(f"Agent {agent_id} registered on A2A Bus with capabilities: {capabilities}")

	async def subscribe(self, topic: str, callback: Callable):
		"""Subscribe an agent/tool to a data stream or topic."""
		if topic not in self.subscribers:
			self.subscribers[topic] = []
		self.subscribers[topic].append(callback)
		logger.info(f"Subscription added for topic: {topic}")

	async def publish(self, topic: str, message_data: Any):
		"""Publish a message to all subscribers of a topic."""
		if topic in self.subscribers:
			logger.info(f"Publishing to topic: {topic} ({len(self.subscribers[topic])} targets)")

			# Wrap in a generic message for the recorder if it's raw sensor data
			if not isinstance(message_data, A2AMessage):
				msg_obj = A2AMessage(from_agent="system", to_agent=f"topic:{topic}", content=message_data, message_type="broadcast")
			else:
				msg_obj = message_data

			recorder.record_event(
				agent_id=msg_obj.from_agent,
				role="system",
				event_type="broadcast",
				content=msg_obj.content,
				metadata={"topic": topic}
			)

			tasks = [callback(message_data) for callback in self.subscribers[topic]]
			await asyncio.gather(*tasks)

	async def send_request(self, message: A2AMessage) -> Any:
		"""Peer-to-peer request between agents."""
		if not message.validate():
			logger.error(f"Invalid A2A message format from {message.from_agent}")
			return None

		target_agent = message.to_agent
		if target_agent in self.agent_registry:
			logger.info(f"A2A REQ: {message.from_agent} -> {target_agent}")

			# Record for digital-twin training
			recorder.record_event(
				agent_id=message.from_agent,
				role="agent",
				event_type="message",
				content=message.content,
				metadata=message.to_dict()
			)

			agent_data = self.agent_registry[target_agent]
			return await agent_data["instance"].handle_request(message)
		else:
			logger.warning(f"Target agent {target_agent} not found.")
			return None

# Global bus instance for the agency
bus = A2ABus()
