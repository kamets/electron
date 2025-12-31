# 🏭 _SUDOTEER: AGENT FACTORY & PERMISSIONS
**Tier**: Platform Architecture
**Status**: Implemented (Core) / Scaling

## 1. Concept: The Tool Manifest
Before an agent is spawned, the Factory defines its "Reach." We treat hardware hooks as **Capabilities** granted via a Tool Registry.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Factory as Agent Factory
    participant Registry as Tool Registry
    participant Agent as New Agent (LLM)
    participant Guard as Permission Guard
    participant HW as Hardware Bus

    Note over User, Factory: Phase 1: Instantiation
    User->>Factory: Spawn "Gardener" Agent
    Factory->>Registry: Fetch Manifest for "Gardener"
    Registry-->>Factory: Returns Allowed Tools: [/pump, /status]

    Factory->>Agent: INIT(Context + Tool Definitions)
    Note right of Factory: Agent now knows tools exist

    Note over Agent, HW: Phase 2: Execution Request
    Agent->>Agent: Decides to water plants
    Agent->>Guard: Request Action: "/pump on 5s"

    Guard->>Guard: Check Policy (Auto-Approve or Ask User?)

    alt Policy = REQUIRE_APPROVAL
        Guard->>User: "Agent wants to run /pump. Allow?"
        User-->>Guard: Approve
    end

    Guard->>HW: EXECUTE: "/pump on 5s"
    HW-->>Agent: Result: "Success"
```

## 2. Permission Guard Logic
The `PermissionGuard` intercepts every agent tool use, preventing hallucinations from touching wires they shouldn't.

```mermaid
flowchart TD
    %% Styling
    classDef safe fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef danger fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;

    Start([Agent Emits Command]) --> Parse[Parse Command & Args]
    Parse --> CheckManifest{Is Command in<br>Agent Manifest?}:::decision

    CheckManifest -- No --> Deny1[DENY: Unauthorized Tool]:::danger
    CheckManifest -- Yes --> CheckParams{Are Args Safe?}:::decision

    CheckParams -- "Out of Range" --> Deny2[DENY: Parameter Limit]:::danger
    CheckParams -- Safe --> CheckMode{Safety Mode?}:::decision

    CheckMode -- "Autonomous" --> Execute[Execute Hardware Action]:::safe
    CheckMode -- "Human-in-Loop" --> AskUser[Prompt User UI]:::decision

    AskUser -- User Rejects --> Deny3[DENY: User Veto]:::danger
    AskUser -- User Approves --> Execute
```
