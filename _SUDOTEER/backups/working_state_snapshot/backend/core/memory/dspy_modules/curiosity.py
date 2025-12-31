import dspy
import logging
from typing import Dict, Any, List
from ..dspy_signatures import CuriosityCheck

logger = logging.getLogger("_SUDOTEER")

class CuriosityModule(dspy.Module):
	"""
	HANDBOOK: Curiosity Loop [2.1].
	Incentivizes reading documentation over guessing.
	"""
	def __init__(self):
		super().__init__()
		self.checker = dspy.ChainOfThought(CuriosityCheck)

	async def evaluate_curiosity(self, task: str, mastery_level: str) -> Dict[str, Any]:
		"""
		Decides if we should read docs or execute tool.
		"""
		logger.info("CuriosityModule: Evaluating if research is needed...")

		result = self.checker(task=task, current_mastery=mastery_level)

		return {
			"action": result.action, # READ_DOCS or EXECUTE_TOOL
			"reasoning": result.reasoning,
			"recommended_docs": result.available_docs if hasattr(result, "available_docs") else []
		}

# Global instance
curiosity_engine = CuriosityModule()
