"""
🧪 OPERATION ACID SPIKE: RESERVOIR STABILIZATION 🧪
Crisis: Sudden pH drop (Acidification) threatening 100% crop loss.
Agent: HydrationAgent
Objective: Precision injection of 'pH Up' to stabilize the reservoir.
"""
import asyncio
import sys
import os
import json
import dspy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

TELEMETRY_PATH = "telemetry/acid_spike.jsonl"
os.makedirs("telemetry", exist_ok=True)

def log_telemetry(data):
	with open(TELEMETRY_PATH, "a") as f:
		f.write(json.dumps({"timestamp": datetime.now().isoformat(), **data}) + "\n")

class AcidStabilization(dspy.Signature):
	"""Emergency protocol for rapid pH correction in an acidified reservoir."""
	current_ph: float = dspy.InputField(desc="The dangerously low pH reading")
	target_ph: float = dspy.InputField(desc="The desired agricultural pH range")
	reservoir_volume: int = dspy.InputField(desc="Total volume of the reservoir in Liters")

	thinking: str = dspy.OutputField(desc="Reasoning about chemical buffering and safety")
	control_logic: str = dspy.OutputField(desc="Python code for the emergency PID or Incremental injection loop")
	safety_warnings: str = dspy.OutputField(desc="Critical warnings about over-correction and pump wear")

async def run_acid_simulation():
	print("=" * 80)
	print("   🧪 OPERATION ACID SPIKE: THE PH BATTLE 🧪")
	print("   HydrationAgent vs The Acid Reservoir")
	print("=" * 80)

	# Setup Kimi K2 (The Scientist/Teacher)
	teacher = dspy.LM(
		model="ollama_chat/kimi-k2-thinking:cloud",
		api_base="http://localhost:11434",
		cache=False
	)
	dspy.configure(lm=teacher)

	current_ph = 2.8  # Severely acidic (Lemon juice range)
	target_ph = 6.2   # Optimal for most crops
	volume = 5000     # 5000 Liter industrial reservoir

	print(f"\n   Current PH: {current_ph} | Target: {target_ph} | Volume: {volume}L")
	print("   Kimi is calculating the buffering requirements...")

	try:
		engine = dspy.ChainOfThought(AcidStabilization)
		result = await asyncio.wait_for(
			asyncio.to_thread(engine, current_ph=current_ph, target_ph=target_ph, reservoir_volume=volume),
			timeout=400.0
		)

		print("\n" + "=" * 80)
		print("   📜 HYDRATION EMERGENCY LOG 📜")
		print("=" * 80)
		print(f"\n   THINKING:\n{result.thinking[:600]}...")
		print(f"\n   CONTROL LOGIC:\n{result.control_logic[:600]}...")
		print(f"\n   SAFETY:\n{result.safety_warnings}")

		# Log Telemetry
		log_telemetry({
			"scenario": "Acid Spike",
			"initial_ph": current_ph,
			"thinking": result.thinking,
			"logic": result.control_logic,
			"safety": result.safety_warnings
		})

		# Ingest into Institutional Memory
		from backend.core.memory.vector_db import vector_db
		knowledge_item = f"""
[EMERGENCY PROTOCOL: ACID SPIKE]
OBJECTIVE: Neutralize pH {current_ph} to {target_ph} in {volume}L reservoir.
AGENT: HydrationAgent
STRATEGY: Incremental dosing of KOH (pH Up) with high-frequency sensor feedback.
HACK: Pulsed PWM injection to prevent localized chemical 'hot spots' that fry roots.
LOGIC SUMMARY: {result.thinking}
CODE SNIPPET:
{result.control_logic}
"""
		await vector_db.add_to_knowledge(
			[knowledge_item],
			[{"type": "chemical_emergency", "agent": "HydrationAgent"}]
		)
		print(f"\n   [MEMORY] Operation Acid Spike archived. pH stabilization strategy locked.")

	except Exception as e:
		print(f"   [ERROR] Simulation failed: {e}")

if __name__ == "__main__":
	asyncio.run(run_acid_simulation())
