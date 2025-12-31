"""
Quick Qwen3-4B Test - Simple task, no source code context.
"""
import asyncio
import sys
import os
import dspy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

async def quick_test():
	print("=" * 60)
	print("   Quick Qwen3-4B Test")
	print("=" * 60)

	# Configure LM
	lm = dspy.LM(
		model="openai/qwen3-4b",
		api_base="http://localhost:1234/v1",
		api_key="lm-studio",
		cache=False
	)
	dspy.configure(lm=lm, experimental=False)
	print("\n[OK] Connected")

	# Simple task
	from backend.core.memory.dspy_signatures import GenerateCode
	generator = dspy.ChainOfThought(GenerateCode)

	task = "Create a pytest test for a function that adds two numbers"

	print(f"\n[TASK] {task}")
	print("   Generating...")

	try:
		result = await asyncio.wait_for(
			asyncio.to_thread(
				generator,
				task_description=task,
				architecture_plan="Simple pytest test with assert"
			),
			timeout=60.0  # 1 minute
		)

		print(f"\n[DONE] {len(result.code)} chars")
		print("\n--- Code ---")
		print(result.code)
		print("--- End ---")

	except asyncio.TimeoutError:
		print("   [TIMEOUT]")
	except Exception as e:
		print(f"   [ERROR] {e}")

if __name__ == "__main__":
	asyncio.run(quick_test())
