"""
Simple test for Hybrid Memory Manager and Splitter.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.memory.manager import memory_manager
from backend.core.dspy_config import initialize_dspy

# Set log level to DEBUG to see what's happening
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MemoryTest")

async def test_memory():
	print("\n[TEST] Initializing DSPy...")
	# We need a dummy LM or real config for the splitter to work
	# For this test, we'll try to auto-configure
	initialize_dspy(auto=True)

	print("\n[TEST] Testing memory 'remember' with automatic splitting...")
	data = "The climate control system depends on the industrial bridge for sensor data. The temperature is currently 22.5C."

	try:
		# This will trigger the DSPy splitter
		result = await memory_manager.remember(
			agent_id="test_agent",
			data=data,
			metadata={"test": True}
		)
		print(f"\n[OK] Memory stored! Result: {result}")

		print("\n[TEST] Testing semantic recall...")
		recall_semantic = await memory_manager.recall("How does the climate system get data?", mode="semantic")
		print(f"\n[OK] Semantic Recall: {len(recall_semantic['semantic_context'])} results found.")

		print("\n[TEST] Testing relational recall...")
		recall_graph = await memory_manager.recall("What is linked to the climate control?", mode="relational")
		print(f"\n[OK] Relational Recall complete.")

	except Exception as e:
		print(f"\n[FAIL] Memory test failed: {e}")
		import traceback
		traceback.print_exc()

if __name__ == "__main__":
	asyncio.run(test_memory())
