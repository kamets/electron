# 📚 Agent Knowledge Base - "The Digital Almanac"

**Purpose**: Central data sources for agents to reference when making predictions
**Inspired by**: Farmer's Almanac (weather, planting calendars, market data)
**For**: Architect Agent + all specialists to make informed decisions

---

## 🌦️ **WEATHER & CLIMATE DATA**

### **1. OpenWeatherMap API** ⭐⭐⭐⭐⭐
**What**: Real-time & forecast weather globally
**Free Tier**: 1000 calls/day
**Data**: Temp, humidity, rainfall, wind
**Python**: `pip install pyowm`

```python
from pyowm import OWM

owm = OWM('your-api-key')
weather = owm.weather_at_place('Seattle,US')
temp = weather.temperature('celsius')
humidity = weather.humidity
```

**Agent Use**: "Based on forecast, recommend harvest in 2 days before rain"

---

### **2. NASA POWER (Free!)** ⭐⭐⭐⭐⭐
**What**: Historical weather data for agriculture
**Free**: Yes, unlimited
**Data**: Solar radiation, temp, rainfall (1981-present)
**Python**: Built into PCSE

```python
from pcse.db import NASAPowerWeatherDataProvider

weather = NASAPowerWeatherDataProvider(latitude=47.6, longitude=-122.3)
```

**Agent Use**: "Historical frost dates suggest plant after March 15"

---

## 🌱 **PLANTING CALENDARS**

### **3. USDA Plant Hardiness Zones**
**What**: Zone-based planting guides
**Data**: Frost dates, suitable crops per zone
**Source**: USDA website (can scrape or use static data)

```python
PLANTING_ZONES = {
    "Zone 8": {
        "last_frost": "March 15",
        "first_frost": "November 15",
        "suitable_crops": ["tomato", "lettuce", "herbs", "cucumber"]
    }
}
```

**Agent Use**: "You're in Zone 8 - plant tomatoes after March 15"

---

### **4. Moon Phase Data** (Lunar Planting)
**What**: Moon phases for traditional planting
**Python**: `pip install astral`

```python
from astral import moon

phase = moon.phase()  # 0-28 (new moon to full moon)

if phase < 7:
    planting_advice = "New moon - ideal for leafy greens"
elif phase < 14:
    planting_advice = "Waxing moon - plant above-ground crops"
```

**Agent Use**: "Lunar calendar suggests planting greens this week"

---

## 💰 **MARKET PRICES & ECONOMICS**

### **5. Commodities API** ⭐⭐⭐⭐
**What**: Real-time commodity prices (corn, wheat, etc.)
**Python**: `pip install commodities-api`
**Price**: Free tier available

```python
from commodities_api import Client

client = Client('your-api-key')
prices = client.latest(['WHEAT', 'CORN', 'SOY'])

wheat_price = prices['WHEAT']  # USD per bushel
```

**Agent Use**: "Wheat prices up 12% - consider switching to wheat next cycle"

---

### **6. USDA Market News**
**What**: Agricultural market reports
**API**: USDA Market News API (free)
**Data**: Prices, supply/demand, trends

**Agent Use**: "Local tomato prices $2.50/lb - project $1200 revenue this harvest"

---

## 📊 **CROP SCIENCE DATA**

### **7. PCSE Crop Models** (Already Covered)
**What**: Scientific growth models
**Data**: Phenology, yield predictions, nutrient needs

**Agent Use**: "WOFOST model predicts 450kg yield at current growth rate"

---

### **8. Plant Nutrition Database (noms)**
**What**: USDA nutrition requirements
**Data**: N-P-K needs, micronutrients

**Agent Use**: "Lettuce requires 150-50-100 NPK in vegetative stage"

---

## 🤖 **AGENT INTEGRATION PLAN**

### **How Agents Use This Data:**

