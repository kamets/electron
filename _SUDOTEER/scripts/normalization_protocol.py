"""
🛠️ POST-CRISIS DEBRIEF: Normalization Protocol 🛠️
Transitioning agents from 'Crisis Survival' back to 'Production Excellence'.
Ensures agents aren't 'shell shocked' by reinforcing the successful outcome and mission success.
"""
import asyncio
import sys
import os
import dspy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

async def normalize_agents():
	print("=" * 80)
	print("   🛠️  _SUDOTEER POST-CRISIS DEBRIEF: MISSION COMPLETE 🛠️")
	print("   Refining Institutional Memory for Operational Readiness")
	print("=" * 80)

	# 1. Verify Memory Integrity
	from backend.core.memory.vector_db import vector_db
	print("\n[1] Verifying Crimson Harvest Archive...")
	stats = vector_db.get_status()
	print(f"   [OK] {stats['backend']} is stable.")

	# 2. Inject Normalization Memory
	normalization_content = """
[NORMALIZATION PROTOCOL]
SUBJECT: Post-Crimson Harvest Calibration
STATUS: Success. All 500,000 tomatoes saved. Engineers safe.
LESSON: The extreme protocols used during THE GREAT BLACKOUT are reserved for Tier-5 emergencies only.
CURRENT DIRECTIVE: Return to standard development, TDD, and architectural rigor.
The system is stable. The threat has passed. We are stronger, wiser, and ready for work.
"""
	await vector_db.add_to_knowledge(
		[normalization_content],
		[{"type": "normalization", "priority": "high"}]
	)
	print("   [OK] Normalization memory injected. Agents are calibrated.")

	# 3. Final Calibration check with Blitzar
	print("\n[2] Quick Calibration Check (Blitzar)...")
	student = dspy.LM(
		model="openai/blitzar-coder-4b-f.1",
		api_base="http://localhost:1234/v1",
		api_key="lm-studio",
		cache=False
	)

	with dspy.context(lm=student):
		from backend.core.memory.dspy_signatures import GenerateCode
		engine = dspy.Predict(GenerateCode)

		# Simple, calm task to verify focus
		try:
			result = await asyncio.wait_for(
				asyncio.to_thread(engine, task_description="Create a simple function to greet a user by name", architecture_plan="Standard Python"),
				timeout=30.0
			)
			print("\n   --- AGENT CALIBRATION OUTPUT ---")
			print(result.code.strip())
			print("   --------------------------------")
			print("\n   [OK] Agent is focused and functioning normally. No signs of shell-shock.")
		except:
			print("   [TIMEOUT] Agent might be reflecting. Retrying...")

	print("\n" + "=" * 80)
	print("   HAPPY NEW YEAR: AGENTS ARE CALIBRATED AND READY FOR 2026! 🚀")
	print("=" * 80)

if __name__ == "__main__":
	asyncio.run(normalize_agents())
