// _SUDOTEER Greenhouse Digital Twin Monitor
// Real-time visualization + bidirectional control

class GreenhouseMonitor {
	constructor() {
		this.container = document.getElementById('greenhouse-panel');
		if (!this.container) {
			console.warn('GreenhouseMonitor: No #greenhouse-panel found');
			return;
		}
		this.pumpActive = false;
		this.init();
	}

	init() {
		this.render();
		this.bindEvents();
	}

	render() {
		this.container.innerHTML = `
			<div class="glass-card industrial-card transition-all hover-lift">
				<div class="card-header">
					<h3 class="text-gradient">🌿 Greenhouse Twin</h3>
					<div id="gh-connection-status" class="status-dot"></div>
				</div>

				<div class="gauges-grid">
					<div class="metric-box transition-all hover-scale animate-fade-in stagger-1">
						<span class="label">TEMP</span>
						<div class="value counter"><span id="gh-temp">--</span>°C</div>
					</div>

					<div class="metric-box transition-all hover-scale animate-fade-in stagger-2">
						<span class="label">HUMIDITY</span>
						<div class="value counter"><span id="gh-humid">--</span>%</div>
					</div>

					<div class="metric-box metric-wide transition-all hover-scale animate-fade-in stagger-3">
						<span class="label">pH LEVEL</span>
						<div class="value counter"><span id="gh-ph">--</span></div>
						<div class="bar-container">
							<div id="ph-bar" class="bar-fill transition-all"></div>
						</div>
					</div>

					<div class="metric-box transition-all hover-scale animate-fade-in stagger-4">
						<span class="label">HEALTH</span>
						<div class="value counter"><span id="gh-health">--</span>%</div>
					</div>
				</div>

				<div class="control-panel animate-fade-in stagger-5">
					<div class="pressure-display">
						<span class="label">Water Pressure</span>
						<span class="pressure-value counter"><span id="gh-psi">0</span> PSI</span>
					</div>

					<button id="btn-pump-toggle" class="btn-industrial transition-fast btn-ripple">
						<span class="btn-icon">🚿</span>
						<span class="btn-text">START PUMP</span>
					</button>
				</div>

				<div class="metrics-footer animate-fade-in stagger-5">
					<span class="micro-stat">⚡ <span id="gh-power" class="counter">0</span> kWh</span>
					<span class="micro-stat">🌱 Stress: <span id="gh-stress" class="counter">0</span>%</span>
				</div>
			</div>
		`;
	}

	bindEvents() {
		const btn = document.getElementById('btn-pump-toggle');

		// 1. LISTEN: Receive Telemetry from Python
		if (window.sudoteerAPI) {
			window.sudoteerAPI.onAgentUpdate((payload) => {
				if (payload.event === 'GREENHOUSE_TELEMETRY') {
					this.updateDisplay(payload.data);
					// Also update control panel displays
					if (typeof updateTelemetryDisplay === 'function') {
						updateTelemetryDisplay(payload.data);
					}
				}
			});
		} else {
			console.warn('sudoteerAPI not available - running in dev mode');
		}

		// 2. ACT: Send Commands to Python (with USER OVERRIDE)
		btn.addEventListener('click', async () => {
			const action = this.pumpActive ? 'STOP_PUMP' : 'START_PUMP';
			const newValue = !this.pumpActive;

			// Use new actuator API with user override
			try {
				const response = await fetch('/api/actuator', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						name: 'pump_active',
						value: newValue,
						action: 'set'
					})
				});
				const result = await response.json();
				console.log(`🔒 Pump ${newValue ? 'ON' : 'OFF'} - User Override Active:`, result.override_active);

				// Immediate UI feedback
				this.pumpActive = newValue;
				this.updatePumpButton();

			} catch (e) {
				console.error('Pump control failed:', e);
				// Fallback to old WebSocket method
				if (window.sudoteerAPI) {
					window.sudoteerAPI.sendCommand('AGENT_MSG', {
						target: 'greenhouse_sim',
						action: action
					});
				}
			}
		});
	}

	updatePumpButton() {
		const btn = document.getElementById('btn-pump-toggle');
		const btnText = btn.querySelector('.btn-text');
		const btnIcon = btn.querySelector('.btn-icon');

		if (this.pumpActive) {
			btnText.innerText = "STOP PUMP 🔒";
			btnIcon.innerText = "🛑";
			btn.classList.add('active');
			btn.style.borderColor = '#ef4444';
			btn.style.color = '#ef4444';
		} else {
			btnText.innerText = "START PUMP";
			btnIcon.innerText = "🚿";
			btn.classList.remove('active');
			btn.style.borderColor = '#22c55e';
			btn.style.color = '#22c55e';
		}
	}

	updateDisplay(data) {
		// Update numeric displays
		document.getElementById('gh-temp').innerText = data.temperature.toFixed(1);
		document.getElementById('gh-humid').innerText = data.humidity.toFixed(1);
		document.getElementById('gh-ph').innerText = data.ph_level.toFixed(2);
		document.getElementById('gh-psi').innerText = data.water_pressure.toFixed(1);
		document.getElementById('gh-health').innerText = (data.plant_health * 100).toFixed(0);
		document.getElementById('gh-stress').innerText = (data.stress_index * 100).toFixed(0);
		document.getElementById('gh-power').innerText = data.power_kwh.toFixed(3);

		// Update pH Bar (Visual indicator)
		const phBar = document.getElementById('ph-bar');
		const phPercent = (data.ph_level / 14) * 100;
		phBar.style.width = `${phPercent}%`;

		// pH Color coding: Green = optimal (5.5-7.5), Yellow = warning, Red = danger
		if (data.ph_level < 5.5 || data.ph_level > 7.5) {
			phBar.style.backgroundColor = '#ef4444'; // Red - out of range
		} else if (data.ph_level < 6.0 || data.ph_level > 7.0) {
			phBar.style.backgroundColor = '#f59e0b'; // Yellow - suboptimal
		} else {
			phBar.style.backgroundColor = '#22c55e'; // Green - optimal
		}

		// Update Pump Button State
		this.pumpActive = data.pump_status;
		const btn = document.getElementById('btn-pump-toggle');
		const btnText = btn.querySelector('.btn-text');
		const btnIcon = btn.querySelector('.btn-icon');

		if (this.pumpActive) {
			btnText.innerText = "STOP PUMP";
			btnIcon.innerText = "🛑";
			btn.classList.add('active');
			btn.style.borderColor = '#ef4444';
			btn.style.color = '#ef4444';
		} else {
			btnText.innerText = "START PUMP";
			btnIcon.innerText = "🚿";
			btn.classList.remove('active');
			btn.style.borderColor = '#22c55e';
			btn.style.color = '#22c55e';
		}

		// Update connection status indicator
		const statusDot = document.getElementById('gh-connection-status');
		statusDot.style.backgroundColor = '#22c55e';
		statusDot.style.boxShadow = '0 0 8px #22c55e';
	}
}

// Auto-initialize if container exists
if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', () => {
		window.greenhouseMonitor = new GreenhouseMonitor();
	});
} else {
	window.greenhouseMonitor = new GreenhouseMonitor();
}
