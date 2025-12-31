"""
📈 GREENHOUSE BUSINESS OPERATIONS & OPTIMIZATION 📈
Teacher: Kimi K2 (Ollama)
Students: ArchitectAgent, OrchestratorAgent, AdministratorAgent
Goal: Ingest high-level business logic, financial optimization, and continuous uptime philosophy.
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
# BUSINESS DOMAINS
# ============================================

BUSINESS_DOMAINS = [
    {
        "category": "Operational Financials",
        "topics": "Managing energy tariffs, peak-demand shaving, nutrient supply chain optimization, and utility bill auditing."
    },
    {
        "category": "Labor & Productivity Architecture",
        "topics": "Employee output maximization, safety compliance (OSHA), and transitioning from human labor to agentic supervision."
    },
    {
        "category": "Zero-Downtime Philosophy (Kaizen)",
        "topics": "Continuous optimization principles. Why 'Restarting' is a failure of planning. Maintaining 100% production uptime."
    },
    {
        "category": "Market ROI & Scaling",
        "topics": "Yield-per-cubic-foot optimization, harvest timing based on market price fluctuations, and scaling from pilot to industrial volume."
    }
]

class BusinessLogicSignature(dspy.Signature):
    """Compiles professional business and operational logic for agent institutional memory."""
    category: str = dspy.InputField(desc="The business/operations domain")
    topics: str = dspy.InputField(desc="Specific topics to cover")

    business_blobs: list[str] = dspy.OutputField(desc="A list of technical, high-value business logic chunks (1 paragraph each)")
    optimization_mandate: str = dspy.OutputField(desc="The strict 'Optimization Plan' for this category - how to never stop and always improve")

async def ingest_business_logic():
    print("=" * 80)
    print("   📈  _SUDOTEER GREENHOUSE BUSINESS OPERATIONS INGESTION 📈")
    print("   Building the 'Economic Conscience' of the Agency")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(BusinessLogicSignature)

    for i, domain in enumerate(BUSINESS_DOMAINS, 1):
        print(f"\n[{i}/{len(BUSINESS_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is architecting the business plan... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=450.0
            )

            # Ingest Chunks
            chunks = result.business_blobs
            chunks.append(f"OPTIMIZATION MANDATE ({domain['category']}): {result.optimization_mandate}")

            metadata = [{"type": "business_logic", "category": domain['category'], "source": "kimi_k2_economics"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} business strategies into ChromaDB.")
            print(f"   [MANDATE] {result.optimization_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   📈  BUSINESS INGESTION COMPLETE! Your agents are now Industrial Economists.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_business_logic())
