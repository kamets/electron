"""
Climate Database - Sacramento, Northern California
Historical averages for realistic greenhouse simulation baseline.
Data based on NOAA climate normals for Sacramento Executive Airport (KSAC).
"""

# Monthly climate data for Sacramento, CA
# Source: NOAA Climate Normals 1991-2020
SACRAMENTO_CLIMATE = {
	1: {  # January
		"month_name": "January",
		"avg_high_c": 12.8,
		"avg_low_c": 3.9,
		"avg_temp_c": 8.3,
		"avg_humidity": 82,
		"avg_precip_mm": 103,
		"rainy_days": 10,
		"sunshine_hours": 5.0,
		"sunrise": "07:20",
		"sunset": "17:10"
	},
	2: {  # February
		"month_name": "February",
		"avg_high_c": 15.6,
		"avg_low_c": 5.0,
		"avg_temp_c": 10.3,
		"avg_humidity": 76,
		"avg_precip_mm": 89,
		"rainy_days": 9,
		"sunshine_hours": 6.5,
		"sunrise": "06:55",
		"sunset": "17:50"
	},
	3: {  # March
		"month_name": "March",
		"avg_high_c": 18.3,
		"avg_low_c": 6.7,
		"avg_temp_c": 12.5,
		"avg_humidity": 68,
		"avg_precip_mm": 69,
		"rainy_days": 8,
		"sunshine_hours": 8.0,
		"sunrise": "06:15",
		"sunset": "18:25"
	},
	4: {  # April
		"month_name": "April",
		"avg_high_c": 22.2,
		"avg_low_c": 8.3,
		"avg_temp_c": 15.3,
		"avg_humidity": 58,
		"avg_precip_mm": 30,
		"rainy_days": 5,
		"sunshine_hours": 10.0,
		"sunrise": "05:25",
		"sunset": "19:00"
	},
	5: {  # May
		"month_name": "May",
		"avg_high_c": 27.2,
		"avg_low_c": 11.1,
		"avg_temp_c": 19.2,
		"avg_humidity": 48,
		"avg_precip_mm": 13,
		"rainy_days": 3,
		"sunshine_hours": 11.5,
		"sunrise": "04:50",
		"sunset": "19:35"
	},
	6: {  # June
		"month_name": "June",
		"avg_high_c": 32.2,
		"avg_low_c": 14.4,
		"avg_temp_c": 23.3,
		"avg_humidity": 42,
		"avg_precip_mm": 5,
		"rainy_days": 1,
		"sunshine_hours": 12.5,
		"sunrise": "04:40",
		"sunset": "20:00"
	},
	7: {  # July
		"month_name": "July",
		"avg_high_c": 35.0,
		"avg_low_c": 16.1,
		"avg_temp_c": 25.6,
		"avg_humidity": 40,
		"avg_precip_mm": 0,
		"rainy_days": 0,
		"sunshine_hours": 12.8,
		"sunrise": "04:55",
		"sunset": "19:55"
	},
	8: {  # August
		"month_name": "August",
		"avg_high_c": 34.4,
		"avg_low_c": 15.6,
		"avg_temp_c": 25.0,
		"avg_humidity": 43,
		"avg_precip_mm": 0,
		"rainy_days": 0,
		"sunshine_hours": 11.8,
		"sunrise": "05:20",
		"sunset": "19:25"
	},
	9: {  # September
		"month_name": "September",
		"avg_high_c": 31.7,
		"avg_low_c": 13.9,
		"avg_temp_c": 22.8,
		"avg_humidity": 47,
		"avg_precip_mm": 5,
		"rainy_days": 1,
		"sunshine_hours": 10.0,
		"sunrise": "05:50",
		"sunset": "18:40"
	},
	10: {  # October
		"month_name": "October",
		"avg_high_c": 25.6,
		"avg_low_c": 10.0,
		"avg_temp_c": 17.8,
		"avg_humidity": 55,
		"avg_precip_mm": 23,
		"rainy_days": 4,
		"sunshine_hours": 8.0,
		"sunrise": "06:20",
		"sunset": "17:50"
	},
	11: {  # November
		"month_name": "November",
		"avg_high_c": 16.7,
		"avg_low_c": 5.6,
		"avg_temp_c": 11.1,
		"avg_humidity": 72,
		"avg_precip_mm": 53,
		"rainy_days": 7,
		"sunshine_hours": 5.5,
		"sunrise": "06:55",
		"sunset": "17:00"
	},
	12: {  # December
		"month_name": "December",
		"avg_high_c": 12.2,
		"avg_low_c": 3.3,
		"avg_temp_c": 7.8,
		"avg_humidity": 82,
		"avg_precip_mm": 84,
		"rainy_days": 9,
		"sunshine_hours": 4.5,
		"sunrise": "07:20",
		"sunset": "16:50"
	}
}

