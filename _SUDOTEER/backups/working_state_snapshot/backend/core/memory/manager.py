"""
_SUDOTEER Hybrid Memory Manager.
Integrates Vector and Graph memory with an automatic splitting heuristic.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from .vector_db import vector_db
from .neo4j_store import Neo4jGraphStore
from .splitter import memory_splitter
from datetime import datetime

logger = logging.getLogger("_SUDOTEER")

class HybridMemoryManager:
	"""
	Routes unstructured knowledge to Vector (ChromaDB/Pinecone) and
	relational entities to Neo4j (Graph).

	Uses the 'Splitter' module to decide where to store and what to retrieve.
	"""
	def __init__(self):
		self.vector_db = vector_db
		self.graph_store = Neo4jGraphStore()
		self.splitter = memory_splitter

	async def remember(self, agent_id: str, data: str, metadata: Optional[Dict[str, Any]] = None):
		"""
		The 'Remember' protocol with automatic splitting.
		"""
		logger.info(f"Memory: Processing 'remember' for {agent_id}")

		# 1. Use the Splitter heuristic to analyze data
		split_plan = await self.splitter.split_storage(data)
		routing = split_plan["routing"]

		results = {"memory_id": None, "graph_synced": False}

		# 2. Store in Vector Memory (Semantic)
		if routing in ["vector", "both"]:
			memory_id = await self.vector_db.store_memory(
				agent_id=agent_id,
				memory_type="observation",
				content=split_plan["semantic_summary"],
				metadata={
					"original_data": data[:500],
					"reasoning": split_plan["reasoning"],
					**(metadata or {})
				}
			)
			results["memory_id"] = memory_id

		# 3. Store in Graph Memory (Relational)
		if routing in ["graph", "both"]:
			relationships = split_plan.get("relationships", [])
			for rel in relationships:
				# rel: {"from": str, "to": str, "type": str, "props": dict}
				await self.graph_store.create_relationship(
					rel.get("from", "unknown"),
					rel.get("to", "unknown"),
					rel.get("type", "RELATED_TO"),
					rel.get("props", {"source_agent": agent_id})
				)
			results["graph_synced"] = True

		logger.info(f"Memory: Split storage complete. Routing: {routing}")
		return results

	async def ingest_document(self, agent_id: str, title: str, content: str, protocol: str = "alpha"):
		"""
		High-precision document ingestion using Advanced Chunking Protocols.
		HANDBOOK: Section 5 - Implementation Directives.
		"""
		logger.info(f"Memory: Ingesting document '{title}' using Protocol {protocol}")

		# 1. Generate Chunks
		chunks = self.splitter.chunk_text(content, protocol=protocol)

		# 2. Prepare Metadata
		metadata = [{
			"source": title,
			"agent_id": agent_id,
			"chunk_index": i,
			"total_chunks": len(chunks),
			"protocol": protocol,
			"timestamp": datetime.now().isoformat()
		} for i in range(len(chunks))]

		# 3. Store in Knowledge Base
		await self.vector_db.add_to_knowledge(chunks, metadata)

		return {"chunks_ingested": len(chunks), "protocol": protocol}

	async def recall(self, query: str, mode: Optional[str] = None) -> Dict[str, Any]:
		"""
		Retrieve context for agent reasoning using the Sifter heuristic.
		"""
		# 1. Use Sifter to decide mode if not provided
		if not mode:
			mode = await self.splitter.sift_query(query)

		logger.info(f"Memory: Recalling context [Mode: {mode}] for: {query}")

		context_results = {
			"query": query,
			"mode": mode,
			"semantic_context": [],
			"episode_context": [],
			"graph_context": {}
		}

		# 2. Retrieve from Vector Store - Knowledge (Semantic)
		if mode in ["semantic", "hybrid"]:
			semantic_results = await self.vector_db.search_knowledge(query, top_k=5)
			context_results["semantic_context"] = semantic_results

		# 3. Retrieve from Vector Store - Episodes (Past Experiences)
		if mode in ["semantic", "hybrid"]:
			episode_results = await self.vector_db.search_episodes(query, top_k=3)
			context_results["episode_context"] = episode_results

		# 4. Retrieve from Graph Store
		if mode in ["relational", "hybrid"]:
			graph_results = await self.graph_store.find_subgraph(query)
			context_results["graph_context"] = graph_results

		return context_results

	async def get_context_sandwich(self, agent_id: str, query: str, extra_context: Optional[str] = None) -> str:
		"""
		HANDBOOK: Sequence Diagram [2.2] - The Context Sandwich Assembly.
		Order: 1. Persona, 2. Lessons (Enriched), 3. Guidelines, 4. Facts.
		"""
		logger.info(f"Memory: Assembling Context Sandwich for {agent_id}")

		# 1. Persona (Base)
		try:
			persona_data = await self.graph_store.find_subgraph("Persona")
			persona_str = f"You are {persona_data.get('name', 'SUDOTEER Agent')}. Style: {persona_data.get('style', 'Clear/Effective')}."
		except:
			persona_str = "You are a specialized agent in the SUDOTEER Agency."

		# 2. Lessons (Episodic Recall - Enriched)
		episodes = await self.vector_db.search_episodes(query, top_k=3)
		lessons_parts = []
		for m in episodes:
			meta = m['metadata']
			summary = f"- EXPERIENCE: {meta.get('summary', m['content'][:200])}"
			worked = f"  - WHAT WORKED: {meta.get('what_worked', 'N/A')}"
			failed = f"  - WHAT FAILED: {meta.get('what_failed', 'N/A')}"
			lessons_parts.extend([summary, worked, failed])

		lessons_str = "\n".join(lessons_parts)

		# 3. Guidelines (Procedural Constraints)
		try:
			rules = await self.graph_store.find_subgraph("Constitution")
			tenets = rules.get("tenets", [])
			guidelines_str = "\n".join([f"! {t}" for t in tenets])
		except:
			guidelines_str = "Follow agency best practices."

		# 4. Facts (Semantic Retrieval)
		facts = await self.vector_db.search_knowledge(query, top_k=5)
		facts_str = "\n".join([f"* {m['content'][:300]}..." for m in facts])

		# 5. Cognitive State (Fog of War) - Extension to Handbook
		from ..gamification import matryoshka_engine
		agent_stats = matryoshka_engine.get_agent_stats(agent_id)
		mastery_level = agent_stats.get("level", 1)
		mastery_note = f"Current Mastery Level: {mastery_level} ({matryoshka_engine.LEVELS[mastery_level]['name']})"

		# Build the final sandwich
		sandwich = f"""
