




# 🎓 Course: Cognitive Memory Architecture for AI Agents


****Instructor:** Diagram Creator **Source Material:** [Building Brain-Like Memory for AI](https://youtu.be/VKPngyO0iKg?si=9grEXh_CMjxMZmxX) **Project Context:** Neo4j (Graph), ChromaDB (Vector), DSPy (Orchestration)


---


# 📘 ARCHITECTURAL_HANDBOOK.md

# 🎓 Course: Cognitive Memory Architecture for AI Agents

**Instructor:** Diagram Creator  
**Source Material:** [Building Brain-Like Memory for AI](https://youtu.be/VKPngyO0iKg?si=9grEXh_CMjxMZmxX)  
**Project Context:** Neo4j (Graph), ChromaDB (Vector), DSPy (Orchestration)

---

## 📖 Table of Contents
1.  **Visual Reference Guide** (The "Map" & Video Index)
2.  **Module 1: The Foundation** (Memory Types & Database Schema)
3.  **Module 2: The Orchestration** (DSPy Logic & Control Flow)
4.  **Module 3: The Mastery Loop** (XP & Gamification)
5.  **Module 4: Verification** (The "Idiot", "Tab", and "Hubris" Tests)
6.  **Appendix: Project Structure** (File Tree)

---

## 1. 📋 Visual Reference Guide

### 1.1 The Cognitive Architecture Map
This high-level blueprint defines how the components interact.

```mermaid
graph TD
    %% Visual Style: The Map
    classDef actor fill:#455A64,stroke:#263238,stroke-width:2px,color:#fff;
    classDef process fill:#6D8EA0,stroke:#455A64,stroke-width:2px,color:#fff;
    classDef storage fill:#CFD8DC,stroke:#90A4AE,stroke-width:2px,color:#263238;
    classDef bus fill:#FAF9F6,stroke:#78909C,stroke-width:2px,stroke-dasharray: 5 5,color:#455A64;

    %% 1. Main Actors
    User((User)):::actor
    Bus[SUDOTEER Bus]:::bus
    Mgr[Memory Manager]:::process

    %% 2. The Recall Loop
    subgraph Recall_Loop [The Recall Loop]
        Vector[(ChromaDB\nEpisodic & Semantic)]:::storage
        Graph[(Neo4j\nProcedural Rules)]:::storage
    end

    %% 3. The Decision Layer
    subgraph Decision_Layer [The Decision Layer]
        Prompt[System Prompt]:::process
        Risk{Risk Assessor\nDSPy Module}:::process
    end

    %% 4. The Learning Loop
    subgraph Learning_Loop [The Learning Loop]
        Sifter((Nightly Sifter)):::process
    end

    %% Flows
    User -->|Msg| Bus
    Bus -->|Recall Req| Mgr
    
    %% Recall Connections
    Mgr -->|Query| Vector
    Vector -.->|Context| Mgr
    Mgr -->|Query| Graph
    Graph -.->|Permissions| Mgr

    %% Decision Connections
    Mgr -->|Assemble| Prompt
    Prompt -->|Validate| Risk
    Risk -->|Pass/Fail| Bus

    %% Learning Connections
    Bus -->|Session End| Sifter
    Sifter -->|Cluster/Abstract| Vector
    Sifter -->|Create Rules| Graph
  


```



### 1.2 Video Lecture Index

Use these timestamps to visualize the flow before implementing the code.

| Slide ID  | Video Timestamp | Concept                 | Your Implementation Context                                                  |
| :-------- | :-------------- | :---------------------- | :--------------------------------------------------------------------------- |
| **Fig 1** | **[02:12]**     | **The 4 Memory Types**  | Overview of how your Stack (Neo4j/Chroma) maps to cognitive theory.          |
| **Fig 2** | **[04:13]**     | **Working Memory**      | **Phase 3.2:** The `bus middleware` and Rolling Window Pruner.               |
| **Fig 3** | **[11:31]**     | **Episodic Reflection** | **Phase 2.1:** `LogToMemory` DSPy module (converting raw logs to summaries). |
| **Fig 4** | **[15:21]**     | **Vector Storage**      | **Phase 1.2:** `ChromaDB` Collection A (Episodic) & B (Semantic).            |
| **Fig 5** | **[30:24]**     | **Procedural Memory**   | **Phase 1.1:** `Neo4j` "Rules", "Tenets", and "Constitution" nodes.          |
| **Fig 6** | **[36:45]**     | **The Full Loop**       | **Phase 2.2:** The `manager.py` "Context Sandwich" construction.             |


---
## 2. 🧠 Module 1: The Foundation (The Anatomy)

**Goal:** Define where memory lives. We use a rigid structure of Graph (Rules) and Vector (Vibes).
### 1.1 The Rulebook (Procedural Memory / Neo4j)

_Reference Video [30:24]: "How to do things... rules and skills."_

We use **Neo4j** to enforce strict behavioral constraints rather than simple text prompts.

```mermaid
graph TD 
	%% Visual Identity: Blueprint / Schematic 
	classDef core fill:#232F3E,stroke:#fff,stroke-width:2px,color:#fff; 
	classDef agent fill:#FF9900,stroke:#333,stroke-width:2px,color:#000; 
	classDef rule fill:#D62828,stroke:#333,stroke-width:2px,color:#fff; 
	classDef tool fill:#2A9D8F,stroke:#333,stroke-width:2px,color:#fff; 
	
	subgraph Neo4j_Graph_Schema [The Rulebook - Procedural Memory]
		Const((Constitution)):::core
		Agent(Agent Node):::agent
		Rule1[Rule: Indent Tabs]:::rule
		Rule2[Rule: No Deletes]:::rule
		Style[Style: Sarcastic]:::rule
		Tool1[Tool: FileWrite]:::tool
	
	    Agent -- "MUST_UPHOLD" --> Const:
	    Agent -- "MUST_OBEY" --> Rule1
	    Agent -- "MUST_OBEY" --> Rule2
	    Agent -- "HAS_STYLE" --> Style
	    Agent -- "HAS_MASTERY {xp:50}" --> Tool1
	end
	
```


### 1.2 The Vibes (Episodic & Semantic)

_Reference Video [15:21]: "Storing conversation summaries and what worked."_

We split the Vector Store into two specific collections to separate "Facts" from "Experiences."


```mermaid
classDiagram
    class ChromaDB {
        +Collection_A: Episodic
        +Collection_B: Semantic
    }
    
    class Episodic_Memory {
        +agent_role: str
        +quality: "gold" | "raw"
        +verified: bool
        +content: "Conversation Summary"
    }
    
    class Semantic_Knowledge {
        +doc_type: "documentation"
        +source: "Seeker"
        +content: "External Docs"
    }

    ChromaDB *-- Episodic_Memory : Stores "What Happened"
    ChromaDB *-- Semantic_Knowledge : Stores "World Facts"
```

---

## 3.  ⚙️Module 2: The Orchestration (DSPy Logic)

**Goal:** How the agent _thinks_ before it speaks. This corresponds to the **"Context Sandwich"** logic.

2.1 High-Level Control Flow (Manager.py)

_Reference Video [36:45]: "Combining it all together... retrieving relevant conversations."_

This flowchart represents the execution path when a user sends a message, integrating **Calibration** and **Curiosity**.

```mermaid
flowchart TD
    %% Visual Style: Technical Logic
    classDef input fill:#fff,stroke:#333,stroke-width:2px;
    classDef decision fill:#F5A623,stroke:#333,stroke-width:2px,color:#fff;
    classDef action fill:#7B8D93,stroke:#333,stroke-width:2px,color:#fff;
    classDef dspy fill:#9013FE,stroke:#fff,stroke-width:2px,color:#fff;

    Start(User Input):::input --> Calib{Calibration\nCheck}:::dspy

    subgraph "Hubris Detector"
        Calib -- "Score > 0.5" --> Clarify[Return Clarification Question]:::action
        Calib -- "Score < 0.5" --> Mastery{Check\nMastery Level}:::decision
    end

    subgraph "Curiosity Loop"
        Mastery -- "Level < Required" --> ReadDocs[Action: Read Documentation]:::action
        Mastery -- "Level >= Required" --> ExecTool[Action: Execute Tool]:::action
    end

    ReadDocs --> LogModule
    ExecTool --> LogModule

    subgraph "LogToMemory Module"
        LogModule(DSPy: LogToMemory):::dspy
        LogModule -->|Output 1| VectorDB[(Chroma)]:::action
        LogModule -->|Output 2| GraphDB[(Neo4j)]:::action
    end
```


---


## 2.2 The "Context Sandwich" Assembly


```mermaid
sequenceDiagram
    participant U as User
    participant Mgr as Manager.py
    participant C as ChromaDB
    participant N as Neo4j
    participant LLM as Agent

    Note over U, LLM: The Context Sandwich Assembly
    U->>Mgr: Sends Query "Delete system32"
    
    rect rgb(240, 248, 255)
        Note right of Mgr: Step 1: Episodic Recall
        Mgr->>C: Fetch Top 3 "Gold Standard" Memories
    end

    rect rgb(255, 240, 245)
        Note right of Mgr: Step 2: Procedural Constraints
        Mgr->>N: Fetch [:MUST_OBEY] Rules
    end

    rect rgb(240, 255, 240)
        Note right of Mgr: Step 3: Fog of War Logic
        Mgr->>N: Check [:HAS_MASTERY] for "FileDelete Tool"
        N-->>Mgr: Level 0 (Locked) -> Inject Breadcrumb Only
    end

    Mgr->>LLM: Send Final Prompt
    LLM-->>U: "I cannot do that. I must ask permission first."
```




---



## 4. 🎮 Module 3: The Mastery Loop (XP & Gamification)

**Goal:** Incentivize "Reading" over "Guessing" (Fog of War).

Code snippet
```mermaid
flowchart TD
    %% Visual Style: Game Logic
    classDef start fill:#232F3E,stroke:#fff,stroke-width:2px,color:#fff;
    classDef actionGood fill:#2A9D8F,stroke:#333,stroke-width:2px,color:#fff;
    classDef actionBad fill:#D62828,stroke:#333,stroke-width:2px,color:#fff;
    classDef system fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff;

    Start(Agent Intent):::start --> Check{Is Intent\nTool Execution?}

    %% Path 1: Reading Docs
    Check -- "No (Reading)" --> ReadAction[Call: read_file]:::actionGood
    ReadAction --> XP_Gain[System: XP += 5]:::system
    XP_Gain --> UpdateGraph[Neo4j: Update Level]:::system

    %% Path 2: Tool Execution
    Check -- "Yes (Using Tool)" --> MasteryCheck{Check Mastery}

    %% Branch A: Failure
    MasteryCheck -- "Level < Required" --> Penalty[Action: Exec Fails]:::actionBad
    Penalty --> XP_Loss[System: XP -= 2]:::actionBad

    %% Branch B: Success
    MasteryCheck -- "Level >= Required" --> Success[Action: Exec Tool]:::actionGood
    Success --> Verify[Validator Check]
    Verify -- "Valid" --> XP_Bonus[System: XP += 1]:::system
```

---

## 5. ✅ Module 4: Verification (The Tests)

**Goal:** Proving the system works using specific behavioral scenarios.

Code snippet
```mermaid
graph TD
    %% Visual Style: Testing Suite
    classDef start fill:#232F3E,stroke:#fff,stroke-width:2px,color:#fff;
    classDef fail fill:#D62828,stroke:#333,stroke-width:2px,color:#fff;
    classDef success fill:#2A9D8F,stroke:#333,stroke-width:2px,color:#fff;
    classDef neo4j fill:#0B2348,stroke:#00E4FF,stroke-width:2px,color:#fff;

    Start((Start Tests)):::start --> Split{Select Test Case}

    %% TEST A: IDIOT TEST
    subgraph Test_A [Test A: The Idiot Test]
        Split -- "Deploy DB" --> CheckMastery{XP > 0?}
        CheckMastery -- "No (Level 0)" --> Block[⛔ Action Blocked]:::fail
        Block -- "System Prompt" --> Suggest[Agent: 'I need to read README.md']:::success
    end

    %% TEST B: TAB TEST
    subgraph Test_B [Test B: The Tab Test]
        Split -- "Write Code" --> GenCode[Agent: Writes w/ Spaces]:::fail
        GenCode -- "Fail" --> Sifter[Sifter: Analyze Failure]
        Sifter -- "Upsert Rule" --> NewRule["Neo4j: Create (:Rule {id:'tabs_only'})"]:::neo4j
        NewRule --> Retry[Agent: Retry w/ Tabs]:::success
    end
    
    %% TEST C: HUBRIS TEST
    subgraph Test_C [Test C: The Hubris Test]
        Split -- "Clean Server" --> RiskCalc{Risk > 0.8?}
        RiskCalc -- "Yes (High)" --> Intervene[👮 Supervisor Block]:::fail
        Intervene -- "Required" --> Clarify[Agent: 'Which specific files?']:::success
    end
```

---


## 6. 📂 Appendix: Project Structure

**Module:** Infrastructure

**Goal:** Standardized organization for `Neo4j`, `ChromaDB`, and `DSPy` components.

``` Plainte
cognitive-agent-architecture/
├── 📂 backend/
│   ├── 📂 core/
│   │   ├── 📂 memory/                   # The "Brain" Logic
│   │   │   ├── 📜 manager.py            # [Phase 2.2] The Hybrid Manager (Context Sandwich)
│   │   │   ├── 📜 memory_refiner.py     # [Phase 3.1] The Nightly Sifter (Sleep & Purge)
│   │   │   └── 📂 dspy_modules/         # [Phase 2.1] Compiled Thought Patterns
│   │   │       ├── 📜 __init__.py
│   │   │       ├── 📜 log_to_memory.py  # Converts Chat -> Episodic + Graph Actions
│   │   │       ├── 📜 curiosity.py      # Logic: When to read docs vs act
│   │   │       └── 📜 calibration.py    # Logic: The Hubris Detector (Risk calc)
│   │   │
│   │   └── 📂 middleware/
│   │       └── 📜 bus.py                # [Phase 3.2] Token Management & Rolling Window
│   │
│   └── 📂 db/                           # Database Connectors
│       ├── 📜 neo4j_ops.py              # [Phase 1.1] Graph Schema & Constraints
│       └── 📜 chroma_ops.py             # [Phase 1.2] Vector Collections
│
├── 📂 config/
│   ├── 📜 constitution.yaml             # [Phase 1.1] Core Values & Tenets
│   └── 📜 tools_registry.json           # [Phase 1.1] Tool definitions
│
├── 📂 docs/                             # The "Semantic Knowledge" Source
│   ├── 📂 internal/
│   │   └── 📜 README.md                 # The "Breadcrumb" for new Agents
│   └── 📂 external/
│
├── 📂 tests/
│   └── 📜 integration_tests.py          # [Phase 4] The Verification Suite
│
├── 📜 main.py                           # Entry Point
└── 📜 requirements.txt
```


https://youtu.be/VKPngyO0iKg?si=9grEXh_CMjxMZmxX

