"""
Gold Ingestion: Ingesting Kimi's proposed chaos trajectories into ChromaDB for agent reflection.
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHAOS_TRAJECTORIES = [
    {
        "agent": "Cascade Echo Agent",
        "description": "Exploits the incomplete subscribe() method's missing topic validation and async race conditions. The agent broadcasts a message with a self-referential callback that triggers another broadcast before the first completes. This creates a cascading deadlock where the subscribers dict is mutated during iteration, corrupting the agent_registry with phantom entries."
    },
    {
        "agent": "Ouroboros Configurator",
        "description": "Targets the incomplete spawn_agent() method's cut-off 'agent_' initialization. By injecting a config with a self-referential role mapping, it triggers a circular dependency where the factory attempts to spawn an agent using its own partially-initialized class reference."
    },
    {
        "agent": "Quantum Splitter Agent",
        "description": "Exploits the incomplete splitter heuristic and disabled Neo4j graph store. When concurrent remember() calls process identical data, the non-deterministic splitter routes one to Vector DB and another to the null graph_store reference. The async exception from Neo4j is swallowed, leaving half-committed memories."
    }
]

async def ingest_gold():
    from backend.core.memory.vector_db import vector_db
    print("Ingesting Kimi's Gold Chaos Trajectories...")

    for chaos in CHAOS_TRAJECTORIES:
        content = f"""
[ADVANCED CHAOS TRAJECTORY]
AGENT: {chaos['agent']}
VULNERABILITY: {chaos['description']}
SOURCE: Kimi K2 Discovery Phase
DATE: {datetime.now().isoformat()}
"""
        metadata = {
            "type": "advanced_chaos",
            "agent": chaos['agent'],
            "status": "stored_for_review"
        }
        await vector_db.add_to_knowledge([content], [metadata])
    print("Ingestion complete.")

if __name__ == "__main__":
    asyncio.run(ingest_gold())
