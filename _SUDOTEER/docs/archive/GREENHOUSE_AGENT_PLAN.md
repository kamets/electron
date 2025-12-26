# Industrial Bridge: GreenhouseAgent with Modbus/PLC Integration

**Status**: 🔲 **Planned** (Phase 7 - Post Core Features)
**Priority**: **Medium** (After CommandServer)
**Complexity**: ⭐⭐⭐⭐⭐ (5/5 - Hardware Integration)

## Overview

Transform _SUDOTEER from a pure software platform into an **Industrial IoT Controller** capable of managing physical greenhouse systems via Modbus/RS485 communication with PLCs (NAiS FP0, Renu HMI).

## Architecture: Digital Twin Pattern

```
[Physical PLC/Sensors]
    ↔ RS485/Modbus →
[GreenhouseAgent Digital Twin]
    ↔ A2A Bus →
[ArchitectAgent / UI]
```

**Key Principle**: The AI never touches hardware directly. All industrial control flows through the GreenhouseAgent's safety layer.

## Current State

### ✅ Already Implemented:
**File**: `backend/sandbox/simulations/greenhouse.py`

This is our **Simulated Digital Twin** - perfect for development/testing without physical hardware.

```python
class GreenhouseSim:
    def __init__(self):
        self.temp = 24.0
        self.ph = 6.8
        self.power_usage = 0.0
        self.waste_produced = 0.0
```

**Usage**: Currently runs in `agency.py` as the "God Process Loop"

## Phase 7: Real Hardware Integration

### 1. Dependencies

```bash
# Add to requirements.txt
uv add pymodbus pyserial
```

**Why These?**
- `pymodbus`: Industry-standard Python Modbus library
- `pyserial`: Cross-platform serial port communication

### 2. GreenhouseAgent Implementation

**File**: `backend/agents/industrial/greenhouse_agent.py`

