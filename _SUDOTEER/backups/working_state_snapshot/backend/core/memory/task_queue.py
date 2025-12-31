import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("_SUDOTEER")

@dataclass
class Task:
	id: str
	description: str
	status: str = "not_started"
	priority: str = "medium"
	assigned_to: Optional[str] = None
	notes: str = ""

	def to_dict(self):
		return asdict(self)

class TaskQueue:
	"""Lean and durability-focused task management."""
	def __init__(self, workspace_dir: str = "."):
		self.path = Path(workspace_dir) / "task_queue.json"
		self.tasks: Dict[str, Task] = self._load()

	def _load(self) -> Dict[str, Task]:
		if self.path.exists():
			try:
				data = json.loads(self.path.read_text())
				return {t["id"]: Task(**t) for t in data.get("tasks", [])}
			except Exception:
				return {}
		return {}

	def save(self):
		data = {
			"updated": datetime.now().isoformat(),
			"tasks": [t.to_dict() for t in self.tasks.values()]
		}
		self.path.write_text(json.dumps(data, indent=2))

	def add_task(self, task_id: str, description: str, priority: str = "medium"):
		self.tasks[task_id] = Task(task_id, description, priority=priority)
		self.save()

	def update_task(self, task_id: str, **kwargs):
		if task_id in self.tasks:
			for k, v in kwargs.items():
				if hasattr(self.tasks[task_id], k):
					setattr(self.tasks[task_id], k, v)
			self.save()

	def get_next(self, agent_id: str = None) -> Optional[Task]:
		# Return first not_started or assigned
		for t in self.tasks.values():
			if t.assigned_to == agent_id and t.status == "in_progress":
				return t
		for t in self.tasks.values():
			if t.status == "not_started":
				return t
		return None

task_queue = TaskQueue()
