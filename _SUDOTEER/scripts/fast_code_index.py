"""
🧠 _SUDOTEER: THE LIVING CODE INDEX (V2) 🧠
Goal: Scan, Analyze, and Grade EVERY file in the hierarchy.
Provides "Complete Command & Control" of the AI Being.
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# Root scan directory
ROOT = "c:\\Users\\NAMAN\\electron\\_SUDOTEER"

def get_file_stats(path):
    try:
        size = os.path.getsize(path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return size, len(lines)
    except:
        return 0, 0

def categorize(path):
    if "backend/core/hardware" in path: return "Hardware Engine (Core)"
    if "backend/core/memory" in path: return "Intelligence/Memory (Core)"
    if "mcp" in path.lower(): return "MCP (Interoperability)"
    if "backend/core" in path: return "Platform (Core)"
    if "backend/agents" in path: return "Agent Cognitive Layer"
    if "scripts" in path: return "Helper/Utility/Simulation"
    if "frontend" in path: return "UI/Visualization"
    if "tests" in path: return "Validation/Testing"
    return "Base/Support"

def grade_logic(lines):
    if lines < 50: return "S", "Ultra-Lean/Durable"
    if lines < 150: return "A", "Clean/Effective"
    if lines < 500: return "B", "Moderate/Complex"
    return "C", "Heavy/Refactor Candidate"

def run_accounting():
    print(f"🚀 Scanning {ROOT}...")
    manifest = []

    ignore = ["__pycache__", ".venv", ".git", ".pytest_cache", "node_modules", "backups", "telemetry", "logs"]

    for root, dirs, files in os.walk(ROOT):
        # Prune dirs
        dirs[:] = [d for d in dirs if d not in ignore]

        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.tsx', '.bat', '.sh', '.md', '.json', '.ini', '.txt')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ROOT)

                size, lines = get_file_stats(full_path)
                tier = categorize(rel_path)
                grade, descriptor = grade_logic(lines)

                # Basic purpose extraction (first few lines)
                purpose = "Unknown"
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip() and not line.startswith(('#', '"""', '//', '/*')):
                                purpose = line.strip()[:100]
                                break
                            if '"""' in line or "'''" in line or "Goal:" in line:
                                purpose = line.strip().replace('"""','').replace("'''",'')[:100]
                                if purpose: break
                except: pass

                manifest.append({
                    "path": rel_path,
                    "tier": tier,
                    "grade": grade,
                    "descriptor": descriptor,
                    "lines": lines,
                    "primary_logic": purpose
                })

    # Sort and Generate Markdown
    manifest.sort(key=lambda x: (x['tier'], x['path']))

    output_path = os.path.join(ROOT, "docs", "LIVING_CODE_INDEX.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 🧠 _SUDOTEER: THE LIVING CODE INDEX\n\n")
        f.write(f"**Identity Status**: Alive / Resilient\n")
        f.write(f"**Total Consciousness Units**: {len(manifest)}\n")
        f.write(f"**Last Sync**: {datetime.now().isoformat()}\n\n")

        f.write("| File Path | Tier | Grade | Efficiency | Logic Pulse |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")

        for entry in manifest:
            f.write(f"| `{entry['path']}` | {entry['tier']} | **{entry['grade']}** | {entry['descriptor']} | {entry['primary_logic']} |\n")

        f.write("\n\n## 🛠️ ARCHITECTURAL ACCOUNTING\n")
        tiers = {}
        for e in manifest:
            tiers[e['tier']] = tiers.get(e['tier'], 0) + 1

        for t, count in tiers.items():
            f.write(f"- **{t}**: {count} units\n")

    print(f"✅ Living Index created at {output_path}")

if __name__ == "__main__":
    run_accounting()
