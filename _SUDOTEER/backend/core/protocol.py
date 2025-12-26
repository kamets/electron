import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("_SUDOTEER")

class MessagePriority(Enum):
	LOW = "low"
	NORMAL = "normal"
	HIGH = "high"
	URGENT = "urgent"

class A2AMessage:
	"""
	Standardized A2A (Agent-to-Agent) Message Protocol.
	Ensures type-safety and visual consistency across the agency.
	"""
	def __init__(
		self,
		from_agent: str,
		to_agent: str,
		content: Any,
		message_type: str = "request",
		priority: MessagePriority = MessagePriority.NORMAL,
		requires_response: bool = False,
		parent_id: Optional[str] = None,
		metadata: Optional[Dict[str, Any]] = None
	):
		self.message_id = str(uuid.uuid4())
		self.timestamp = datetime.now().isoformat()
		self.from_agent = from_agent
		self.to_agent = to_agent
		self.content = content
		self.message_type = message_type
		self.priority = priority
		self.requires_response = requires_response
		self.parent_id = parent_id
		self.metadata = metadata or {}

	def to_dict(self) -> Dict[str, Any]:
		return {
			"message_id": self.message_id,
			"timestamp": self.timestamp,
			"from_agent": self.from_agent,
			"to_agent": self.to_agent,
			"content": self.content,
			"message_type": self.message_type,
			"priority": self.priority.value,
			"requires_response": self.requires_response,
			"parent_id": self.parent_id,
			"metadata": self.metadata
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
		msg = cls(
			from_agent=data["from_agent"],
			to_agent=data["to_agent"],
			content=data["content"],
			message_type=data.get("message_type", "request"),
			priority=MessagePriority(data.get("priority", "normal")),
			requires_response=data.get("requires_response", False),
			parent_id=data.get("parent_id")
		)
		msg.message_id = data.get("message_id", msg.message_id)
		msg.timestamp = data.get("timestamp", msg.timestamp)
		return msg

	def validate(self) -> bool:
		"""Check if the message adheres to the protocol."""
		if not self.from_agent or not self.to_agent or not self.content:
			return False
		return True
