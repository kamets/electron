import os
import logging
from typing import Dict, Any, List, Optional
from neo4j import AsyncGraphDatabase
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

logger = logging.getLogger("_SUDOTEER")

class Neo4jGraphStore:
	"""
	Neo4j Graph Store Wrapper with tab-centric elegance.
	Maps p2p agent relationships and knowledge lineage.
	"""
	def __init__(
		self,
		uri: str = None,
		user: str = None,
		password: str = None
	):
		self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
		self.auth = (
			user or os.getenv("NEO4J_USER", "neo4j"),
			password or os.getenv("NEO4J_PASSWORD", "")
		)
		self.driver = None

	async def connect(self):
		"""Establish the transactional driver connection."""
		if not self.driver:
			try:
				self.driver = AsyncGraphDatabase.driver(self.uri, auth=self.auth)
				await self.driver.verify_connectivity()
				logger.info("✓ Neo4j connection established.")
			except Exception as e:
				logger.error(f"Neo4j link failure: {e}")
				self.driver = None

	async def close(self):
		"""Close the database driver."""
		if self.driver:
			await self.driver.close()
			self.driver = None

	async def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
		"""Durable query execution helper."""
		if not self.driver:
			await self.connect()
		if not self.driver:
			return []

		try:
			async with self.driver.session() as session:
				result = await session.run(query, parameters or {})
				return await result.data()
		except Exception as e:
			logger.error(f"Neo4j Transaction Error: {e}")
			return []

	async def create_relationship(self, from_node: str, to_node: str, rel_type: str, props: Dict[str, Any]):
		"""Atomic MERGE for agent relationships."""
		query = (
			f"MERGE (a:Entity {{id: $from_id}}) "
			f"MERGE (b:Entity {{id: $to_id}}) "
			f"MERGE (a)-[r:{rel_type}]->(b) "
			"SET r += $props "
			"RETURN r"
		)
		params = {"from_id": from_node, "to_id": to_node, "props": props}
		await self.execute_query(query, params)
		logger.info(f"✓ Linked: ({from_node})-[{rel_type}]->({to_node})")

	async def find_subgraph(self, start_node: str, depth: int = 2):
		"""Semantic traversal of knowledge nodes."""
		query = (
			f"MATCH (n:Entity {{id: $start_id}})-[r*1..{depth}]-(m) "
			"RETURN n, r, m"
		)
		return await self.execute_query(query, {"start_id": start_node})
