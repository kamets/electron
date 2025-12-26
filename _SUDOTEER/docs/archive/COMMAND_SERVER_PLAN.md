# Command Server & Dynamic Agent Factory - Implementation Plan

**Status**: 🔲 **Planned** (Not Yet Implemented)
**Priority**: **High** (Phase 6 - Post-Visualization)
**Complexity**: ⭐⭐⭐⭐ (4/5)

## Overview

This feature enables the Electron frontend to **dynamically spawn and kill agents at runtime** by sending JSON commands over stdin. This transforms _SUDOTEER from a static 5-agent system into a **scalable multi-agent platform**.

## Architecture

```
[Electron UI]
    → IPC Command →
[Main Process]
    → stdin.write() →
[Python CommandServer Thread]
    → AgentFactory.spawn_agent() →
[New Agent Instance on A2A Bus]
    → UIBridge.broadcast("AGENT_SPAWNED") →
[Electron UI updates]
```

## Components to Build

### 1. Python: CommandServer (backend/core/command_server.py)

**Purpose**: Listen to stdin for commands from Electron
**Thread**: Daemon thread (non-blocking)
**Input Format**: Single-line JSON strings

```python
import sys
import json
import threading
import logging

class CommandServer:
    def __init__(self, factory_instance):
        self.factory = factory_instance
        self.logger = logging.getLogger("CommandServer")
        self.running = True

    def start(self):
        """Starts the listener thread."""
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()

    def _listen_loop(self):
        """
        Continuously reads lines from stdin.
        Electron sends commands as single-line JSON strings.
        """
        while self.running:
            try:
                # Blocking read - waits for input from Electron
                line = sys.stdin.readline()
                if not line:
                    break # End of stream

                self._process_command(line.strip())
            except Exception as e:
                self.logger.error(f"Input error: {e}")

    def _process_command(self, raw_json):
        if not raw_json: return

        try:
            cmd = json.loads(raw_json)
            command_type = cmd.get("command")
            payload = cmd.get("payload", {})

            # ROUTING LOGIC
            if command_type == "SPAWN_AGENT":
                self.factory.spawn_agent(
                    role=payload.get("role"),
                    name=payload.get("name"),
                    capabilities=payload.get("capabilities", [])
                )

            elif command_type == "KILL_AGENT":
                self.factory.kill_agent(payload.get("name"))

            elif command_type == "START_MISSION":
                # Future: Trigger orchestrator with payload
                pass

        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON received: {raw_json}")
```

### 2. Python: Enhanced AgentFactory (backend/core/factory.py)

**Current State**: Static factory (spawns agents at startup)
**Enhancement Needed**: Add dynamic spawn/kill methods

**New Methods:**
```python
def spawn_agent(self, role: str, name: str, capabilities: list):
    """
    Dynamic Instantiation Logic
    """
    if name in self.active_agents:
        ui_bridge.broadcast("ERROR", "system", {"msg": f"Agent {name} already exists"})
        return

    agent_class = self.blueprints.get(role.lower())

    if not agent_class:
        ui_bridge.broadcast("ERROR", "system", {"msg": f"Unknown role: {role}"})
        return

    try:
        # 1. Instantiate
        new_agent = agent_class(agent_id=name, role=role)

        # 2. Register on A2A bus
        bus.register_agent(name, new_agent, capabilities)

        # 3. Track in factory
        self.active_agents[name] = new_agent

        # 4. Notify UI
        ui_bridge.broadcast("AGENT_SPAWNED", "system", {
            "name": name,
            "role": role,
            "status": "ready",
            "capabilities": capabilities
        })

        logger.info(f"✅ Dynamically spawned: {name} ({role})")

    except Exception as e:
        ui_bridge.broadcast("ERROR", "system", {"msg": f"Failed to spawn {name}: {str(e)}"})

def kill_agent(self, name: str):
    if name in self.active_agents:
        agent = self.active_agents.pop(name)

        # Graceful shutdown if agent has cleanup method
        if hasattr(agent, 'shutdown'):
            agent.shutdown()

        ui_bridge.broadcast("AGENT_REMOVED", "system", {"name": name})
        logger.info(f"🔻 Removed agent: {name}")
```

**Blueprint Registry:**
```python
self.blueprints = {
    "architect": ArchitectAgent,
    "coder": CoderAgent,
    "tester": TesterAgent,
    "documenter": DocumenterAgent,
    "validator": ValidatorAgent,
    "seeker": SeekerAgent,
    # Future:
    # "greenhouse": GreenhouseAgent,
    # "industrial": IndustrialControlAgent
}
```

### 3. Frontend: AgentControls Component

**File**: `frontend/views/agent-controls.js`

