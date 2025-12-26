# _SUDOTEER - Troubleshooting Guide 🔍

Common issues and their resolutions for the **_SUDOTEER** Agency and Industrial Bridge.

---

## 🛑 Backend Issues

### 1. "Agent initialization failed: DSPy not configured"
*   **Symptom**: Common during startup. Logs show agents can't reach the LM.
*   **Cause**: LM Studio is not running or API keys are missing.
*   **Fix**:
    1.  Ensure **LM Studio** is running on port 1234 with a model loaded.
    2.  Check `.env` for `GEMINI_API_KEY` or `OPENAI_API_KEY`.
    3.  Run `test_dspy_agents.py` to verify individual connectivity.

### 2. "System Heartbeat: STALLED" (Yellow LED)
*   **Symptom**: Health monitor turns yellow.
*   **Cause**: The Python main thread is blocked by a long-running synchronous operation or a frozen agent logic loop.
*   **Fix**:
    1.  Check the terminal for infinite loop logs.
    2.  If it recovers after a few seconds, it was likely just a large LLM inference pass.
    3.  Ensure agents use `asyncio.sleep()` in loops.

### 3. "PLC Connection Failed"
*   **Symptom**: No telemetry, `GreenhouseAgent` logs errors.
*   **Cause**: Incorrect COM port or RS485 adapter disconnected.
*   **Fix**:
    1.  Verify the COM port in Device Manager.
    2.  Update `COM_PORT` in `.env`.
    3.  Toggle the "Simulation Mode" if hardware is not physically present.

---

## 🎨 UI & Frontend Issues

### 1. "White Screen" on Launch
*   **Symptom**: Electron window opens but stays blank.
*   **Cause**: JavaScript error in the renderer process (likely during initialization).
*   **Fix**:
    1.  Press `Ctrl+Shift+I` to open DevTools.
    2.  Check the **Console** tab for errors.
    3.  Common culprit: Path mismatch in `index.html` script tags.

### 2. "Workflow not animating"
*   **Symptom**: Agents don't light up even though the goal is running.
*   **Cause**: `ui_bridge` is not broadcasting properly or the `SUDO` delimiter is being stripped.
*   **Fix**:
    1.  Check the Python terminal to see if `::SUDO::` packets are being printed.
    2.  Verify `frontend/views/workflow.js` is loaded correctly.

---

## 🧠 Memory & DB Issues

### 1. "Vex: Connection Refused"
*   **Symptom**: Cannot connect to Vector DB sidebar.
*   **Cause**: ChromaDB server is not running on port 8000.
*   **Fix**:
    ```powershell
    .\.venv\Scripts\chroma.exe run --path .\backend\data\vector_db --port 8000
    ```

### 2. "Supabase Key Missing"
*   **Symptom**: Persistent memory fails to save.
*   **Cause**: `.env` has placeholder values.
*   **Fix**: Get your Project URL and Service Role Key from the Supabase Dashboard and update `.env`.

---

## 🛠️ Diagnostics
To run a full system check, execute:
```powershell
.\.venv\Scripts\python.exe test_agency_init.py
```
This will verify agents, bus registration, memory access, and industrial bridge simulation in one sweep.
