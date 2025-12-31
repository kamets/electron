"""
Voice Bridge Module
Connects the Electron HMI 'Voice Orbs' to the backend via WebSocket.
Follows SPECS.md requirements.
"""

import logging
from fastapi import WebSocket, WebSocketDisconnect
from backend.core.intent_router import intent_router
from backend.core.orchestrator import orchestrator

logger = logging.getLogger("_SUDOTEER")

class VoiceBridge:
    def __init__(self):
        self.active_connection: WebSocket = None
        self.state = "idle"  # idle, listening, processing

    async def connect(self, websocket: WebSocket):
        """Accepts the WS connection and stores reference."""
        await websocket.accept()
        self.active_connection = websocket
        logger.info("VoiceBridge: HMI Connected")
        await self.send_status("idle")

    async def disconnect(self):
        """Cleans up connection."""
        self.active_connection = None
        logger.info("VoiceBridge: HMI Disconnected")

    async def handle_audio_stream(self, websocket: WebSocket):
        """Main loop for handling incoming audio packets."""
        try:
            while True:
                # Receive message (Text control or Binary audio)
                message = await websocket.receive()

                if "text" in message:
                    await self._handle_control_message(message["text"])
                elif "bytes" in message:
                    await self._handle_audio_data(message["bytes"])

        except WebSocketDisconnect:
            await self.disconnect()
        except Exception as e:
            logger.error(f"VoiceBridge Error: {e}")
            await self.disconnect()

    async def _handle_control_message(self, text: str):
        """Process JSON control signals or raw voice text."""
        logger.info(f"Voice Command Received: {text}")

        # 1. Parse Intent
        analysis = intent_router.route(text)

        # 2. Update HMI Feedback State
        if analysis["intent"] != "UNKNOWN":
            await self.send_status("processing", {"intent": analysis["intent"]})

            # 3. Dispatch to Agency Orchestrator
            # This triggers the actual agents (Nutrient, Light, etc.)
            await orchestrator.execute_validation_chain(text)

            await self.send_status("idle", {"reply": f"Executing {analysis['intent']}"})
        else:
            await self.send_status("idle", {"reply": "I didn't understand that command."})

    async def _handle_audio_data(self, data: bytes):
        """Process raw PCM/WAV chunks."""
        size = len(data)
        # Week 1 TODO: buffer this for Whisper
        logger.debug(f"Voice Audio Chunk: {size} bits")

    async def send_status(self, status: str, payload: Dict[str, Any] = None):
        """Send state update to HMI to animate Orbs."""
        if not self.active_connection:
            return

        msg = {"status": status}
        if payload:
            msg.update(payload)

        await self.active_connection.send_json(msg)

# Global Instance
voice_bridge = VoiceBridge()