### 🥪 THE CONTEXT SANDWICH

**Part 1: Persona (Base)**
{persona_str}

**Part 2: Lessons (Episodic)**
{lessons_str if lessons_str else "No relevant lessons from past experiences."}

**Part 3: Guidelines (Procedural)**
{guidelines_str}

**Part 4: Facts (Semantic)**
{facts_str if facts_str else "No specific grounding facts found."}
{f"**Extra System Context:**\n{extra_context}" if extra_context else ""}

**Part 5: Cognitive State (Fog of War)**
{mastery_note}
---
DOCS_BREADCRUMB: If you lack information, READ the /docs/ directory to gain XP.
---
"""
		return sandwich

	async def sifter_session_end(self, agent_id: str):
		"""
		HANDBOOK: The Learning Loop [Part 1, Figure 1].
		Converts the current session's monologue into high-level 'Wisdom'.
		Includes the Procedural Update Loop (Rewriting Guidelines).
		"""
		from ..monologue import recorder
		from .dspy_modules.log_to_memory import reflection_engine

		# HANDBOOK: The Learning Loop [Part 1]
		logger.info(f"Sifter: Archiving session for {agent_id}...")

		# Use last 10 events for a compact summary
		history = recorder.history[-10:] if recorder.history else []
		if not history: return

		raw_log = json.dumps(history, indent=2)

		# 1. Reflect on the log (Episodic Reflection)
		reflection = await reflection_engine.reflect(raw_log)

		# 2. Store in Episodic Memory
		await self.vector_db.store_episode(
			agent_id=agent_id,
			content=raw_log,
			summary=reflection["summary"],
			tags=reflection["entities"],
			quality=reflection["quality"],
			what_worked=reflection.get("what_worked", []),
			what_failed=reflection.get("what_failed", [])
		)

		# 3. Procedural Update Loop (Update Guidelines)
		if reflection["quality"] > 0.8:
			logger.info("Sifter: High-quality experience detected. Updating Procedural Guidelines...")
			try:
				# HANDBOOK: Rewrite Rules (Procedural Update)
				if reflection.get("improvement_plan"):
					new_tenet = f"IMPROVEMENT: {reflection['improvement_plan']}"
					await self.graph_store.create_relationship(
						"Constitution", "Agency", "GOVERNS",
						{"id": "core_values", "tenets": [new_tenet]}
					)
			except Exception as e:
				logger.error(f"Sifter: Procedural update failed: {e}")

		# 4. Entity Graphing
		for entity in reflection["entities"]:
			try:
				await self.graph_store.create_relationship(
					agent_id, entity, "LEARNED_FROM", {"timestamp": "now", "wisdom": reflection["summary"]}
				)
			except:
				pass

		logger.info(f"✓ Sifter: session complete. Episodic saved & Procedural refined.")

# Global memory manager instance
memory_manager = HybridMemoryManager()
