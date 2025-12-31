"""
TDD Test Suite: Industrial Safety Watchdog
Tests critical safety constraints for hardware protection.
Grade Target: A (100% coverage of safety-critical paths)
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from backend.core.hardware.safety import SafetyWatchdog


class TestSafetyWatchdogInitialization:
	"""Test suite for SafetyWatchdog initialization."""

	def test_default_safe_ranges(self):
		"""Verify default safety thresholds are correctly configured."""
		watchdog = SafetyWatchdog()

		assert "S02_TEMP" in watchdog.safe_ranges
		assert "S04_PH" in watchdog.safe_ranges
		assert "S03_HUM" in watchdog.safe_ranges

		# Verify specific ranges
		assert watchdog.safe_ranges["S02_TEMP"] == (10.0, 45.0)
		assert watchdog.safe_ranges["S04_PH"] == (4.0, 9.0)
		assert watchdog.safe_ranges["S03_HUM"] == (10.0, 95.0)

	def test_emergency_lock_default_state(self):
		"""Verify emergency lock is OFF by default."""
		watchdog = SafetyWatchdog()
		assert watchdog.emergency_lock is False


class TestActuatorValidation:
	"""Test suite for actuator command validation."""

	def test_actuator_request_allowed_when_unlocked(self):
		"""PASS: Normal actuator requests should be allowed."""
		watchdog = SafetyWatchdog()
		assert watchdog.validate_actuator_request("PUMP_01", True) is True

	def test_actuator_request_rejected_when_locked(self):
		"""CRITICAL: All commands must be rejected during emergency lock."""
		watchdog = SafetyWatchdog()
		watchdog.emergency_lock = True

		assert watchdog.validate_actuator_request("PUMP_01", True) is False
		assert watchdog.validate_actuator_request("FAN_01", False) is False
		assert watchdog.validate_actuator_request("HEATER_01", 50) is False


class TestTelemetryChecks:
	"""Test suite for sensor telemetry validation."""

	def test_valid_telemetry_does_not_trigger_emergency(self):
		"""Nominal sensor data should pass without triggering emergency."""
		watchdog = SafetyWatchdog()

		sensors = {
			"S02_TEMP": 25.0,  # Within 10-45
			"S04_PH": 6.5,     # Within 4-9
			"S03_HUM": 60.0    # Within 10-95
		}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is False

	def test_temperature_out_of_range_triggers_emergency(self):
		"""CRITICAL: Out-of-range temperature must trigger emergency stop."""
		watchdog = SafetyWatchdog()

		sensors = {
			"S02_TEMP": 50.0,  # EXCEEDS 45 max
			"S04_PH": 6.5,
			"S03_HUM": 60.0
		}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is True

	def test_ph_out_of_range_triggers_emergency(self):
		"""CRITICAL: Out-of-range pH must trigger emergency stop."""
		watchdog = SafetyWatchdog()

		sensors = {
			"S02_TEMP": 25.0,
			"S04_PH": 2.0,  # BELOW 4 min
			"S03_HUM": 60.0
		}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is True

	def test_humidity_out_of_range_triggers_emergency(self):
		"""CRITICAL: Out-of-range humidity must trigger emergency stop."""
		watchdog = SafetyWatchdog()

		sensors = {
			"S02_TEMP": 25.0,
			"S04_PH": 6.5,
			"S03_HUM": 99.0  # EXCEEDS 95 max
		}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is True

	def test_sensor_timeout_triggers_emergency(self):
		"""CRITICAL: Stale sensor data must trigger emergency stop."""
		watchdog = SafetyWatchdog()
		watchdog.last_sensor_update = time.time() - 35  # 35 seconds ago (>30s timeout)

		sensors = {"S02_TEMP": 25.0, "S04_PH": 6.5, "S03_HUM": 60.0}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is True


class TestEmergencyStop:
	"""Test suite for emergency stop functionality."""

	def test_trigger_emergency_stop_sets_lock(self):
		"""Verify emergency stop properly engages lock."""
		watchdog = SafetyWatchdog()
		watchdog.trigger_emergency_stop()

		assert watchdog.emergency_lock is True

	def test_emergency_lock_persists(self):
		"""Verify emergency lock cannot be cleared by normal operations."""
		watchdog = SafetyWatchdog()
		watchdog.trigger_emergency_stop()

		# Try various operations
		watchdog.validate_actuator_request("PUMP", True)
		watchdog.check_telemetry({"S02_TEMP": 25.0})

		# Lock should still be engaged
		assert watchdog.emergency_lock is True


class TestEdgeCases:
	"""Edge case tests for robustness."""

	def test_missing_sensor_in_telemetry(self):
		"""Handle missing sensors gracefully without false emergency."""
		watchdog = SafetyWatchdog()

		# Only one sensor reported (others missing)
		sensors = {"S02_TEMP": 25.0}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is False

	def test_none_sensor_value(self):
		"""Handle None sensor values gracefully."""
		watchdog = SafetyWatchdog()

		sensors = {
			"S02_TEMP": None,
			"S04_PH": 6.5,
			"S03_HUM": 60.0
		}

		watchdog.check_telemetry(sensors)
		assert watchdog.emergency_lock is False
