import dspy
import logging
from typing import Dict, Any
from ..dspy_signatures import CalibrationCheck

logger = logging.getLogger("_SUDOTEER")

class ConfidenceMonitor(dspy.Module):
	"""
	HANDBOOK: Hubris Detector [2.1].
	Prevents agents from assuming user intent.
	"""
	def __init__(self):
		super().__init__()
		self.calibrator = dspy.ChainOfThought(CalibrationCheck)

	async def verify_plan(self, user_request: str, proposed_plan: str) -> Dict[str, Any]:
		"""
		Runs the calibration check on a proposed plan.
		Returns high-confidence plan or a required clarification question.
		"""
		logger.info("ConfidenceMonitor: Calibrating plan confidence...")

		result = self.calibrator(user_request=user_request, proposed_plan=proposed_plan)

		try:
			ambiguity = float(result.ambiguity_score)
		except:
			ambiguity = 0.0

		return {
			"is_confident": ambiguity <= 0.5,
			"ambiguity_score": ambiguity,
			"assumptions": result.implicit_assumptions,
			"clarification": result.clarification_question if ambiguity > 0.5 else None
		}

# Global monitor instance
confidence_monitor = ConfidenceMonitor()
