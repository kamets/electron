import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("_SUDOTEER")

class AgencyMatryoshka:
	"""
	The Strategic Ingestion Engine.
	Manages agent 'Knowledge Levels' and 'Unlocked Concepts'.
	Follows the Matryoshka pattern: Layered knowledge reveal.
	"""

	LEVELS = {
		1: {
			"name": "Module 1: The Foundation",
			"description": "Anatomy of Memory (Graph Rules & Vector Vibes).",
			"unlocked_features": ["dvr", "episodic_recall", "semantic_recall"],
			"xp_required": 0
		},
		2: {
			"name": "Module 2: The Orchestration",
			"description": "The Context Sandwich & DSPy logic (Hubris Detector).",
			"unlocked_features": ["constitution", "confidence_calibration", "context_sandwich"],
			"xp_required": 50
		},
		3: {
			"name": "Module 3: The Mastery Loop",
			"description": "XP-based tool gating (Fog of War) and Curiosity loop.",
			"unlocked_features": ["tool_mastery", "curiosity_loop", "read_docs_xp"],
			"xp_required": 200
		},
		4: {
			"name": "Module 4: Verification",
			"description": "Advanced self-audit and automated rule learning (Sifter).",
			"unlocked_features": ["anti_pattern_learning", "risk_assessment", "self_audit"],
			"xp_required": 500
		}
	}

	def __init__(self, persistence_file: str = "sandbox/knowledge_state.json"):
		self.persistence_file = Path(persistence_file)
		self.state = self._load_state()

	def _load_state(self) -> Dict[str, Any]:
		if self.persistence_file.exists():
			try:
				with open(self.persistence_file, "r") as f:
					state = json.load(f)
					# Migration for missing keys
					if "agent_levels" not in state: state["agent_levels"] = {}
					if "agent_stats" not in state: state["agent_stats"] = {}
					if "global_level" not in state: state["global_level"] = 1
					return state
			except Exception as e:
				logger.error(f"Failed to load state: {e}. Resetting...")

		return {"global_level": 1, "agent_stats": {}, "agent_levels": {}}

	def _save_state(self):
		os.makedirs(self.persistence_file.parent, exist_ok=True)
		with open(self.persistence_file, "w") as f:
			json.dump(self.state, f, indent=4)

	def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
		if agent_id not in self.state["agent_stats"]:
			self.state["agent_stats"][agent_id] = {"xp": 0, "level": 1, "mastery": {}}
		return self.state["agent_stats"][agent_id]

	def add_xp(self, agent_id: str, amount: int):
		stats = self.get_agent_stats(agent_id)
		stats["xp"] += amount
		logger.info(f"✨ Agent {agent_id} gained {amount} XP! Total: {stats['xp']}")

		# Check level up
		next_level = stats["level"] + 1
		if next_level in self.LEVELS and stats["xp"] >= self.LEVELS[next_level]["xp_required"]:
			stats["level"] = next_level
			logger.info(f"🏆 LEVEL UP! {agent_id} reached {self.LEVELS[next_level]['name']}")

		self._save_state()

	def get_level(self, agent_id: str = None) -> int:
		if agent_id and agent_id in self.state["agent_levels"]:
			return self.state["agent_levels"][agent_id]
		return self.state["global_level"]

	def unlock_level(self, level: int, agent_id: str = None):
		"""Strategic advancement of agent capabilities."""
		if level not in self.LEVELS:
			return

		if agent_id:
			self.state["agent_levels"][agent_id] = level
			logger.info(f"🏆 Agent {agent_id} leveled up to Level {level}: {self.LEVELS[level]['name']}!")
		else:
			self.state["global_level"] = level
			logger.info(f"🌟 Global Agency Level set to {level}: {self.LEVELS[level]['name']}!")

		self._save_state()

	def check_unlocked(self, feature: str, agent_id: str = None) -> bool:
		current_level = self.get_level(agent_id)
		for l_idx in range(1, current_level + 1):
			if feature in self.LEVELS[l_idx]["unlocked_features"]:
				return True
		return False

# Global instance
matryoshka_engine = AgencyMatryoshka()
