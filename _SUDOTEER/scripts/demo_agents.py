"""
Agent Workflow Demo: Coder + Observer working together.
Shows how agents collaborate with memory to generate and review code.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.dspy_config import initialize_dspy
from backend.agents.coder.agent import CoderAgent
from backend.agents.observer.agent import CodeReviewObserver, TestObserver

async def demo_workflow():
	print("=" * 60)
	print("   _SUDOTEER Agent Workflow Demo")
	print("   Coder Agent + Observer Agents")
	print("=" * 60)

	# Initialize LLM (try LM Studio -> Ollama -> Gemini)
	print("\n[1] Initializing LLM backend...")
	if not initialize_dspy():
		print("   [WARN] No LLM available - running in mock mode")
	else:
		print("   [OK] LLM connected")

	# Create agents
	print("\n[2] Spawning agents...")
	coder = CoderAgent(agent_id="coder_demo")
	code_reviewer = CodeReviewObserver(agent_id="reviewer_demo")
	test_observer = TestObserver(agent_id="test_observer_demo")

	print(f"   - {coder.agent_id} ({coder.role})")
	print(f"   - {code_reviewer.agent_id} ({code_reviewer.role})")
	print(f"   - {test_observer.agent_id} ({test_observer.role})")

	# Demo task: Generate a simple utility function
	task = "Create a Python function to calculate moving average of sensor readings"

	print(f"\n[3] Task assigned to Coder:")
	print(f"    '{task}'")

	# Step 1: Coder generates code
	print("\n[4] Coder Agent working...")
	try:
		result = await coder.forward(task)
		code = result.get("code", "# No code generated")
		status = result.get("status", "unknown")

		print(f"   Status: {status}")
		print(f"   Code preview: {code[:200]}..." if len(code) > 200 else f"   Code: {code}")

		# Step 2: Observer reviews the code
		print("\n[5] Code Reviewer observing...")
		review = await code_reviewer.review_code(code, context=task)
		print(f"   Quality Score: {review['quality_score']:.2f}")
		print(f"   Observations: {review['observations']}")
		print(f"   Recommendation: {review['recommendation']}")

		# Step 3: Observer records the pattern
		print("\n[6] Recording to memory...")
		observation = {
			"type": "code_generation",
			"agent_id": coder.agent_id,
			"success": status == "success",
			"code": code,
			"explanation": result.get("explanation", "")
		}
		learn_result = await code_reviewer.forward(observation)
		print(f"   Learning status: {learn_result['status']}")

		# Step 4: Simulate test run
		print("\n[7] Test Observer monitoring...")
		test_results = {
			"passed": 5,
			"failed": 0,
			"failures": []
		}
		test_learning = await test_observer.observe_test_run(test_results)
		print(f"   Test status: {test_learning['status']}")

	except Exception as e:
		print(f"   [ERROR] {e}")
		# Fallback demo with mock code
		code = '''
def moving_average(readings: list, window: int = 5) -> list:
	"""Calculate moving average of sensor readings."""
	if len(readings) < window:
		return readings
	return [sum(readings[i:i+window])/window for i in range(len(readings)-window+1)]
'''
		print(f"   [MOCK] Using fallback code")
		review = await code_reviewer.review_code(code, context=task)
		print(f"   Review: {review['recommendation']}")

	# Final summary
	print("\n[8] Session Summary:")
	reviewer_stats = code_reviewer.get_stats()
	print(f"   Code Reviewer: {reviewer_stats['observations']} observations, {reviewer_stats['learnings']} learnings")

	print("\n" + "=" * 60)
	print("   Demo Complete!")
	print("=" * 60)

if __name__ == "__main__":
	asyncio.run(demo_workflow())