```python
"""
_SUDOTEER Industrial Bridge: Greenhouse Controller
Manages physical greenhouse systems via Modbus/RS485 PLC communication.
Implements Digital Twin pattern with safety interlocks.
"""

import time
import logging
from typing import Dict, Any, Optional
from pymodbus.client import ModbusSerialClient
from backend.core.agent_base import SudoAgent
from backend.core.protocol import A2AMessage

logger = logging.getLogger("_SUDOTEER")

class GreenhouseAgent(SudoAgent):
    """
    Industrial Bridge Agent for greenhouse automation.
    Communicates with NAiS FP0 / Renu HMI PLCs via Modbus.

    Safety Features:
    - Hard limits on pH, temperature, pressure
    - Emergency shutdown on critical conditions
    - Rate limiting on actuator commands
    - Watchdog timer for sensor staleness
    """

    def __init__(
        self,
        agent_id: str = "greenhouse_01",
        role: str = "IndustrialBridge",
        port: str = '/dev/ttyUSB0',  # Linux/Mac
        # port: str = 'COM3',  # Windows
        baudrate: int = 9600,
        slave_id: int = 1
    ):
        super().__init__(agent_id, role)

        # PLC Connection Config (NAiS FP0 defaults)
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id

        # Modbus Client
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity='E',      # Even parity (common for industrial)
            stopbits=1,
            bytesize=8,
            timeout=1
        )

        # Digital Twin State
        self.state = {
            "temperature": 0.0,      # °C
            "humidity": 0.0,         # %
            "ph_level": 7.0,         # pH
            "water_pressure": 0.0,   # PSI
            "pump_status": False,
            "valve_a_open": False,
            "valve_b_open": False,
            "last_hardware_sync": None,
            "health": "unknown"      # unknown, healthy, degraded, critical
        }

        # Safety Limits (CRITICAL - AI cannot override)
        self.LIMITS = {
            "ph_min": 4.5,
            "ph_max": 8.5,
            "temp_min": 10.0,
            "temp_max": 40.0,
            "pressure_max": 80.0  # PSI
        }

        # Watchdog
        self.sensor_timeout = 30.0  # Seconds before sensor data considered stale

    async def setup(self):
        """Initialize PLC connection."""
        if self.client.connect():
            logger.info(f"✅ [{self.agent_id}] Connected to PLC at {self.port}")
            self.broadcast_to_ui("PLC_CONNECTED", {
                "port": self.port,
                "baudrate": self.baudrate
            })
        else:
            logger.error(f"❌ [{self.agent_id}] Failed to connect to PLC at {self.port}")
            self.broadcast_to_ui("PLC_ERROR", {
                "error": "Connection failed",
                "port": self.port
            })

    async def forward(self, *args, **kwargs):
        """
        Main control loop (DSPy entry point).
        Called by orchestrator or A2A messages.
        """
        # This agent primarily runs in background loop,
        # but can respond to specific queries
        return {"state": self.state, "health": self._evaluate_health()}

    async def handle_request(self, message: A2AMessage) -> Any:
        """
        Handle A2A commands from other agents or UI.

        Valid commands:
        - GET_STATE: Return current digital twin state
        - START_PUMP: Activate fertigation pump
        - STOP_PUMP: Deactivate pump
        - SET_VALVE: Open/close specific valve
        - EMERGENCY_STOP: Shut down all actuators
        """
        command = message.content.get("action")
        payload = message.content.get("payload", {})

        self.log_interaction(f"Received command: {command}", event_type="thought")

        if command == "GET_STATE":
            return {"state": self.state}

        elif command == "START_PUMP":
            return await self._start_pump()

        elif command == "STOP_PUMP":
            return await self._stop_pump()

        elif command == "SET_VALVE":
            valve = payload.get("valve")  # 'A' or 'B'
            open_valve = payload.get("open", False)
            return await self._set_valve(valve, open_valve)

        elif command == "EMERGENCY_STOP":
            return await self._emergency_shutdown()

        else:
            logger.warning(f"Unknown command: {command}")
            return {"status": "error", "msg": f"Unknown command: {command}"}

    async def run_background_loop(self):
        """
        Background polling loop (runs in separate thread/task).
        Syncs hardware state with digital twin every 2-5 seconds.
        """
        while self.running:
            try:
                # 1. SYNC: Read sensors from PLC
                await self._sync_with_hardware()

                # 2. SAFETY: Check for critical conditions
                await self._safety_check()

                # 3. BROADCAST: Send telemetry to UI
                self.broadcast_to_ui("TELEMETRY", self.state)

                # 4. TICK: Watchdog for stall detection
                ui_bridge.tick()

                # 5. SLEEP: Don't flood RS485 bus
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Background loop error: {e}")
                await asyncio.sleep(5)  # Back off on error

    async def _sync_with_hardware(self):
        """
        Read sensor registers from PLC via Modbus.

        Register Map (NAiS FP0 Example):
        - 100: Temperature (raw * 10 = °C)
        - 101: Humidity (raw = %)
        - 102: pH Level (raw * 100 = pH)
        - 103: Water Pressure (raw = PSI)
        - 104-105: Reserved
        """
        if not self.client.connected:
            logger.warning("PLC not connected, skipping sync")
            return

        try:
            # Read 6 holding registers starting at address 100
            rr = self.client.read_holding_registers(
                address=100,
                count=6,
                slave=self.slave_id
            )

            if rr.isError():
                logger.error(f"Modbus read error: {rr}")
                return

            # Parse raw register values
            raw_temp = rr.registers[0]
            raw_humidity = rr.registers[1]
            raw_ph = rr.registers[2]
            raw_pressure = rr.registers[3]

            # Convert to engineering units
            self.state["temperature"] = raw_temp / 10.0
            self.state["humidity"] = raw_humidity
            self.state["ph_level"] = raw_ph / 100.0
            self.state["water_pressure"] = raw_pressure
            self.state["last_hardware_sync"] = time.time()

            # Read coil status (actuators)
            rc = self.client.read_coils(address=0, count=3, slave=self.slave_id)
            if not rc.isError():
                self.state["pump_status"] = rc.bits[0]
                self.state["valve_a_open"] = rc.bits[1]
                self.state["valve_b_open"] = rc.bits[2]

        except Exception as e:
            logger.error(f"Modbus sync exception: {e}")
            self.state["health"] = "degraded"

    async def _safety_check(self):
        """
        CRITICAL: Safety interlock logic.
        AI cannot override these checks.
        """
        # Check sensor staleness
        if self.state["last_hardware_sync"]:
            age = time.time() - self.state["last_hardware_sync"]
            if age > self.sensor_timeout:
                logger.critical("⚠️  SENSOR TIMEOUT - Initiating emergency stop")
                await self._emergency_shutdown()
                return

        # Check pH limits
        ph = self.state["ph_level"]
        if ph < self.LIMITS["ph_min"] or ph > self.LIMITS["ph_max"]:
            logger.critical(f"⚠️  pH OUT OF RANGE: {ph} - Emergency stop")
            await self._emergency_shutdown()
            return

        # Check temperature limits
        temp = self.state["temperature"]
        if temp < self.LIMITS["temp_min"] or temp > self.LIMITS["temp_max"]:
            logger.critical(f"⚠️  TEMPERATURE CRITICAL: {temp}°C - Emergency stop")
            await self._emergency_shutdown()
            return

        # Check pressure
        if self.state["water_pressure"] > self.LIMITS["pressure_max"]:
            logger.critical("⚠️  OVERPRESSURE - Shutting valves")
            await self._set_valve('A', False)
            await self._set_valve('B', False)
            return

        # All checks passed
        self.state["health"] = "healthy"

    async def _start_pump(self) -> Dict[str, Any]:
        """Start fertigation pump (Coil 0)."""
        try:
            result = self.client.write_coil(
                address=0,
                value=True,
                slave=self.slave_id
            )

            if not result.isError():
                self.state["pump_status"] = True
                self.log_interaction("🚿 Fertigation pump STARTED", event_type="action")
                return {"status": "success", "action": "pump_started"}
            else:
                logger.error(f"Failed to start pump: {result}")
                return {"status": "error", "msg": "Modbus write failed"}

        except Exception as e:
            logger.error(f"Pump start exception: {e}")
            return {"status": "error", "msg": str(e)}

    async def _stop_pump(self) -> Dict[str, Any]:
        """Stop fertigation pump (Coil 0)."""
        try:
            result = self.client.write_coil(
                address=0,
                value=False,
                slave=self.slave_id
            )

            if not result.isError():
                self.state["pump_status"] = False
                self.log_interaction("🛑 Fertigation pump STOPPED", event_type="action")
                return {"status": "success", "action": "pump_stopped"}
            else:
                return {"status": "error", "msg": "Modbus write failed"}

        except Exception as e:
            return {"status": "error", "msg": str(e)}

    async def _set_valve(self, valve: str, open_valve: bool) -> Dict[str, Any]:
        """Control valve A or B (Coils 1, 2)."""
        valve_map = {'A': 1, 'B': 2}

        if valve not in valve_map:
            return {"status": "error", "msg": f"Invalid valve: {valve}"}

        try:
            address = valve_map[valve]
            result = self.client.write_coil(
                address=address,
                value=open_valve,
                slave=self.slave_id
            )

            if not result.isError():
                state_key = f"valve_{valve.lower()}_open"
                self.state[state_key] = open_valve
                action = "OPENED" if open_valve else "CLOSED"
                self.log_interaction(f"Valve {valve} {action}", event_type="action")
                return {"status": "success", "valve": valve, "open": open_valve}
            else:
                return {"status": "error", "msg": "Modbus write failed"}

        except Exception as e:
            return {"status": "error", "msg": str(e)}

    async def _emergency_shutdown(self) -> Dict[str, Any]:
        """
        CRITICAL: Emergency shutdown procedure.
        Closes all valves, stops all pumps.
        """
        logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")

        try:
            # Stop pump
            self.client.write_coil(0, False, slave=self.slave_id)
            # Close valve A
            self.client.write_coil(1, False, slave=self.slave_id)
            # Close valve B
            self.client.write_coil(2, False, slave=self.slave_id)

            self.state["pump_status"] = False
            self.state["valve_a_open"] = False
            self.state["valve_b_open"] = False
            self.state["health"] = "critical"

            self.broadcast_to_ui("EMERGENCY_STOP", {
                "reason": "Safety interlock triggered",
                "state": self.state
            })

            return {"status": "emergency_stop_complete"}

        except Exception as e:
            logger.critical(f"Emergency shutdown failed: {e}")
            return {"status": "error", "msg": str(e)}

    def _evaluate_health(self) -> str:
        """Evaluate overall system health."""
        if not self.state["last_hardware_sync"]:
            return "unknown"

        age = time.time() - self.state["last_hardware_sync"]
        if age > self.sensor_timeout:
            return "critical"

        # Check if values are within safe ranges
        ph = self.state["ph_level"]
        temp = self.state["temperature"]

        if (self.LIMITS["ph_min"] <= ph <= self.LIMITS["ph_max"] and
            self.LIMITS["temp_min"] <= temp <= self.LIMITS["temp_max"]):
            return "healthy"
        else:
            return "degraded"

    def broadcast_to_ui(self, event_type: str, data: Dict[str, Any]):
        """Convenience method to broadcast to UI bridge."""
        from backend.core.ui_bridge import ui_bridge
        ui_bridge.broadcast(event_type, self.agent_id, data)

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info(f"Shutting down {self.agent_id}")
        await self._stop_pump()  # Safety: ensure pump is off
        self.client.close()
```

