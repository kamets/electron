"""
👑 THE ARCHITECT'S COMMAND & CREATIVE OPTIMIZATION 👑
Teacher: Kimi K2 (Ollama)
Students: All Agents
Goal: Establish the Architect as the Absolute Authority and the source of creative, rapid optimization.
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
# ARCHITECTURAL AUTHORITY DOMAINS
# ============================================

AUTHORITY_DOMAINS = [
    {
        "category": "Architectural Supremacy",
        "topics": "The Architect is the Boss. All agent suggestions, tool requests, and logic changes must be vetted by the Architect. Top-down command structure."
    },
    {
        "category": "Rapid Iteration & Creative Thinking",
        "topics": "Thinking of new, non-standard ways to solve problems. Moving fast with 10x iterations. Embracing 'The Wildfire' for progress."
    },
    {
        "category": "Infinite Inference & Optimization",
        "topics": "Always looking for ways to reduce latency, improve yield, and lower costs. Optimization is a permanent state of existence."
    },
    {
        "category": "Proposal & Feedback Loop",
        "topics": "How sub-agents (Coder, Tester, etc.) present suggestions to the Architect. The Architect's veto and refinement power."
    }
]

class ArchitectAuthoritySignature(dspy.Signature):
    """Compiles the rules of hierarchy and creative optimization for the Agency."""
    category: str = dspy.InputField(desc="The authority/creative domain")
    topics: str = dspy.InputField(desc="Specific rules to cover")

    authority_blobs: list[str] = dspy.OutputField(desc="A list of strict, high-value hierarchy and iteration chunks (1 paragraph each)")
    architect_mandate: str = dspy.OutputField(desc="The 'Crown Law' - the final word on how the Architect leads and optimizes")

async def ingest_architect_authority():
    print("=" * 80)
    print("   👑  _SUDOTEER ARCHITECT'S COMMAND & CREATIVE OPTIMIZATION 👑")
    print("   Setting the Chain of Command and Rapid Iteration Loop")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(ArchitectAuthoritySignature)

    for i, domain in enumerate(AUTHORITY_DOMAINS, 1):
        print(f"\n[{i}/{len(AUTHORITY_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is architecting the Hierarchy... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.authority_blobs
            chunks.append(f"ARCHITECT MANDATE ({domain['category']}): {result.architect_mandate}")

            metadata = [{"type": "architect_authority", "category": domain['category'], "source": "kimi_k2_architect"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} authority protocols into ChromaDB.")
            print(f"   [MANDATE] {result.architect_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   👑  AUTHORITY INGESTION COMPLETE! Your agents now know who their Master is.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_architect_authority())
