"""
🎬 _SUDOTEER AGENCY ENGINE 🎬
The primary entrypoint for the backend.
Orchestrates the boot sequence, starts the WebServer, and maintains the Simulation Loop.
"""
import asyncio
import logging
import sys
import json
import threading
from backend.core.boot import SudoBootstrapper
from backend.core.command_server import CommandServer
from backend.core.orchestrator import orchestrator
from backend.core.industrial_bridge import industrial_bridge
from backend.core.ui_bridge import ui_bridge
from backend.core.factory import agent_factory
from backend.sandbox.simulations.greenhouse import greenhouse_sim

logger = logging.getLogger("_SUDOTEER")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    logger.info("🎬 Launching _SUDOTEER Agency Engine...")

    # 1. Boot Subsystems (Async)
    # This now starts SudoteerEngine, SensoryEngine, and IndustrialBridge
    await SudoBootstrapper.initialize_subsystems()

    # 2. Register Roles & Spawn Initial Agency
    SudoBootstrapper.register_agency_roles()
    await SudoBootstrapper.spawn_baseline_agents()

    # 3. Start Simulation Loop
    asyncio.create_task(run_simulation_loop())

    # 4. Start WebServer in background thread
    from backend.webserver import start_webserver
    web_thread = threading.Thread(target=start_webserver, kwargs={"host": "127.0.0.1", "port": 8000}, daemon=True)
    web_thread.start()
    logger.info("✅ WebServer thread started on port 8000")

    # 5. Start Command Server
    cmd_server = CommandServer(agent_factory)
    cmd_server.start()

    # 6. Handle UI Command Line Tasks (If any)
    if len(sys.argv) > 1 and sys.argv[1].startswith('{'):
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
    """
    The background physics/biology calculation loop.
    This steps the Digital Twin state, which simulated hardware reads from.
    """
    logger.info("⌛ Simulation Loop: Started at 1Hz")
    while True:
        try:
            # 1. Step the physics simulation
            greenhouse_sim.step(delta_time_sec=1.0)  # 1Hz update rate

            # 2. Broadcast High-Level UI Telemetry
            # (In-depth telemetry is handled by IndustrialBridge/SensoryEngine)
            ui_bridge.broadcast("GREENHOUSE_TELEMETRY", "greenhouse_sim",
                greenhouse_sim.get_telemetry_packet())

            # 3. Tick UI heartbeat/watchdog
            ui_bridge.tick()
        except Exception as e:
            logger.error(f"Simulation Loop Error: {e}")

        await asyncio.sleep(1.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🎬 Agency shutting down...")
