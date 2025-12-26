import asyncio
import logging
import sys
import json
from backend.core.boot import SudoBootstrapper
from backend.core.command_server import CommandServer
from backend.core.orchestrator import orchestrator
from backend.core.industrial_bridge import industrial_bridge
from backend.core.ui_bridge import ui_bridge
from backend.core.factory import agent_factory
from backend.sandbox.simulations.greenhouse import greenhouse_sim

async def main():
	logger.info("🎬 Launching _SUDOTEER Agency Engine...")

	# 1. Boot Subsystems
	SudoBootstrapper.initialize_subsystems()
	await SudoBootstrapper.connect_industrial_io()

	# 2. Register Roles & Spawn Initial Agency
	SudoBootstrapper.register_agency_roles()
	await SudoBootstrapper.spawn_baseline_agents()

	# 3. Start Simulation & Command Server
	asyncio.create_task(run_simulation_loop())

	cmd_server = CommandServer(agent_factory)
	cmd_server.start()

	# 4. Handle UI Command Line Tasks (If any)
	if len(sys.argv) > 1:
		await handle_argv_task(sys.argv[1])
	else:
		logger.info("Agency running in Daemon mode. Listening for UI commands...")
		while True:
			await asyncio.sleep(1)

async def handle_argv_task(raw_data: str):
	"""Handle one-off tasks passed via command line."""
	try:
		task_data = json.loads(raw_data)
		goal = task_data.get("command", "Audit active sensors")
		logger.info(f"Received CLI Goal: {goal}")
		result = await orchestrator.execute_validation_chain(goal)
		print(json.dumps({"status": "success", "result": result}))
	except Exception as e:
		logger.error(f"CLI Task Execution failed: {e}")
		print(json.dumps({"status": "error", "message": str(e)}))

async def run_simulation_loop():
	"""The background physics/biology calculation loop with real-time telemetry."""
	while True:
		# 1. Step the physics simulation
		greenhouse_sim.step(delta_time_sec=1.0)  # 1Hz update rate

		# 2. Synchronize bridge sensors with sim state
		industrial_bridge.sensors = greenhouse_sim.get_sensor_readings()

		# 3. Broadcast telemetry to UI
		ui_bridge.broadcast("GREENHOUSE_TELEMETRY", "greenhouse_sim",
			greenhouse_sim.get_telemetry_packet())

		# 4. Tick watchdog
		ui_bridge.tick()

		await asyncio.sleep(1.0)

if __name__ == "__main__":
	asyncio.run(main())
