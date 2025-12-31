"""
🤖 AGENCY PROCEDURAL PROTOCOLS INGESTION 🤖
Teacher: Kimi K2 (Ollama)
Students: All Agents
Goal: Ingest the core operational 'Laws of the Agency' - Sandbox isolation, Atomic Decomposition, and Guardrails.
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
# PROCEDURAL DOMAINS (The Laws)
# ============================================

PROCEDURAL_DOMAINS = [
    {
        "category": "Workstation Isolation & Sandbox Protocol",
        "topics": "Each agent operates in a dedicated Workbench isolation layer. Code execution MUST only occur within the verified sandbox. No cross-pollution of file systems."
    },
    {
        "category": "Atomic Problem Decomposition",
        "topics": "Breaking complex industrial problems into 'Atomic Tasks'. One task = one specific outcome. Identifying dependencies between atomic units."
    },
    {
        "category": "Sub-Agent Spawning & Orchestration",
        "topics": "How an agent spawns a specialist sub-agent to handle an atomic task. The recursive nature of the Agency (Architect -> Coder -> Tester -> Validator)."
    },
    {
        "category": "Constitutional Guardrails",
        "topics": "Never break the Base -> Platform -> Workbench layer hierarchy. 100% Tabs. JSDoc for all interfaces. No unauthorized network calls."
    }
]

class ProceduralProtocolSignature(dspy.Signature):
    """Compiles technical agency protocols and operational laws for agent brains."""
    category: str = dspy.InputField(desc="The agency procedural/operational domain")
    topics: str = dspy.InputField(desc="Specific protocols to cover")

    protocol_blobs: list[str] = dspy.OutputField(desc="A list of strict, high-value procedural chunks (1 paragraph each)")
    operational_mandate: str = dspy.OutputField(desc="The 'Golden Law' - the non-negotiable rule for this category")

async def ingest_agent_protocols():
    print("=" * 80)
    print("   🤖  _SUDOTEER AGENCY PROCEDURAL PROTOCOLS INGESTION 🤖")
    print("   Programming the 'Operational DNA' of the Agency")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(ProceduralProtocolSignature)

    for i, domain in enumerate(PROCEDURAL_DOMAINS, 1):
        print(f"\n[{i}/{len(PROCEDURAL_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is architecting the Laws... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.protocol_blobs
            chunks.append(f"OPERATIONAL MANDATE ({domain['category']}): {result.operational_mandate}")

            metadata = [{"type": "agency_protocol", "category": domain['category'], "source": "kimi_k2_protocols"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} procedural protocols into ChromaDB.")
            print(f"   [MANDATE] {result.operational_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   🤖  PROTOCOL INGESTION COMPLETE! Your agents are now Architecturally Compliant.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_agent_protocols())
