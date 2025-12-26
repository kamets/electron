import os
import dspy
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("_SUDOTEER")
load_dotenv(Path(__file__).parent.parent.parent / ".env")

class DSPyConfig:
	"""Lean DSPy configuration with focus on local-first durability."""
	def __init__(self):
		self.lm = None
		self.provider = "None"

	def configure(self, provider: str = "auto") -> bool:
		if provider == "auto":
			return self._auto()
		elif provider == "local":
			return self._local()
		elif provider == "gemini":
			return self._gemini()
		return False

	def _local(self):
		try:
			self.lm = dspy.LM(model="openai/local-model", api_base="http://localhost:1234/v1", api_key="lm-studio")
			self.provider = "LM Studio (Local)"
			dspy.configure(lm=self.lm)
			return True
		except Exception: return False

	def _gemini(self):
		key = os.getenv("GEMINI_API_KEY")
		if not key: return False
		try:
			self.lm = dspy.LM(model="gemini/gemini-2.0-flash-exp", api_key=key)
			self.provider = "Gemini"
			dspy.configure(lm=self.lm)
			return True
		except Exception: return False

	def _auto(self):
		logger.info("[DSPy] Auto-detecting LM...")
		if self._local(): return True
		if self._gemini(): return True
		logger.error("[DSPy] ❌ No LM backend found.")
		return False

dspy_config = DSPyConfig()

def initialize_dspy(auto: bool = True):
	return dspy_config.configure("auto" if auto else "local")
