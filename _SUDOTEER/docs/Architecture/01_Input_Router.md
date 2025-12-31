# 🔀 _SUDOTEER: THE HYBRID INPUT ROUTER
**Tier**: Platform Architecture
**Status**: Implemented / Live

## 1. Concept: The Input Funnel
The Electron frontend acts as a "Traffic Controller," splitting traffic between the local LLM and the direct Hardware connection to ensure safety and responsiveness.

```mermaid
graph TD
    %% Styling
    classDef ui fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef logic fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef hardware fill:#424242,stroke:#000,stroke-width:2px,color:#fff;

    User((User Input)) -->|Text or Click| InputHandler[Electron Input Handler]:::ui

    subgraph "Frontend Router Logic"
        InputHandler --> CheckType{Input Type?}:::logic
        CheckType -- "Slash Command (/)" --> RegexParser[Regex Parser]:::logic
        CheckType -- "UI Interaction (Slider/Btn)" --> Debounce[Debounce Logic]:::logic
        CheckType -- "Natural Language" --> LLM[LLM Context Window]:::logic
    end

    subgraph "Backend Execution"
        RegexParser -->|IPC: HARDWARE_ACTION| PythonBridge[Python Event Bus]:::backend
        Debounce -->|IPC: HARDWARE_ACTION| PythonBridge
        LLM -->|IPC: AGENT_PROMPT| AgentFactory[Agent Factory]:::backend
    end

    subgraph "Physical Layer"
        PythonBridge -->|Serial Write| PLC[Industrial PLC]:::hardware
        AgentFactory -->|Reasoning| PythonBridge
        PLC -->|Sensor Feedback| PythonBridge
    end
```

## 2. Slash Command Parser (Deterministic Path)
**Goal:** Bypass the LLM for safety-critical or zero-latency commands (e.g., Emergency Stop, specific pump toggles).

### Logic Flow
```mermaid
flowchart LR
    Start([User Types Input]) --> Match{Matches Regex?}

    Match -- Yes --> Extract[Extract Command & Args]
    Extract --> Sanitize[Sanitize Payload]
    Sanitize --> IPC[Send via IPC to Python]
    IPC --> Exec[Execute Hardware Function]

    Match -- No --> Agent[Send to LLM Agent]
    Agent --> Vector[Vectorize & Contextualize]
    Vector --> Reply[Generate AI Response]

    style Match fill:#ffccbc,stroke:#d84315
    style Exec fill:#c8e6c9,stroke:#2e7d32
```

### Pattern
`^\/(\w+)(?:\s+(.*))?$`

---

## 3. Virtual HMI (Debounced Control)
**Goal:** Enable "Analog" feel for digital controls without flooding the PLC serial buffer.

```mermaid
sequenceDiagram
    participant User
    participant UI as Electron UI (Optimistic)
    participant Timer as Debounce Timer
    participant Python as Python Backend
    participant PLC as PLC

    User->>UI: Click [+] (Value 50 -> 51)
    UI->>UI: Update Display to "51"
    UI->>Timer: Start 300ms Timer

    User->>UI: Click [+] (Value 51 -> 52)
    UI->>UI: Update Display to "52"
    UI->>Timer: Reset 300ms Timer

    Timer-->>UI: Timer Expired!
    UI->>Python: Send "set_speed(52)"
    Python->>PLC: Protocol Write
    PLC-->>Python: ACK
```
