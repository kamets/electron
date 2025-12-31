# 🧠 _SUDOTEER: HYBRID-COGNITIVE MEMORY
**Tier**: Platform Architecture
**Status**: Implemented / Live

## 1. The Dual-Write Architecture
_SUDOTEER_ implements a 3-layer hybrid memory system to ensure that agents are both Structurally Aware (Causality) and Semantically Grounded (Intelligence).

```mermaid
graph TD
    %% Styling
    classDef ai fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef store fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef process fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;

    AgentInput((Agent Reasoning)) --> DSPy[DSPy Module]:::ai

    subgraph "DSPy Output Processing"
        DSPy -->|Generates| JSON[Structured JSON Log]:::process
    end

    subgraph "Dual-Write Persistence"
        JSON -->|Extract Embeddings| Chroma[ChromaDB]:::store
        JSON -->|Extract Entities| Neo4j[Neo4j Graph]:::store
    end

    Chroma -- "Semantic Recall" --> DSPy
    Neo4j -- "Causal Context" --> DSPy

    NoteChroma["Stores: 'Reasoning', 'Summaries'"]
    NoteNeo4j["Stores: (Agent)-[:RAN]->(Command)-[:AFFECTED]->(Hardware)"]
```

## 2. Memory Subsystems

### A. ChromaDB (Semantic Memory)
- **Purpose**: "What did I do last time the situation looked like this?"
- **Content**: Reasoning snippets, crisis debriefs, and horticultural wisdom.
- **Partitioning**: Each agent (Climate, Nutrient) has its own isolated collection to prevent "context pollution."

### B. Neo4j (Structural Audit)
- **Purpose**: "Who turned on the pump at 3 AM?"
- **Logic**: Models causal chains. (Agent) -> (Event) -> (Action) -> (Hardware Change).
- **Protocol**: Every `/command` write triggers a Graph Relation update.

### C. DSPy (The Cognitive Bridge)
- **Purpose**: Enforces typed outputs.
- **Role**: Ensures that chaotic agent thoughts are unified into structured JSON before being committed to memory.
