"""
Standard PLC Register Mapping
Maps JSON keys to Modbus/Industrial Addresses.
"""

PLC_MAP = {
    # READS (Sensors)
    "S01_LUX": {"addr": 0, "type": "int", "unit": "lux"},
    "S02_TEMP": {"addr": 1, "type": "float", "unit": "C"},
    "S03_HUM": {"addr": 2, "type": "float", "unit": "%"},
    "S04_PH": {"addr": 3, "type": "float", "unit": "pH"},
    "S05_EC": {"addr": 4, "type": "float", "unit": "mS/cm"},

    # WRITES (Actuators)
    "A01_LIGHT_MAIN": {"addr": 100, "type": "bool"},
    "A02_PUMP_WATER": {"addr": 101, "type": "bool"},
    "A03_PUMP_PH_UP": {"addr": 102, "type": "bool"},
    "A04_PUMP_PH_DOWN": {"addr": 103, "type": "bool"},
    "A05_PUMP_NUTRI_A": {"addr": 104, "type": "bool"},
    "A06_PUMP_NUTRI_B": {"addr": 105, "type": "bool"},
}

def get_register(key: str) -> int:
    return PLC_MAP.get(key, {}).get("addr", -1)

def get_keys_by_type(reg_type: str):
    return [k for k, v in PLC_MAP.items() if v.get("type") == reg_type]
