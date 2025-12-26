# _SUDOTEER - API & Message Reference 📡

This document defines the communication protocols used between Agents, the Orchestrator, and the Frontend.

---

## 🚌 A2A (Agent-to-Agent) Bus Protocol

All agents communicate using the `A2AMessage` format.

### Message Structure:
```json
{
  "message_id": "uuid-v4",
  "sender": "architect_01",
  "recipient": "coder_01",
  "type": "REQUEST",
  "content": {
    "action": "GENERATE_CODE",
    "payload": {
      "language": "python",
      "task": "Write a CSV parser"
    }
  },
  "timestamp": "2025-12-23T18:00:00Z"
}
```

### Common Actions:
| Action | Payload Keys | Description |
|--------|--------------|-------------|
| `GENERATE_CODE` | `language`, `task`, `standards` | Request code from Coder Agent |
| `RUN_TESTS` | `code_path`, `framework` | Request validation from Tester Agent |
| `AUDIT_SECURITY` | `source_dir` | Request scan from Validator Agent |
| `SPAWN_AGENT` | `role`, `name`, `capabilities` | Command to Factory to create new agent |
| `START_PUMP` | `duration` | Command to GreenhouseAgent |

---

## 🌉 UI Integration Protocol (::SUDO::)

Real-time telemetry and status updates are streamed over stdout with a standard delimiter.

### 1. Heartbeat (`SYSTEM_HEARTBEAT`)
Sent every 2 seconds by `ui_bridge.py`.
```json
::SUDO::{"type": "IPC_EVENT", "event": "SYSTEM_HEARTBEAT", "agent_id": "system", "data": {"status": "alive", "uptime": 120.5}}
```

### 2. Agent Status (`AGENT_ACTIVE` / `AGENT_SUCCESS`)
```json
::SUDO::{"type": "IPC_EVENT", "event": "AGENT_ACTIVE", "agent_id": "coder_01", "data": {"task": "Refactoring API"}}
```

### 3. Telemetry (`GREENHOUSE_TELEMETRY`)
```json
::SUDO::{"type": "IPC_EVENT", "event": "GREENHOUSE_TELEMETRY", "agent_id": "greenhouse_sim", "data": {"temperature": 24.5, "humidity": 60, "pump_status": true}}
```

---

## ⌨️ Command Inbound (stdin)

The Frontend sends commands to the Backend as single-line JSON strings.

### 1. Execute Goal
```json
{"command": "EXECUTE_GOAL", "payload": {"goal": "Optimize greenhouse settings"}}
```

### 2. Actuator Control
```json
{"command": "AGENT_MSG", "payload": {"target": "greenhouse_main", "action": "START_PUMP"}}
```

### 3. Management
```json
{"command": "SPAWN_AGENT", "payload": {"role": "Tester", "name": "tester_secondary"}}
```

---

## 🗄️ Memory Schema (ChromaDB Metadata)

When querying the Vector DB via Vex, metadata follows this schema:
*   `agent_id`: Source agent of the memory.
*   `memory_type`: `observation`, `thought`, or `action`.
*   `timestamp`: ISO format.
*   `original_data`: Snippet of the raw input.

---
