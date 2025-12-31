import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("_SUDOTEER")

class ContextEngine:
	"""
	_SUDOTEER Context Engine
	Manages information flow, compaction, and retrieval

	Core Principle: "Git History + Artifacts = State Persistence"
	Instead of external vector DBs, we read context from:
	- Git commits
	- Artifact files
	- Progress logs
	- Handoff notes
	"""

	def __init__(self, workspace_dir: str = "."):
		self.workspace = Path(workspace_dir)
		self.MAX_CONTEXT_SIZE = 50000  # characters

	async def load_full_context(self) -> str:
		"""
		Load complete context from all sources.

		Returns:
			Markdown-formatted context string ready for LLM consumption
		"""
		logger.info("Loading full context from artifacts...")

		context_parts = []

		# 1. Git History
		git_log = await self._read_git_log(n=10)
		if git_log:
			context_parts.append(f"## Git History (Last 10 Commits)\n\n{git_log}")

		# 2. Progress Log
		progress = self._read_progress_log()
		if progress:
			context_parts.append(f"## Recent Progress\n\n{progress}")

		# 3. Handoff Notes
		handoff = self._read_handoff_notes()
		if handoff:
			context_parts.append(f"## Handoff Notes\n\n{handoff}")

		# 4. Feature Status
		features = self._read_feature_status()
		if features:
			context_parts.append(f"## Feature Status\n\n{features}")

		# 5. Recent Decisions
		decisions = self._read_recent_decisions(n=20)
		if decisions:
			context_parts.append(f"## Recent Decisions\n\n{decisions}")

		full_context = "\n\n---\n\n".join(context_parts)

		# Check if compaction needed
		if len(full_context) > self.MAX_CONTEXT_SIZE:
			logger.warning(f"Context too large ({len(full_context)} chars), compaction recommended")

		logger.info(f"Context loaded: {len(full_context)} characters")
		return full_context

	# ============================================
	# SOURCE READERS
	# ============================================

	async def _read_git_log(self, n: int = 10) -> Optional[str]:
		"""
		Read last N git commits.

		Format:
		- <hash> <date> <author> <message>
		"""
		try:
			result = subprocess.run(
				['git', 'log', f'-{n}', '--oneline', '--date=short', '--pretty=format:%h %ad %an: %s'],
				cwd=self.workspace,
				capture_output=True,
				text=True,
				timeout=5
			)

			if result.returncode == 0 and result.stdout:
				return result.stdout
			else:
				logger.debug("No git history available")
				return None

		except Exception as e:
			logger.debug(f"Git log failed: {e}")
			return None

	def _read_progress_log(self) -> Optional[str]:
		"""Read progress_log.md, last 1000 lines."""
		progress_file = self.workspace / "progress_log.md"

		if progress_file.exists():
			try:
				lines = progress_file.read_text().split('\n')
				# Keep last 1000 lines (recent sessions)
				recent_lines = lines[-1000:]
				return '\n'.join(recent_lines)
			except Exception as e:
				logger.error(f"Failed to read progress log: {e}")
				return None
		return None

	def _read_handoff_notes(self) -> Optional[str]:
		"""Read context_handoff.txt."""
		handoff_file = self.workspace / "context_handoff.txt"

		if handoff_file.exists():
			return handoff_file.read_text()
		return None

	def _read_feature_status(self) -> Optional[str]:
		"""Read and format feature_status.json."""
		features_file = self.workspace / "feature_status.json"

		if features_file.exists():
			try:
				import json
				features = json.loads(features_file.read_text())

				# Format as human-readable string
				status_str = f"""
**Total Features**: {features.get('total_features', 0)}
**Completed**: {features.get('completed', 0)}
**In Progress**: {features.get('in_progress', 0)}
**Blocked**: {features.get('blocked', 0)}

**Current Features**:
"""
				for feat in features.get('features', [])[:10]:  # Show first 10
					tests = f"{feat.get('tests_passing', 0)}/{feat.get('tests_total', 0)}" if 'tests_total' in feat else "N/A"
					status_str += f"- {feat.get('id', 'unknown')}: {feat.get('status', 'unknown')} (Tests: {tests})\n"

				return status_str

			except Exception as e:
				logger.error(f"Failed to read feature status: {e}")
				return None
		return None

	def _read_recent_decisions(self, n: int = 20) -> Optional[str]:
		"""Read last N decisions from decisions.log."""
		decisions_file = self.workspace / "decisions.log"

		if decisions_file.exists():
			try:
				lines = decisions_file.read_text().split('\n')
				recent = lines[-n:]
				return '\n'.join(recent)
			except Exception as e:
				logger.error(f"Failed to read decisions: {e}")
				return None
		return None

	# ============================================
	# CONTEXT COMPACTION
	# ============================================

	async def compact_context(self, old_context: str, llm_client: Any = None) -> str:
		"""
		Summarize old context using LLM.

		This prevents context window overflow by:
		1. Extracting key points
		2. Removing redundant information
		3. Keeping only critical decisions

		Args:
			old_context: Full context string
			llm_client: Optional LLM client for summarization

		Returns:
			Compacted context (20-30% of original size)
		"""
		if not llm_client:
			logger.warning("No LLM available for compaction, truncating instead")
			return self._truncate_context(old_context)

		summary_prompt = f"""
You are a context summarization system. Summarize the following agent session context into key points.

Focus on:
- What was accomplished
- Key decisions made and why
- Current blockers
- Next steps
- Test results

Be concise but preserve critical information.

CONTEXT TO SUMMARIZE:
{old_context}

SUMMARY:
"""

		try:
			summary = await llm_client.summarize(summary_prompt)
			logger.info(f"Context compacted: {len(old_context)} → {len(summary)} chars")
			return summary

		except Exception as e:
			logger.error(f"LLM compaction failed: {e}, truncating instead")
			return self._truncate_context(old_context)

	def _truncate_context(self, context: str) -> str:
		"""
		Simple truncation fallback if LLM unavailable.
		Keeps first 50% and last 25% of context.
		"""
		length = len(context)

		if length < self.MAX_CONTEXT_SIZE:
			return context

		# Keep beginning (setup) and end (recent work)
		first_half = int(self.MAX_CONTEXT_SIZE * 0.5)
		last_quarter = int(self.MAX_CONTEXT_SIZE * 0.25)

		truncated = context[:first_half] + "\n\n... [CONTEXT TRUNCATED] ...\n\n" + context[-last_quarter:]

		logger.info(f"Context truncated: {length} → {len(truncated)} chars")
		return truncated

	# ============================================
	# CONTEXT UTILITIES
	# ============================================

	def get_context_stats(self, context: str) -> Dict[str, Any]:
		"""Analyze context size and structure."""
		return {
			"total_length": len(context),
			"total_lines": len(context.split('\n')),
			"needs_compaction": len(context) > self.MAX_CONTEXT_SIZE,
			"git_commits": context.count("Git History"),
			"progress_entries": context.count("###"),
			"decisions": context.count("DECISION")
		}

# Global instance
context_engine = ContextEngine()
