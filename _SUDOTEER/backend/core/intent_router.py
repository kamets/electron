"""
Voice Transcriber & Intent Router
Translates audio data/text to actionable Agent Commands.
"""
import logging
import re
from typing import Dict, Any

logger = logging.getLogger("_SUDOTEER")

class IntentRouter:
    """Classifies text into industrial control intents."""

    PATTERNS = {
        "LIGHT_CONTROL": r"(light|lamp|lux|growlight)",
        "PUMP_CONTROL": r"(pump|water|nutrient|dosing|dose)",
        "CLIMATE_CONTROL": r"(temp|humidity|fan|air|climate)",
        "STATUS_QUERY": r"(status|check|how is|ready|health)",
        "EMERGENCY_STOP": r"(stop|halt|emergency|shutdown|abort)"
    }

    def route(self, text: str) -> Dict[str, Any]:
        text = text.lower()
        logger.info(f"Routing Intent for: '{text}'")

        for intent, pattern in self.PATTERNS.items():
            if re.search(pattern, text):
                return {
                    "intent": intent,
                    "target": self._extract_target(text, intent),
                    "action": self._extract_action(text),
                    "value": self._extract_value(text)
                }

        return {"intent": "UNKNOWN", "original_text": text}

    def _extract_action(self, text: str) -> str:
        if any(w in text for w in ["on", "start", "enable", "increase", "add"]): return "set_on"
        if any(w in text for w in ["off", "stop", "disable", "decrease", "remove"]): return "set_off"
        return "query"

    def _extract_target(self, text: str, intent: str) -> str:
        # Basic extraction logic
        if "water" in text: return "water_pump"
        if "ph" in text: return "ph_pump"
        if "light" in text: return "main_lights"
        return intent.lower()

    def _extract_value(self, text: str) -> float:
        # Simple regex for numbers
        match = re.search(r"(\d+)", text)
        return float(match.group(1)) if match else 0.0

intent_router = IntentRouter()