### 3. Registration in Factory

**File**: `backend/core/factory.py`

```python
from backend.agents.industrial.greenhouse_agent import GreenhouseAgent

class AgentFactory:
    def __init__(self):
        # ... existing ...

        self.blueprints = {
            "architect": ArchitectAgent,
            "coder": CoderAgent,
            "tester": TesterAgent,
            "documenter": DocumenterAgent,
            "validator": ValidatorAgent,
            "seeker": SeekerAgent,
            "greenhouse": GreenhouseAgent  # <--- NEW
        }
```

### 4. UI Spawning with Hardware Config

**File**: `frontend/views/agent-controls.js` (enhancement)

```javascript
spawnGreenhouseAgent() {
    const port = document.getElementById('greenhouse-port').value || '/dev/ttyUSB0';
    const baudrate = parseInt(document.getElementById('greenhouse-baudrate').value) || 9600;

    window.sudoteerAPI.sendCommand('SPAWN_AGENT', {
        role: 'greenhouse',
        name: 'greenhouse_main',
        payload: {
            port: port,
            baudrate: baudrate,
            slave_id: 1
        }
    });
}
```

## Safety Architecture

### Why This is Safer Than Direct AI Control

1. **Abstraction Layer**: AI sends `{"action": "START_PUMP"}`, not raw Modbus commands
2. **Hard Limits**: pH/temp limits are hardcoded, AI cannot override
3. **Emergency Interlocks**: Automatic shutdown on critical conditions
4. **Sensor Watchdog**: Detects stale/failed sensors
5. **Rate Limiting**: Prevents actuator thrashing
6. **Simulation Mode**: Test without hardware

