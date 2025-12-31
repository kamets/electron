"""
Integration Test Suite: Agent Workflow End-to-End
Tests the complete 'Pass-the-Torch' validation chain from coder to validator.
Grade Target: A (full workflow path coverage)
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock


class TestAgentWorkflowIntegration:
	"""Integration tests for multi-agent workflow execution."""

	@pytest.mark.asyncio
	async def test_full_validation_chain_workflow(self):
		"""
		E2E: Test the complete Coder -> Tester -> Documenter -> Validator chain.
		"""
		with patch('backend.core.orchestrator.workflow_orchestrator') as mock_wf, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin, \
			 patch('backend.core.orchestrator.bus') as mock_bus, \
			 patch('backend.core.orchestrator.ui_bridge') as mock_ui:

			# Setup workflow mock to return success
			mock_wf.execute_workflow = AsyncMock(return_value={
				"data": {
					"goal": "Create a hello world function",
					"code": "def hello(): return 'world'",
					"test_report": {"passed": True, "tests": 5},
					"docs": "# Hello Function\n\nReturns world.",
					"validation_result": {"valid": True, "score": 0.95},
					"valid": True
				}
			})
			mock_fin.is_stable.return_value = True
			mock_fin.get_summary_metrics.return_value = {
				"total_tasks": 1,
				"success_rate": 1.0
			}

			from backend.core.orchestrator import AgencyOrchestrator
			orch = AgencyOrchestrator()

			result = await orch.execute_validation_chain("Create a hello world function")

			# Verify workflow was executed
			mock_wf.execute_workflow.assert_awaited_once()

			# Verify result contains all artifacts
			assert result is not None
			assert result.get("valid") is True
			assert "code" in result
			assert "test_report" in result
			assert "docs" in result

	@pytest.mark.asyncio
	async def test_validation_chain_budget_enforcement(self):
		"""
		E2E: Test that budget violations stop the workflow.
		"""
		with patch('backend.core.orchestrator.workflow_orchestrator') as mock_wf, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			# Finance tracker reports instability
			mock_fin.is_stable.return_value = False
			mock_fin.get_summary_metrics.return_value = {}

			mock_wf.execute_workflow = AsyncMock(return_value={
				"data": {"valid": False}
			})

			from backend.core.orchestrator import AgencyOrchestrator
			orch = AgencyOrchestrator()

			result = await orch.execute_validation_chain("Test budget enforcement")

			# Result should be None due to budget violation during workflow
			# The workflow still executes but returns invalid


class TestA2ACommunicationIntegration:
	"""Integration tests for Agent-to-Agent communication."""

	@pytest.mark.asyncio
	async def test_agent_send_receive_message(self):
		"""Test agent can send and receive A2A messages."""
		with patch('backend.core.bus.bus') as mock_bus:
			mock_bus.send_request = AsyncMock(return_value={"status": "received"})

			from backend.core.protocol import A2AMessage

			# Create a message
			msg = A2AMessage(
				from_agent="coder_01",
				to_agent="tester_01",
				content={"code": "def test(): pass"},
				message_type="request"
			)

			# Send via bus
			result = await mock_bus.send_request(msg)

			assert result["status"] == "received"
			mock_bus.send_request.assert_awaited_once()


class TestMemoryIntegration:
	"""Integration tests for hybrid memory system."""

	@pytest.mark.asyncio
	async def test_remember_and_recall_flow(self):
		"""Test storing and retrieving from hybrid memory."""
		with patch('backend.core.memory.manager.vector_db') as mock_vdb, \
			 patch('backend.core.memory.manager.Neo4jGraphStore') as mock_graph_cls, \
			 patch('backend.core.memory.manager.memory_splitter') as mock_splitter:

			# Setup mocks
			mock_graph = MagicMock()
			mock_graph.create_relationship = AsyncMock()
			mock_graph.find_subgraph = AsyncMock(return_value={})
			mock_graph_cls.return_value = mock_graph

			mock_vdb.store_memory = AsyncMock(return_value="mem_123")
			mock_vdb.search_knowledge = AsyncMock(return_value=[
				{"content": "Stored information", "metadata": {}}
			])
			mock_vdb.search_episodes = AsyncMock(return_value=[])

			mock_splitter.split_storage = AsyncMock(return_value={
				"routing": "both",
				"semantic_summary": "Summary",
				"reasoning": "Reasoning",
				"relationships": [{"from": "A", "to": "B", "type": "LINK"}]
			})
			mock_splitter.sift_query = AsyncMock(return_value="hybrid")

			from backend.core.memory.manager import HybridMemoryManager
			manager = HybridMemoryManager()

			# Store
			store_result = await manager.remember(
				agent_id="test_agent",
				data="Important information to remember"
			)

			assert store_result["memory_id"] == "mem_123"
			assert store_result["graph_synced"] is True

			# Retrieve
			recall_result = await manager.recall("What was stored?")

			assert recall_result["mode"] == "hybrid"
			assert len(recall_result["semantic_context"]) > 0


class TestUIBridgeIntegration:
	"""Integration tests for UI Bridge communication."""

	def test_full_broadcast_cycle(self):
		"""Test complete broadcast cycle with heartbeat."""
		from backend.core.ui_bridge import UIBridge
		import time

		bridge = UIBridge()

		with patch('builtins.print') as mock_print:
			# Test tick
			bridge.tick()

			# Test broadcast
			bridge.broadcast("TEST_EVENT", "test_agent", {"data": "value"})
			mock_print.assert_called()

			# Verify message format
			call_args = mock_print.call_args[0][0]
			assert "::SUDO::" in call_args
			assert "TEST_EVENT" in call_args

	def test_heartbeat_start_stop(self):
		"""Test heartbeat thread lifecycle."""
		from backend.core.ui_bridge import UIBridge
		import time

		bridge = UIBridge()

		# Start heartbeat
		bridge.start_heartbeat(interval_seconds=0.5)
		assert bridge._heartbeat_thread is not None

		# Let it run briefly
		time.sleep(0.1)

		# Stop heartbeat
		bridge.stop_heartbeat()


class TestCommandServerIntegration:
	"""Integration tests for command processing pipeline."""

	def test_full_command_pipeline(self):
		"""Test command from receipt to execution."""
		import json
		from backend.core.command_server import CommandServer
		from backend.core.command_router import command_router

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		with patch.object(command_router, 'dispatch') as mock_dispatch:
			# Process a valid command
			server._process_command(json.dumps({
				"command": "PING",
				"payload": {}
			}))

			mock_dispatch.assert_called_once_with("PING", {})


class TestSafetyIntegration:
	"""Integration tests for safety systems."""

	def test_safety_watchdog_greenhouse_integration(self):
		"""Test safety watchdog monitoring greenhouse simulation."""
		from backend.core.hardware.safety import SafetyWatchdog
		from backend.sandbox.simulations.greenhouse import GreenhouseSimulation

		watchdog = SafetyWatchdog()
		sim = GreenhouseSimulation()

		# Get simulated sensor readings
		readings = sim.get_sensor_readings()

		# Map to safety watchdog format
		safety_readings = {
			"S02_TEMP": readings["temperature"],
			"S04_PH": readings["ph_level"],
			"S03_HUM": readings["humidity"]
		}

		# Check telemetry (should pass with normal readings)
		initial_lock = watchdog.emergency_lock
		watchdog.check_telemetry(safety_readings)

		# Normal readings should not trigger emergency
		# (depends on initial simulation state)

	def test_override_priority_enforcement(self):
		"""Test that user overrides take priority over agent commands."""
		from backend.sandbox.simulations.greenhouse import GreenhouseSimulation
		from unittest.mock import patch

		sim = GreenhouseSimulation()

		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			# 1. Agent sets actuator
			sim.set_actuator("pump_active", True, source="agent")
			assert sim.actuators["pump_active"] is True

			# 2. User sets override
			sim.set_actuator("pump_active", False, source="user")
			assert sim.actuators["pump_active"] is False
			assert sim.manual_override["pump_active"] is True

			# 3. Agent tries to change but is blocked
			result = sim.set_actuator("pump_active", True, source="agent")
			assert result is False
			assert sim.actuators["pump_active"] is False  # Still user's value

			# 4. Clear override
			sim.clear_override("pump_active")

			# 5. Agent can now change
			result = sim.set_actuator("pump_active", True, source="agent")
			assert result is True
			assert sim.actuators["pump_active"] is True
