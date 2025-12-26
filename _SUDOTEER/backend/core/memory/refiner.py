import dspy
import logging
from typing import List, Dict, Any
from .manager import memory_manager

logger = logging.getLogger("_SUDOTEER")

class LearnAntiPattern(dspy.Signature):
	"""
	Analyze a correction log where a user said 'Stop' or 'No'.
	Extract the 'Anti-Pattern' (what the agent did wrong) and generate a blocking rule.
	"""
	correction_log = dspy.InputField()

	anti_pattern = dspy.OutputField(desc="Description of the forbidden action (e.g., 'Deleting folders without backup')")
	meta_lesson = dspy.OutputField(desc="A generalized rule to follow (e.g., 'NEVER delete files without explicit user verification')")
	blocking_rule = dspy.OutputField(desc="A tuple mapping for Graph: (Action, Constraint)")

class MemoryRefiner:
	"""
	The 'Nightly Sifter' update.
	Learns not just skills, but boundaries (Anti-Patterns).
	"""
	def __init__(self):
		self.learner = dspy.ChainOfThought(LearnAntiPattern)

	async def refine_boundaries(self, logs: List[str]):
		"""Process logs to find clusters of user dissatisfaction."""
		logger.info("MemoryRefiner: Sifting logs for boundary learning...")

		for log in logs:
			if "stop" in log.lower() or "no" in log.lower() or "error" in log.lower():
				result = self.learner(correction_log=log)

				logger.info(f"Learned Anti-Pattern: {result.anti_pattern}")

				# Store in Graph as FORBIDDEN_TO
				await memory_manager.graph_store.create_relationship(
					"Agent", "Action", "FORBIDDEN_TO",
					{
						"action": result.anti_pattern,
						"lesson": result.meta_lesson,
						"source_log": log[:100]
					}
				)
				logger.info("Anti-Pattern persisted to Graph.")

# Global instance
memory_refiner = MemoryRefiner()