### Triple-Layer Safety

```
[Layer 1: Physical] PLC has hardware interlocks
    ↓
[Layer 2: GreenhouseAgent] Software safety checks
    ↓
[Layer 3: ArchitectAgent] High-level AI logic
```

## Testing Strategy

### Phase 1: Simulation (Current)
- Use existing `greenhouse_sim.py`
- No hardware required
- Safe for AI experimentation

### Phase 2: Hardware-in-Loop
- Connect real PLC
- Read-only mode (no writes)
- Verify sensor readings

### Phase 3: Controlled Actuation
- Enable pump/valve control
- Manual supervision
- Emergency stop button

### Phase 4: Autonomous Operation
- AI can send commands
- Safety interlocks active
- Remote monitoring

## Hardware Requirements

### Minimum:
- NAiS FP0 PLC or compatible Modbus RTU device
- USB-to-RS485 adapter
- Python 3.9+

### Recommended:
- Renu HMI for visualization
- UPS for power reliability
- Wireless monitoring (4G/WiFi)

## Integration Points

### With Existing Systems:
1. **A2A Bus**: GreenhouseAgent is just another agent
2. **UIBridge**: Telemetry streams to frontend
3. **WorkflowVisualizer**: Shows greenhouse status in real-time
4. **CommandServer**: UI can spawn multiple greenhouse zones

## Dependencies

```toml
# requirements.txt additions
pymodbus>=3.5.0  # Modbus protocol implementation
pyserial>=3.5    # Serial port communication
```

## Timeline Estimate

- **Core Agent**: 4 hours
- **Modbus Integration**: 3 hours
- **Safety Interlocks**: 2 hours
- **UI Controls**: 2 hours
- **Hardware Testing**: 4 hours (on-site)
- **Total**: ~15 hours

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Hardware failure | Simulation mode fallback |
| Modbus timeout | Watchdog timer + alerts |
| Safety bypass attempt | Hard-coded limits in agent |
| Power loss | UPS + graceful shutdown |
| AI hallucination | Command validation layer |

## Future Enhancements

- [ ] Multi-zone support (greenhouse_01, greenhouse_02...)
- [ ] Predictive maintenance (sensor drift detection)
- [ ] Machine learning for optimal setpoints
- [ ] Cloud data logging (Supabase integration)
- [ ] Mobile alerts (Twilio/SMS)

---

**Status**: 🔲 **Ready for Implementation** (After Phase 6)
**Blocker**: CommandServer must be implemented first
**Hardware**: NAiS FP0 PLC required for testing

*_SUDOTEER Industrial Integration Team*
