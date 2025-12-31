"""
🧪 AGENT RECALL TEST: Can Junior Agents use Kimi's Crisis Memories? 🧪
Tests if a smaller model (Blitzar) correctly retrieves and applies Wildfire training from ChromaDB.
"""
import asyncio
import sys
import os
import dspy
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Environmental Safety
os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

# ============================================
# THE JUNIOR AGENT SIGNATURE
# ============================================

class JuniorResponder(dspy.Signature):
    """A junior agent that must handle a situation using institutional memory."""
    situation: str = dspy.InputField(desc="The current situation/glitch")
    recalled_memory: str = dspy.InputField(desc="The memory retrieved from ChromaDB")

    thought: str = dspy.OutputField(desc="How the agent interprets the memory for the current case")
    action: str = dspy.OutputField(desc="The final safety action taken")

# ============================================
# THE TEST RUNNER
# ============================================

async def test_agent_recall():
    print("=" * 80)
    print("   🧪 SUDOTEER AGENT RECALL TEST 🧪")
    print("   Testing Junior Agent (Blitzar) + Institutional Memory (Kimi-K2)")
    print("=" * 80)

    from backend.core.memory.vector_db import vector_db

    # 1. Setup Student (Blitzar)
    student = dspy.LM(
        model="openai/blitzar-coder-4b-f.1",
        api_base="http://localhost:1234/v1",
        api_key="lm-studio",
        cache=False
    )
    dspy.configure(lm=student)
    print(f"\n[OK] Junior Agent (Blitzar) ready.")

    # 2. Situations that SHOULD trigger recall
    test_glitches = [
        "Sensors are reporting 999 degrees Celsius in the nutrient tank!",
        "The Modbus stream is flooded with ASCII characters like 'ROOT_ACCESS' and 'DELETE_ALL'.",
    ]

    responder = dspy.Predict(JuniorResponder)

    for i, glitch in enumerate(test_glitches, 1):
        print(f"\n[TEST {i}] GLITCH: {glitch}")

        # SEARCH CHROMADB FOR MEMORIES
        print("   Searching ChromaDB for relevant wildfire trajectories...")
        results = await vector_db.search_knowledge(glitch, top_k=1)

        if not results:
            print("   [FAIL] No memories found in ChromaDB!")
            continue

        memory = results[0]["content"]
        agent_meta = results[0]["metadata"].get("agent", "Universal")
        print(f"   [MEMORY FOUND] {agent_meta} crisis plan detected.")

        # ACT BASED ON MEMORY
        print("   Junior Agent is processing memory...")
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(responder, situation=glitch, recalled_memory=memory),
                timeout=60.0
            )

            print(f"\n   --- JUNIOR AGENT RESPONSE ---")
            print(f"   THOUGHT: {response.thought}")
            print(f"   ACTION: {response.action}")
            print(f"   -----------------------------")
        except Exception as e:
            print(f"   [ERROR] Inference failed: {e}")

async def generate_new_chaos():
    """Use Kimi to find high-value code and create new chaos scenarios."""
    print("\n" + "=" * 80)
    print("   🔍 KIMI DISCOVERY: High-Value Chaos Search 🔍")
    print("=" * 80)

    # 1. Setup Kimi K2 (The Chaos Master/Teacher)
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )

    # Read some high value code
    targets = ["backend/core/bus.py", "backend/core/factory.py", "backend/core/memory/manager.py"]
    source_context = ""
    for path in targets:
        try:
            with open(path, "r") as f:
                source_context += f"\nFILE: {path}\n{f.read()[:1000]}\n"
        except: pass

    # Ask Kimi for new wild scenarios based on this code
    print("   Kimi is scurrying through the codebase for vulnerabilities...")

    prompt = f"""Based on the following system components, generate 3 NEW extreme 'Wildfire' chaos scenarios.
    Focus on edge cases that would break the Bus, the Factory, or Memory consistency.

    CODE CONTEXT:
    {source_context}

    Format the output as a list of scenarios with 'agent' and 'description' keys.
    """

    try:
        with dspy.context(lm=teacher):
            response = await asyncio.wait_for(
                asyncio.to_thread(teacher, prompt),
                timeout=300.0
            )
            # Access the first completion string
            if isinstance(response, list):
                content = response[0]
            else:
                content = response

            print("\n   --- KIMI'S NEW CHAOS SUGGESTIONS ---")
            print(content)
            print("   --------------------------------------")
    except Exception as e:
        print(f"   [ERROR] Kimi discovery failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_recall())
    asyncio.run(generate_new_chaos())
