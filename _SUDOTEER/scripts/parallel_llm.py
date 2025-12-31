"""
PARALLEL LLM: Blitzar (LM Studio) + Kimi K2 (Ollama)
Run both models simultaneously for maximum output!
"""
import asyncio
import sys
import os
import dspy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

async def run_with_model(name: str, model: str, api_base: str, api_key: str, tasks: list):
	"""Run tasks with a specific model."""
	results = []

	try:
		if api_key:
			lm = dspy.LM(model=model, api_base=api_base, api_key=api_key, cache=False)
		else:
			lm = dspy.LM(model=model, api_base=api_base, cache=False)

		print(f"[{name}] Connected!")

		from backend.core.memory.dspy_signatures import GenerateCode

		for i, task in enumerate(tasks, 1):
			print(f"[{name}] Task {i}/{len(tasks)}: {task[:40]}...")

			try:
				# Create fresh generator with this LM
				with dspy.context(lm=lm):
					generator = dspy.ChainOfThought(GenerateCode)
					result = await asyncio.wait_for(
						asyncio.to_thread(
							generator,
							task_description=task,
							architecture_plan="Python with docstrings"
						),
						timeout=120.0
					)

				print(f"[{name}] Task {i}: OK ({len(result.code)} chars)")
				results.append({"task": task, "code": result.code, "model": name})

			except asyncio.TimeoutError:
				print(f"[{name}] Task {i}: TIMEOUT")
			except Exception as e:
				print(f"[{name}] Task {i}: ERROR - {str(e)[:50]}")

	except Exception as e:
		print(f"[{name}] Connection failed: {e}")

	return results

async def main():
	print("=" * 70)
	print("   PARALLEL LLM: Blitzar + Kimi K2")
	print("   Running both models simultaneously!")
	print("=" * 70)

	# Tasks for Blitzar (code generation)
	blitzar_tasks = [
		"Create a function to calculate moving average of sensor readings",
		"Create a function to validate pH sensor reading is in safe range",
		"Create a pytest test for a temperature controller class",
	]

	# Tasks for Kimi K2 (architecture/complex reasoning)
	kimi_tasks = [
		"Design a greenhouse automation system with sensors and actuators",
		"Create a safety watchdog system that monitors hardware timeouts",
		"Design an agent communication protocol for A2A messaging",
	]

	print(f"\nBlitzar tasks: {len(blitzar_tasks)}")
	print(f"Kimi K2 tasks: {len(kimi_tasks)}")
	print("\nStarting parallel execution...")
	print()

	# Run both in parallel
	blitzar_future = run_with_model(
		"BLITZAR",
		"openai/blitzar-coder-4b-f.1",
		"http://localhost:1234/v1",
		"lm-studio",
		blitzar_tasks
	)

	kimi_future = run_with_model(
		"KIMI_K2",
		"ollama_chat/kimi-k2-thinking:cloud",
		"http://localhost:11434",
		None,
		kimi_tasks
	)

	# Wait for both
	results = await asyncio.gather(blitzar_future, kimi_future, return_exceptions=True)

	blitzar_results = results[0] if isinstance(results[0], list) else []
	kimi_results = results[1] if isinstance(results[1], list) else []

	# Save to ChromaDB
	print("\n" + "=" * 70)
	print("   SAVING TO CHROMADB")
	print("=" * 70)

	from backend.core.memory.vector_db import vector_db

	all_results = blitzar_results + kimi_results
	for r in all_results:
		content = f"MODEL: {r['model']}\nTASK: {r['task']}\n\nCODE:\n{r['code']}"
		await vector_db.add_to_knowledge(
			[content],
			[{"type": "parallel_gen", "model": r["model"], "task": r["task"][:50]}]
		)

	print(f"   Saved {len(all_results)} generations to ChromaDB!")

	# Summary
	print("\n" + "=" * 70)
	print("   SUMMARY")
	print("=" * 70)
	print(f"   Blitzar: {len(blitzar_results)}/{len(blitzar_tasks)} tasks")
	print(f"   Kimi K2: {len(kimi_results)}/{len(kimi_tasks)} tasks")
	print(f"   Total saved: {len(all_results)}")

	# Show sample
	if all_results:
		print("\n   Sample output:")
		print(all_results[0]["code"][:400])

if __name__ == "__main__":
	asyncio.run(main())
