import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.memory.vector_db import vector_db
from backend.core.memory.neo4j_store import Neo4jGraphStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("_SUDOTEER_INIT")

async def initialize_systems():
	logger.info("--- 🗄️ INITIALIZING DATABASE SYSTEMS ---")

	# 1. ChromaDB (Vector)
	logger.info("Initializing ChromaDB...")
	try:
		# Test storage
		mem_id = await vector_db.store_episode(
			agent_id="system_init",
			content="Database initialization sequence started.",
			summary="Init logs",
			tags=["init", "system"],
			quality=1.0
		)
		if mem_id:
			logger.info(f"✅ ChromaDB Online. Test entry created: {mem_id}")
		else:
			logger.error("❌ ChromaDB Failed to return record ID.")
	except Exception as e:
		logger.error(f"❌ ChromaDB Error: {e}")

	# 2. Neo4j (Graph)
	logger.info("Connecting to Neo4j Graph Database (Bolt Protocol)...")
	graph_store = Neo4jGraphStore(uri="bolt://localhost:7687", password="password")

	try:
		await graph_store.connect()
		if graph_store.driver:
			result = await graph_store.execute_query("RETURN 1 as connection_test")
			if result and result[0].get("connection_test") == 1:
				logger.info("✅ Neo4j Graph Online and responding.")
			else:
				logger.error("❌ Neo4j responded with invalid data.")
			await graph_store.close()
		else:
			logger.error("❌ Neo4j Driver could not establish link.")
	except Exception as e:
		logger.error(f"❌ Neo4j Error: {e}")

	logger.info("--- 🗄️ INITIALIZATION COMPLETE ---")

if __name__ == "__main__":
	asyncio.run(initialize_systems())
