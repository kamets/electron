"""
Sequential LLM Agent Test - Run one at a time to avoid DSPy conflicts.
"""
import asyncio
import sys
import os
import dspy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

async def test_single_agent(name: str, model: str, api_base: str, task: str):
	"""Test one agent with one LLM."""
	print(f"\n{'='*60}")
	print(f"   [{name}] Testing with {model}")
	print(f"{'='*60}")

	# Configure LM
	if "ollama" in model:
		lm = dspy.LM(model=model, api_base=api_base, cache=False)
	else:
		lm = dspy.LM(model=model, api_base=api_base, api_key="lm-studio", cache=False)

	dspy.configure(lm=lm, experimental=False)
	print(f"   [OK] LM configured")

	# Import fresh agent (avoid caching issues)
	from backend.core.memory.dspy_signatures import GenerateCode

	# Use DSPy directly instead of full agent (bypass Neo4j)
	generator = dspy.ChainOfThought(GenerateCode)

	print(f"   Task: {task}")
	print(f"   Generating...")

	try:
		result = await asyncio.wait_for(
			asyncio.to_thread(
				generator,
				task_description=task,
				architecture_plan="Simple Python function with docstring"
			),
			timeout=120.0
		)

		code = result.code
		explanation = result.explanation

		print(f"\n   [DONE] Generated {len(code)} chars")
		print(f"\n   --- Code ---")
		print(code)
		print(f"   --- End ---")
		print(f"\n   Explanation: {explanation[:200]}...")

		return {"name": name, "code": code, "success": True}

	except asyncio.TimeoutError:
		print(f"   [TIMEOUT]")
		return {"name": name, "code": "", "success": False}
	except Exception as e:
		print(f"   [ERROR] {e}")
		return {"name": name, "code": str(e), "success": False}

async def main():
	print("=" * 60)
	print("   Sequential LLM Agent Test")
	print("   LM Studio then Ollama")
	print("=" * 60)

	task = "Create a function called sensor_average that returns the average of a list of numbers"

	# Test 1: LM Studio
	result1 = await test_single_agent(
		"LM_STUDIO",
		"openai/ministral-3-3b",
		"http://localhost:1234/v1",
		task
	)

	# Test 2: Ollama
	result2 = await test_single_agent(
		"OLLAMA",
		"ollama_chat/qwen3:1.7b",
		"http://localhost:11434",
		task
	)

	# Summary
	print(f"\n{'='*60}")
	print("   SUMMARY")
	print(f"{'='*60}")
	print(f"   LM Studio: {'SUCCESS' if result1['success'] else 'FAILED'} ({len(result1['code'])} chars)")
	print(f"   Ollama:    {'SUCCESS' if result2['success'] else 'FAILED'} ({len(result2['code'])} chars)")

if __name__ == "__main__":
	asyncio.run(main())
