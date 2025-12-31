"""
🔍 VARIATION DISCOVERY ENGINE: INFERENCE FROM BENIGN 🔍
Teacher: Kimi K2 (Ollama)
Goal: Analyze historical sensor data to find "The Third Item"—hidden correlations and
novel variations that are "staring us in the face."
"""
import asyncio
import sys
import os
import json
import dspy
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

# ============================================
# MOCK HISTORICAL DATASET (High Fidelity)
# ============================================

def generate_historical_dataset(days=7):
    """Generates a complex dataset with hidden 'benign' correlations."""
    data = []
    base_time = datetime.now() - timedelta(days=days)

    for i in range(days * 24): # Hourly for 7 days
        ts = base_time + timedelta(hours=i)

        # Benign signals
        temp = 22 + 5 * np.sin(i * 2 * np.pi / 24) + np.random.normal(0, 0.5)
        humidity = 60 - 10 * np.sin(i * 2 * np.pi / 24) + np.random.normal(0, 2)
        light_intensity = max(0, 1000 * np.sin(i * 2 * np.pi / 24))

        # HIDDEN BENIGN VARIATION:
        # A tiny micro-vibration in the Pump (EC stability) linked to Fan Speed (Temp control)
        # That actually predicts a filtration clog.
        fan_speed = 50 + 40 * (temp > 25)
        ec_stability = 0.98 - (0.001 * fan_speed if i > 100 else 0) + np.random.normal(0, 0.01)

        data.append({
            "timestamp": ts.isoformat(),
            "temp": round(temp, 2),
            "humidity": round(humidity, 2),
            "light": round(light_intensity, 2),
            "fan_speed": int(fan_speed),
            "ec_stability": round(ec_stability, 3)
        })
    return data

# ============================================
# DSPy SIGNATURE FOR DISCOVERY
# ============================================

class DiscoverVariations(dspy.Signature):
    """Analyze historical greenhouse data to find hidden 'Genius' variations."""
    historical_data: str = dspy.InputField(desc="The JSON dataset of historical sensor readings")
    context: str = dspy.InputField(desc="Focus: Inference from Benign - find the 'Third Item'")

    thinking: str = dspy.OutputField(desc="Deep reasoning over the data patterns")
    discovery: str = dspy.OutputField(desc="The specific 'hidden variation' found (The Third Item)")
    operational_impact: str = dspy.OutputField(desc="How this discovery saves money or improves yield")
    implementation_plan: str = dspy.OutputField(desc="How to program the agents to monitor this new variation")

async def run_variation_discovery():
    print("=" * 80)
    print("   🔍 _SUDOTEER: VARIATION DISCOVERY ENGINE 🔍")
    print("   Searching for the 'Third Item' in Historical Data")
    print("=" * 80)

    # 1. Generate/Load Data
    print("[1] Compiling 7-day High-Fidelity Historical Dataset...")
    dataset = generate_historical_dataset()
    data_str = json.dumps(dataset[:50], indent=2) # Send a representative sample

    # 2. Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    print("\n[2] Kimi K2 is performing 'Inference from Benign'...")

    try:
        engine = dspy.ChainOfThought(DiscoverVariations)
        result = await asyncio.wait_for(
            asyncio.to_thread(
                engine,
                historical_data=data_str,
                context="Look for the 'Golden Variation'—something staring us in the face that links unrelated signals."
            ),
            timeout=500.0
        )

        print("\n" + "=" * 80)
        print("   📜 THE DISCOVERY ARCHIVE 📜")
        print("=" * 80)
        print(f"\n   THE THIRD ITEM:\n   {result.discovery}")
        print(f"\n   REASONING:\n{result.thinking[:600]}...")
        print(f"\n   PLAN:\n{result.implementation_plan}")

        # 3. Ingest into Institutional Memory
        from backend.core.memory.vector_db import vector_db
        content = f"""
[DATA DISCOVERY: THE THIRD ITEM]
DISCOVERY: {result.discovery}
THINKING: {result.thinking}
PLAN: {result.implementation_plan}
DATA SOURCE: Historical 7-day Analysis
DATE: {datetime.now().isoformat()}
"""
        await vector_db.add_to_knowledge(
            [content],
            [{"type": "data_inference", "topic": "variation_discovery"}]
        )
        print(f"\n   [MEMORY] Discovery ingested. The agents 'know' the secret variation now.")

    except Exception as e:
        print(f"   [ERROR] Discovery failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_variation_discovery())