def get_month_climate(month: int) -> dict:
	"""Get climate data for a specific month (1-12)."""
	return SACRAMENTO_CLIMATE.get(month, SACRAMENTO_CLIMATE[1])

def get_daily_weather(month: int, day_of_month: int = 1) -> dict:
	"""
	Generate realistic daily weather based on monthly averages.
	Adds variation for more realistic simulation.
	"""
	import random
	import math

	climate = get_month_climate(month)

	# Daily variation (warmer mid-month, cooler at edges - simplified season curve)
	day_offset = (day_of_month - 15) / 15.0  # -1 to +1
	seasonal_adjust = day_offset * 1.5  # ±1.5°C variation through month

	# Random daily variation
	daily_variation = random.uniform(-3.0, 3.0)

	high = climate["avg_high_c"] + seasonal_adjust + daily_variation
	low = climate["avg_low_c"] + seasonal_adjust + daily_variation * 0.5

	# Weather condition based on rainy days probability
	rain_chance = climate["rainy_days"] / 30.0
	if random.random() < rain_chance:
		condition = "rain"
	elif random.random() < 0.3:
		condition = "overcast"
	else:
		condition = "sunny"

	# Humidity adjustment based on weather
	humidity = climate["avg_humidity"]
	if condition == "rain":
		humidity = min(95, humidity + 15)
	elif condition == "sunny":
		humidity = max(30, humidity - 10)

	return {
		"month": month,
		"month_name": climate["month_name"],
		"high_c": round(high, 1),
		"low_c": round(low, 1),
		"humidity": round(humidity),
		"condition": condition,
		"sunrise": climate["sunrise"],
		"sunset": climate["sunset"],
		"sunshine_hours": climate["sunshine_hours"]
	}

def get_temp_for_hour(month: int, hour: float, condition: str = "sunny") -> float:
	"""
	Calculate realistic temperature for a specific hour of day.
	Uses sinusoidal curve peaking at ~15:00 (3 PM).
	"""
	import math

	climate = get_month_climate(month)
	high = climate["avg_high_c"]
	low = climate["avg_low_c"]

	# Temperature follows sin curve, min at 6am, max at 3pm
	# Shift so 6am = min, 15 (3pm) = max
	hour_adjusted = hour - 6  # 0 = 6am
	if hour_adjusted < 0:
		hour_adjusted += 24

	# Use sine wave: min at 0 (6am), max at 9 (3pm)
	if hour_adjusted <= 9:
		temp_ratio = math.sin(hour_adjusted / 9 * math.pi / 2)
	else:
		# Cooling after 3pm
		temp_ratio = math.cos((hour_adjusted - 9) / 15 * math.pi / 2)

	temp = low + (high - low) * temp_ratio

	# Weather affects temperature
	if condition == "overcast":
		temp -= 3.0
	elif condition == "rain":
		temp -= 6.0

	return round(temp, 1)

# Seasonal growing recommendations for Sacramento
GROWING_SEASONS = {
	"tomato": {"best_months": [4, 5, 6, 7, 8], "avoid_months": [11, 12, 1, 2]},
	"lettuce": {"best_months": [2, 3, 4, 10, 11], "avoid_months": [6, 7, 8]},
	"pepper": {"best_months": [4, 5, 6, 7, 8], "avoid_months": [11, 12, 1, 2]},
	"cucumber": {"best_months": [4, 5, 6, 7, 8, 9], "avoid_months": [11, 12, 1, 2]},
	"basil": {"best_months": [4, 5, 6, 7, 8, 9], "avoid_months": [11, 12, 1]},
	"strawberry": {"best_months": [3, 4, 5, 9, 10], "avoid_months": [7, 8]}
}

def is_good_growing_season(plant_id: str, month: int) -> dict:
	"""Check if it's a good time to grow a specific plant."""
	seasons = GROWING_SEASONS.get(plant_id.lower(), {})
	best = seasons.get("best_months", [])
	avoid = seasons.get("avoid_months", [])

	if month in best:
		return {"status": "excellent", "message": f"Great time to grow {plant_id}!"}
	elif month in avoid:
		return {"status": "poor", "message": f"Not recommended for {plant_id} this month - greenhouse climate control needed."}
	else:
		return {"status": "moderate", "message": f"Acceptable season for {plant_id} with minor adjustments."}
