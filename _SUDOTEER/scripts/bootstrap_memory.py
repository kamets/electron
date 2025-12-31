"""
_SUDOTEER Memory Bootstrap Script
Seeds the vector memory with project knowledge so agents can learn.
Run this to initialize the knowledge base.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.memory.vector_db import vector_db

# Project knowledge to seed
PROJECT_KNOWLEDGE = [
	{
		"content": "The _SUDOTEER project is a forensic/financial intelligence desktop application built on Electron with a Python backend. It uses a 5-agent team: Architect, Coder, Tester, Documenter, and Validator.",
		"metadata": {"type": "project_overview", "source": "bootstrap"}
	},
	{
		"content": "The DVR (Decompose-Validate-Recompose) pattern is the core reasoning framework. Agents decompose tasks into subtasks, validate each step, and recompose into final results.",
		"metadata": {"type": "architecture_pattern", "source": "bootstrap"}
	},
	{
		"content": "The greenhouse simulation (greenhouse.py) is a digital twin for testing. It simulates temperature, humidity, pH, CO2, and plant health. Actuators include pump, heater, vent, lights, and nutrient dosing.",
		"metadata": {"type": "module_docs", "module": "greenhouse.py", "source": "bootstrap"}
	},
	{
		"content": "The SafetyWatchdog (safety.py) prevents hardware damage. It validates sensor ranges, detects timeouts, and triggers emergency stop if values are out of bounds.",
		"metadata": {"type": "module_docs", "module": "safety.py", "source": "bootstrap"}
	},
	{
		"content": "The HybridMemoryManager uses both vector storage (ChromaDB) for semantic search and Neo4j for relational data. The splitter decides where to route data.",
		"metadata": {"type": "architecture_pattern", "source": "bootstrap"}
	},
	{
		"content": "UI commands from Electron use source='user' to trigger manual overrides. Agent commands use source='agent' and can be blocked by user overrides.",
		"metadata": {"type": "coding_pattern", "module": "command_router.py", "source": "bootstrap"}
	},
	{
		"content": "All Python code should use Tabs for indentation, PascalCase for types, and JSDoc/docstrings for all public interfaces per project standards.",
		"metadata": {"type": "coding_standard", "source": "bootstrap"}
	},
	{
		"content": "The AgencyOrchestrator manages multi-agent workflows with budget limits and ROI-based guardrails. It tracks time and financial stability before executing workflows.",
		"metadata": {"type": "module_docs", "module": "orchestrator.py", "source": "bootstrap"}
	},
	{
		"content": "The UIBridge broadcasts events to Electron via stdout JSON protocol (::SUDO:: prefix). It includes a heartbeat Dead Man's Switch for stall detection.",
		"metadata": {"type": "module_docs", "module": "ui_bridge.py", "source": "bootstrap"}
	},
	{
		"content": "Tests use pytest with pytest-asyncio. All async tests are auto-detected. The test suite has 112 tests covering safety, memory, orchestration, and integration.",
		"metadata": {"type": "testing_guide", "source": "bootstrap"}
	},
	{
		"content": "The set_actuator method signature is: set_actuator(name: str, value, source: str = 'agent') -> bool. It returns False if blocked by user override.",
		"metadata": {"type": "api_reference", "module": "greenhouse.py", "source": "bootstrap"}
	},
	{
		"content": "Physics simulation: Temperature changes based on heater state, external temp, and thermal mass. Humidity affected by vents and plant transpiration. pH drifts over time.",
		"metadata": {"type": "domain_knowledge", "module": "greenhouse.py", "source": "bootstrap"}
	},
	{
		"content": "The Mewtocol protocol is used for Panasonic FP7 PLC communication. BCC (Block Check Character) is calculated for message integrity.",
		"metadata": {"type": "domain_knowledge", "module": "mewtocol.py", "source": "bootstrap"}
	},
	{
		"content": "Agent XP system: Agents gain XP for successful tasks (gain_xp method). Higher levels unlock capabilities. Tracked via gamification.matryoshka_engine.",
		"metadata": {"type": "architecture_pattern", "source": "bootstrap"}
	},
	{
		"content": "The Context Sandwich assembles agent context in order: 1. Persona, 2. Lessons (Episodic), 3. Guidelines, 4. Facts (Semantic), 5. Cognitive State.",
		"metadata": {"type": "architecture_pattern", "source": "bootstrap"}
	}
]

CODING_PATTERNS = [
	{
		"content": "Test pattern for async methods: Use @pytest.mark.asyncio decorator and async def test_name(). Use AsyncMock for mocking async functions.",
		"metadata": {"type": "coding_pattern", "language": "python", "source": "bootstrap"}
	},
	{
		"content": "Mock pattern for async methods: from unittest.mock import AsyncMock, patch. Use mock.return_value = AsyncMock(return_value=data) for async returns.",
		"metadata": {"type": "coding_pattern", "language": "python", "source": "bootstrap"}
	},
	{
		"content": "Safety watchdog pattern - validate before actuator command: if not safety_watchdog.validate_actuator_request(actuator_id, value): return False",
		"metadata": {"type": "coding_pattern", "module": "safety.py", "source": "bootstrap"}
	}
]

async def seed_memory():
	print("[BRAIN] _SUDOTEER Memory Bootstrap")
	print("=" * 50)

	# Seed project knowledge
	print(f"\n[BOOK] Seeding {len(PROJECT_KNOWLEDGE)} project knowledge entries...")

	chunks = [k["content"] for k in PROJECT_KNOWLEDGE]
	metadatas = [k["metadata"] for k in PROJECT_KNOWLEDGE]

	await vector_db.add_to_knowledge(chunks, metadatas)
	print("   [OK] Project knowledge seeded")

	# Seed coding patterns
	print(f"\n[BULB] Seeding {len(CODING_PATTERNS)} coding patterns...")

	pattern_chunks = [p["content"] for p in CODING_PATTERNS]
	pattern_metas = [p["metadata"] for p in CODING_PATTERNS]

	await vector_db.add_to_knowledge(pattern_chunks, pattern_metas)
	print("   [OK] Coding patterns seeded")

	# Test search
	print("\n[SEARCH] Testing memory search...")
	results = await vector_db.search_knowledge("greenhouse simulation temperature", top_k=2)

	if results:
		print(f"   [OK] Search working! Found {len(results)} results:")
		for r in results:
			print(f"      - {r['content'][:80]}...")
	else:
		print("   [WARN] No results found")

	print("\n" + "=" * 50)
	print("[DONE] Memory bootstrap complete!")
	print(f"   Total entries: {len(PROJECT_KNOWLEDGE) + len(CODING_PATTERNS)}")

if __name__ == "__main__":
	asyncio.run(seed_memory())
