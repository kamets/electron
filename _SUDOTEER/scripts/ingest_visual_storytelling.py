"""
📊 ADVANCED MATPLOTLIB & FINANCIAL STORYTELLING 📊
Teacher: Kimi K2 (Ollama)
Students: ArchitectAgent, DocumenterAgent, FinancialAgent
Goal: Master complex data visualization, signal mixing, and financial reporting using Matplotlib.
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
# VISUALIZATION DOMAINS
# ============================================

VISUAL_DOMAINS = [
    {
        "category": "Multi-Signal Correlative Plotting",
        "topics": "Overlaying disparate signals (Temperature vs. Humidity vs. Nutrient EC). Dual-axis plots, normalized scales, and identifying biological lag in charts."
    },
    {
        "category": "Financial Time-Series & ROI Analytics",
        "topics": "Visualizing Quarterly energy bills vs. Crop Yield. Trend analysis (Year-over-Year), Moving Averages, and Cost-per-Tomato visualizations."
    },
    {
        "category": "Storytelling & Architectural Presentation",
        "topics": "Using Matplotlib for high-level idea presentation. Annotations, highlight zones (e.g., 'The Harvest Window'), and industrial-grade aesthetic skins."
    },
    {
        "category": "Historical Comparison (24h/1w/1q/1y)",
        "topics": "Templates for rapid temporal comparison. Subplots for multi-scale review and 'Difference Mapping' between periods."
    }
]

class VisualStorytellingSignature(dspy.Signature):
    """Compiles advanced Matplotlib and financial data visualization knowledge."""
    category: str = dspy.InputField(desc="The visualization/reporting domain")
    topics: str = dspy.InputField(desc="Specific plotting concepts to cover")

    visual_blobs: list[str] = dspy.OutputField(desc="A list of technical, high-value Matplotlib/Data chunks (1 paragraph each)")
    charting_mandate: str = dspy.OutputField(desc="The 'Golden Rule' of Visualization - how to make data tell a compelling story")

async def ingest_visual_storytelling():
    print("=" * 80)
    print("   📊  _SUDOTEER ADVANCED MATPLOTLIB & FINANCIAL STORYTELLING 📊")
    print("   Training Agents in the Art of the Data Narrative")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(VisualStorytellingSignature)

    for i, domain in enumerate(VISUAL_DOMAINS, 1):
        print(f"\n[{i}/{len(VISUAL_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is rendering the charts... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.visual_blobs
            chunks.append(f"CHARTING MANDATE ({domain['category']}): {result.charting_mandate}")

            metadata = [{"type": "visual_storytelling", "category": domain['category'], "source": "kimi_k2_viz"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} visualization strategies into ChromaDB.")
            print(f"   [MANDATE] {result.charting_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   📊  STORYTELLING INGESTION COMPLETE! Your agents are now Visual Data Scientists.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_visual_storytelling())
