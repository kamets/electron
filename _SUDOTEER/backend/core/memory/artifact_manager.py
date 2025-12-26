import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("_SUDOTEER")

class ArtifactManager:
	"""
	Lean Artifact Manager for human-readable audit trails.
	Focuses on transparency and durability of the session history.
	"""
	def __init__(self, workspace_dir: str = "."):
		self.workspace = Path(workspace_dir)
		self.progress_file = self.workspace / "progress_log.md"
		self.decisions_file = self.workspace / "decisions.log"
		self.workspace.mkdir(exist_ok=True)

	def log_progress(self, agent_id: str, message: str):
		"""Append a timestamped entry to the markdown progress log."""
		ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		entry = f"[{ts}] **{agent_id}**: {message}\n"

		with open(self.progress_file, "a", encoding="utf-8") as f:
			f.write(entry)
		logger.debug(f"Progress recorded: {agent_id}")

	def log_decision(self, agent_id: str, decision: str, rationale: str):
		"""Log a critical architectural or operational decision."""
		ts = datetime.now().isoformat()
		entry = f"{ts} | {agent_id} | DECISION | {decision} | RATIONALE: {rationale}\n"

		with open(self.decisions_file, "a", encoding="utf-8") as f:
			f.write(entry)
		logger.info(f"Decision persisted: {decision}")

# Global instance
artifact_manager = ArtifactManager()
