"""
🤝 AGENT COLLABORATION & PEER LEARNING INGESTION 🤝
Teacher: Kimi K2 (Ollama)
Students: All Agents
Goal: Ingest protocols for Agent-to-Agent (A2A) communication, collaborative inference, and peer-to-peer teaching.
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
# COLLABORATION DOMAINS
# ============================================

COLLAB_DOMAINS = [
    {
        "category": "Agent-to-Agent (A2A) Communication",
        "topics": "Unified Message Bus (Bus.py), JSON payload standards, and non-blocking asynchronous gossip protocols."
    },
    {
        "category": "Collaborative Inference",
        "topics": "Cross-domain reasoning (e.g., ClimateAgent identifying a humidity spike to help NutrientAgent adjust transpiration-based feeding)."
    },
    {
        "category": "Peer-to-Peer Teaching",
        "topics": "Sharing high-fidelity 'Trajectories' and 'Rationales' through ChromaDB so agents learn from each other's failures and successes."
    },
    {
        "category": "Collective Intelligence Sync",
        "topics": "Periodic synchronization of individual agent 'Fact Bases' into a unified Greenhouse Operating System strategy."
    }
]

class CollaborativeSignature(dspy.Signature):
    """Compiles technical protocols for agent collaboration and learning."""
    category: str = dspy.InputField(desc="The collaboration/learning domain")
    topics: str = dspy.InputField(desc="Specific collaboration patterns to cover")

    collab_blobs: list[str] = dspy.OutputField(desc="A list of strict, high-value collaborative chunks (1 paragraph each)")
    social_mandate: str = dspy.OutputField(desc="The 'Social Contract' - how agents MUST interact and share knowledge")

async def ingest_collab_learning():
    print("=" * 80)
    print("   🤝  _SUDOTEER AGENT COLLABORATION & LEARNING INGESTION 🤝")
    print("   Enabling the 'Social Mind' of the Agency")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(CollaborativeSignature)

    for i, domain in enumerate(COLLAB_DOMAINS, 1):
        print(f"\n[{i}/{len(COLLAB_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is architecting the Social Mind... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.collab_blobs
            chunks.append(f"SOCIAL MANDATE ({domain['category']}): {result.social_mandate}")

            metadata = [{"type": "agent_collaboration", "category": domain['category'], "source": "kimi_k2_collab"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} collaboration protocols into ChromaDB.")
            print(f"   [MANDATE] {result.social_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   🤝  COLLABORATION INGESTION COMPLETE! Your agents are now a Unified Team.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_collab_learning())
