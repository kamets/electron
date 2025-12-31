"""
Quick test: Run Coder agent on ONE module with longer timeout.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def quick_test():
	print("=" * 60)
	print("   Quick Coder Agent Test (5 min timeout)")
	print("=" * 60)

	# Initialize LLM
	print("\n[1] Connecting to LLM...")
	try:
		from backend.core.dspy_config import initialize_dspy, dspy_config
		if initialize_dspy():
			print(f"   [OK] {dspy_config.provider}")
		else:
			print("   [FAIL] No LLM")
			return
	except Exception as e:
		print(f"   [FAIL] {e}")
		return

	# Load Coder agent
	print("\n[2] Loading Coder agent...")
	from backend.agents.coder.agent import CoderAgent
	coder = CoderAgent(agent_id="coder_quick")
	print(f"   [OK] {coder.agent_id} ready")

	# Simple task
	task = "Create a Python function to calculate moving average of a list of numbers"

	print(f"\n[3] Task: {task}")
	print("   Generating... (up to 5 minutes)")

	try:
		result = await asyncio.wait_for(
			coder.forward(task),
			timeout=300.0  # 5 minutes
		)

		code = result.get("code", "")
		status = result.get("status", "unknown")

		print(f"\n[4] Result:")
		print(f"   Status: {status}")
		print(f"   Code length: {len(code)} chars")
		print("\n   --- Generated Code ---")
		print(code[:1000] if code else "No code generated")
		print("   --- End ---")

	except asyncio.TimeoutError:
		print("   [TIMEOUT] 5 minutes exceeded")
	except Exception as e:
		print(f"   [ERROR] {e}")

	print("\n" + "=" * 60)

if __name__ == "__main__":
	asyncio.run(quick_test())
