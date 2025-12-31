"""
📡 _SUDOTEER SENSORY ENGINE 📡
The high-frequency data nervous system.
Handles 10Hz+ polling, edge-filtering, and Latent Variable Inference.
"""
import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from .modbus_driver import modbus_driver
from ..bus import bus

logger = logging.getLogger("_SUDOTEER")

class SensoryEngine:
    """
    High-frequency sensory processor.
    Calculates Latent Variables (VPD, Nutrient Density) and performs edge filtering.
    """
    def __init__(self, polling_rate: float = 0.1): # 10Hz Default
        self.polling_rate = polling_rate
        self.is_running = False
        self.raw_buffer: Dict[str, List[float]] = {}
        self.buffer_size = 100  # Keep last 10 seconds of 10Hz data
        self.latent_states: Dict[str, float] = {}

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._sampling_loop())
        logger.info(f"SensoryEngine: Started sampling at {1/self.polling_rate}Hz")

    async def stop(self):
        self.is_running = False
        logger.info("SensoryEngine: Stopped")

    async def _sampling_loop(self):
        """Main 10Hz acquisition and inference loop."""
        while self.is_running:
            try:
                start_time = asyncio.get_event_loop().time()

                # 1. Multi-Sensor Acquisition (Parallel reads for speed)
                sensors = ["temp_air", "humidity_air", "temp_root", "ec_nutrient", "ph_nutrient"]
                tasks = [modbus_driver.read_sensor(s) for s in sensors]
                results = await asyncio.gather(*tasks)

                sensor_data = dict(zip(sensors, results))

                # 2. Update Frequency Buffers
                for s, val in sensor_data.items():
                    if val is not None:
                        if s not in self.raw_buffer: self.raw_buffer[s] = []
                        self.raw_buffer[s].append(val)
                        if len(self.raw_buffer[s]) > self.buffer_size:
                            self.raw_buffer[s].pop(0)

                # 3. EDGE INFERENCE: Latent Variable Calculation (Genius Tier)
                await self._perform_inference(sensor_data)

                # 4. Publish Normalized Telemetry to A2A Bus
                await bus.publish("telemetry/high_freq", {
                    "raw": sensor_data,
                    "latent": self.latent_states,
                    "timestamp": datetime.now().isoformat()
                })

                # Precise Timing
                elapsed = asyncio.get_event_loop().time() - start_time
                await asyncio.sleep(max(0, self.polling_rate - elapsed))

            except Exception as e:
                logger.error(f"Sensory Loop Error: {e}")
                await asyncio.sleep(1)

    async def _perform_inference(self, data: Dict[str, Optional[float]]):
        """
        Calculate Latent Variables (States that aren't directly measured).
        Example: VPD = f(Temp, Humidity)
        """
        try:
            # 1. Vapor Pressure Deficit (VPD)
            temp = data.get("temp_air")
            hum = data.get("humidity_air")
            if temp is not None and hum is not None:
                # Simple VPD calculation
                svp = 0.61078 * np.exp(17.27 * temp / (temp + 237.3)) # Saturation Vapor Pressure
                avg = svp * (hum / 100.0) # Actual Vapor Pressure
                self.latent_states["vpd"] = svp - avg

            # 2. Signal Cleanliness (Variance as an 'Health' indicator)
            for s in self.raw_buffer:
                if len(self.raw_buffer[s]) > 10:
                    self.latent_states[f"{s}_noise"] = float(np.std(self.raw_buffer[s]))

        except Exception as e:
            logger.error(f"Inference Error: {e}")

# Global instance
sensory_engine = SensoryEngine()
