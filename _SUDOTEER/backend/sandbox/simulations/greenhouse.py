"""
Greenhouse Digital Twin Simulation
Enhanced with realistic physics, day/night cycles, and UIBridge integration
"""

import logging
import time
import math
import random
import asyncio
from typing import Dict, Any

logger = logging.getLogger("_SUDOTEER")

class GreenhouseSimulation:
	"""
	Greenhouse Digital Twin Engine.
	Models realistic physics with sine-wave day/night cycles.
	Acts as the 'God Process' for the simulation sandbox.
	"""
	def __init__(self):
		self.start_time = time.time()

		# Core State Vector (Real-time Physics)
		self.state = {
			# Environmental Sensors
			"temperature": 22.0,      # °C
			"humidity": 45.0,         # %
			"ph_level": 6.5,          # pH
			"water_pressure": 0.0,    # PSI
			"co2": 400.0,             # ppm

			# Biological State
			"stress_index": 0.0,
			"plant_health": 1.0,
			"yield_potential": 100.0,  # kg
			"total_harvested": 0.0,
			"wasted_crops": 0.0,

			# Simulation Meta
			"sim_time": 0.0,
			"cycle_count": 0
		}

		# Actuator States
		self.actuators = {
			"pump_active": False,
			"heater": False,
			"vent": 0.0,            # 0.0 to 1.0 (closed to fully open)
			"fan": False,
			"nutrient_pump": False
		}

		# Operational Metrics
		self.opex = {
			"electricity_kwh": 0.0,
			"nutrients_liters": 0.0,
			"man_hours_saved": 0.0,
			"utility_cost": 0.0
		}

		# Constants
		self.POWER_CONSUMPTION = {
			"heater": 1.5,  # kW
			"fan": 0.2,
			"pump": 0.1
		}
		self.ELECTRICITY_RATE = 0.12  # $/kWh

		# Physics Constants
		self.TEMP_BASE = 20.0        # °C baseline
		self.TEMP_AMPLITUDE = 5.0    # Day/night swing
		self.CYCLE_SPEED = 0.1       # Faster for demo (real would be 0.001)

	def step(self, delta_time_sec: float = 1.0):
		"""
		Calculate next state based on realistic physics.
		Runs at 1Hz for smooth real-time updates.
		"""
		elapsed = time.time() - self.start_time
		self.state["sim_time"] = elapsed
		self.state["cycle_count"] += 1

		dt_ratio = delta_time_sec / 3600.0  # For hourly conversions

		# === REALISTIC PHYSICS SIMULATION ===

		# 1. TEMPERATURE: Sine wave day/night cycle
		# Base temp + sine wave + small random noise
		base_temp = self.TEMP_BASE + (self.TEMP_AMPLITUDE * math.sin(elapsed * self.CYCLE_SPEED))
		noise = random.uniform(-0.1, 0.1)

		# Heater influence
		if self.actuators["heater"]:
			base_temp += 2.0

		# Vent cooling
		if self.actuators["vent"] > 0:
			base_temp -= self.actuators["vent"] * 3.0

		self.state["temperature"] = base_temp + noise

		# 2. HUMIDITY: Inverse relationship with temperature
		# Hot air holds more water but feels drier
		self.state["humidity"] = 50 + (10 * math.cos(elapsed * self.CYCLE_SPEED)) + random.uniform(-0.5, 0.5)

		# 3. pH LEVEL: Drifts based on pump activity
		if self.actuators["pump_active"] or self.actuators["nutrient_pump"]:
			# Nutrient injection raises pH slightly
			drift = 0.05 * random.random()
			self.state["ph_level"] = min(8.5, self.state["ph_level"] + drift)
		else:
			# Natural acidification over time
			drift = -0.01 * random.random()
			self.state["ph_level"] = max(4.0, self.state["ph_level"] + drift)

		# 4. WATER PRESSURE: Smooth ramp up/down based on pump
		target_pressure = 40.0 if self.actuators["pump_active"] else 0.0
		# Exponential smoothing (lerp)
		self.state["water_pressure"] += (target_pressure - self.state["water_pressure"]) * 0.2

		# 5. CO2: Affected by plant respiration and ventilation
		if self.actuators["vent"] > 0.5:
			self.state["co2"] = max(300, self.state["co2"] - 5)  # Fresh air
		else:
			self.state["co2"] = min(1200, self.state["co2"] + 2)  # Plants breathing

		# === OPERATIONAL METRICS ===

		# Power consumption
		if self.actuators["heater"]:
			self.opex["electricity_kwh"] += self.POWER_CONSUMPTION["heater"] * dt_ratio

		if self.actuators["fan"]:
			self.opex["electricity_kwh"] += self.POWER_CONSUMPTION["fan"] * dt_ratio

		if self.actuators["pump_active"]:
			self.opex["electricity_kwh"] += self.POWER_CONSUMPTION["pump"] * dt_ratio

		self.opex["utility_cost"] = self.opex["electricity_kwh"] * self.ELECTRICITY_RATE

		# Nutrient consumption
		if self.actuators["nutrient_pump"] or self.actuators["pump_active"]:
			self.opex["nutrients_liters"] += 0.01 * (delta_time_sec / 60.0)

		# === BIOLOGY & YIELD ===

		# Temperature stress
		if self.state["temperature"] > 32.0:
			stress_gain = (self.state["temperature"] - 32.0) * 0.01
			self.state["stress_index"] = min(1.0, self.state["stress_index"] + stress_gain)
		elif self.state["temperature"] < 15.0:
			stress_gain = (15.0 - self.state["temperature"]) * 0.01
			self.state["stress_index"] = min(1.0, self.state["stress_index"] + stress_gain)
		else:
			# Recovery in optimal range
			self.state["stress_index"] = max(0.0, self.state["stress_index"] - 0.005)

		# pH stress
		if self.state["ph_level"] < 5.5 or self.state["ph_level"] > 7.5:
			self.state["stress_index"] = min(1.0, self.state["stress_index"] + 0.002)

		# Plant health (inverse of stress)
		self.state["plant_health"] = 1.0 - self.state["stress_index"]

		# Yield impact
		if self.state["stress_index"] > 0.5:
			loss = (self.state["stress_index"] - 0.5) * 0.1
			self.state["yield_potential"] = max(0, self.state["yield_potential"] - loss)
			self.state["wasted_crops"] += loss

		# Labor savings (AI prevents manual intervention)
		if self.state["stress_index"] < 0.2:
			self.opex["man_hours_saved"] += 0.5 * dt_ratio

		# Periodic logging (every 60 cycles = ~1 minute)
		if self.state["cycle_count"] % 60 == 0:
			logger.info(
				f"SIM | Temp: {self.state['temperature']:.1f}°C | "
				f"pH: {self.state['ph_level']:.2f} | "
				f"Power: {self.opex['electricity_kwh']:.2f}kWh | "
				f"Waste: {self.state['wasted_crops']:.2f}kg"
			)

	def set_actuator(self, actuator: str, value: Any):
		"""
		Set actuator state.
		Called by commands from UI or agents.
		"""
		if actuator in self.actuators:
			self.actuators[actuator] = value
			logger.info(f"Actuator {actuator} set to {value}")
		else:
			logger.warning(f"Unknown actuator: {actuator}")

	def get_sensor_readings(self) -> Dict[str, Any]:
		"""Return current state for telemetry broadcasting."""
		return {
			**self.state,
			**self.actuators,
			**self.opex
		}

	def get_telemetry_packet(self) -> Dict[str, Any]:
		"""
		Optimized packet for UIBridge broadcast.
		Only includes fields that UI cares about.
		"""
		return {
			"temperature": round(self.state["temperature"], 1),
			"humidity": round(self.state["humidity"], 1),
			"ph_level": round(self.state["ph_level"], 2),
			"water_pressure": round(self.state["water_pressure"], 1),
			"pump_status": self.actuators["pump_active"],
			"plant_health": round(self.state["plant_health"], 2),
			"stress_index": round(self.state["stress_index"], 2),
			"power_kwh": round(self.opex["electricity_kwh"], 3)
		}

# Global simulation instance
greenhouse_sim = GreenhouseSimulation()

