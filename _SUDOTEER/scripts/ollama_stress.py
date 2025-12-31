"""
Ollama Stress Test - Multiple code generation tasks to verify reliability.
"""
import asyncio
import sys
import os
import dspy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

TASKS = [
	"Create a function to calculate the average of a list",
	"Create a function to find the maximum value in a list",
	"Create a function to reverse a string",
	"Create a pytest test for a function that multiplies two numbers",
	"Create a class called Sensor with temperature and humidity attributes",
]

async def run_task(generator, task: str, index: int):
	"""Run a single generation task."""
	print(f"\n[{index+1}] {task[:50]}...")

	try:
		result = await asyncio.wait_for(
			asyncio.to_thread(
				generator,
				task_description=task,
				architecture_plan="Simple Python with docstring"
			),
			timeout=60.0
		)

		code = result.code
		print(f"   [OK] {len(code)} chars")
		return {"task": task, "code": code, "success": True}

	except asyncio.TimeoutError:
		print(f"   [TIMEOUT]")
		return {"task": task, "code": "", "success": False}
	except Exception as e:
		print(f"   [ERROR] {e}")
		return {"task": task, "code": str(e), "success": False}

async def main():
	print("=" * 60)
	print("   Ollama qwen3:1.7b Stress Test")
	print(f"   {len(TASKS)} tasks to verify reliability")
	print("=" * 60)

	# Configure Ollama
	lm = dspy.LM(
		model="ollama_chat/qwen3:1.7b",
		api_base="http://localhost:11434",
		cache=False
	)
	dspy.configure(lm=lm, experimental=False)
	print("\n[OK] Connected to Ollama")

	# Load generator
	from backend.core.memory.dspy_signatures import GenerateCode
	generator = dspy.ChainOfThought(GenerateCode)

	# Run all tasks
	results = []
	for i, task in enumerate(TASKS):
		result = await run_task(generator, task, i)
		results.append(result)

	# Summary
	print("\n" + "=" * 60)
	print("   RESULTS")
	print("=" * 60)

	success = sum(1 for r in results if r["success"])
	print(f"\n   Success: {success}/{len(TASKS)} ({100*success//len(TASKS)}%)")

	print("\n   Generated Code Samples:")
	for r in results:
		if r["success"]:
			preview = r["code"][:150].replace('\n', ' ')
			print(f"\n   [{r['task'][:30]}...]")
			print(f"   {preview}...")

	print("\n" + "=" * 60)

if __name__ == "__main__":
	asyncio.run(main())
