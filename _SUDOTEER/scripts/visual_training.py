"""
🎨 VISUAL INTELLIGENCE TRAINING: NumPy & Beautiful Graphing 🎨
Teacher: Kimi K2 (Ollama)
Students: ArchitectAgent, DocumenterAgent
Goal: Master data manipulation with NumPy and aesthetic visualization.

Saves ALL telemetry to telemetry/visual_training.jsonl for review.
"""
import asyncio
import sys
import os
import json
import dspy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

TELEMETRY_PATH = "telemetry/visual_training.jsonl"
os.makedirs("telemetry", exist_ok=True)

def log_telemetry(data):
    """Write data to the telemetry log."""
    with open(TELEMETRY_PATH, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(),
            **data
        }) + "\n")

# ============================================
# TRAJECTORIES: Data Viz & NumPy
# ============================================

VISUAL_TOPICS = [
    {
        "topic": "High-Density Sensor Data Processing with NumPy",
        "focus": "Vectorized operations, rolling averages, and noise reduction for agricultural telemetry."
    },
    {
        "topic": "Aesthetic Industrial Dashboards",
        "focus": "Using Matplotlib/Plotly with sleek, dark-themed palettes matching the _SUDOTEER aesthetic."
    },
    {
        "topic": "Structural Architecture Diagrams",
        "focus": "Creating dependency graphs and system state visualizations using NetworkX and Graphviz."
    }
]

class VisualMastery(dspy.Signature):
    """Teacher instruction on visualization and data manipulation."""
    topic: str = dspy.InputField(desc="The topic to teach")
    focus: str = dspy.InputField(desc="Specific areas of focus")

    thinking: str = dspy.OutputField(desc="Deep pedagogical reasoning")
    lesson_plan: str = dspy.OutputField(desc="Step-by-step technical lesson")
    code_examples: str = dspy.OutputField(desc="Practical Python code examples using NumPy/Matplotlib/Plotly")
    architectural_impact: str = dspy.OutputField(desc="How this improves the _SUDOTEER dashboard architecture")

async def run_visual_training():
    print("=" * 80)
    print("   🎨 SUDOTEER VISUAL INTELLIGENCE TRAINING 🎨")
    print("   Teacher: Kimi K2 | Learning the Art of Data")
    print("=" * 80)

    # 1. Setup Kimi K2
    teacher = dspy.LM(
        model="ollama_chat/kimi-k2-thinking:cloud",
        api_base="http://localhost:11434",
        cache=False
    )
    dspy.configure(lm=teacher)
    print(f"\n[OK] Chaos Master ready to teach aesthetics.")

    engine = dspy.ChainOfThought(VisualMastery)

    for i, item in enumerate(VISUAL_TOPICS, 1):
        print(f"\n[{i}/{len(VISUAL_TOPICS)}] TOPIC: {item['topic']}")

        try:
            print("   Kimi is composing the lesson... (Deep Thinking Mode)")
            result = await asyncio.wait_for(
                asyncio.to_thread(engine, topic=item['topic'], focus=item['focus']),
                timeout=400.0
            )

            # Log Telemetry
            telemetry_data = {
                "topic": item['topic'],
                "thinking": result.thinking,
                "lesson": result.lesson_plan,
                "code": result.code_examples,
                "impact": result.architectural_impact
            }
            log_telemetry(telemetry_data)
            print(f"   [TELEMETRY] Logged to {TELEMETRY_PATH}")

            # Store in ChromaDB
            from backend.core.memory.vector_db import vector_db
            knowledge_content = f"""
[VISUAL INTELLIGENCE TRAINING]
TOPIC: {item['topic']}
LESSON: {result.lesson_plan}
ARCHITECTURE: {result.architectural_impact}
CODE EXAMPLES:
{result.code_examples}
"""
            await vector_db.add_to_knowledge(
                [knowledge_content],
                [{"type": "visual_training", "topic": item['topic']}]
            )
            print(f"   [MEMORY] Lesson ingested into ChromaDB Knowledge Store.")

        except Exception as e:
            print(f"   [ERROR] Lesson composition failed: {e}")
            log_telemetry({"topic": item['topic'], "error": str(e)})

    print("\n" + "=" * 80)
    print("   🎨 VISUAL TRAINING COMPLETE! Dashboard and Data Agents are now Aesthetic Masters.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_visual_training())
