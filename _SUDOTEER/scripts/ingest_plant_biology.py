"""
🌱 PLANT PHYSIOLOGY & BIOLOGICAL SURVIVAL INGESTION 🌱
Teacher: Kimi K2 (Ollama)
Students: All Agents (especially Nutrient, Climate, and Crop agents)
Goal: Master the deep biology of plant stressors, nutrition, and physiological responses.
"""
import asyncio
import sys
import os
import dspy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

# ============================================
# BIOLOGICAL DOMAINS
# ============================================

BIOLOGY_DOMAINS = [
    {
        "category": "Plant Nutrition & Nutrient Uptake",
        "topics": "Macronutrients (NPK), Micronutrients (Fe, Ca, Mg), and pH-dependent nutrient availability in the rhizosphere."
    },
    {
        "category": "Physiological Stressors: Heat, Cold & Wilting",
        "topics": "Turgor pressure mechanics, thermal shock response, frost protection, and the wilting point (permanent vs transient)."
    },
    {
        "category": "Atmospheric Chemistry: CO2 vs. CO",
        "topics": "CO2 enrichment for photosynthetic acceleration vs. CO (Carbon Monoxide) toxicity and detection protocols."
    },
    {
        "category": "Photomorphogenesis & UV Radiation",
        "topics": "UV-A and UV-B impacts on plant secondary metabolites, leaf cuticular thickening, and ultraviolet stress response."
    }
]

class PlantBiologySignature(dspy.Signature):
    """Compiles technical plant biology and physiology knowledge for agent brains."""
    category: str = dspy.InputField(desc="The biological/physiological domain")
    topics: str = dspy.InputField(desc="Specific topics to cover")

    biological_blobs: list[str] = dspy.OutputField(desc="A list of technical, high-value biology chunks (1 paragraph each)")
    survival_mandate: str = dspy.OutputField(desc="The 'Biological Guardrail' - how the agent must protect the plant in this category")

async def ingest_plant_biology():
    print("=" * 80)
    print("   🌱  _SUDOTEER PLANT PHYSIOLOGY & BIOLOGY INGESTION 🌱")
    print("   Installing the 'Biological Heart' of the Agency")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(PlantBiologySignature)

    for i, domain in enumerate(BIOLOGY_DOMAINS, 1):
        print(f"\n[{i}/{len(BIOLOGY_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is dissecting plant biology... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.biological_blobs
            chunks.append(f"SURVIVAL MANDATE ({domain['category']}): {result.survival_mandate}")

            metadata = [{"type": "plant_biology", "category": domain['category'], "source": "kimi_k2_biology"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} biological principles into ChromaDB.")
            print(f"   [MANDATE] {result.survival_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   🌱  BIOLOGY INGESTION COMPLETE! Your agents are now Plant Physiologists.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_plant_biology())
