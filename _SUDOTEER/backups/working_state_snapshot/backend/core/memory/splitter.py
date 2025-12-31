"""
_SUDOTEER Memory Splitter
Automatic self-splitting heuristic for Vector and Graph memory.
Uses DSPy to classify information and extract structured relationships.
"""

import logging
import dspy
import asyncio
from typing import Dict, Any, List, Optional, Literal
from .dspy_signatures import SiftMemoryRequest, SplitMemoryStorage
import re

logger = logging.getLogger("_SUDOTEER")

class MemorySplitter:
	"""
	The 'Splitter' module that sits between the agents and the storage layer.
	It uses DSPy to intelligently route data to Vector (semantic) and Graph (relational).
	"""

	def __init__(self):
		# DSPy Modules
		self.sifter = dspy.ChainOfThought(SiftMemoryRequest)
		self.splitter = dspy.ChainOfThought(SplitMemoryStorage)

	async def sift_query(self, query: str) -> str:
		"""
		Determines if a query is semantic, relational, or hybrid.
		"""
		logger.info(f"Splitter: Sifting query -> {query}")

		# Description of stores for the LLM context
		available_stores = (
			"Vector Store: Best for semantic similarity, concepts, and finding 'similar' things.\n"
			"Graph Store: Best for relationships, dependencies, workflows, and 'how things are linked'."
		)

		result = await asyncio.to_thread(self.sifter, query=query, available_stores=available_stores)

		strategy = result.strategy.lower()
		if "hybrid" in strategy:
			return "hybrid"
		elif "relational" in strategy or "graph" in strategy:
			return "relational"
		else:
			return "semantic"

	async def split_storage(self, data: str) -> Dict[str, Any]:
		"""
		Analyzes data to decide how to store it and extracts graph relationships.
		"""
		logger.info("Splitter: Analyzing data for hybrid storage...")

		result = await asyncio.to_thread(self.splitter, data=data)

		# Clean up list/dict from DSPy output if needed (signatures handle this mostly)
		return {
			"routing": result.routing.lower(),
			"semantic_summary": result.semantic_summary,
			"entities": result.entities,
			"relationships": result.relationships,
			"facts": getattr(result, "facts", []),
			"reasoning": result.reasoning
		}

	# =========================================================================
	# HANDBOOK: Section 5 - Implementation Directives (Advanced Chunking)
	# =========================================================================

	def chunk_text(self, text: str, protocol: Literal["alpha", "beta"] = "alpha") -> List[str]:
		"""Main entry point for mission-critical chunking."""
		if protocol == "alpha":
			return self._protocol_alpha_recursive(text)
		else:
			return self._protocol_beta_semantic(text)

	def _protocol_alpha_recursive(self, text: str, chunk_size: int = 200, overlap: int = 20) -> List[str]:
		"""
		Protocol Alpha: Recursive Character Split (The 'Camry' / Sniper).
		Limits noise by keeping chunks small (200 tokens).
		"""
		logger.info(f"Splitter: Executing Protocol Alpha (Recursive 200/20)")

		# Simple recursive split implementation (simplified for vanilla context)
		separators = ["\n\n", "\n", ". ", " ", ""]

		def split_recursive(content: str, seps: List[str]) -> List[str]:
			if len(content.split()) <= chunk_size:
				return [content]

			if not seps:
				# Fallback hard split if no seps left
				words = content.split()
				return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size - overlap)]

			sep = seps[0]
			final_chunks = []
			parts = content.split(sep)

			current_chunk = ""
			for p in parts:
				if len((current_chunk + sep + p).split()) <= chunk_size:
					current_chunk = (current_chunk + sep + p) if current_chunk else p
				else:
					if current_chunk:
						final_chunks.append(current_chunk)
					# If a single part is too big, go deeper
					if len(p.split()) > chunk_size:
						final_chunks.extend(split_recursive(p, seps[1:]))
						current_chunk = ""
					else:
						current_chunk = p

			if current_chunk:
				final_chunks.append(current_chunk)
			return final_chunks

		return split_recursive(text, separators)

	def _protocol_beta_semantic(self, text: str, threshold: float = 0.85) -> List[str]:
		"""
		Protocol Beta: Cluster Semantic Chunker (Antigravity Mode).
		Logic: Split into atoms -> Embed -> Cluster by Similarity.
		"""
		logger.info(f"Splitter: Executing Protocol Beta (Semantic Clustering)")

		# 1. Atomic Split (Sentences)
		atoms = re.split(r'(?<=[.!?]) +', text)
		if not atoms: return [text]

		# 2. Vectorize atoms (Using dspy to get embeddings if available,
		# but here we'll simulate or use a simple heuristic if no embedder exposed)
		# MISSION: Implement true vector clustering when embedder is connected.

		# Heuristic fallback: Group sentences until a topic shift or size limit
		chunks = []
		current_chunk = atoms[0]

		for i in range(1, len(atoms)):
			# Heuristic similarity (simulated for now until Embedder ready)
			# In a real implementation: similarity = cosine_sim(embed(current), embed(p))
			if len((current_chunk + " " + atoms[i]).split()) <= 250:
				current_chunk += " " + atoms[i]
			else:
				chunks.append(current_chunk)
				current_chunk = atoms[i]

		chunks.append(current_chunk)
		return chunks

# Global instance
memory_splitter = MemorySplitter()