```python
# backend/agents/architect/knowledge_base.py

class AgentKnowledgeBase:
    """
    Central data hub for all agents.
    Like a digital Farmer's Almanac.
    """

    def __init__(self):
        self.weather_api = OpenWeatherMap('api-key')
        self.price_api = CommoditiesAPI('api-key')
        self.planting_zones = self._load_usda_zones()
        self.crop_models = PCSE()

    def get_planting_recommendation(self, location, crop_type):
        """
        Agent asks: "Should I plant tomatoes today?"

        Checks:
        1. Weather forecast (frost risk?)
        2. Hardiness zone (suitable?)
        3. Moon phase (traditional timing)
        4. Market prices (is it profitable?)
        5. Crop model (days to harvest)

        Returns: "Yes, plant now" or "Wait until March 20"
        """
        # Get frost risk
        forecast = self.weather_api.get_forecast(location, days=14)
        frost_risk = any(day['temp_min'] < 0 for day in forecast)

        # Check hardiness zone
        zone = self.get_zone(location)
        suitable = crop_type in zone['suitable_crops']

        # Get market price
        price = self.price_api.get_price('TOMATO')
        profitable = price > 2.00  # threshold

        # Combine all factors
        if frost_risk:
            return "❌ Wait - frost risk in next 14 days"
        elif not suitable:
            return f"❌ {crop_type} not suitable for Zone {zone['id']}"
        elif not profitable:
            return f"⚠️ Low prices (${price}/lb) - consider waiting"
        else:
            harvest_days = self.crop_models.predict_harvest(crop_type)
            return f"✅ Plant now - harvest in {harvest_days} days, project ${price * 100} revenue"
```

---

## 📋 **DATA INTEGRATION TIERS**

### **Tier 1: Essential (Implement First)** ⭐⭐⭐⭐⭐
- ✅ PCSE crop models (growth predictions)
- ✅ OpenWeatherMap (weather)
- ✅ Static planting zones (USDA data)

**Why**: Cover 80% of use cases, all free/cheap

---

### **Tier 2: Enhanced (Add Later)** ⭐⭐⭐⭐
- Commodities API (market prices)
- Moon phases (traditional planting)
- NASA POWER (historical weather)

**Why**: Adds depth, still manageable complexity

---

### **Tier 3: Advanced (Future)** ⭐⭐⭐
- Machine learning price predictions
- Satellite imagery analysis
- IoT sensor fusion

**Why**: Nice to have, not critical

---

## 💾 **INSTALLATION (Tier 1)**

```bash
# Lightweight almanac stack
uv pip install PCSE pyowm

# Total: ~7MB
```

**API Keys Needed** (all have free tiers):
- OpenWeatherMap: [openweathermap.org/api](https://openweathermap.org/api)

---

## 🎯 **AGENT DECISION EXAMPLE**

**Scenario**: Foreman asks "Should I plant lettuce today?"

**Agent thinks** (using Knowledge Base):
1. ✅ **Weather**: No frost in 14-day forecast
2. ✅ **Zone**: Lettuce suitable for Zone 8
3. ✅ **Moon**: Waxing moon (good for leafy greens)
4. ✅ **Price**: Lettuce at $3.50/lb (profitable)
5. ✅ **Model**: 45 days to harvest, yield 150kg predicted

**Agent says**:
> "✅ **PLANT NOW**
> - Weather clear for 14 days
> - Harvest in 45 days (March 8)
> - Projected yield: 150kg
> - Market price: $3.50/lb
> - **Estimated revenue: $1,150**"

**Instead of**: "Temperature is 24.5°C" (useless!)

---

## 📈 **VALUE TO FOREMAN**

**Before** (dumb system):
```
Temperature: 24.5°C
Humidity: 62%
```

**After** (smart almanac):
```
✅ OPTIMAL CONDITIONS
Plant lettuce today for:
- Harvest: March 8
- Yield: 150kg
- Revenue: $1,150
- Weather: Clear 14 days
```

**Decision**: Clear yes/no with $ attached!

---

## 🚀 **RECOMMENDATION**

**Start with Tier 1**:
1. PCSE (growth models) ✅
2. OpenWeatherMap (forecast) ✅
3. Static USDA zone data ✅

**Result**: Agents give **actionable** recommendations with **revenue projections**

**Want me to implement Tier 1 now?** (30 min to integrate)