```javascript
class AgentControls {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
    }

    render() {
        this.container.innerHTML = `
            <div class="agent-factory-panel glass-card">
                <h3>Agent Factory 🏭</h3>

                <div class="spawn-controls">
                    <select id="agent-role">
                        <option value="architect">Architect</option>
                        <option value="coder">Coder</option>
                        <option value="tester">Tester</option>
                        <option value="documenter">Documenter</option>
                        <option value="validator">Validator</option>
                    </select>

                    <input
                        id="agent-name"
                        type="text"
                        placeholder="Agent Name (e.g., coder_02)"
                    />

                    <button id="spawn-btn" class="btn-primary">
                        🚀 Spawn Agent
                    </button>
                </div>

                <div id="active-agents-list"></div>
            </div>
        `;

        // Event listeners
        document.getElementById('spawn-btn').addEventListener('click', () => {
            this.spawnAgent();
        });

        // Listen for spawn confirmations
        if (window.sudoteerAPI) {
            window.sudoteerAPI.onAgentUpdate((payload) => {
                if (payload.event === 'AGENT_SPAWNED') {
                    this.updateAgentList(payload.data);
                }
            });
        }
    }

    spawnAgent() {
        const role = document.getElementById('agent-role').value;
        const name = document.getElementById('agent-name').value;

        if (!name) {
            alert('Please enter an agent name');
            return;
        }

        // Send command to Python
        window.sudoteerAPI.sendCommand('SPAWN_AGENT', {
            role: role,
            name: name,
            capabilities: [role] // Default: role-based capabilities
        });

        console.log(`Spawning ${role} agent: ${name}`);
    }

    updateAgentList(agentData) {
        // Update the active agents list in UI
        console.log('Agent spawned:', agentData);
        // TODO: Render live agent roster
    }
}
```

### 4. Electron Main Process: stdin Writer

**File**: `electron/main.ts` (or main.js)

```typescript
// Listen for commands from the Frontend (via preload)
ipcMain.on('frontend-command', (event, { command, payload }) => {
    if (pythonProcess && pythonProcess.stdin) {
        // Construct the JSON packet
        const jsonCmd = JSON.stringify({ command, payload });

        // Write to Python's Standard Input + Newline (Critical!)
        pythonProcess.stdin.write(jsonCmd + '\n');

        console.log(`[Main → Python] ${command}:`, payload);
    } else {
        console.error('Python process not available for command:', command);
    }
});
```

### 5. Preload.js: sendCommand API

**Enhancement to existing preload.js:**

```javascript
contextBridge.exposeInMainWorld('sudoteerAPI', {
    // ... existing onAgentUpdate ...

    /**
     * OUTGOING: Send commands to the Agents (e.g., "SPAWN_AGENT")
     */
    sendCommand: (command: string, payload: any) => {
        if (typeof command === 'string') {
            ipcRenderer.send('frontend-command', { command, payload });
        }
    },

    // ... existing methods ...
});
```

## Integration into agency.py

```python
# backend/agency.py
from backend.core.command_server import CommandServer

async def main():
    # ... existing initialization ...

    # Start Command Server (listens for UI commands)
    cmd_server = CommandServer(agent_factory)
    cmd_server.start()
    logger.info("CommandServer started - UI can now spawn/kill agents dynamically")

    # ... rest of existing code ...
```

## Use Cases

### 1. **Parallel Processing**
Spawn 5 coder agents to work on different files simultaneously:
- `coder_01` → Refactors `api.py`
- `coder_02` → Writes tests for `utils.py`
- `coder_03` → Updates `README.md`

### 2. **Industrial Scaling**
Spawn multiple greenhouse controllers:
- `greenhouse_01` → Zone A (Tomatoes)
- `greenhouse_02` → Zone B (Lettuce)
- `greenhouse_03` → Zone C (Herbs)

### 3. **Load Balancing**
Monitor system load and spawn additional testers during CI/CD peaks.

## Testing Plan

1. **Unit Test**: CommandServer JSON parsing
2. **Integration Test**: Spawn → Register → Execute task
3. **UI Test**: Click spawn button → See agent appear in roster
4. **Stress Test**: Spawn 10 agents simultaneously
5. **Cleanup Test**: Kill agent → Verify graceful shutdown

## Benefits

- ✅ **Dynamic Scaling**: Add agents on-demand
- ✅ **Hot-Reload**: Update agent code without restarting system
- ✅ **Fault Isolation**: Kill misbehaving agents without crashing app
- ✅ **Industrial Ready**: Scale to hundreds of specialized agents
- ✅ **User Control**: Non-technical users can spawn agents via UI

## Dependencies

- ✅ UIBridge (already implemented)
- ✅ AgentFactory (exists, needs enhancement)
- ✅ A2A Bus (exists)
- ✅ Preload.js security layer (exists)
- 🔲 CommandServer (new)
- 🔲 Agent Controls UI (new)

## Timeline Estimate

- **CommandServer**: 2 hours
- **Factory Enhancement**: 1 hour
- **Frontend Controls**: 2 hours
- **Testing & Integration**: 2 hours
- **Total**: ~7 hours

---

**Status**: Ready for implementation after current visualization phase completes
**Blocker**: None
**Risk**: Low (well-defined architecture)
