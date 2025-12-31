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
	TIME_SPEED = 60.0 # 1 real second = 1 simulation minute
	def __init__(self):
		self.start_time = time.time()

		# Current Crop Configuration
		self.crop = {
			"plant_id": "tomato",           # Current plant type
			"plant_name": "Tomato",
			"stage": "vegetative",          # Current growth stage
			"day_planted": 1,               # Sim day when planted
			"days_in_stage": 0              # Days in current stage
		}

		# Core State Vector (Real-time Physics)
		self.state = {
			# Environmental Sensors
			"temperature": 22.0,      # °C
			"humidity": 45.0,         # %
			"co2": 400.0,             # ppm
			"lux": 15000.0,           # Lux meter - light intensity

			# Nutrient Solution Sensors
			"ph_level": 6.5,          # pH probe
			"ec_level": 1.8,          # EC probe (mS/cm)
			"water_pressure": 0.0,    # PSI
			"water_temp": 20.0,       # °C - reservoir temperature
			"dissolved_o2": 8.0,      # mg/L - dissolved oxygen

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
			# Main Water System
			"pump_active": False,           # Main water pump
			"backflow_valve": True,         # Backflow preventer (normally closed = True = safe)

			# Nutrient Dosing - Peristaltic Pumps
			"nutrient_a": False,            # Nutrition A (Grow/Micro)
			"nutrient_b": False,            # Nutrition B (Bloom)
			"ph_up_pump": False,            # pH Up dosing
			"ph_down_pump": False,          # pH Down dosing
			"o2_pump": False,               # Oxygen/air pump for reservoir

			# Climate Control
			"heater": False,
			"vent": 0.0,                    # 0.0 to 1.0 (closed to fully open)
			"fan": False,
			"lights": False                 # Grow lights on/off
		}

		# Manual Override Tracking - UI takes priority over agents
		# When True, agents cannot change this actuator
		self.manual_override = {
			"pump_active": False,
			"backflow_valve": False,
			"nutrient_a": False,
			"nutrient_b": False,
			"ph_up_pump": False,
			"ph_down_pump": False,
			"o2_pump": False,
			"heater": False,
			"vent": False,
			"fan": False,
			"lights": False
		}

		# Time & Weather Simulation
		self.environment = {
			"sim_day": 1,                   # Simulated day counter
			"sim_month": 6,                 # Current month (1-12), default June
			"sim_hour": 6.0,                # 24-hour time (6.0 = 06:00)
			"weather": "sunny",             # sunny, overcast, rain
			"outside_temp": 18.0,           # Ambient outside temperature °C
			"sunrise": 5,                   # Hour of sunrise
			"sunset": 20,                   # Hour of sunset
			"location": "Sacramento, CA"    # Climate baseline location
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
			"pump": 0.1,
			"lights": 0.6,
			"o2_pump": 0.05
		}
		self.ELECTRICITY_RATE = 0.12  # $/kWh

		# Physics Constants - SLOWER for realistic simulation
		self.TEMP_BASE = 20.0          # °C baseline
		self.TEMP_AMPLITUDE = 3.0      # Day/night swing (reduced from 5)
		self.CYCLE_SPEED = 0.005       # Much slower (was 0.1) - one cycle = ~20 min real time
		self.PH_DRIFT_RATE = 0.001     # Very slow pH drift
		self.TIME_SPEED = 60.0         # 1 real second = 1 sim minute (60x speed)

	def set_actuator(self, name: str, value, source: str = "agent") -> bool:
		"""
		Set an actuator state with source tracking.
		source: "user" (UI click) or "agent" (automatic)
		Returns True if change was applied, False if blocked by override.
		"""
		if name not in self.actuators:
			return False

		# If user is setting, mark as manual override
		if source == "user":
			self.actuators[name] = value
			self.manual_override[name] = True

			# BCC Insurance Calculation
			from backend.core.utils.mewtocol import MewtocolFrame
			bcc = MewtocolFrame.calculate_bcc(f"USER_SET_{name}_{value}")
			logger.info(f"🔒 USER OVERRIDE: {name} = {value} [BCC: {bcc}] (agents locked out)")
			return True

		# If agent is setting, check for override
		if source == "agent" and self.manual_override.get(name, False):
			logger.info(f"⚠️ Agent tried to change {name} but USER OVERRIDE is active")
			return False

		# Agent can change (no override)
		self.actuators[name] = value
		# BCC Insurance for Agent command
		from backend.core.utils.mewtocol import MewtocolFrame
		bcc = MewtocolFrame.calculate_bcc(f"AGENT_SET_{name}_{value}")
		logger.info(f"🤖 AGENT COMMAND: {name} = {value} [BCC: {bcc}]")
		return True

	def clear_override(self, name: str) -> None:
		"""Clear manual override for an actuator (agent can control again)."""
		if name in self.manual_override:
			self.manual_override[name] = False
			logger.info(f"🔓 Override cleared for {name} - agents can control")

	def clear_all_overrides(self) -> None:
		"""Clear all manual overrides."""
		for key in self.manual_override:
			self.manual_override[key] = False
		logger.info("🔓 All overrides cleared - full agent control restored")

	def step(self, delta_time_sec: float = 1.0):
		"""
		Calculate next state based on realistic physics.
		Runs at 1Hz for smooth real-time updates.
		"""
		# Input validation - prevent negative delta causing complex numbers
		delta_time_sec = max(0.0, delta_time_sec)

		elapsed = time.time() - self.start_time
		self.state["sim_time"] = elapsed
		self.state["cycle_count"] += 1

		dt_ratio = delta_time_sec / 3600.0  # For hourly conversions

		# === TIME SIMULATION ===
		# Advance simulated time (1 real sec = TIME_SPEED sim seconds)
		sim_minutes = (delta_time_sec * self.TIME_SPEED) / 60.0
		self.environment["sim_hour"] += sim_minutes / 60.0

		# Roll over to next day
		if self.environment["sim_hour"] >= 24.0:
			self.environment["sim_hour"] -= 24.0
			self.environment["sim_day"] += 1
			# Random weather change each day
			self.environment["weather"] = random.choice(["sunny", "sunny", "overcast", "overcast", "rain"])

		# === WEATHER & OUTSIDE TEMP SIMULATION ===
		hour = self.environment["sim_hour"]
		# Outside temp follows day/night cycle
		day_progress = (hour - 6) / 12.0 if 6 <= hour <= 18 else 0
		base_outside = 15.0 + (10.0 * math.sin(day_progress * math.pi)) if 6 <= hour <= 18 else 10.0

		# Weather affects outside temp
		if self.environment["weather"] == "overcast":
			base_outside -= 3.0
		elif self.environment["weather"] == "rain":
			base_outside -= 6.0

		self.environment["outside_temp"] = base_outside + random.uniform(-0.5, 0.5)

		# === REALISTIC PHYSICS SIMULATION ===

		# 1. TEMPERATURE: Based on time of day and outside temp
		is_daytime = self.environment["sunrise"] <= hour < self.environment["sunset"]
		base_temp = self.TEMP_BASE + (self.TEMP_AMPLITUDE * math.sin((hour - 6) * math.pi / 12)) if is_daytime else self.TEMP_BASE - 2
		noise = random.uniform(-0.05, 0.05)  # Reduced noise

		# Outside influence (greenhouse walls aren't perfect)
		outside_influence = (self.environment["outside_temp"] - base_temp) * 0.1
		base_temp += outside_influence

		# Heater influence
		if self.actuators["heater"]:
			base_temp += 2.0

		# Vent cooling
		if self.actuators["vent"] > 0:
			base_temp -= self.actuators["vent"] * 3.0

		self.state["temperature"] = base_temp + noise

		# 2. HUMIDITY: Inverse relationship with temperature, affected by weather
		base_humidity = 50 + (10 * math.cos((hour - 12) * math.pi / 12))
		if self.environment["weather"] == "rain":
			base_humidity += 15
		elif self.environment["weather"] == "overcast":
			base_humidity += 5
		self.state["humidity"] = max(20, min(95, base_humidity + random.uniform(-0.3, 0.3)))

		# 3. LUX: Based on time of day and weather
		if is_daytime:
			base_lux = 30000 * math.sin((hour - 6) * math.pi / 12)
			if self.environment["weather"] == "overcast":
				base_lux *= 0.4
			elif self.environment["weather"] == "rain":
				base_lux *= 0.2
		else:
			base_lux = 0

		# Add artificial lights contribution
		if self.actuators["lights"]:
			base_lux += 15000

		self.state["lux"] = max(0, base_lux + random.uniform(-100, 100))

		# 3. pH LEVEL: Drifts based on pump activity
		if self.actuators["pump_active"] or self.actuators["nutrient_a"] or self.actuators["nutrient_b"]:
			# Nutrient injection affects pH. If number (0-100), scale the drift.
			strength = self.actuators["nutrient_a"] if isinstance(self.actuators["nutrient_a"], (int, float)) else (100 if self.actuators["nutrient_a"] else 0)
			strength += self.actuators["nutrient_b"] if isinstance(self.actuators["nutrient_b"], (int, float)) else (100 if self.actuators["nutrient_b"] else 0)
			strength = min(100, strength)

			drift = 0.05 * (strength / 100.0) * random.random()
			self.state["ph_level"] = min(8.5, self.state["ph_level"] + drift)
		elif self.actuators["ph_down_pump"]:
			# pH Down pump decreases pH
			strength = self.actuators["ph_down_pump"] if isinstance(self.actuators["ph_down_pump"], (int, float)) else 100
			drift = -0.08 * (strength / 100.0) * random.random()
			self.state["ph_level"] = max(4.0, self.state["ph_level"] + drift)
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
		if self.actuators["nutrient_a"] or self.actuators["nutrient_b"]:
			# Scale usage based on speed (0-100)
			speed_a = self.actuators["nutrient_a"] if isinstance(self.actuators["nutrient_a"], (int, float)) else (100 if self.actuators["nutrient_a"] else 0)
			speed_b = self.actuators["nutrient_b"] if isinstance(self.actuators["nutrient_b"], (int, float)) else (100 if self.actuators["nutrient_b"] else 0)
			avg_speed = (speed_a + speed_b) / 200.0

			self.opex["nutrients_liters"] += 0.01 * avg_speed * (delta_time_sec / 60.0)
			# EC rises when dosing nutrients
			self.state["ec_level"] = min(3.5, self.state["ec_level"] + 0.01 * avg_speed)
		else:
			# EC slowly drops as plants absorb
			self.state["ec_level"] = max(0.5, self.state["ec_level"] - 0.001)

		# === PLANT HEALTH CALCULATION ===
		# Based on: Temperature, pH, EC, Humidity, Light, Dissolved O2
		stress_factors = []

		# 1. TEMPERATURE stress (optimal: 20-28°C)
		temp = self.state["temperature"]
		if temp > 32.0:
			stress_factors.append(("temp_high", (temp - 32.0) * 0.03))
		elif temp > 28.0:
			stress_factors.append(("temp_warm", (temp - 28.0) * 0.01))
		elif temp < 15.0:
			stress_factors.append(("temp_cold", (15.0 - temp) * 0.03))
		elif temp < 18.0:
			stress_factors.append(("temp_cool", (18.0 - temp) * 0.01))

		# 2. pH stress (optimal: 5.8-6.5)
		ph = self.state["ph_level"]
		if ph < 5.5 or ph > 7.0:
			stress_factors.append(("ph_extreme", 0.02))
		elif ph < 5.8 or ph > 6.5:
			stress_factors.append(("ph_suboptimal", 0.005))

		# 3. EC stress (optimal: 1.2-2.4 mS/cm)
		ec = self.state["ec_level"]
		if ec < 0.8:
			stress_factors.append(("ec_low", (0.8 - ec) * 0.02))  # Nutrient deficiency
		elif ec > 3.0:
			stress_factors.append(("ec_high", (ec - 3.0) * 0.03))  # Nutrient burn

		# 4. HUMIDITY stress (optimal: 50-70%)
		humidity = self.state["humidity"]
		if humidity > 85:
			stress_factors.append(("humidity_high", (humidity - 85) * 0.002))  # Mold risk
		elif humidity < 30:
			stress_factors.append(("humidity_low", (30 - humidity) * 0.002))   # Drying out

		# 5. LIGHT stress (need adequate DLI - Daily Light Integral)
		lux = self.state["lux"]
		if lux < 5000 and is_daytime:
			stress_factors.append(("light_low", 0.01))  # Not enough light during day

		# 6. DISSOLVED O2 in reservoir (optimal: 6-10 mg/L)
		if self.actuators["o2_pump"]:
			self.state["dissolved_o2"] = min(12.0, self.state["dissolved_o2"] + 0.1)
		else:
			self.state["dissolved_o2"] = max(3.0, self.state["dissolved_o2"] - 0.02)

		o2 = self.state["dissolved_o2"]
		if o2 < 5.0:
			stress_factors.append(("o2_low", (5.0 - o2) * 0.02))  # Root suffocation

		# Calculate total stress
		total_stress_gain = sum(factor[1] for factor in stress_factors)
		if total_stress_gain > 0:
			self.state["stress_index"] = min(1.0, self.state["stress_index"] + total_stress_gain * dt_ratio * 10)
		else:
			# Recovery when all conditions optimal
			self.state["stress_index"] = max(0.0, self.state["stress_index"] - 0.01)

		# Plant health (inverse of stress, with smooth curve)
		self.state["plant_health"] = max(0.0, 1.0 - (self.state["stress_index"] ** 0.7))

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

	# NOTE: set_actuator is defined above with source tracking for user/agent priority
	# See lines 134-165 for the implementation with manual override support

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

