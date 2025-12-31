"""
📋 GREENHOUSE BOM & OPTIMIZATION REPORT (800 PLANTS) 📋
Teacher: Kimi K2 (Ollama)
Goal: Generate a professional industrial Bill of Materials (BOM) for a medium-sized greenhouse (800 plants),
including sensor counts, drivers, and estimated pricing.
"""
import asyncio
import sys
import os
import dspy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

class GreenhouseBOMSignature(dspy.Signature):
    """Generates an industrial-grade BOM and Driver list for an 800-plant facility."""
    facility_size: str = dspy.InputField(desc="Number of plants and general facility scale")
    focus_area: str = dspy.InputField(desc="The core focus: Engine and Sensors")

    sensor_bom: list[str] = dspy.OutputField(desc="List of sensors, counts, and reasons (e.g. 10x Graphene VPD sensors)")
    drivers_hardware: list[str] = dspy.OutputField(desc="PLCs, Gateways, and industrial communication drivers needed")
    pricing_estimates: str = dspy.OutputField(desc="Estimated cost breakdown for the hardware")
    genius_tip: str = dspy.OutputField(desc="Optimization tip for saving money on this specific BOM")

async def generate_greenhouse_bom():
    print("=" * 80)
    print("   📋 _SUDOTEER: INDUSTRIAL BOM GENERATOR 📋")
    print("   Facility Scale: 800 Plants | Target: Engine & Sensors")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    try:
        engine = dspy.ChainOfThought(GreenhouseBOMSignature)
        print("\n   Kimi is architecting the hardware stack... (Deep Thinking Mode)")
        result = await asyncio.wait_for(
            asyncio.to_thread(engine, facility_size="800 Plants (Medium Greenhouse)", focus_area="Engine & Sensors"),
            timeout=500.0
        )

        print("\n" + "=" * 80)
        print("   🛠️ SENSOR BILL OF MATERIALS 🛠️")
        print("=" * 80)
        for item in result.sensor_bom:
            print(f"   • {item}")

        print("\n" + "=" * 80)
        print("   ⚙️ DRIVERS & HARDWARE (THE ENGINE) ⚙️")
        print("=" * 80)
        for item in result.drivers_hardware:
            print(f"   • {item}")

        print("\n" + "=" * 80)
        print("   💰 ESTIMATED PRICING (USD) 💰")
        print("=" * 80)
        print(result.pricing_estimates)

        print(f"\n   💡 GENIUS TIP: {result.genius_tip}")

        # Save for reference
        with open("docs/GREENHOUSE_BOM_800_PLANTS.md", "w", encoding="utf-8") as f:
            f.write(f"# Greenhouse BOM (800 Plants)\n\n## Sensors\n" + "\n".join(result.sensor_bom))
            f.write(f"\n\n## Drivers & Engine\n" + "\n".join(result.drivers_hardware))
            f.write(f"\n\n## Pricing\n{result.pricing_estimates}")
            f.write(f"\n\n## Genius Tip\n{result.genius_tip}")

    except Exception as e:
        print(f"   [ERROR] BOM generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(generate_greenhouse_bom())
