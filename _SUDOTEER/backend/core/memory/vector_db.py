import os
import logging
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("_SUDOTEER")

class VectorDatabaseManager:
	"""
	Lean Vector DB Manager focusing on ChromaDB for local durability.
	"""
	def __init__(self, backend: str = "chroma"):
		self.client = None
		self.collection = None
		self.backend_type = backend
		self._init_backend(backend)

	def _init_backend(self, backend: str):
		try:
			import chromadb
			db_path = Path("data/vector_db")
			db_path.mkdir(parents=True, exist_ok=True)

			self.client = chromadb.PersistentClient(path=str(db_path))

			# HANDBOOK: Collection 'episodes' (Past Experiences)
			self.episodes = self.client.get_or_create_collection(
				name="episodes",
				metadata={"hnsw:space": "cosine"}
			)

			# HANDBOOK: Collection 'knowledge' (Facts/Docs)
			self.knowledge = self.client.get_or_create_collection(
				name="knowledge",
				metadata={"hnsw:space": "cosine"}
			)

			logger.info(f"✓ VectorDB initialized: ChromaDB @ {db_path}")
		except Exception as e:
			logger.error(f"VectorDB Init Failed: {e}")

	async def store_episode(self, agent_id: str, content: str, summary: str, tags: List[str], quality: float, what_worked: List[str] = None, what_failed: List[str] = None) -> str:
		"""HANDBOOK: Part 3.A.2 - episodes collection (Enriched)."""
		if not self.episodes: return ""
		mem_id = f"{agent_id}_ep_{int(datetime.now().timestamp())}"
		self.episodes.add(
			ids=[mem_id],
			documents=[content],
			metadatas=[{
				"agent_id": agent_id,
				"summary": summary,
				"tags": ",".join(tags),
				"what_worked": ",".join(what_worked or []),
				"what_failed": ",".join(what_failed or []),
				"quality_score": quality,
				"timestamp": datetime.now().isoformat()
			}]
		)
		return mem_id

	async def search_memories(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
		"""DEPRECATED: Use search_episodes or search_knowledge."""
		return await self.search_episodes(query, top_k)

	async def search_episodes(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
		if not self.episodes: return []
		results = self.episodes.query(query_texts=[query], n_results=top_k)
		return self._parse_results(results)

	async def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
		if not self.knowledge: return []
		results = self.knowledge.query(query_texts=[query], n_results=top_k)
		return self._parse_results(results)

	async def add_to_knowledge(self, chunks: List[str], metadata: List[Dict[str, Any]] = None):
		"""
		HANDBOOK: Collection 'knowledge' (Facts/Docs).
		Efficiently stores large numbers of chunks.
		"""
		if not self.knowledge or not chunks: return
		ids = [f"chunk_{uuid.uuid4().hex[:8]}" for _ in chunks]

		# Ensure metadata is same length as chunks
		if not metadata:
			metadata = [{"timestamp": datetime.now().isoformat()} for _ in chunks]

		self.knowledge.add(
			ids=ids,
			documents=chunks,
			metadatas=metadata
		)
		logger.info(f"VectorDB: Added {len(chunks)} chunks to 'knowledge' collection.")

	def _parse_results(self, results):
		memories = []
		if results and results['documents']:
			for i, doc in enumerate(results['documents'][0]):
				memories.append({
					"content": doc,
					"metadata": results['metadatas'][0][i],
					"distance": results['distances'][0][i]
				})
		return memories

	async def store_memory(self, agent_id: str, memory_type: str, content: str, metadata: Dict = None) -> str:
		if not self.collection: return ""

		mem_id = f"{agent_id}_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:4]}"
		meta = {
			"agent_id": agent_id,
			"type": memory_type,
			"timestamp": datetime.now().isoformat(),
			**(metadata or {})
		}

		self.collection.add(
			ids=[mem_id],
			documents=[content],
			metadatas=[meta]
		)
		return mem_id

	async def search_memories(self, query: str, top_k: int = 5) -> List[Dict]:
		if not self.collection: return []

		results = self.collection.query(query_texts=[query], n_results=top_k)
		memories = []
		if results and results['documents']:
			for i, doc in enumerate(results['documents'][0]):
				memories.append({
					"content": doc,
					"metadata": results['metadatas'][0][i],
					"distance": results['distances'][0][i]
				})
		return memories

	def get_status(self):
		return {"status": "online" if self.collection else "offline", "backend": "ChromaDB"}

# Global instance
vector_db = VectorDatabaseManager()

def initialize_vector_db(backend: str = "chroma"):
	return vector_db.get_status()["status"] == "online"
