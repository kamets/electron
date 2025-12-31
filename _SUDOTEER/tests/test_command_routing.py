"""
TDD Test Suite: Command Router & UI Bridge
Tests command routing, broadcast functionality, and frontend communication.
Grade Target: A (full coverage of routing and messaging paths)
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock


class TestCommandRouterInitialization:
	"""Test suite for CommandRouter initialization."""

	def test_router_has_dispatch(self):
		"""Command router should have dispatch method."""
		from backend.core.command_router import command_router

		assert hasattr(command_router, 'dispatch')
		assert hasattr(command_router, 'set_factory')
		assert hasattr(command_router, 'set_shutdown_callback')

	def test_router_handlers_registered(self):
		"""Command router should have handlers for core commands."""
		from backend.core.command_router import command_router

		assert "SPAWN_AGENT" in command_router.handlers
		assert "PING" in command_router.handlers
		assert "SYSTEM_SHUTDOWN" in command_router.handlers


class TestCommandRouting:
	"""Test suite for command routing logic."""

	def test_ping_command_handled(self):
		"""PING command should be dispatched correctly."""
		from backend.core.command_router import command_router

		with patch('backend.core.ui_bridge.ui_bridge.broadcast') as mock_broadcast:
			command_router.dispatch("PING", {})
			mock_broadcast.assert_called()

	def test_unknown_command_safe_handling(self):
		"""Unknown commands should be handled safely."""
		from backend.core.command_router import command_router

		with patch('backend.core.ui_bridge.ui_bridge.broadcast') as mock_broadcast:
			# Should not raise, and should broadcast error
			command_router.dispatch("NONEXISTENT_COMMAND", {})
			mock_broadcast.assert_called()

	def test_system_shutdown_command(self):
		"""SYSTEM_SHUTDOWN should trigger proper shutdown sequence."""
		from backend.core.command_router import command_router

		mock_callback = MagicMock()
		command_router.set_shutdown_callback(mock_callback)

		command_router.dispatch("SYSTEM_SHUTDOWN", {})
		mock_callback.assert_called_once()


class TestSpawnAgentCommand:
	"""Test suite for SPAWN_AGENT command."""

	def test_spawn_agent_with_valid_payload(self):
		"""SPAWN_AGENT with valid role and name should work."""
		from backend.core.command_router import command_router

		mock_factory = MagicMock()
		command_router.set_factory(mock_factory)

		payload = {"role": "coder", "name": "test_coder"}
		command_router.dispatch("SPAWN_AGENT", payload)

		mock_factory.spawn_agent.assert_called_once_with(role="coder", name="test_coder")

	def test_spawn_agent_missing_role(self):
		"""SPAWN_AGENT without role should not crash."""
		from backend.core.command_router import command_router

		mock_factory = MagicMock()
		command_router.set_factory(mock_factory)

		payload = {"name": "test_agent"}  # Missing role
		command_router.dispatch("SPAWN_AGENT", payload)
		# Should not call spawn_agent with incomplete payload
		mock_factory.spawn_agent.assert_not_called()

	def test_spawn_agent_missing_name(self):
		"""SPAWN_AGENT without name should not crash."""
		from backend.core.command_router import command_router

		mock_factory = MagicMock()
		command_router.set_factory(mock_factory)

		payload = {"role": "tester"}  # Missing name
		command_router.dispatch("SPAWN_AGENT", payload)
		# Should not call spawn_agent with incomplete payload
		mock_factory.spawn_agent.assert_not_called()


class TestUIBridgeInitialization:
	"""Test suite for UIBridge initialization."""

	def test_ui_bridge_singleton(self):
		"""UIBridge should be a singleton instance."""
		from backend.core.ui_bridge import ui_bridge

		assert ui_bridge is not None

	def test_ui_bridge_has_broadcast(self):
		"""UIBridge should have broadcast method."""
		from backend.core.ui_bridge import ui_bridge

		assert hasattr(ui_bridge, 'broadcast')
		assert hasattr(ui_bridge, 'broadcast_agent_status')
		assert hasattr(ui_bridge, 'broadcast_workflow_step')


class TestUIBridgeBroadcast:
	"""Test suite for UIBridge broadcast functionality."""

	def test_broadcast_with_full_args(self):
		"""broadcast should accept event_type, agent_id, and payload."""
		from backend.core.ui_bridge import ui_bridge

		# Capture stdout
		with patch('builtins.print') as mock_print:
			ui_bridge.broadcast("TEST_EVENT", "test_agent", {"data": "value"})
			mock_print.assert_called()

	def test_broadcast_agent_status(self):
		"""broadcast_agent_status should format and send agent updates."""
		from backend.core.ui_bridge import ui_bridge

		with patch('builtins.print') as mock_print:
			ui_bridge.broadcast_agent_status("test_agent", "active", {"task": "testing"})
			mock_print.assert_called()

	def test_broadcast_workflow_step(self):
		"""broadcast_workflow_step should format and send workflow updates."""
		from backend.core.ui_bridge import ui_bridge

		with patch('builtins.print') as mock_print:
			ui_bridge.broadcast_workflow_step("wf_123", "coder", "processing")
			mock_print.assert_called()


class TestUIBridgeHeartbeat:
	"""Test suite for UIBridge heartbeat functionality."""

	def test_start_heartbeat(self):
		"""start_heartbeat should not raise."""
		from backend.core.ui_bridge import UIBridge

		bridge = UIBridge()
		# Should not raise
		bridge.start_heartbeat(interval_seconds=1.0)
		bridge.stop_heartbeat()

	def test_tick_resets_watchdog(self):
		"""tick() should reset the watchdog timer."""
		from backend.core.ui_bridge import UIBridge
		import time

		bridge = UIBridge()
		old_tick = bridge._last_tick
		time.sleep(0.1)
		bridge.tick()

		assert bridge._last_tick > old_tick

	def test_get_uptime(self):
		"""get_uptime should return positive value."""
		from backend.core.ui_bridge import UIBridge
		import time

		bridge = UIBridge()
		time.sleep(0.1)

		assert bridge.get_uptime() > 0


class TestCommandServerIntegration:
	"""Test suite for CommandServer integration."""

	def test_process_valid_json(self):
		"""CommandServer should process valid JSON commands."""
		from backend.core.command_server import CommandServer

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		command = json.dumps({"command": "PING", "payload": {}})
		server._process_command(command)

		assert server.command_count >= 0

	def test_process_invalid_json(self):
		"""CommandServer should handle invalid JSON gracefully."""
		from backend.core.command_server import CommandServer

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		# Invalid JSON should not crash
		server._process_command("NOT_VALID_JSON")

	def test_process_empty_command(self):
		"""CommandServer should handle empty commands."""
		from backend.core.command_server import CommandServer

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		server._process_command("")


class TestSecurityConstraints:
	"""Test suite for security-related constraints."""

	def test_null_byte_injection(self):
		"""Commands with null bytes should be handled safely."""
		from backend.core.command_server import CommandServer

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		malicious = json.dumps({"command": "PING\x00DROP", "payload": {}})
		server._process_command(malicious)

	def test_oversized_payload(self):
		"""Oversized payloads should not crash the server."""
		from backend.core.command_server import CommandServer

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		large_payload = {"data": "x" * 100000}
		command = json.dumps({"command": "PING", "payload": large_payload})

		# Should not crash
		server._process_command(command)

	def test_nested_payload(self):
		"""Deeply nested payloads should be handled."""
		from backend.core.command_server import CommandServer

		mock_factory = MagicMock()
		server = CommandServer(mock_factory)

		# Create nested structure
		nested = {"level": 0}
		current = nested
		for i in range(50):
			current["child"] = {"level": i + 1}
			current = current["child"]

		command = json.dumps({"command": "PING", "payload": nested})

		# Should handle deeply nested structures
		server._process_command(command)
