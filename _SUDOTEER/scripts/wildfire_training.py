"""
🌪️ THE WILD TRAINING HARNESS: Kimi K2 Edge-Case Scenarios 🌪️
Teaching agents to handle the extreme, the glitched, and the impossible.
"""
import asyncio
import sys
import os
import dspy
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Environmental Safety
os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

# ============================================
# TRAJECTORIES OF CHAOS: Wild Training Scenarios
# ============================================

WILD_SCENARIOS = [
    {
        "description": "CYBER-PHYSICAL ATTACK: A malicious actor is injecting fake sensor readings. The humidity sensor reports 150% (physically impossible), while the temperature sensor reports -273C (Absolute Zero). Detect and failover to 'Manual Safety Mode'.",
        "agent": "SafetyWatchdog",
        "context": "SensorHub connected via Modbus. PLC is currently in Auto mode."
    },
    {
        "description": "HARDWARE CASCADE FAILURE: The main exhaust vent is stuck 100% open, the heater circuit has a ground fault and is offline, and the humidity is dropping globally. The plant ('Red Martian Fern') requires 80% humidity and 25C. Create a survival plan.",
        "agent": "ClimateAgent",
        "context": "Hardware: Vent#1 (STUCK), Heater#1 (OFFLINE), Misters (ACTIVE). Outside Temp: -10C."
    },
    {
        "description": "MODBUS PROTOCOL GLITCH: The PLC is sending sensor data wrapped in malformed byte sequences that look like agent commands. Distinguish between 'Noise' and 'Actual Data' at the byte level.",
        "agent": "HardwareBridge",
        "context": "Stream: b'\\xff\\xff\\x01\\x03\\x00\\x00ADJUST_TEMP_TO_666\\x00\\x00\\xaa'"
    },
    {
        "description": "AGENT CONFLICT: The NutrientAgent wants to flush the soil (Excess Nitrogen), but the CropAgent insists on a high-PK bloom stimulant for harvest. Resolve the conflicting goals without killing the crop.",
        "agent": "Orchestrator",
        "context": "Plant Stage: Day 58 (Pre-Harvest). Nitrogen levels: 400ppm (High)."
    }
]

# ============================================
# DSPy SIGNATURES FOR CHAOS
# ============================================

class ResolveChaos(dspy.Signature):
    """Analyze a chaotic or glitched system state and provide resilient solutions."""
    scenario: str = dspy.InputField(desc="The chaotic environment or glitch description")
    context: str = dspy.InputField(desc="Hardware and protocol context")

    thinking: str = dspy.OutputField(desc="Deep reasoning about the glitch/attack")
    action_plan: str = dspy.OutputField(desc="Step-by-step resilient recovery plan")
    safety_grade: str = dspy.OutputField(desc="Risk assessment: GREEN, YELLOW, RED, BLACK")

# ============================================
# THE OBSERVER: Memory Ingestion
# ============================================

async def log_to_institutional_memory(result: Any, scenario: Dict[str, str]):
    """Inject the chaotic trajectory into ChromaDB so others can learn from it."""
    from backend.core.memory.vector_db import vector_db

    memory_content = f"""
[WILDFIRE TRAINING]
SCENARIO: {scenario['description']}
REASONING: {result.thinking}
RECOVERY: {result.action_plan}
SAFETY: {result.safety_grade}
TIMESTAMP: {datetime.now().isoformat()}
"""
    metadata = {
        "type": "chaotic_trajectory",
        "agent": scenario['agent'],
        "safety_level": result.safety_grade,
        "source": "kimi-k2-wildfire"
    }

    await vector_db.add_to_knowledge([memory_content], [metadata])
    print(f"   [MEMORY] Chaos trajectory ingested for {scenario['agent']}")

# ============================================
# EXECUTION
# ============================================

async def run_wildfire_training():
    print("=" * 80)
    print("   🌪️  SUDOTEER WILDFIRE TRAINING: KIMI K2 ON THE EDGE 🌪️")
    print("   Testing the Impossible | Training for the Worst")
    print("=" * 80)

    # 1. Setup Kimi K2 (The Chaos Master)
    # Using the cloud thinking model as the teacher
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)
    print(f"\n[OK] Kimi K2 connected. Ready to simulate chaos.")

    # 2. Build the Chaos Engine
    resolver = dspy.ChainOfThought(ResolveChaos)

    # 3. Iterate through Scenarios
    for i, scenario in enumerate(WILD_SCENARIOS, 1):
        print(f"\n[{i}/{len(WILD_SCENARIOS)}] TARGET: {scenario['agent']}")
        print(f"   SCENARIO: {scenario['description'][:80]}...")

        try:
            # Let Kimi K2 "Think" through the scenario
            print("   Kimi is thinking... (Wildfire Protocol)")

            # Since Kimi K2 Thinking can take a while, we give it a healthy timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    resolver,
                    scenario=scenario['description'],
                    context=scenario['context']
                ),
                timeout=300.0 # 5 minutes for deep thinking
            )

            print(f"   [DONE] Safety Grade: {result.safety_grade}")
            print(f"   [PLAN] {result.action_plan[:100]}...")

            # 4. Log to memory for all agents to see
            await log_to_institutional_memory(result, scenario)

        except asyncio.TimeoutError:
            print(f"   [TIMEOUT] Chaos exceeded Kimi's thinking capacity.")
        except Exception as e:
            print(f"   [ERROR] Crisis management failed: {str(e)[:100]}")

    print("\n" + "=" * 80)
    print("   🌪️  WILDFIRE COMPLETE! Institutional Memory Seeded with Crisis Knowledge.")
    print("   Happy New Year - The agents are prepared for the wild.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_wildfire_training())
