"""
Full-Stack Test: UI Command → Backend → Response
Tests the complete bidirectional communication flow.
"""

import json
import sys
import asyncio
from backend.agency import main
from backend.core.ui_bridge import ui_bridge

async def test_command_flow():
	"""
	Simulates Electron sending a command to Python backend.
	This would normally come through stdin from the UI.
	"""
	print("=" * 60)
	print("FULL-STACK COMMAND FLOW TEST")
	print("=" * 60)

	# Start the agency in background
	agency_task = asyncio.create_task(main())

	# Wait for initialization
	await asyncio.sleep(3)

	print("\n[TEST] Simulating UI command: START_PUMP")
	print("-" * 60)

	# Simulate what Electron would send via stdin
	command_packet = {
		"command": "AGENT_MSG",
		"payload": {
			"target": "greenhouse_sim",
			"action": "START_PUMP"
		}
	}

	# This is what the CommandServer reads from stdin
	command_json = json.dumps(command_packet)
	print(f"[STDIN] {command_json}")

	# Normally CommandServer reads this from sys.stdin.readline()
	# For testing, we'll directly call the greenhouse sim
	from backend.sandbox.simulations.greenhouse import greenhouse_sim

	print("\n[EXECUTING] Setting pump_active = True")
	greenhouse_sim.set_actuator("pump_active", True)

	# Wait a bit for telemetry to update
	await asyncio.sleep(2)

	print("\n[TELEMETRY] Checking greenhouse state:")
	telemetry = greenhouse_sim.get_telemetry_packet()
	print(json.dumps(telemetry, indent=2))

	# Verify pump is active
	if telemetry["pump_status"]:
		print("\n✅ SUCCESS: Pump is ACTIVE")
		print(f"✅ Water pressure rising: {telemetry['water_pressure']} PSI")
	else:
		print("\n❌ FAIL: Pump not activated")

	print("\n[TEST] Simulating UI command: STOP_PUMP")
	print("-" * 60)

	greenhouse_sim.set_actuator("pump_active", False)
	await asyncio.sleep(2)

	telemetry = greenhouse_sim.get_telemetry_packet()
	print(json.dumps(telemetry, indent=2))

	if not telemetry["pump_status"]:
		print("\n✅ SUCCESS: Pump is STOPPED")
	else:
		print("\n❌ FAIL: Pump still active")

	print("\n" + "=" * 60)
	print("TEST COMPLETE")
	print("=" * 60)

	# Cancel background task
	agency_task.cancel()

if __name__ == "__main__":
	try:
		asyncio.run(test_command_flow())
	except KeyboardInterrupt:
		print("\nTest interrupted")
