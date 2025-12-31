"""
_SUDOTEER Modbus TCP Driver
Handles low-level communication with industrial PLCs.
Supports a Simulation Fallback to the Greenhouse Digital Twin.
"""
import logging
import asyncio
from typing import Any, Optional
from pymodbus.client import AsyncModbusTcpClient
from .plc_mapper import PLC_MAP, get_register
from ...sandbox.simulations.greenhouse import greenhouse_sim

logger = logging.getLogger("_SUDOTEER")

class ModbusDriver:
    def __init__(self, host: str = "127.0.0.1", port: int = 502):
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host, port=port)
        self.is_connected = False

    async def connect(self) -> bool:
        """Establish connection to the PLC."""
        try:
            self.is_connected = await self.client.connect()
            if self.is_connected:
                logger.info(f"Modbus: Connected to {self.host}:{self.port}")
            else:
                logger.warning(f"Modbus: Hardware offline. Using Simulation Fallback.")
            return self.is_connected
        except Exception as e:
            logger.error(f"Modbus Connection Error: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        self.client.close()
        self.is_connected = False
        logger.info("Modbus: Disconnected")

    async def read_sensor(self, key: str) -> Optional[float]:
        """Read a sensor value (Hardware or Sim)."""
        if self.is_connected:
            reg_info = PLC_MAP.get(key)
            if not reg_info: return None
            try:
                result = await self.client.read_holding_registers(reg_info["addr"], 1)
                if not result.isError():
                    raw_val = result.registers[0]
                    if reg_info["type"] == "float":
                        return raw_val / 100.0
                    return float(raw_val)
            except Exception as e:
                logger.error(f"Modbus Read Error ({key}): {e}")

        # Simulation Fallback
        sim_data = greenhouse_sim.get_sensor_readings()
        # Map PLC keys to Simulation state keys (e.g. 'temp_air' -> 'temperature')
        # This is a bit of a shim - ideally PLC_MAP would have sim_key
        mapping = {
            "temp_air": "temperature",
            "humidity_air": "humidity",
            "ph_nutrient": "ph_level",
            "ec_nutrient": "ec_level"
        }
        sim_key = mapping.get(key, key)
        return sim_data.get(sim_key)

    async def write_actuator(self, key: str, value: Any) -> bool:
        """Write an actuator state (Hardware or Sim)."""
        if self.is_connected:
            reg_info = PLC_MAP.get(key)
            if not reg_info: return False
            try:
                write_val = int(value) if reg_info["type"] == "bool" else int(value * 100)
                result = await self.client.write_register(reg_info["addr"], write_val)
                return not result.isError()
            except Exception as e:
                logger.error(f"Modbus Write Error ({key}): {e}")

        # Simulation Fallback
        return greenhouse_sim.set_actuator(key, value, source="agent")

# Global Instance
modbus_driver = ModbusDriver()
