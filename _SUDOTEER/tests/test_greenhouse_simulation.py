"""
TDD Test Suite: Greenhouse Digital Twin Simulation
Tests physics simulation, actuator control, and telemetry.
Grade Target: A (coverage of all public interfaces and state transitions)
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.sandbox.simulations.greenhouse import GreenhouseSimulation


class TestGreenhouseInitialization:
	"""Test suite for Greenhouse simulation initialization."""

	def test_default_state_values(self):
		"""Verify initialization with state dictionary."""
		sim = GreenhouseSimulation()

		# Check state exists
		assert hasattr(sim, 'state')
		assert "temperature" in sim.state
		assert "humidity" in sim.state
		assert "ph_level" in sim.state

	def test_actuators_initialized(self):
		"""Verify all actuators start in defined state."""
		sim = GreenhouseSimulation()

		# All actuators should exist
		assert hasattr(sim, 'actuators')
		assert "pump_active" in sim.actuators
		assert "heater" in sim.actuators
		assert "vent" in sim.actuators

	def test_time_speed_multiplier(self):
		"""Verify time acceleration constant is set."""
		sim = GreenhouseSimulation()
		assert sim.TIME_SPEED == 60.0

	def test_manual_override_initialized(self):
		"""Verify manual override tracking is initialized."""
		sim = GreenhouseSimulation()
		assert hasattr(sim, 'manual_override')
		assert "pump_active" in sim.manual_override


class TestActuatorControl:
	"""Test suite for actuator state management."""

	def test_set_actuator_agent_default(self):
		"""set_actuator without source defaults to 'agent'."""
		sim = GreenhouseSimulation()

		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			result = sim.set_actuator("pump_active", True)

		assert result is True
		assert sim.actuators["pump_active"] is True
		# Should NOT set override (agent source)
		assert sim.manual_override["pump_active"] is False

	def test_set_actuator_agent_explicit(self):
		"""set_actuator with source='agent' should work without override."""
		sim = GreenhouseSimulation()

		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			result = sim.set_actuator("pump_active", True, source="agent")

		assert result is True
		assert sim.actuators["pump_active"] is True
		assert sim.manual_override["pump_active"] is False

	def test_set_actuator_user_source(self):
		"""set_actuator with source='user' should set override."""
		sim = GreenhouseSimulation()

		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			result = sim.set_actuator("pump_active", True, source="user")

		assert result is True
		assert sim.actuators["pump_active"] is True
		assert sim.manual_override["pump_active"] is True  # Override set!

	def test_user_override_blocks_agent(self):
		"""User override should block subsequent agent commands."""
		sim = GreenhouseSimulation()

		# User sets an override
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			sim.set_actuator("pump_active", True, source="user")

		# Agent should be blocked
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			result = sim.set_actuator("pump_active", False, source="agent")

		assert result is False
		assert sim.actuators["pump_active"] is True  # Still True from user

	def test_set_actuator_different_types(self):
		"""set_actuator should handle different value types."""
		sim = GreenhouseSimulation()

		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			# Boolean
			sim.set_actuator("pump_active", True)
			assert sim.actuators["pump_active"] is True

			# Float (for vent)
			sim.set_actuator("vent", 0.5)
			assert sim.actuators["vent"] == 0.5

	def test_set_actuator_unknown_returns_false(self):
		"""Setting unknown actuator should return False."""
		sim = GreenhouseSimulation()

		result = sim.set_actuator("nonexistent_actuator", True)
		assert result is False


class TestClearOverrides:
	"""Test suite for override clearing functionality."""

	def test_clear_single_override(self):
		"""Clearing a single override should allow agent control again."""
		sim = GreenhouseSimulation()

		# Set user override
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			sim.set_actuator("pump_active", True, source="user")

		assert sim.manual_override["pump_active"] is True

		# Clear override
		sim.clear_override("pump_active")

		assert sim.manual_override["pump_active"] is False

		# Agent can now control
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			result = sim.set_actuator("pump_active", False, source="agent")

		assert result is True
		assert sim.actuators["pump_active"] is False

	def test_clear_all_overrides(self):
		"""Clear all overrides at once."""
		sim = GreenhouseSimulation()

		# Set multiple overrides
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			sim.set_actuator("pump_active", True, source="user")
			sim.set_actuator("heater", True, source="user")

		assert sim.manual_override["pump_active"] is True
		assert sim.manual_override["heater"] is True

		# Clear all
		sim.clear_all_overrides()

		# Both should be cleared
		assert sim.manual_override["pump_active"] is False
		assert sim.manual_override["heater"] is False


class TestPhysicsSimulation:
	"""Test suite for physics step calculations."""

	def test_physics_step_runs(self):
		"""Physics step should execute without errors."""
		sim = GreenhouseSimulation()

		# Should not raise
		sim.step(delta_time_sec=1.0)

	def test_temperature_changes_over_time(self):
		"""Temperature should change with physics updates."""
		sim = GreenhouseSimulation()
		initial_temp = sim.state["temperature"]

		# Activate heater
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			sim.set_actuator("heater", True)

		# Run several physics steps
		for _ in range(10):
			sim.step(delta_time_sec=1.0)

		# Temperature should have changed
		assert sim.state["temperature"] != initial_temp

	def test_state_cycle_count_increases(self):
		"""Cycle count should increase with each step."""
		sim = GreenhouseSimulation()
		initial_count = sim.state["cycle_count"]

		sim.step(delta_time_sec=1.0)

		assert sim.state["cycle_count"] == initial_count + 1

	def test_negative_delta_time_clamped(self):
		"""Negative delta time should be clamped to 0."""
		sim = GreenhouseSimulation()

		# Should not crash or produce complex numbers
		sim.step(delta_time_sec=-1.0)

		# Stress index should still be a real number
		assert isinstance(sim.state["stress_index"], float)
		assert not isinstance(sim.state["stress_index"], complex)


class TestTelemetryOutput:
	"""Test suite for sensor reading output."""

	def test_get_sensor_readings_returns_dict(self):
		"""Sensor readings should return a dictionary."""
		sim = GreenhouseSimulation()
		readings = sim.get_sensor_readings()

		assert isinstance(readings, dict)
		assert "temperature" in readings
		assert "humidity" in readings

	def test_get_telemetry_packet_format(self):
		"""Telemetry packet should include all required fields."""
		sim = GreenhouseSimulation()
		packet = sim.get_telemetry_packet()

		assert isinstance(packet, dict)
		assert "temperature" in packet
		assert "humidity" in packet
		assert "ph_level" in packet
		assert "pump_status" in packet
		assert "plant_health" in packet


class TestDayNightCycle:
	"""Test suite for day/night cycle simulation."""

	def test_simulation_tracks_time(self):
		"""Simulation should track elapsed time."""
		sim = GreenhouseSimulation()
		initial_time = sim.state["sim_time"]

		# Run some steps
		for _ in range(10):
			sim.step(delta_time_sec=1.0)

		# Time should have advanced
		assert sim.state["sim_time"] > initial_time

	def test_environment_has_time_data(self):
		"""Environment should track sim_hour and sim_day."""
		sim = GreenhouseSimulation()

		assert "sim_hour" in sim.environment
		assert "sim_day" in sim.environment
		assert "weather" in sim.environment


class TestEdgeCases:
	"""Edge case and robustness tests."""

	def test_zero_delta_time(self):
		"""Simulation should handle zero delta time."""
		sim = GreenhouseSimulation()
		sim.step(delta_time_sec=0.0)
		# Should not crash

	def test_large_delta_time(self):
		"""Simulation should handle large delta time jumps."""
		sim = GreenhouseSimulation()
		sim.step(delta_time_sec=3600.0)  # 1 hour jump
		# Should not crash


class TestOpexTracking:
	"""Test suite for operational expense tracking."""

	def test_electricity_tracking(self):
		"""Electricity consumption should accumulate."""
		sim = GreenhouseSimulation()

		# Turn on heater
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			sim.set_actuator("heater", True)

		# Run physics
		for _ in range(10):
			sim.step(delta_time_sec=1.0)

		# Should have consumed some electricity
		assert sim.opex["electricity_kwh"] > 0

	def test_utility_cost_calculation(self):
		"""Utility cost should be calculated from kWh."""
		sim = GreenhouseSimulation()

		# Turn on heater
		with patch('backend.core.utils.mewtocol.MewtocolFrame.calculate_bcc', return_value="BCC"):
			sim.set_actuator("heater", True)

		# Run physics
		for _ in range(10):
			sim.step(delta_time_sec=1.0)

		# Cost should be calculated
		expected_cost = sim.opex["electricity_kwh"] * sim.ELECTRICITY_RATE
		assert abs(sim.opex["utility_cost"] - expected_cost) < 0.001


class TestCropState:
	"""Test suite for crop state tracking."""

	def test_crop_initialized(self):
		"""Crop state should be initialized."""
		sim = GreenhouseSimulation()

		assert hasattr(sim, 'crop')
		assert "plant_id" in sim.crop
		assert "stage" in sim.crop

	def test_plant_health_tracking(self):
		"""Plant health should be tracked in state."""
		sim = GreenhouseSimulation()

		assert "plant_health" in sim.state
		assert 0 <= sim.state["plant_health"] <= 1

	def test_stress_index_tracking(self):
		"""Stress index should be tracked in state."""
		sim = GreenhouseSimulation()

		assert "stress_index" in sim.state
		assert sim.state["stress_index"] >= 0
