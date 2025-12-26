import pytest
import json
from unittest.mock import MagicMock, patch
from backend.core.command_server import CommandServer

@pytest.fixture
def mock_factory():
	return MagicMock()

@pytest.fixture
def cmd_server(mock_factory):
	from backend.core.command_router import command_router
	server = CommandServer(mock_factory)
	# Router is global, so we must inject the mock factory into it
	command_router.set_factory(mock_factory)
	command_router.set_shutdown_callback(server.stop)
	return server

def test_json_integrity_malformed(cmd_server):
	"""Security: Ensure malformed JSON doesn't crash the server."""
	cmd_server._process_command("NOT_JSON")
	assert cmd_server.command_count == 0

def test_unknown_command_safety(cmd_server):
	"""Safety: Ensure unknown commands are handled without side effects."""
	with patch('backend.core.ui_bridge.ui_bridge.broadcast') as mock_broadcast:
		cmd_server._process_command(json.dumps({"command": "HACK_SYSTEM", "payload": {}}))
		assert cmd_server.command_count == 1
		# Verify broadcast was called on the instance
		assert mock_broadcast.called

def test_spawn_agent_integrity(cmd_server, mock_factory):
	"""Integrity: Ensure SPAWN_AGENT routes correctly with valid payload."""
	payload = {"role": "coder", "name": "test_coder"}
	cmd_server._process_command(json.dumps({"command": "SPAWN_AGENT", "payload": payload}))

	mock_factory.spawn_agent.assert_called_once_with(role="coder", name="test_coder")

def test_spawn_agent_missing_fields(cmd_server, mock_factory):
	"""Security: Ensure partial payloads don't trigger factory calls."""
	payload = {"role": "coder"} # Missing name
	cmd_server._process_command(json.dumps({"command": "SPAWN_AGENT", "payload": payload}))
	mock_factory.spawn_agent.assert_not_called()

def test_injection_attempt_null_bytes(cmd_server):
	"""Security: Atypical injection attempt with null bytes in command name."""
	cmd_server._process_command(json.dumps({"command": "PING\u0000", "payload": {}}))
	assert cmd_server.command_count == 1

def test_greenhouse_command_safety(cmd_server):
	"""Integrity: Ensure greenhouse commands route to simulation."""
	with patch('backend.sandbox.simulations.greenhouse.greenhouse_sim.set_actuator') as mock_set:
		cmd_server._process_command(json.dumps({
			"command": "AGENT_MSG",
			"payload": {"target": "greenhouse_sim", "action": "START_PUMP"}
		}))
		mock_set.assert_called_once_with("pump_active", True)

def test_shutdown_state_transition(cmd_server):
	"""Safety: Ensure SYSTEM_SHUTDOWN transitions state correctly."""
	assert cmd_server.running is True
	cmd_server._process_command(json.dumps({"command": "SYSTEM_SHUTDOWN"}))
	assert cmd_server.running is False
