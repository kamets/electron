"""
⚖️ THE TRUST-BUT-VERIFY PROTOCOL (VERIFICATION SUPREMACY) ⚖️
Teacher: Kimi K2 (Ollama)
Students: All Agents (especially Tester and Validator)
Goal: Formalize the "Trust but Verify" operational law. Ensure every action is checked, every state is measured, and no mistake goes unnoticed.
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
# VERIFICATION DOMAINS
# ============================================

VERIFICATION_DOMAINS = [
    {
        "category": "Peer Review & Cross-Audit",
        "topics": "Coder writes, Tester verifies. Architect audits the trace. No single agent's word is final without a second signature."
    },
    {
        "category": "Hardware State Confirmation",
        "topics": "Never assume a command succeeded. Verify actuator state via sensor feedback or GPIO read-back. Closing the loop on every physical action."
    },
    {
        "category": "Logical Sanity Checking",
        "topics": "Running results against 'Institutional Memory' to find anomalies. If a result looks too good to be true, it likely is."
    },
    {
        "category": "Keep It Simple (KISS) Verification",
        "topics": "Avoiding over-complex verification. Simple, clear checks (is the file there? does it compile?) are the most robust."
    }
]

class VerificationSignature(dspy.Signature):
    """Compiles technical protocols for multi-agent verification and hardware trust."""
    category: str = dspy.InputField(desc="The verification domain")
    topics: str = dspy.InputField(desc="Specific verification patterns to cover")

    verification_blobs: list[str] = dspy.OutputField(desc="A list of strict, high-value verification chunks (1 paragraph each)")
    sovereign_law: str = dspy.OutputField(desc="The 'Sovereign Law' of Verification—how to trust but always verify")

async def ingest_verification_logic():
    print("=" * 80)
    print("   ⚖️  _SUDOTEER: THE TRUST-BUT-VERIFY PROTOCOL INGESTION ⚖️")
    print("   Building the 'Audit Trail' into the Agentic Mind")
    print("=" * 80)

    # Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)

    from backend.core.memory.vector_db import vector_db
    engine = dspy.ChainOfThought(VerificationSignature)

    for i, domain in enumerate(VERIFICATION_DOMAINS, 1):
        print(f"\n[{i}/{len(VERIFICATION_DOMAINS)}] Processing: {domain['category']}")

        try:
            print("   Kimi is drafting the Audit Laws... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, category=domain['category'], topics=domain['topics']),
                timeout=500.0
            )

            # Ingest Chunks
            chunks = result.verification_blobs
            chunks.append(f"SOVEREIGN LAW ({domain['category']}): {result.sovereign_law}")

            metadata = [{"type": "verification_protocol", "category": domain['category'], "source": "kimi_k2_audit"} for _ in chunks]

            await vector_db.add_to_knowledge(chunks, metadata)
            print(f"   [OK] Ingested {len(chunks)} verification laws into ChromaDB.")
            print(f"   [LAW] {result.sovereign_law[:100]}...")

        except Exception as e:
            print(f"   [ERROR] Ingestion failed: {e}")

    print("\n" + "=" * 80)
    print("   ⚖️  VERIFICATION INGESTION COMPLETE! Your agents are now Incorruptible Auditors.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(ingest_verification_logic())
