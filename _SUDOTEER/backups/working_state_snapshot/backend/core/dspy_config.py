import os

# CRITICAL: Disable DSPy's structured outputs BEFORE importing dspy
# This prevents the 'response_format.type' error with LM Studio
os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

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
			lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
			lm_model = os.getenv("LM_STUDIO_MODEL", "openai/local-model")
			# Disable JSON mode and caching - not supported by LM Studio
			self.lm = dspy.LM(
				model=lm_model,
				api_base=lm_url,
				api_key="lm-studio",
				cache=False
			)
			self.provider = f"LM Studio ({lm_model})"
			# Configure with experimental features off
			dspy.configure(lm=self.lm, experimental=False)
			logger.info(f"[DSPy] Connected to LM Studio: {lm_model} @ {lm_url}")
			return True
		except Exception as e:
			logger.warning(f"[DSPy] LM Studio connection failed: {e}")
			return False

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
