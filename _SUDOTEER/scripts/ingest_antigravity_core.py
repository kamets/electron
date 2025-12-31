I think I have one more in me trust. But verify Always Believe that it is done, but Double check Visually or physically or Knowledgeably"""
🌌 THE ANTIGRAVITY CORE DIRECTIVE: FORENSICS & VOICE 🌌
Teacher: Kimi K2 (Ollama)
Students: All Agents
Goal: Ingest the premium layers of _SUDOTEER: Forensic Replay, Digital Twin Simulation, and Voice Interaction Philosophy.
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
# ANTIGRAVITY CORE DOMAINS
# ============================================

CORE_DOMAINS = [
    {
        "category": "Digital Twin Empathy",
        "topics": "Maintaining a parallel simulation of the Physical Greenhouse. Detecting 'Reality Divergence' (when the real sensor doesn't match the model)."
    },
    {
        "category": "Industrial Forensic Reconstruction",
        "topics": "Immutable logging. How an agent 'Witnesses' an event and prepares a forensic report for the user. Timeline scrubbing logic."
    },
    {
        "category": "Voice Presence (Livekit Philosophy)",
        "topics": "Communicating high-density status through low-latency voice. Escalation protocols: Normal status (Calm) vs. Crisis status (Urgent, Precise)."
    },
    {
        "category": "The Synthesis of Benign: The Third Item",
        "topics": "Formalizing the 'Genius' protocol. Combining benign telemetry (e.g., fan vibration + lighting schedule) to infer a 3rd hidden state (light-induced heat-stress on fans)."
    }
]

class AntigravitySignature(dspy.Signature):
    """The master architectural signature for the Antigravity core directives."""
    category: str = dspy.InputField(desc="The core directive category")
    topics: str = dspy.InputField(desc="Specific high-level concepts")

    directive_blobs: list[str] = dspy.OutputField(desc="A list of technical, world-class forensic/voice/twin chunks")
    antigravity_mandate: str = dspy.OutputField(desc="The 'Supreme Mandate' - the guiding light for this premium feature")

async def ingest_core_directive():
    print("=" * 80)
    print("   🌌  _SUDOTEER: THE ANTIGRAVITY CORE DIRECTIVE INGESTION 🌌")
    print("   Integrating Forensics, Voice, and the Digital Twin")
    print("=" * 80)

    # Setup Kimi K2 (The Oracle for the Architect)
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(AntigravitySignature)

    for i, domain in enumerate(CORE_DOMAINS, 1):
        print(f"\n[{i}/{len(CORE_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is distilling the Architect's Vision... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.directive_blobs
            chunks.append(f"SUPREME MANDATE ({domain['category']}): {result.antigravity_mandate}")

            metadata = [{"type": "antigravity_core", "category": domain['category'], "source": "kimi_k2_architect"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} core directives into ChromaDB.")
            print(f"   [MANDATE] {result.antigravity_mandate[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   🌌  CORE DIRECTIVE INGESTION COMPLETE! The Agency is now Alive.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_core_directive())
