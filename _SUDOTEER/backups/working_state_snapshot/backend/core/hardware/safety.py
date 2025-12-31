"""
Industrial Safety Watchdog
Prevents hardware damage from software errors or sensor failure.
"""
import logging
import time
from typing import Dict, Any

logger = logging.getLogger("_SUDOTEER")

class SafetyWatchdog:
    def __init__(self):
        self.safe_ranges = {
            "S02_TEMP": (10.0, 45.0),
            "S04_PH": (4.0, 9.0),
            "S03_HUM": (10.0, 95.0)
        }
        self.last_sensor_update = time.time()
        self.emergency_lock = False

    def validate_actuator_request(self, actuator_id: str, value: Any) -> bool:
        """Checks if a command is safe to execute."""
        if self.emergency_lock:
            logger.error("SAFETY: Emergency Lock active. Command REJECTED.")
            return False

        # Example: Prevent pH Up and pH Down from running simultaneously
        # (Conflict Resolution)
        return True

    def check_telemetry(self, sensors: Dict[str, Any]):
        """Sanity check on all incoming sensor data."""
        now = time.time()

        # 1. Timeout Check
        if now - self.last_sensor_update > 30.0:
            logger.critical("SAFETY: Sensor Data Outdated! Entering Safe State.")
            self.trigger_emergency_stop()

        # 2. Range Check
        for key, (min_v, max_v) in self.safe_ranges.items():
            val = sensors.get(key)
            if val is not None and (val < min_v or val > max_v):
                logger.critical(f"SAFETY: {key} OUT OF RANGE ({val}). SHUTTING DOWN.")
                self.trigger_emergency_stop()

        self.last_sensor_update = now

    def trigger_emergency_stop(self):
        self.emergency_lock = True
        logger.info("SAFETY: ALL ACTUATORS REJECTED. MANUAL RESET REQUIRED.")
        # In a real system, we'd send a hard Modbus broadcast to kill all relays here.

safety_watchdog = SafetyWatchdog()
