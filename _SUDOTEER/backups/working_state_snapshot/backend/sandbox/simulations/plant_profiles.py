"""
Plant Profile Database
Species-specific optimal ranges for hydroponics at each growth stage.
"""

# Growth Stages
STAGES = ["seedling", "vegetative", "flowering", "fruiting", "harvest"]

# Plant Profile Database
# Each profile contains optimal ranges per growth stage
PLANT_PROFILES = {
	"tomato": {
		"name": "Tomato",
		"scientific": "Solanum lycopersicum",
		"days_to_harvest": 90,
		"stages": {
			"seedling": {
				"duration_days": 14,
				"temp_min": 20, "temp_max": 25,
				"humidity_min": 65, "humidity_max": 80,
				"ph_min": 5.8, "ph_max": 6.3,
				"ec_min": 0.8, "ec_max": 1.2,
				"light_dli": 12,  # mol/m²/day
				"notes": "Keep warm, high humidity for germination"
			},
			"vegetative": {
				"duration_days": 28,
				"temp_min": 21, "temp_max": 27,
				"humidity_min": 50, "humidity_max": 70,
				"ph_min": 5.8, "ph_max": 6.5,
				"ec_min": 1.5, "ec_max": 2.5,
				"light_dli": 25,
				"notes": "Strong light, moderate feeding"
			},
			"flowering": {
				"duration_days": 21,
				"temp_min": 18, "temp_max": 26,
				"humidity_min": 40, "humidity_max": 60,
				"ph_min": 6.0, "ph_max": 6.5,
				"ec_min": 2.0, "ec_max": 3.0,
				"light_dli": 30,
				"notes": "Reduce humidity to prevent mold, increase K"
			},
			"fruiting": {
				"duration_days": 30,
				"temp_min": 18, "temp_max": 28,
				"humidity_min": 50, "humidity_max": 65,
				"ph_min": 6.0, "ph_max": 6.5,
				"ec_min": 2.5, "ec_max": 3.5,
				"light_dli": 30,
				"notes": "High potassium for fruit development"
			}
		}
	},
	"lettuce": {
		"name": "Lettuce",
		"scientific": "Lactuca sativa",
		"days_to_harvest": 45,
		"stages": {
			"seedling": {
				"duration_days": 10,
				"temp_min": 16, "temp_max": 21,
				"humidity_min": 60, "humidity_max": 75,
				"ph_min": 5.5, "ph_max": 6.0,
				"ec_min": 0.5, "ec_max": 0.8,
				"light_dli": 10,
				"notes": "Cool temps prevent bolting"
			},
			"vegetative": {
				"duration_days": 35,
				"temp_min": 15, "temp_max": 22,
				"humidity_min": 50, "humidity_max": 70,
				"ph_min": 5.5, "ph_max": 6.5,
				"ec_min": 0.8, "ec_max": 1.4,
				"light_dli": 17,
				"notes": "Keep cool, avoid tip burn"
			}
		}
	},
	"pepper": {
		"name": "Bell Pepper",
		"scientific": "Capsicum annuum",
		"days_to_harvest": 100,
		"stages": {
			"seedling": {
				"duration_days": 21,
				"temp_min": 24, "temp_max": 29,
				"humidity_min": 65, "humidity_max": 80,
				"ph_min": 5.8, "ph_max": 6.3,
				"ec_min": 0.8, "ec_max": 1.2,
				"light_dli": 12,
				"notes": "Peppers need heat to germinate"
			},
			"vegetative": {
				"duration_days": 35,
				"temp_min": 21, "temp_max": 28,
				"humidity_min": 50, "humidity_max": 70,
				"ph_min": 5.8, "ph_max": 6.5,
				"ec_min": 1.8, "ec_max": 2.8,
				"light_dli": 25,
				"notes": "Strong stems need calcium"
			},
			"flowering": {
				"duration_days": 21,
				"temp_min": 20, "temp_max": 27,
				"humidity_min": 40, "humidity_max": 60,
				"ph_min": 6.0, "ph_max": 6.5,
				"ec_min": 2.0, "ec_max": 3.0,
				"light_dli": 30,
				"notes": "Shake plants to help pollination"
			},
			"fruiting": {
				"duration_days": 30,
				"temp_min": 18, "temp_max": 28,
				"humidity_min": 50, "humidity_max": 65,
				"ph_min": 6.0, "ph_max": 6.5,
				"ec_min": 2.5, "ec_max": 3.5,
				"light_dli": 30,
				"notes": "High K for fruit set"
			}
		}
	},
	"cucumber": {
		"name": "Cucumber",
		"scientific": "Cucumis sativus",
		"days_to_harvest": 60,
		"stages": {
			"seedling": {
				"duration_days": 10,
				"temp_min": 24, "temp_max": 30,
				"humidity_min": 70, "humidity_max": 85,
				"ph_min": 5.5, "ph_max": 6.0,
				"ec_min": 1.0, "ec_max": 1.5,
				"light_dli": 12,
				"notes": "High humidity for rapid growth"
			},
			"vegetative": {
				"duration_days": 20,
				"temp_min": 22, "temp_max": 28,
				"humidity_min": 60, "humidity_max": 75,
				"ph_min": 5.5, "ph_max": 6.5,
				"ec_min": 1.5, "ec_max": 2.5,
				"light_dli": 25,
				"notes": "Train vines, remove side shoots"
			},
			"fruiting": {
				"duration_days": 30,
				"temp_min": 20, "temp_max": 27,
				"humidity_min": 60, "humidity_max": 70,
				"ph_min": 5.8, "ph_max": 6.5,
				"ec_min": 2.0, "ec_max": 3.0,
				"light_dli": 30,
				"notes": "Harvest daily for continuous production"
			}
		}
	},
	"basil": {
		"name": "Basil",
		"scientific": "Ocimum basilicum",
		"days_to_harvest": 28,
		"stages": {
			"seedling": {
				"duration_days": 7,
				"temp_min": 21, "temp_max": 27,
				"humidity_min": 60, "humidity_max": 75,
				"ph_min": 5.5, "ph_max": 6.5,
				"ec_min": 0.6, "ec_max": 1.0,
				"light_dli": 12,
				"notes": "Keep moist, warm"
			},
			"vegetative": {
				"duration_days": 21,
				"temp_min": 20, "temp_max": 28,
				"humidity_min": 45, "humidity_max": 65,
				"ph_min": 5.5, "ph_max": 6.5,
				"ec_min": 1.0, "ec_max": 1.6,
				"light_dli": 18,
				"notes": "Pinch flowers, harvest from top"
			}
		}
	},
	"strawberry": {
		"name": "Strawberry",
		"scientific": "Fragaria × ananassa",
		"days_to_harvest": 90,
		"stages": {
			"vegetative": {
				"duration_days": 30,
				"temp_min": 15, "temp_max": 22,
				"humidity_min": 50, "humidity_max": 70,
				"ph_min": 5.5, "ph_max": 6.5,
				"ec_min": 1.0, "ec_max": 1.5,
				"light_dli": 18,
				"notes": "Establish runners, strong roots"
			},
			"flowering": {
				"duration_days": 21,
				"temp_min": 15, "temp_max": 24,
				"humidity_min": 40, "humidity_max": 60,
				"ph_min": 5.8, "ph_max": 6.2,
				"ec_min": 1.2, "ec_max": 1.8,
				"light_dli": 22,
				"notes": "Pollinate by hand or with fans"
			},
			"fruiting": {
				"duration_days": 40,
				"temp_min": 15, "temp_max": 25,
				"humidity_min": 50, "humidity_max": 65,
				"ph_min": 5.8, "ph_max": 6.2,
				"ec_min": 1.0, "ec_max": 1.4,
				"notes": "Lower EC for sweeter fruit"
			}
		}
	}
}

