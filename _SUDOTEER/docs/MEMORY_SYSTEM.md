# 🧠 _SUDOTEER Hybrid Memory System

## Overview

The _SUDOTEER Memory System is a sophisticated, dual-layered storage architecture designed to provide agents with both semantic intuition and structural precision. It integrates **Vector Databases** for semantic search and **Graph Databases** for relational knowledge.

## Architecture

### 1. Hybrid Memory Manager (`manager.py`)

The central orchestrator that exposes the `remember` and `recall` protocols. It manages the flow of information between the Splitter and the underlying storage engines.

- **Remember**: Documents observations, reasoning traces, and facts.
- **Recall**: Retrieves relevant context based on natural language queries.

### 2. Memory Splitter (`splitter.py`)

The "brain" of the memory system, powered by **DSPy**. It uses LLM-based heuristics to:

- **Sift Queries**: Decide if a query requires semantic search (Vector) or relationship traversal (Graph).
- **Split Storage**: Analyze incoming data to extract structured relationships for the Graph while summarizing unstructured content for the Vector store.

### 3. Vector Store (`vector_db.py`)

Handles high-dimensional embeddings and semantic similarity.

- **Backends**: ChromaDB (default local), Supabase Vector, Pinecone.
- **Purpose**: "I remember talking about something similar to X."

### 4. Graph Store (`neo4j_store.py`)

Handles explicit relationships and dependencies.

- **Backend**: Neo4j.
- **Purpose**: "Agent A depends on Tool B, which is currently offline."

## Memory Routing Logic

| Data Type | Storage | Reasoning |
| :--- | :--- | :--- |
| **Narrative / Thoughts** | Vector | Semantic search is best for "vibes" and general topics. |
| **Explicit Links** | Graph | Captures hard dependencies and lineage. |
| **Hybrid** | Both | Critical data that needs both fast lookup and relationship mapping. |

## Usage Patterns

### Storing Memory

```python
from backend.core.memory.manager import memory_manager

await memory_manager.remember(
	agent_id="architect_01",
	data="The Coder agent depends on the output of the Architect's plan.",
	metadata={"importance": "high"}
)
```

### Recalling Context

```python
# Automatic sifting
context = await memory_manager.recall("Who does the Coder depend on?")

# Explicit mode
semantic_context = await memory_manager.recall("Code generation tips", mode="semantic")
```

## Technical Standards

- **Indentation**: 100% Tabs.
- **Naming**: PascalCase for Classes, snake_case for functions/variables.
- **Documentation**: JSDoc-style docstrings (adapted for Python).
