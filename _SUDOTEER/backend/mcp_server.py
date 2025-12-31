"""
📡 _SUDOTEER HARDWARE MCP SERVER 📡
Exposes the Industrial Bridge and Sensory Engine as a standard MCP Server.
Allows any MCP-compatible client to control the Greenhouse.
"""
from mcp.server.fastmcp import FastMCP
import logging
import asyncio
import os
import sys

# Ensure backend is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

mcp = FastMCP("_SUDOTEER Hardware")

@mcp.tool()
async def get_greenhouse_telemetry() -> str:
    """Retrieve real-time sensor data (Temp, Humidity, pH, EC)."""
    from backend.core.hardware.sensory_engine import sensory_engine
    telemetry = sensory_engine.get_telemetry()
    return f"Live Telemetry: {telemetry}"

@mcp.tool()
async def control_pump(state: bool) -> str:
    """Turn the nutrient pump ON or OFF."""
    from backend.core.industrial_bridge import industrial_bridge
    # We use 'agent' source here to indicate automatic control
    success = await industrial_bridge.write_setpoint("pump", state)
    return "Action: Pump " + ("STARTED" if state else "STOPPED") + " | Status: " + ("Success" if success else "Denied/Failed")

@mcp.tool()
async def set_lights(intensity: int) -> str:
    """Set grow light intensity (0-100)."""
    from backend.core.industrial_bridge import industrial_bridge
    success = await industrial_bridge.write_setpoint("lights", intensity)
    return f"Action: Lights set to {intensity}% | Status: {'Success' if success else 'Failed'}"

if __name__ == "__main__":
    # FastMCP uses stdio by default when run as a script
    mcp.run()