def get_plant_profile(plant_id: str) -> dict | None:
	"""Get profile for a specific plant."""
	return PLANT_PROFILES.get(plant_id.lower())

def get_stage_targets(plant_id: str, stage: str) -> dict | None:
	"""Get optimal targets for a plant at a specific growth stage."""
	profile = get_plant_profile(plant_id)
	if profile and stage in profile["stages"]:
		return profile["stages"][stage]
	return None

def list_available_plants() -> list:
	"""List all available plant profiles."""
	return [{"id": k, "name": v["name"], "days": v["days_to_harvest"]} for k, v in PLANT_PROFILES.items()]

def check_condition_optimal(plant_id: str, stage: str, sensor_data: dict) -> dict:
	"""
	Check if current conditions are optimal for the given plant/stage.
	Returns a dict with status for each parameter.
	"""
	targets = get_stage_targets(plant_id, stage)
	if not targets:
		return {"error": "Unknown plant or stage"}

	results = {}

	# Temperature
	temp = sensor_data.get("temperature", 0)
	if temp < targets["temp_min"]:
		results["temperature"] = {"status": "low", "value": temp, "target": f"{targets['temp_min']}-{targets['temp_max']}°C"}
	elif temp > targets["temp_max"]:
		results["temperature"] = {"status": "high", "value": temp, "target": f"{targets['temp_min']}-{targets['temp_max']}°C"}
	else:
		results["temperature"] = {"status": "optimal", "value": temp}

	# pH
	ph = sensor_data.get("ph_level", 0)
	if ph < targets["ph_min"]:
		results["ph"] = {"status": "low", "value": ph, "target": f"{targets['ph_min']}-{targets['ph_max']}"}
	elif ph > targets["ph_max"]:
		results["ph"] = {"status": "high", "value": ph, "target": f"{targets['ph_min']}-{targets['ph_max']}"}
	else:
		results["ph"] = {"status": "optimal", "value": ph}

	# EC
	ec = sensor_data.get("ec_level", 0)
	if ec < targets["ec_min"]:
		results["ec"] = {"status": "low", "value": ec, "target": f"{targets['ec_min']}-{targets['ec_max']} mS/cm"}
	elif ec > targets["ec_max"]:
		results["ec"] = {"status": "high", "value": ec, "target": f"{targets['ec_min']}-{targets['ec_max']} mS/cm"}
	else:
		results["ec"] = {"status": "optimal", "value": ec}

	# Humidity
	humidity = sensor_data.get("humidity", 0)
	if humidity < targets["humidity_min"]:
		results["humidity"] = {"status": "low", "value": humidity, "target": f"{targets['humidity_min']}-{targets['humidity_max']}%"}
	elif humidity > targets["humidity_max"]:
		results["humidity"] = {"status": "high", "value": humidity, "target": f"{targets['humidity_min']}-{targets['humidity_max']}%"}
	else:
		results["humidity"] = {"status": "optimal", "value": humidity}

	# Overall score
	optimal_count = sum(1 for v in results.values() if v.get("status") == "optimal")
	results["overall_score"] = optimal_count / len(results) if results else 0
	results["notes"] = targets.get("notes", "")

	return results
