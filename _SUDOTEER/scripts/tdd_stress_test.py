"""
TDD Stress Test: Run Coder + Tester agents to generate tests.
Uses existing agents to demonstrate the agency workflow.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Modules that need test coverage
MODULES_TO_TEST = [
	{
		"name": "vector_db",
		"path": "backend/core/memory/vector_db.py",
		"task": "Create pytest tests for the VectorDB class covering add_to_knowledge, search_knowledge, store_memory, and search_episodes methods"
	},
	{
		"name": "factory",
		"path": "backend/core/factory.py",
		"task": "Create pytest tests for AgentFactory covering spawn_agent, kill_agent, and get_agent methods"
	},
	{
		"name": "bus",
		"path": "backend/core/bus.py",
		"task": "Create pytest tests for A2ABus covering send_request, broadcast, and subscribe methods"
	}
]

async def stress_test():
	print("=" * 60)
	print("   _SUDOTEER TDD Stress Test")
	print("   Coder + Tester Agent Workflow")
	print("=" * 60)

	# Try to initialize LLM
	print("\n[1] Checking LLM backend...")
	try:
		from backend.core.dspy_config import initialize_dspy, dspy_config
		if initialize_dspy():
			print(f"   [OK] Connected to: {dspy_config.provider}")
		else:
			print("   [WARN] No LLM - using mock mode")
	except Exception as e:
		print(f"   [WARN] LLM init failed: {e}")

	# Import agents
	print("\n[2] Loading agents...")
	try:
		from backend.agents.coder.agent import CoderAgent
		from backend.agents.tester.agent import TesterAgent

		coder = CoderAgent(agent_id="coder_stress")
		tester = TesterAgent(agent_id="tester_stress")
		print(f"   [OK] {coder.agent_id} ready")
		print(f"   [OK] {tester.agent_id} ready")
	except Exception as e:
		print(f"   [ERROR] Agent load failed: {e}")
		return

	# Process each module
	for i, module in enumerate(MODULES_TO_TEST, 1):
		print(f"\n{'='*60}")
		print(f"[{i}/{len(MODULES_TO_TEST)}] Module: {module['name']}")
		print(f"{'='*60}")

		# Read the source file
		try:
			with open(module["path"], "r") as f:
				source_code = f.read()
			print(f"   Source: {len(source_code)} chars")
		except Exception as e:
			print(f"   [SKIP] Cannot read: {e}")
			continue

		# Step 1: Coder generates test code
		print(f"\n   [CODER] Generating tests...")
		try:
			coder_result = await asyncio.wait_for(
				coder.forward(
					task=module["task"],
					architecture_plan=f"Source module: {module['path']}"
				),
				timeout=60.0
			)

			test_code = coder_result.get("code", "")
			status = coder_result.get("status", "unknown")
			print(f"   Status: {status}")
			print(f"   Generated: {len(test_code)} chars")

			if test_code:
				# Show preview
				preview = test_code[:300].replace('\n', '\n   ')
				print(f"   Preview:\n   {preview}...")

		except asyncio.TimeoutError:
			print("   [TIMEOUT] Coder took too long")
			continue
		except Exception as e:
			print(f"   [ERROR] Coder failed: {e}")
			continue

		# Step 2: Tester validates the code
		print(f"\n   [TESTER] Validating...")
		try:
			tester_result = await asyncio.wait_for(
				tester.forward(
					code=test_code,
					requirements=f"Tests for {module['name']}"
				),
				timeout=60.0
			)

			is_valid = tester_result.get("is_valid", False)
			issues = tester_result.get("issues", [])
			print(f"   Valid: {is_valid}")
			if issues:
				print(f"   Issues: {issues[:3]}")

		except asyncio.TimeoutError:
			print("   [TIMEOUT] Tester took too long")
		except Exception as e:
			print(f"   [ERROR] Tester failed: {e}")

	print(f"\n{'='*60}")
	print("   Stress Test Complete!")
	print(f"{'='*60}")

if __name__ == "__main__":
	asyncio.run(stress_test())
