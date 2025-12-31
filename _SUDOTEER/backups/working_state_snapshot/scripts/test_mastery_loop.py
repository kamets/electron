import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agents.supervisor.agent import SupervisorAgent
from backend.core.gamification import matryoshka_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("_SUDOTEER_TEST")

async def test_mastery_loop():
	logger.info("--- STARTING MASTERY LOOP TEST ---")

	agent = SupervisorAgent(agent_id="test_master_01")

	# 1. Initial State
	stats = matryoshka_engine.get_agent_stats(agent.agent_id)
	logger.info(f"Initial Stats: {stats}")

	# 2. Read Documentation (Ingest Facts + Gain XP)
	doc_path = os.path.abspath("docs/DSpy/Advanced Chunking Protocols.md")
	logger.info(f"Reading documentation: {doc_path}")

	result = await agent.read_documentation(doc_path)
	logger.info(f"Ingestion Result: {result}")

	# 3. Check Stats again
	stats = matryoshka_engine.get_agent_stats(agent.agent_id)
	logger.info(f"Post-Reading Stats: {stats}")

	# 4. Perform a task with the newly ingested context
	# (In a real test, the context sandwich would now include the chunking protocols info)
	user_goal = "Analyze the best chunking strategy for technical docs."
	logger.info(f"Agent reasoning about goal: {user_goal}")

	# We simulate a forward pass.
	# Note: In a real environment, this calls OpenAI/Anthropic.
	# For local test without API keys, it might fail unless dspy is mocked.
	try:
		# We just check if get_context returns the sandwich with facts
		context = await agent.get_context(user_goal)
		logger.info(f"Assembled Context Sandwich Preview:\n{context[:500]}...")

		if "Advanced Chunking Protocols" in context or "Protocol Beta" in context:
			logger.info("✅ Context Sandwich successfully includes ingested documentation facts!")
		else:
			logger.info("❌ Context Sandwich missing ingested facts.")

	except Exception as e:
		logger.error(f"Reasoning test failed (likely missing API keys): {e}")

	# 5. Test Reflection (Sifter)
	logger.info("Triggering Sifter session-end reflection...")
	from backend.core.memory.manager import memory_manager
	await memory_manager.sifter_session_end(agent.agent_id)

	logger.info("--- MASTERY LOOP TEST COMPLETE ---")

if __name__ == "__main__":
	asyncio.run(test_mastery_loop())
