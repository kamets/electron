# 🏗️ _SUDOTEER Architecture Documentation (v11.1.0+)

## Overview
This document provides a high-level representation of the **_SUDOTEER** ecosystem, a premium forensic and financial intelligence desktop application specialized for industrial greenhouse automation and agricultural intelligence.

---

## 🏛️ System Topology
The following diagram illustrates the relationship between the Electron frontend, the Python Agency backend, the Hybrid Memory system, and the Industrial control layer.

```mermaid
architecture-beta
	group client(logos:electron)[Desktop Client]
	service ui(logos:javascript)[UI Renderer] in client
	service bridge(logos:typescript)[Electron Bridge] in client

	group backend(logos:python)[Agency Middleware]
	service web(logos:fastapi)[Web Server] in backend
	service cmd(logos:python)[Command Server] in backend
	service orch(logos:python)[Orchestrator] in backend

	group agent_team(logos:openai)[Specialized Agents]
	service architect(logos:python)[Architect] in agent_team
	service coder(logos:python)[Coder] in agent_team
	service climate(logos:python)[Climate Agent] in agent_team
	service nutrient(logos:python)[Nutrient Agent] in agent_team

	group knowledge(logos:database)[Hybrid Memory]
	service manager(logos:python)[Memory Manager] in knowledge
	service chroma(logos:chromadb)[ChromaDB (Local)] in knowledge
	service neo4j(logos:neo4j)[Neo4j (Local)] in knowledge
	service supabase(logos:supabase)[Supabase (Cloud)] in knowledge

	group industrial(logos:arduino)[Process Control]
	service bridge_plc(logos:python)[Industrial Bridge] in industrial
	service twin(logos:python)[Hardware Twin] in industrial

	group external(cloud)[External Data]
	service weather(logos:google-cloud-functions)[OpenWeather] in external
	service nasa(logos:google-cloud-functions)[NASA POWER] in external
	service market(logos:google-cloud-functions)[Market News] in external

	ui:R -- L:bridge
	bridge:B -- T:web
	web:B -- T:cmd
	cmd:B -- T:orch

	orch:B -- T:architect
	orch:B -- T:coder
	orch:B -- T:climate
	orch:B -- T:nutrient

	architect:L -- R:manager
	coder:L -- R:manager
	climate:L -- R:manager
	nutrient:L -- R:manager

	manager:B -- T:chroma
	manager:R -- L:neo4j
	manager:B -- T:supabase

	climate:R -- L:bridge_plc
	bridge_plc:B -- T:twin

	architect:T -- B:weather
	architect:T -- B:nasa
	architect:T -- B:market
```

---

## 🧱 Layered Architecture (Base -> Platform -> Workbench)
As defined in the core directive, _SUDOTEER follows a strict layered architecture to ensure isolation and scalability.

```mermaid
architecture-beta
	group workbench(logos:electron)[Workbench Layer]
	service desktop(logos:electron)[SUDOTEER Desktop] in workbench
	service voice(logos:livekit)[LiveKit Voice] in workbench

	group platform(logos:python)[Platform Layer]
	service agency(logos:python)[Agent Agency] in platform
	service dspy(logos:python)[DSPy Engine] in platform
	service bus(logos:python)[Event Bus] in platform

	group base(logos:database)[Base Layer]
	service memory(logos:database)[Hybrid Memory] in base
	service bridge(logos:arduino)[PLC Bridge] in base
	service data(logos:supabase)[Persistence] in base

	desktop:B -- T:agency
	voice:B -- T:agency
	agency:L -- R:dspy
	agency:R -- L:bus
	agency:B -- T:memory
	agency:B -- T:bridge
	memory:B -- T:data
```

---

## 📡 Service Component Definition

| Tier | Component | Responsibility |
| :--- | :--- | :--- |
| **Workbench** | `UI Renderer` | Glassmorphism-based UI, Workflow Visualizer, Digital Twin dash. |
| **Workbench** | `LiveKit Voice` | Real-time voice interaction and agent dialogue. |
| **Platform** | `Agency Middleware` | IPC Management, WebSockets, Command routing to agents. |
| **Platform** | `DSPy Engine` | Intelligent routing and memory splitting optimization. |
| **Platform** | `Orchestrator` | Managing the lifecycle of the 5-Agent team. |
| **Base** | `Hybrid Memory` | 3-Layer router: Semantic (Chroma), Relational (Neo4j), Persistent (Supabase). |
| **Base** | `PLC Bridge` | Industrial protocol translation (MQTT/Modbus/OPC UA). |

---

## 🔄 Data Movement Patterns

### 1. The Command Flow (Top-Down)
1. **Human** interacts with Electron UI or Voice.
2. **Bridge** forwards command to **Web Server** via WebSocket.
3. **Command Server** dispatches to **Orchestrator**.
4. **Architect Agent** decomposes the goal into tasks.
5. **Specialist Agents** (Climate/Coder) execute tasks via tools.

### 2. The Memory Flow (Hybrid)
1. Agent generates a **Thought** or **Fact**.
2. **Memory Manager** receives the observation.
3. **DSPy Splitter** extracts structured relations.
4. Facts go to **Neo4j** (as Nodes/Edges).
5. Narrative goes to **ChromaDB** (as Embeddings).
6. Sync task pushes to **Supabase** for cross-session persistence.

---

## 🛠 Tech Stack (v11.1.0+)
- **Frontend**: Electron, Javascript (Vanilla ES6+), CSS3 (Glassmorphism).
- **Backend**: Python 3.10+, FastAPI, PCSE (Crop Science).
- **Agents**: DSPy, OpenAI/Local LLM (LM Studio/Ollama).
- **Storage**: ChromaDB, Neo4j, Supabase.
- **Communication**: WebSockets, WebRTC (LiveKit).
- **Diagrams**: Mermaid.js v11.1.0+ (Architecture-beta).
