import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("_SUDOTEER")

class MonologueRecorder:
	"""
	_SUDOTEER Agent Observation System.
	Records minute-by-minute internal thought processes and external communications.
	Produces structured JSON datasets for training (SFT/DPO) and forensic auditing.
	"""
	def __init__(self, base_path: str = "sandbox/monologues"):
		self.base_path = base_path
		os.makedirs(self.base_path, exist_ok=True)
		self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
		self.log_file = os.path.join(self.base_path, f"session_{self.session_id}.json")
		self.history: List[Dict[str, Any]] = []

	def record_event(self, agent_id: str, role: str, event_type: str, content: Any, metadata: Dict[str, Any] = None):
		"""
		Capture a specific grain of agent activity.
		event_type: 'thought' (internal), 'message' (A2A), 'action' (Tool), 'result'.
		"""
		entry = {
			"timestamp": datetime.now().isoformat(),
			"agent_id": agent_id,
			"role": role,
			"type": event_type,
			"content": content,
			"metadata": metadata or {}
		}

		# Log to terminal for real-time visibility ("Window into their world")
		log_prefix = f"[{agent_id}]"
		if event_type == 'thought':
			logger.info(f"{log_prefix} THOUGHT: {content[:100]}...")
		elif event_type == 'message':
			logger.info(f"{log_prefix} COMM: Sending to {metadata.get('target', 'unknown')}")

		self.history.append(entry)
		self._persist()

	def _persist(self):
		"""Save current session history to disk as a JSON training set."""
		try:
			with open(self.log_file, 'w') as f:
				json.dump(self.history, f, indent='\t')
		except Exception as e:
			logger.error(f"Failed to persist monologue: {e}")

	def get_agent_status(self) -> Dict[str, Any]:
		"""Summarize current status of all agents based on latest events."""
		status_map = {}
		for entry in self.history:
			status_map[entry["agent_id"]] = {
				"latest_event": entry["type"],
				"latest_content": entry["content"],
				"time": entry["timestamp"]
			}
		return status_map

# Global observation instance
recorder = MonologueRecorder()
