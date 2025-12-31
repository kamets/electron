import os
import json
import logging
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("_SUDOTEER")

class VectorDatabaseManager:
	"""
	Universal Vector DB Manager.
	Switched to HttpClient to allow multi-process access (Agency + IDE Extension).
	Connects to the Chroma Core running on port 8001.
	"""
	def __init__(self, host: str = "127.0.0.1", port: int = 8001):
		self.client = None
		self.episodes = None
		self.knowledge = None
		self.host = host
		self.port = port
		self._init_client()

	def _init_client(self):
		try:
			import chromadb
			# Use HttpClient for multi-process compatibility
			self.client = chromadb.HttpClient(host=self.host, port=self.port)

			# Test connection
			self.client.heartbeat()

			# Initialize collections
			self.episodes = self.client.get_or_create_collection(
				name="episodes",
				metadata={"hnsw:space": "cosine"}
			)
			self.knowledge = self.client.get_or_create_collection(
				name="knowledge",
				metadata={"hnsw:space": "cosine"}
			)

			logger.info(f"✓ VectorDB connected: ChromaDB @ {self.host}:{self.port}")
		except Exception as e:
			logger.error(f"VectorDB Connection Failed: {e}")
			# Note: We don't raise here to allow the system to start in 'degraded' mode
			self.client = None

	async def store_episode(self, agent_id: str, content: str, summary: str, tags: List[str], quality: float, what_worked: List[str] = None, what_failed: List[str] = None) -> str:
		if not self.episodes: return ""
		mem_id = f"{agent_id}_ep_{int(datetime.now().timestamp())}"
		try:
			await asyncio.to_thread(
				self.episodes.add,
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
		except Exception as e:
			logger.error(f"Failed to store episode: {e}")
			return ""

	async def search_episodes(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
		if not self.episodes: return []
		try:
			results = await asyncio.to_thread(self.episodes.query, query_texts=[query], n_results=top_k)
			return self._parse_results(results)
		except Exception as e:
			logger.error(f"Search episodes failed: {e}")
			return []

	async def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
		if not self.knowledge: return []
		try:
			results = await asyncio.to_thread(self.knowledge.query, query_texts=[query], n_results=top_k)
			return self._parse_results(results)
		except Exception as e:
			logger.error(f"Search knowledge failed: {e}")
			return []

	async def add_to_knowledge(self, chunks: List[str], metadata: List[Dict[str, Any]] = None):
		if not self.knowledge or not chunks: return
		ids = [f"chunk_{uuid.uuid4().hex[:8]}" for _ in chunks]
		if not metadata:
			metadata = [{"timestamp": datetime.now().isoformat()} for _ in chunks]
		try:
			await asyncio.to_thread(self.knowledge.add, ids=ids, documents=chunks, metadatas=metadata)
			logger.info(f"VectorDB: Added {len(chunks)} chunks to 'knowledge'.")
		except Exception as e:
			logger.error(f"Add to knowledge failed: {e}")

	def _parse_results(self, results):
		memories = []
		if results and results.get('documents') and results['documents'][0]:
			for i, doc in enumerate(results['documents'][0]):
				memories.append({
					"content": doc,
					"metadata": results['metadatas'][0][i],
					"distance": results.get('distances', [[0]*len(doc)])[0][i]
				})
		return memories

	def get_status(self):
		try:
			if self.client:
				self.client.heartbeat()
				return {"status": "online", "backend": "ChromaDB (Remote)"}
		except:
			pass
		return {"status": "offline", "backend": "ChromaDB (Remote)"}

# Global instance
vector_db = VectorDatabaseManager()

def initialize_vector_db(backend: str = "chroma"):
    # Attempt to reconnect if previously failed
    if vector_db.client is None:
        vector_db._init_client()
    return vector_db.get_status()["status"] == "online"
