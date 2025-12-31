import sys
import os
import pytest
import pytest_asyncio
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Configure pytest-asyncio to run all async tests
pytest_plugins = ['pytest_asyncio']

@pytest.fixture(autouse=True)
def setup_logging():
	import logging
	logging.basicConfig(level=logging.INFO)

@pytest.fixture
def mock_dspy_lm(monkeypatch):
	import dspy

	class MockLM:
		def __init__(self):
			self.history = []

		def __call__(self, *args, **kwargs):
			# Minimal mock logic
			return [{"text": "mock response"}]

	# Instead of full mock, we can just use a simple one if needed
	# But better to just mock the modules in the splitter
	pass
