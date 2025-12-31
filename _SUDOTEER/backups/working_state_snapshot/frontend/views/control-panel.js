/**
 * Control Panel - Actuator UI Controls
 * Handles toggle buttons, displays, and manual override system
 */

class ControlPanel {
	constructor() {
		this.overrides = {};
		this.init();
	}

	init() {
		// Bind crop selector
		const cropSelect = document.getElementById('crop-select');
		if (cropSelect) {
			cropSelect.addEventListener('change', (e) => this.changeCrop(e.target.value));
		}

		// Start telemetry updates
		this.startTelemetryPolling();
	}

	async startTelemetryPolling() {
		// Poll every 2 seconds for telemetry updates
		setInterval(async () => {
			await this.updateDisplays();
		}, 2000);

		// Initial update
		await this.updateDisplays();
	}

	async updateDisplays() {
		try {
			// Fetch simulation state
			const response = await fetch('/api/status');
			const data = await response.json();

			// For now, we'll update via WebSocket telemetry
			// This is a fallback polling mechanism
		} catch (e) {
			console.error('Telemetry update failed:', e);
		}
	}

	async toggleActuator(name) {
		try {
			const response = await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name, action: 'toggle' })
			});
			const result = await response.json();

			if (result.override_active) {
				this.showOverrideIndicator(name, result.value);
			}

			return result;
		} catch (e) {
			console.error('Toggle failed:', e);
		}
	}

	async clearOverride(name) {
		try {
			const response = await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name, action: 'clear_override' })
			});
			return await response.json();
		} catch (e) {
			console.error('Clear override failed:', e);
		}
	}

	async clearAllOverrides() {
		try {
			const response = await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ action: 'clear_all' })
			});
			return await response.json();
		} catch (e) {
			console.error('Clear all overrides failed:', e);
		}
	}

	showOverrideIndicator(name, value) {
		console.log(`🔒 Override active: ${name} = ${value}`);
		// Could add visual indicator here (e.g., orange border on button)
	}

	async changeCrop(plantId) {
		try {
			// Send goal to supervisor to change crop
			const response = await fetch('/api/goal', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ goal: `Switch to growing ${plantId}` })
			});
			const result = await response.json();
			console.log('Crop change result:', result);

			// Update stage display
			const stageEl = document.getElementById('crop-stage');
			if (stageEl) {
				stageEl.textContent = 'Stage: Seedling';
			}
		} catch (e) {
			console.error('Crop change failed:', e);
		}
	}
}

// Update telemetry displays from WebSocket data
function updateTelemetryDisplay(data) {
	// Time & Day
	const simTimeEl = document.getElementById('sim-time');
	if (simTimeEl && data.environment) {
		const env = data.environment;
		const hour = Math.floor(env.sim_hour || 6);
		const minute = Math.floor(((env.sim_hour || 6) % 1) * 60);
		simTimeEl.textContent = `Day ${env.sim_day || 1} · ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
	}

	// Weather
	const weatherIconEl = document.getElementById('weather-icon');
	const weatherTextEl = document.getElementById('weather-text');
	if (weatherIconEl && data.environment) {
		const weather = data.environment.weather || 'sunny';
		const icons = { 'sunny': '☀️', 'overcast': '☁️', 'rain': '🌧️' };
		weatherIconEl.textContent = icons[weather] || '☀️';
		if (weatherTextEl) {
			weatherTextEl.textContent = weather.charAt(0).toUpperCase() + weather.slice(1);
		}
	}

	// Outside temp
	const outsideTempEl = document.getElementById('outside-temp');
	if (outsideTempEl && data.environment) {
		outsideTempEl.textContent = `${(data.environment.outside_temp || 18).toFixed(1)}°C`;
	}

	// Humidity
	const humidityEl = document.getElementById('humidity-value');
	if (humidityEl && data.state) {
		humidityEl.textContent = `${(data.state.humidity || 50).toFixed(0)}%`;
	}

	// Plant health
	const healthEl = document.getElementById('plant-health');
	if (healthEl && data.state) {
		const health = (data.state.plant_health || 1) * 100;
		healthEl.textContent = `${health.toFixed(0)}%`;
		healthEl.className = health > 70 ? 'value secure' : health > 40 ? 'value warning' : 'value danger';
	}

	// Crop stage
	const stageEl = document.getElementById('crop-stage');
	if (stageEl && data.crop) {
		stageEl.textContent = `Stage: ${(data.crop.stage || 'vegetative').charAt(0).toUpperCase() + (data.crop.stage || 'vegetative').slice(1)}`;
	}
}

// Initialize on page load
const controlPanel = new ControlPanel();

// Hook into WebSocket telemetry (if bridge.js is loaded)
if (window.sudoteerAPI) {
	window.sudoteerAPI.onTelemetry = updateTelemetryDisplay;
}
