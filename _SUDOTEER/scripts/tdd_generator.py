"""
TDD Generator with Blitzar-coder-4b (LM Studio)
Our best performing model so far!
"""
import asyncio
import sys
import os
import dspy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

MODULES_TO_TEST = [
	{
		"name": "bus",
		"path": "backend/core/bus.py",
		"output": "tests/test_bus_generated.py",
		"task": "Create pytest tests for A2ABus class testing send_request and broadcast methods"
	},
	{
		"name": "factory",
		"path": "backend/core/factory.py",
		"output": "tests/test_factory_generated.py",
		"task": "Create pytest tests for AgentFactory class testing spawn_agent and get_agent methods"
	},
	{
		"name": "workflow",
		"path": "backend/core/workflow.py",
		"output": "tests/test_workflow_generated.py",
		"task": "Create pytest tests for WorkflowEngine testing add_step and execute methods"
	}
]

async def generate_tests():
	print("=" * 60)
	print("   TDD Generator - Blitzar-coder-4b (LM Studio)")
	print("   THE CHAMPION MODEL!")
	print("=" * 60)

	# Configure LM Studio with Blitzar
	lm = dspy.LM(
		model="openai/blitzar-coder-4b",
		api_base="http://localhost:1234/v1",
		api_key="lm-studio",
		cache=False
	)
	dspy.configure(lm=lm, experimental=False)
	print("\n[OK] Connected to Blitzar-coder-4b")

	# Load generator
	from backend.core.memory.dspy_signatures import GenerateTests
	generator = dspy.ChainOfThought(GenerateTests)

	results = []

	for i, module in enumerate(MODULES_TO_TEST, 1):
		print(f"\n{'='*60}")
		print(f"[{i}/{len(MODULES_TO_TEST)}] {module['name']}")
		print(f"{'='*60}")

		# Read source (smaller context for speed)
		try:
			with open(module["path"], "r") as f:
				source = f.read()
			# Limit to first 1500 chars for speed
			source = source[:1500]
			print(f"   Source: {len(source)} chars")
		except Exception as e:
			print(f"   [SKIP] {e}")
			continue

		print(f"   Task: {module['task']}")
		print(f"   Generating...")

		try:
			result = await asyncio.wait_for(
				asyncio.to_thread(
					generator,
					code=source,
					requirements=module["task"]
				),
				timeout=120.0  # 2 minutes
			)

			test_code = result.test_code
			print(f"   [OK] {len(test_code)} chars")

			# Clean markdown fences
			if "```python" in test_code:
				test_code = test_code.split("```python")[1].split("```")[0]
			elif "```" in test_code:
				parts = test_code.split("```")
				if len(parts) > 1:
					test_code = parts[1]

			# Build final file
			final_code = f'''"""
Auto-generated tests for {module['name']}.py
Model: Blitzar-coder-4b via DSPy
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

{test_code.strip()}
'''

			# Save
			with open(module["output"], "w") as f:
				f.write(final_code)
			print(f"   [SAVED] {module['output']}")

			# Show preview
			print(f"\n   --- Preview ---")
			print(test_code[:500])
			print("   --- End ---")

			results.append({"name": module["name"], "success": True, "chars": len(test_code)})

		except asyncio.TimeoutError:
			print(f"   [TIMEOUT]")
			results.append({"name": module["name"], "success": False, "chars": 0})
		except Exception as e:
			print(f"   [ERROR] {e}")
			results.append({"name": module["name"], "success": False, "chars": 0})

	# Summary
	print("\n" + "=" * 60)
	print("   BLITZAR RESULTS")
	print("=" * 60)

	success = sum(1 for r in results if r["success"])
	print(f"\n   Success: {success}/{len(MODULES_TO_TEST)}")

	for r in results:
		status = "[OK]" if r["success"] else "[FAIL]"
		print(f"   {status} {r['name']}: {r['chars']} chars")

	# Quick syntax check
	if success > 0:
		print("\n   Checking syntax...")
		for module in MODULES_TO_TEST:
			if os.path.exists(module["output"]):
				try:
					with open(module["output"], "r") as f:
						code = f.read()
					compile(code, module["output"], "exec")
					print(f"   [OK] {module['output']} - Valid Python")
				except SyntaxError as e:
					print(f"   [SYNTAX] {module['output']}: {e}")

if __name__ == "__main__":
	asyncio.run(generate_tests())
