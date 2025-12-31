"""
🧜‍♂️ MERMAID ORCHESTRATION & NOVEL SYNTHESIS (BENIGN TO GENIUS) 🧜‍♂️
Teacher: Kimi K2 (Ollama)
Students: ArchitectAgent, OrchestratorAgent, DocumenterAgent
Goal: Master Mermaid for workflow visualization and train the 'Synthesis Engine' to combine benign items into novel, useful tools.
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
# SYNTHESIS & FLOW DOMAINS
# ============================================

SYNTHESIS_DOMAINS = [
    {
        "category": "Mermaid Flowcharting & Sequence Logic",
        "topics": "Visualizing complex A2A sequence diagrams. 'Who goes after who'. Mapping the lifecycle of a task from Architect to Validator using Mermaid syntax."
    },
    {
        "category": "Inter-Agent Dependency Mapping",
        "topics": "Using graph logic to prevent deadlocks. Modeling the Greenhouse OS as a live state machine where humidity, CO2, and nutrient flow are nodes in a Mermaid graph."
    },
    {
        "category": "Novel Synthesis: Benign Item Convergence",
        "topics": "The 'Inference from Benign' method. How to take two unrelated data signals (e.g., Fan RPM noise + pH Drift) and synthesize a 3rd insight (e.g., Predictive Pump Cavitation failure)."
    },
    {
        "category": "Genius-Level Workflows",
        "topics": "Designing 'Self-Optimizing Loops' where agents invent new sub-routines by observing side-effects of their primary tasks."
    }
]

class SynthesisSignature(dspy.Signature):
    """Compiles advanced logic for Mermaid visualization and novel multi-agent synthesis."""
    category: str = dspy.InputField(desc="The visualization or synthesis domain")
    topics: str = dspy.InputField(desc="Specific logical concepts to cover")

    synthesis_blobs: list[str] = dspy.OutputField(desc="A list of technical, high-value logic/visualization chunks (1 paragraph each)")
    genius_mandate: str = dspy.OutputField(desc="The 'Crown Mandate' - how to achieve 'Inference from Benign' for novel utility")

async def ingest_synthesis_logic():
    print("=" * 80)
    print("   🧜‍♂️  _SUDOTEER MERMAID ORCHESTRATION & NOVEL SYNTHESIS 🧜‍♂️")
    print("   Teaching Agents to Visualize the Invisible and Synthesize the New")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(SynthesisSignature)

    for i, domain in enumerate(SYNTHESIS_DOMAINS, 1):
        print(f"\n[{i}/{len(SYNTHESIS_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is manifesting the synthesis... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.synthesis_blobs
            chunks.append(f"GENIUS MANDATE ({domain['category']}): {result.genius_mandate}")

            metadata = [{"type": "novel_synthesis", "category": domain['category'], "source": "kimi_k2_synthesis"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} synthesis protocols into ChromaDB.")
            print(f"   [MANDATE] {result.genius_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   🧜‍♂️  SYNTHESIS INGESTION COMPLETE! Your agents are now Creative Orchestrators.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_synthesis_logic())
