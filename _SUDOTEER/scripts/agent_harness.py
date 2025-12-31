"""
_SUDOTEER Simple Agent Harness
ChromaDB-only memory with session handoff.
Based on the agent-harness pattern.
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ChromaDB-only memory
from backend.core.memory.vector_db import vector_db

HANDOFF_FILE = Path("scripts/agent_handoff.txt")
FEATURE_LIST = Path("memory/feature_list.json")
PROGRESS_FILE = Path("memory/progress.txt")

class ContextEngine:
	"""OS-level context management for stateless agents."""

	def __init__(self):
		Path("memory").mkdir(exist_ok=True)

	def load_state(self):
		"""Load current project state."""
		# Feature list
		try:
			with open(FEATURE_LIST, "r") as f:
				features = json.load(f)
		except FileNotFoundError:
			features = {
				"status": "active",
				"features": [
					{"name": "test_vector_db", "status": "pending"},
					{"name": "test_factory", "status": "pending"},
					{"name": "test_bus", "status": "pending"},
					{"name": "test_workflow", "status": "pending"},
					{"name": "test_boot", "status": "pending"}
				]
			}

		# Progress notes
		try:
			with open(PROGRESS_FILE, "r") as f:
				notes = f.read()
		except FileNotFoundError:
			notes = "Session started."

		return {"features": features, "notes": notes}

	def save_state(self, features, notes):
		"""Persist state to disk."""
		with open(FEATURE_LIST, "w") as f:
			json.dump(features, f, indent=2)
		with open(PROGRESS_FILE, "w") as f:
			f.write(notes)

	async def recall_context(self, query: str, top_k: int = 5):
		"""Recall from ChromaDB vector memory."""
		try:
			results = await vector_db.search_knowledge(query, top_k=top_k)
			return results
		except Exception as e:
			print(f"   [WARN] Memory recall failed: {e}")
			return []

	async def remember(self, content: str, metadata: dict = None):
		"""Store in ChromaDB vector memory."""
		try:
			await vector_db.add_to_knowledge([content], [metadata or {}])
			return True
		except Exception as e:
			print(f"   [WARN] Memory store failed: {e}")
			return False


async def run_harness():
	print("=" * 60)
	print("   _SUDOTEER Agent Harness")
	print("   ChromaDB Memory | Session-Based Learning")
	print("=" * 60)

	engine = ContextEngine()

	# Load state
	print("\n[1] Loading state...")
	state = engine.load_state()
	pending = [f for f in state["features"]["features"] if f["status"] == "pending"]
	print(f"   Pending features: {len(pending)}")

	# Recall context from memory
	print("\n[2] Recalling context from ChromaDB...")
	context = await engine.recall_context("TDD testing patterns pytest")
	if context:
		print(f"   Found {len(context)} relevant memories")
		for c in context[:3]:
			preview = c.get("content", "")[:60]
			print(f"   - {preview}...")
	else:
		print("   No context found")

	# Show current task
	if pending:
		current_task = pending[0]
		print(f"\n[3] Current task: {current_task['name']}")
		print("   Status: Ready for Coder Agent")

		# Mark as in_progress
		current_task["status"] = "in_progress"
		engine.save_state(
			state["features"],
			f"Session {datetime.now().isoformat()}: Working on {current_task['name']}"
		)

		# Remember this session
		await engine.remember(
			f"Started working on {current_task['name']} at {datetime.now().isoformat()}",
			{"type": "session_start", "feature": current_task["name"]}
		)
	else:
		print("\n[3] All features complete!")

	print("\n" + "=" * 60)
	print("   Harness ready. Spawn agents to process tasks.")
	print("=" * 60)

if __name__ == "__main__":
	asyncio.run(run_harness())
