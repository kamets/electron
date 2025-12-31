"""
🧠 _SUDOTEER: THE LIVING CODE INDEX 🧠
Teacher: Kimi K2 (Ollama)
Goal: Scan, Analyze, Grade, and Index EVERY line of code in the Agency.
Provides "Complete Command & Control" by turning the codebase into a queryable AI Being.
"""
import asyncio
import os
import sys
import json
import dspy
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

# ============================================
# ANALYSIS SIGNATURE
# ============================================

class AnalyzeCodeUnit(dspy.Signature):
    """Deeply analyze a code file for purpose, quality, and durability."""
    file_path: str = dspy.InputField(desc="Relative path of the file")
    code_content: str = dspy.InputField(desc="The actual source code")
    context: str = dspy.InputField(desc="Agency Context: _SUDOTEER forensic/industrial intelligence")

    summary: str = dspy.OutputField(desc="1-sentence summary of what this code does")
    purpose_tier: str = dspy.OutputField(desc="Tier: Core, Platform, Tool, Helper, or Simulation")
    quality_grade: str = dspy.OutputField(desc="Grade (S, A, B, C) based on simplicity/effectiveness")
    durability_score: int = dspy.OutputField(desc="1-10 rating of how 'future-proof' and robust the code is")
    genius_critique: str = dspy.OutputField(desc="Short 'Genius' insight on how this fits the 'Alive Being' metaphor")

# ============================================
# THE INDEXER ENGINE
# ============================================

class LivingIndexEngine:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.manifest_path = "docs/CODE_MANIFEST.md"
        self.index_data = []

        # Setup Kimi
        self.teacher = dspy.LM(
            model="ollama_chat/kimi-k2-thinking:cloud",
            api_base="http://localhost:11434",
            cache=False
        )
        dspy.configure(lm=self.teacher)

    def should_ignore(self, path: str) -> bool:
        ignore_list = [
            "__pycache__", ".venv", ".git", ".pytest_cache",
            "node_modules", "dist", "out", ".vs", "backups", "telemetry"
        ]
        return any(part in path for part in ignore_list)

    async def scan_and_analyze(self):
        print(f"🚀 Starting Deep Scan: {self.root_dir}")
        print("   Thinking like an Alive AI Being...")

        analyzer = dspy.ChainOfThought(AnalyzeCodeUnit)

        file_list = []
        for root, dirs, files in os.walk(self.root_dir):
            if self.should_ignore(root): continue
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.tsx', '.css', '.html', '.bat', '.sh')):
                    file_list.append(os.path.join(root, file))

        print(f"📂 Found {len(file_list)} code units to index.")

        for i, full_path in enumerate(file_list):
            rel_path = os.path.relpath(full_path, self.root_dir)
            print(f"[{i+1}/{len(file_list)}] Analyzing: {rel_path}...")

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Limit content size for LLM context
                snippet = content if len(content) < 5000 else content[:4000] + "\n...[TRUNCATED]..."

                result = await asyncio.to_thread(
                    analyzer,
                    file_path=rel_path,
                    code_content=snippet,
                    context="Forensic Greenhouse Intelligence Application"
                )

                entry = {
                    "path": rel_path,
                    "summary": result.summary,
                    "tier": result.purpose_tier,
                    "grade": result.quality_grade,
                    "durability": result.durability_score,
                    "critique": result.genius_critique,
                    "timestamp": datetime.now().isoformat()
                }
                self.index_data.append(entry)

                # Store in ChromaDB
                from backend.core.memory.vector_db import vector_db
                await vector_db.add_to_knowledge(
                    [f"FILE: {rel_path}\nSUMMARY: {result.summary}\nTIER: {result.purpose_tier}\nCRITIQUE: {result.genius_critique}"],
                    [{"type": "code_index", "path": rel_path, "grade": str(result.quality_grade)}]
                )

            except Exception as e:
                print(f"   [ERROR] Skipping {rel_path}: {e}")

    def generate_report(self):
        print(f"\n📑 Generating Master Manifest: {self.manifest_path}")

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            f.write("# 🧠 _SUDOTEER: LIVING CODE MANIFEST\n\n")
            f.write(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Total Code Units: {len(self.index_data)}*\n\n")

            f.write("| File Path | Tier | Grade | Durability | Summary |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")

            for entry in sorted(self.index_data, key=lambda x: x['tier']):
                f.write(f"| `{entry['path']}` | {entry['tier']} | **{entry['grade']}** | {entry['durability']}/10 | {entry['summary']} |\n")

            f.write("\n## 🧬 GENIUS CRITIQUES (The Life of the Code)\n\n")
            for entry in self.index_data:
                f.write(f"### `{entry['path']}`\n- **Critique**: {entry['critique']}\n\n")

        print("✅ Manifest Complete.")

async def main():
    root = "c:\\Users\\NAMAN\\electron\\_SUDOTEER"
    engine = LivingIndexEngine(root)
    await engine.scan_and_analyze()
    engine.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
