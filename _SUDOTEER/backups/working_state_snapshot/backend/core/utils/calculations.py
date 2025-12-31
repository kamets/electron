"""
Horticultural Mathematics & Calculations
Includes VPD (Vapor Pressure Deficit) and specialized agro-metrics.
"""
import math
import logging

logger = logging.getLogger("_SUDOTEER")

def calculate_vpd(temp_c: float, humidity_pct: float) -> float:
    """
    Calculates Vapor Pressure Deficit (VPD) in kPa.
    Essential for determining plant transpiration rates.
    """
    # 1. Calculate Saturation Vapor Pressure (SVP)
    svp = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))

    # 2. Calculate Actual Vapor Pressure (AVP)
    avp = svp * (humidity_pct / 100)

    # 3. VPD is the difference
    vpd = svp - avp
    return round(vpd, 2)

def calculate_dli(ppfd: float, hours: float) -> float:
    """Calculates Daily Light Integral (DLI)."""
    return round((ppfd * hours * 3600) / 1_000_000, 2)
