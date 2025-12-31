# Voice Bridge Specification (Week 1 / Task 1)

## Role: Coder Agent V2
**Supervisor:** "The Angel"
**Objective**: Build a WebSocket bridge that connects the Electron Frontend "Voice Orbs" to the Python Backend.

## 1. Architecture Requirements
*   **Framework**: Match existing backend (Sanic/FastAPI).
*   **Location**: `backend/core/voice/bridge.py`
*   **Endpoint**: `ws://localhost:8000/ws/voice`

## 2. Functionality
1.  **Handshake**: Accept connection from Electron. Log "Voice Client Connected".
2.  **State Management**: Track if the user is "Speaking" or "Silent".
3.  **Audio Ingestion**: Accept binary/blob messages. (For V1, just log the byte size).
4.  **Feedback Loop**:
    *   When audio starts -> Send `{"status": "listening"}` (Frontend turns Orbs Orange).
    *   When audio ends -> Send `{"status": "processing"}` (Frontend Orbs Pulse).
    *   Reply -> Send `{"status": "idle", "reply": "Audio received"}` (Frontend Orbs Blue).

## 3. Integration Plan
The `bridge.py` must expose a `attach_voice_routes(app)` function that `webserver.py` can import and use.

## 4. "Code Style" Memory
*   Use `PascalCase` for Classes (`VoiceBridge`).
*   Use `snake_case` for methods.
*   Type hint EVERYTHING (`def connect(self, websocket: WebSocket) -> None:`).
*   Add docstrings summarizing the "Intent" of the function.

**Deliverable**: Validate that the HMI "Agent Interface" connects to this socket and logs are visible.
