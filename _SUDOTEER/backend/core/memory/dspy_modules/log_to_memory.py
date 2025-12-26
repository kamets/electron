import dspy
import logging
from typing import Dict, Any, List
from ..dspy_signatures import LogToMemory

logger = logging.getLogger("_SUDOTEER")

class ReflectionModule(dspy.Module):
	"""
	HANDBOOK: Episodic Reflection [1.1, 1.2].
	Converts raw session logs into meaningful memories.
	"""
	def __init__(self):
		super().__init__()
		self.reflector = dspy.ChainOfThought(LogToMemory)

	async def reflect(self, raw_log: str) -> Dict[str, Any]:
		"""
		Generates an episodic summary for vector store and entities for graph.
		"""
		logger.info("ReflectionModule: Processing raw log into memory...")

		result = self.reflector(raw_log=raw_log)

		return {
			"summary": result.summary,
			"entities": result.entities,
			"quality": result.quality_score,
			"what_worked": result.what_worked,
			"what_failed": result.what_failed,
			"improvement_plan": result.improvement_plan
		}

# Global instance
reflection_engine = ReflectionModule()
