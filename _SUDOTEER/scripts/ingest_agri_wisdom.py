"""
📚 GLOBAL AGRICULTURAL WISDOM INGESTION 📚
Teacher: Kimi K2 (Ollama)
Students: All Agents
Goal: Ingest a high-density library of agricultural science, economics, and purpose-driven growing strategies.
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
# KNOWLEDGE CATEGORIES
# ============================================

KNOWLEDGE_DOMAINS = [
    {
        "category": "Environmental Physics",
        "topics": "VPD (Vapor Pressure Deficit) optimization, DLI (Daily Light Integral), and leaf surface temperature vs. ambient air."
    },
    {
        "category": "Production Purpose: Food vs. Seeds",
        "topics": "Growing for flavor/biomass (Food) vs. growing for genetic stability/desiccation/storage (Seeds). Nutrient shifts needed for seed set."
    },
    {
        "category": "Greenhouse Economics",
        "topics": "Reducing energy costs via peak-shaving, thermal mass usage, and optimal yield-per-watt strategies."
    },
    {
        "category": "Seasonality & Crop Calendars",
        "topics": "Adjusting photoperiod and spectrum based on simulated vs. natural seasons in controlled environments."
    }
]

class AgriLibrarySignature(dspy.Signature):
    """Compiles high-density agricultural knowledge for agent institutional memory."""
    category: str = dspy.InputField(desc="The agricultural domain category")
    topics: str = dspy.InputField(desc="Specific topics to cover")

    knowledge_blobs: list[str] = dspy.OutputField(desc="A list of technical, high-value knowledge chunks (1 paragraph each)")
    strategy_summary: str = dspy.OutputField(desc="The 'Golden Rule' or best scenario for saving money and maximizing yield in this category")

async def ingest_agri_library():
    print("=" * 80)
    print("   📚  _SUDOTEER GLOBAL AGRICULTURAL WISDOM INGESTION 📚")
    print("   Updating Agent Brains with Industrial-Grade Ag-Science")
    print("=" * 80)

    # Setup Kimi K2 (The Oracle)
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(AgriLibrarySignature)

    for i, domain in enumerate(KNOWLEDGE_DOMAINS, 1):
        print(f"\n[{i}/{len(KNOWLEDGE_DOMAINS)}] Processing: {domain['category']}")
        print(f"   Topics: {domain['topics']}")

        try:
            print("   Kimi is compiling the library... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=400.0
            )

            # Ingest Chunks
            chunks = result.knowledge_blobs
            # Add the strategy summary as a chunk too
            chunks.append(f"STRATEGY SUMMARY ({domain['category']}): {result.strategy_summary}")

            metadata = [{"type": "agri_wisdom", "category": domain['category'], "source": "kimi_k2_library"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} wisdom chunks into ChromaDB.")
            print(f"   [STRATEGY] {result.strategy_summary[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   📚  INGESTION COMPLETE! Your agents are now Ag-Science Experts.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_agri_library())
