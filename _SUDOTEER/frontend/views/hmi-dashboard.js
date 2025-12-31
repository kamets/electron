/**
 * HMI Dashboard - Industrial Control Panel
 * Handles 24h graphs, vertical bar gauges, and telemetry updates
 */

class HMIDashboard {
	constructor() {
		// Data history for 24h graphs (last 24 data points)
		this.history = {
			lux: [],
			humidity: [],
			temperature: [],
			watering: [],
			nutriA: [],
			nutriB: [],
			phDown: []
		};
		this.maxHistoryPoints = 24;

		// Current values
		this.values = {
			lux: 88,
			humidity: 63,
			tempIn: 25,
			tempOut: 27,
			nutriA: 89,
			nutriB: 59,
			phDown: 75,
			pumpActive: false,
			lightsOn: true
		};

		// Map for debounced save functions (per setting key)
		this.saveTimeouts = {};

		this.init();
	}

	init() {
		this.bindEvents();
		this.initGraphs();
		this.startClock();
		this.startTelemetryPolling();

		// Initialize with some history data
		this.generateInitialHistory();
		this.updateAllDisplays();

		// Startup status log
		this.addLogEntry('System Ready: MEWTOCOL BCC Insurance Active');
	}

	bindEvents() {
		// Water Pump toggle (in pH & Water Control card)
		const waterPumpBtn = document.getElementById('water-pump-toggle');
		if (waterPumpBtn) {
			waterPumpBtn.addEventListener('click', () => this.toggleWaterPump());
		}

		// Light button toggle (Main Dashboard)
		const lightBtn = document.getElementById('light-toggle');
		if (lightBtn) {
			lightBtn.addEventListener('click', () => this.toggleLightBtn());
		}

		// Nutrient toggles
		['nutri-a', 'nutri-b', 'ph-down'].forEach(id => {
			const toggle = document.getElementById(`${id}-toggle`);
			if (toggle) {
				toggle.addEventListener('change', (e) => this.toggleNutrient(id, e.target.checked));
			}
		});

		// Theme toggle - Sun/Moon buttons
		const dayBtn = document.getElementById('day-mode');
		const nightBtn = document.getElementById('night-mode');

		if (dayBtn) {
			dayBtn.addEventListener('click', () => this.setTheme('light'));
		}
		if (nightBtn) {
			nightBtn.addEventListener('click', () => this.setTheme('dark'));
		}

		// Time range toggles (24H / DAILY / WEEKLY)
		document.querySelectorAll('.time-range-toggle').forEach(container => {
			const graphType = container.dataset.graph;
			container.querySelectorAll('.range-btn').forEach(btn => {
				btn.addEventListener('click', (e) => this.switchTimeRange(graphType, e.target.dataset.range, container));
			});
		});

		// Initialize vertical sliders for pump speed control
		this.initVerticalSliders();

		// Initialize expandable cards with long-press detection for full-screen modal
		this.initExpandableCards();
	}

	initExpandableCards() {
		const expandableCards = document.querySelectorAll('.expandable-card');
		const HOLD_DURATION = 500; // 500ms hold to expand

		expandableCards.forEach(card => {
			let holdTimer = null;
			let isHolding = false;

			// Long press to open full-screen modal
			const startHold = (e) => {
				// Don't expand if interacting with sliders or controls
				if (e.target.closest('.vertical-slider') ||
					e.target.closest('.toggle-switch') ||
					e.target.closest('.setting-select') ||
					e.target.closest('.setting-input')) {
					return;
				}

				isHolding = true;
				card.classList.add('pressing');
				holdTimer = setTimeout(() => {
					if (isHolding) {
						card.classList.remove('pressing');
						const modalType = card.dataset.modal;
						this.openFullscreenModal(modalType, card);
					}
				}, HOLD_DURATION);
			};

			const cancelHold = () => {
				isHolding = false;
				card.classList.remove('pressing');
				if (holdTimer) {
					clearTimeout(holdTimer);
					holdTimer = null;
				}
			};

			// Mouse events
			card.addEventListener('mousedown', startHold);
			card.addEventListener('mouseup', cancelHold);
			card.addEventListener('mouseleave', cancelHold);

			// Touch events
			card.addEventListener('touchstart', startHold, { passive: true });
			card.addEventListener('touchend', cancelHold);
			card.addEventListener('touchcancel', cancelHold);
		});

		// Modal close button
		const closeBtn = document.getElementById('modal-close');
		if (closeBtn) {
			closeBtn.addEventListener('click', () => this.closeFullscreenModal());
		}

		// Click backdrop to close
		const backdrop = document.querySelector('.modal-backdrop');
		if (backdrop) {
			backdrop.addEventListener('click', () => this.closeFullscreenModal());
		}
	}

	async openFullscreenModal(type, card) {
		const modal = document.getElementById('fullscreen-modal');
		const title = document.getElementById('modal-title');
		const body = document.getElementById('modal-body');

		if (!modal || !title || !body) return;

		// Helper to create a tactile stepper (arrow on each side)
		const createStepper = (key, value, unit = 'mL', min = 1, max = 500, step = 1) => `
			<div class="setting-row">
				<span>${key}</span>
				<div class="tactile-stepper" data-key="${key}">
					<button class="step-btn down" onclick="hmiDashboard.adjustStepper(this, -${step}, ${min}, ${max})">
						<i class="fas fa-chevron-left"></i>
					</button>
					<div class="step-value-container">
						<input type="number" class="setting-input step-input" data-key="${key}" value="${value}" min="${min}" max="${max}" step="${step}">
						<span class="step-unit">${unit}</span>
					</div>
					<button class="step-btn up" onclick="hmiDashboard.adjustStepper(this, ${step}, ${min}, ${max})">
						<i class="fas fa-chevron-right"></i>
					</button>
				</div>
			</div>
		`;

		const createUsageBars = (data) => `
			<div class="usage-history-bars">
				${['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, i) => `
					<div class="usage-bar-group">
						<div class="usage-bar" style="height: ${data[i] || 0}%"></div>
						<span class="usage-day">${day}</span>
					</div>
				`).join('')}
			</div>
		`;

		// Set title and content based on type
		if (type === 'nutrient-settings') {
			title.textContent = 'NUTRIENT PUMP SETTINGS';
			body.innerHTML = `
				<div class="pump-configs-row">
					<div class="modal-section pump-config-box">
						<h3>PUMP A Configuration</h3>
						<div class="setting-row"><span>PLC Control ID</span><input type="text" class="setting-input hardware-id" data-key="PLC Control ID" value="PLC_PUMP_1" placeholder="e.g. DT0"></div>
						<div class="setting-row"><span>Interval</span><select class="setting-select" data-key="Interval"><option>AT EVERY WATERING</option><option>Every 1 hr</option><option>Every 2 hr</option></select></div>
						${createStepper('Dose Amount', 10, 'mL', 1, 100)}
						${createStepper('Max Daily Dose', 100, 'mL', 10, 1000, 10)}
					</div>
					<div class="modal-section pump-config-box">
						<h3>PUMP B Configuration</h3>
						<div class="setting-row"><span>PLC Control ID</span><input type="text" class="setting-input hardware-id" data-key="PLC Control ID" value="PLC_PUMP_2" placeholder="e.g. DT1"></div>
						<div class="setting-row"><span>Interval</span><select class="setting-select" data-key="Interval"><option>AT EVERY WATERING</option><option>Every 1 hr</option><option>Every 2 hr</option></select></div>
						${createStepper('Dose Amount', 10, 'mL', 1, 100)}
						${createStepper('Max Daily Dose', 100, 'mL', 10, 1000, 10)}
					</div>
				</div>
				<div class="modal-section full-width chart-bottom">
					<h3>Combined Nutrient Delivery History</h3>
					<div class="usage-summary-row" style="display: flex; gap: 30px; margin-bottom: 20px;">
						<div class="weekly-usage-mini visible" id="usage-A" style="flex: 1;">
							<h4>WEEKLY USAGE (PUMP 01)</h4>
							${createUsageBars([40, 60, 30, 80, 50, 20, 10])}
						</div>
						<div class="weekly-usage-mini visible" id="usage-B" style="flex: 1;">
							<h4>WEEKLY USAGE (PUMP 02)</h4>
							${createUsageBars([20, 30, 45, 10, 65, 90, 40])}
						</div>
					</div>
					<div class="combined-graph-container">
						<h4>SYSTEM DELIVERY TREND (24H)</h4>
						<canvas id="modal-nutri-chart" style="width:100%; height:100px;"></canvas>
					</div>
				</div>
			`;
		} else if (type === 'ph-settings') {
			title.textContent = 'pH & WATER SETTINGS';
			body.innerHTML = `
				<div class="pump-configs-row">
					<!-- PUMP 03 (pH) -->
					<div class="modal-section pump-config-box">
						<h3>PUMP 03 (pH) Configuration</h3>
						<!-- Row 1: Hardware ID -->
						<div class="setting-row"><span>PLC Control ID</span><input type="text" class="setting-input hardware-id" data-key="PLC Control ID" value="PLC_PUMP_03" placeholder="e.g. DT2"></div>
						<!-- Row 2: Mode/Interval (Select) -->
						<div class="setting-row"><span>Check Interval</span><select class="setting-select" data-key="Check Interval"><option>Every 15 min</option><option>Every 30 min</option><option>Every 1 hr</option></select></div>
						<!-- Row 3: Primary Target (Stepper) -->
						${createStepper('Target pH', 6.0, '', 5.0, 7.0, 0.1)}
						<!-- Row 4: Secondary Setting (Stepper) -->
						${createStepper('Tolerance', 0.2, '±', 0.1, 0.5, 0.1)}
						<!-- Row 5: Limit/Safety (Stepper) -->
						${createStepper('Dose Amount', 5, 'mL', 1, 50)}
					</div>

					<!-- WATER PUMP -->
					<div class="modal-section pump-config-box">
						<h3>WATER PUMP Configuration</h3>
						<!-- Row 1: Hardware ID -->
						<div class="setting-row"><span>PLC Control ID</span><input type="text" class="setting-input hardware-id" data-key="PLC Water ID" value="PLC_WATER_MAIN" placeholder="e.g. DT3"></div>
						<!-- Row 2: Mode/Operation (Select) -->
						<div class="setting-row"><span>Operation Mode</span><select class="setting-select" data-key="Water Mode"><option>Cyclic</option><option>Continuous</option><option>Demand</option></select></div>
						<!-- Row 3: Primary Target (Stepper) -->
						${createStepper('Cycle Duration', 15, 'min', 1, 60)}
						<!-- Row 4: Secondary Setting (Stepper) -->
						${createStepper('Flow Rate', 100, 'L/h', 10, 500, 10)}
						<!-- Row 5: Limit/Safety (Stepper) -->
						${createStepper('Temp Cutoff', 30, '°C', 20, 40, 1)}
					</div>
				</div>
				<div class="modal-section full-width chart-bottom">
					<h3>Combined Output History</h3>
					<div class="usage-summary-row" style="display: flex; gap: 30px; margin-bottom: 20px;">
						<div class="weekly-usage-mini visible" style="flex: 1;">
							<h4>WEEKLY pH CORRECTION</h4>
							${createUsageBars([10, 15, 5, 8, 12, 20, 10])}
						</div>
						<div class="weekly-usage-mini visible" style="flex: 1;">
							<h4>WEEKLY WATER VOLUME</h4>
							${createUsageBars([80, 85, 90, 80, 75, 80, 82])}
						</div>
					</div>
					<canvas id="modal-ph-chart" style="width:100%; height:150px;"></canvas>
				</div>
			`;
		} else if (type === 'light-settings') {
			title.textContent = 'GROW LIGHT SETTINGS';
			body.innerHTML = `
				<div class="pump-configs-row">
					<!-- LEFT: Main Control -->
					<div class="modal-section pump-config-box">
						<h3>MAIN LIGHTING</h3>
						<div class="setting-row">
							<span>Master Power</span>
							<label class="toggle-switch">
								<input type="checkbox" class="setting-toggle" data-key="Master Light Power" checked>
								<span class="toggle-slider"></span>
							</label>
						</div>
						<div class="setting-row"><span>Spectrum Mode</span><select class="setting-select" data-key="Spectrum Mode"><option>VEG (Blue Dom)</option><option>BLOOM (Red Dom)</option><option>FULL SPECTRUM</option></select></div>
						${createStepper('Intensity', 80, '%', 0, 100, 5)}
						${createStepper('Target Lux', 50, 'kLux', 10, 100, 1)}
					</div>

					<!-- RIGHT: Configuration -->
					<div class="modal-section pump-config-box">
						<h3>CONFIGURATION</h3>
						<div class="setting-row"><span>PLC Control ID</span><input type="text" class="setting-input hardware-id" data-key="PLC Light ID" value="PLC_LIGHT_MAIN" placeholder="e.g. DT4"></div>
						<div class="setting-row"><span>Schedule Mode</span><select class="setting-select" data-key="Light Schedule"><option>18/6 (Veg)</option><option>12/12 (Flower)</option><option>24/0 (Seedling)</option><option>Custom</option></select></div>
						${createStepper('Sunrise/Sunset', 30, 'min', 0, 60, 5)}
						${createStepper('Dim Limit Temp', 35, '°C', 25, 45, 1)}
					</div>
				</div>

				<div class="modal-section full-width chart-bottom">
					<h3>LIGHTING HISTORY</h3>
					<div class="usage-summary-row" style="display: flex; gap: 30px; margin-bottom: 20px;">
						<div class="weekly-usage-mini visible" style="flex: 1;">
							<h4>DAILY LIGHT INTEGRAL (DLI)</h4>
							${createUsageBars([35, 38, 36, 40, 42, 39, 38])}
						</div>
					</div>
					<canvas id="modal-lux-chart" style="width:100%; height:150px;"></canvas>
				</div>
			`;
		}

		// Load persisted settings
		await this.loadSettingsIntoModal(type);

		modal.classList.add('active');
		this.addLogEntry(`Opened ${type} full-screen settings`);

		// Attach change/input listeners to all controls in the modal
		this.attachSettingsListeners(type);
	}

	adjustStepper(btn, delta, min, max) {
		const container = btn.closest('.tactile-stepper');
		const input = container.querySelector('.step-input');
		if (!input) return;

		let val = parseFloat(input.value) || 0;
		val = Math.max(min, Math.min(max, val + delta));
		input.value = val;

		// Trigger change event to fire debounced save
		input.dispatchEvent(new Event('change', { bubbles: true }));
	}

	async loadSettingsIntoModal(modalType) {
		try {
			const response = await fetch('/api/settings');
			const allSettings = await response.json();
			const settings = allSettings[modalType];

			if (!settings) return;

			const body = document.getElementById('modal-body');
			body.querySelectorAll('.modal-section').forEach(section => {
				const sectionTitle = section.querySelector('h3')?.textContent;
				if (sectionTitle && settings[sectionTitle]) {
					const sectionData = settings[sectionTitle];

					// Update standard settings
					section.querySelectorAll('.setting-row').forEach(row => {
						const label = row.querySelector('span')?.textContent;
						const input = row.querySelector('.setting-input, .setting-select');
						if (label && input && sectionData[label] !== undefined) {
							input.value = sectionData[label];
						}
					});
				}
			});
		} catch (e) {
			console.error('Failed to load settings into modal:', e);
		}
	}

	attachSettingsListeners(modalType) {
		const body = document.getElementById('modal-body');
		if (!body) return;

		// Include toggles in the selection
		const inputs = body.querySelectorAll('.setting-input, .setting-select, .setting-toggle');

		inputs.forEach(input => {
			// Listen for 'input' (typing) AND 'change' (steppers/selects/toggles)
			// This ensures stepper buttons (which dispatch 'change') are caught
			['input', 'change'].forEach(evt => {
				input.addEventListener(evt, () => {
					this.debounceSave(modalType);
				});
			});
		});
	}

	debounceSave(modalType) {
		const DEBOUNCE_DELAY = 1000; // 1 second debounce
		if (this.saveTimeouts[modalType]) {
			clearTimeout(this.saveTimeouts[modalType]);
		}

		this.saveTimeouts[modalType] = setTimeout(() => {
			this.saveSettings(modalType);
		}, DEBOUNCE_DELAY);
	}

	updateTelemetry(data) {
		this.telemetry = data;

		// Update MQTT status if present in telemetry
		if (data.edge_status) {
			this.updateEdgeStatus(data.edge_status);
		}

		this.updateAllDisplays();
	}

	updateEdgeStatus(status) {
		const dot = document.getElementById('mqtt-status-dot');
		const text = document.getElementById('mqtt-status-text');
		const nodeName = document.getElementById('edge-node-id');

		if (!dot || !text) return;

		if (status.connected) {
			dot.className = 'status-indicator online';
			text.textContent = 'ONLINE';
			text.className = 'status-text success';
		} else {
			dot.className = 'status-indicator offline';
			text.textContent = 'OFFLINE';
			text.className = 'status-text warning';
		}

		if (nodeName && status.unit_id) {
			nodeName.textContent = status.unit_id;
		}
	}

	async saveSettings(modalType) {
		const body = document.getElementById('modal-body');
		if (!body || !document.getElementById('fullscreen-modal').classList.contains('active')) return;

		// Collect all settings from the current modal
		const settings = {};
		body.querySelectorAll('.modal-section').forEach(section => {
			const sectionTitle = section.querySelector('h3')?.textContent || 'General';
			settings[sectionTitle] = {};

			section.querySelectorAll('.setting-row').forEach(row => {
				const label = row.querySelector('span')?.textContent;
				const input = row.querySelector('.setting-input, .setting-select');
				if (label && input) {
					settings[sectionTitle][label] = input.value;
				}
			});
		});

		try {
			const response = await fetch('/api/settings', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ type: modalType, settings })
			});
			const result = await response.json();
			if (result.status === 'success' && result.bcc) {
				console.log(`Settings for ${modalType} autosaved. BCC: ${result.bcc}`);
				this.addLogEntry(`Autosaved CONFIG [BCC: ${result.bcc}]`);
			}
		} catch (e) {
			console.error('Autosave failed:', e);
		}
	}

	closeFullscreenModal() {
		const modal = document.getElementById('fullscreen-modal');
		if (modal && modal.classList.contains('active')) {
			// Get the type if stored on data-modal-type (we should probably add it or retrieve it)
			// For now, let's just trigger a final save for all current inputs
			const titleEl = document.getElementById('modal-title');
			const type = titleEl.textContent.includes('NUTRIENT') ? 'nutrient-settings' : 'ph-settings';

			// Final instant save on close
			this.saveSettings(type);

			modal.classList.remove('active');
			this.addLogEntry('Closed settings modal (Autosaved)');
		}
	}

	switchTimeRange(graphType, range, container) {
		// Update active button
		container.querySelectorAll('.range-btn').forEach(btn => {
			btn.classList.toggle('active', btn.dataset.range === range);
		});

		// Get canvas and fade out
		const canvasId = `${graphType}-graph`;
		const canvas = document.getElementById(canvasId);
		if (!canvas) return;

		canvas.classList.add('fade-out');

		// After fade out, update data and fade in
		setTimeout(() => {
			const data = this.getDataForRange(graphType, range);
			this.drawLineGraph(canvasId, data, '#66FCF1');
			canvas.classList.remove('fade-out');
			canvas.classList.add('fade-in');

			// Update label
			const labels = { '24h': 'HOURLY', 'daily': 'DAILY', 'weekly': 'WEEKLY' };
			const labelEl = container.nextElementSibling;
			if (labelEl && labelEl.classList.contains('graph-label')) {
				labelEl.textContent = labels[range] || 'HOURLY';
			}

			// Remove fade-in class after animation
			setTimeout(() => canvas.classList.remove('fade-in'), 300);
		}, 150);
	}

	getDataForRange(graphType, range) {
		// Get appropriate history based on time range
		const historyMap = {
			'lux': this.history.lux,
			'humidity': this.history.humidity,
			'nutrition': this.history.temperature
		};

		const data = historyMap[graphType] || [];

		if (range === '24h') {
			return data.slice(-24);
		} else if (range === 'daily') {
			// Aggregate to daily averages (7 days)
			return this.aggregateToDaily(data, 7);
		} else if (range === 'weekly') {
			// Aggregate to weekly (4 weeks)
			return this.aggregateToWeekly(data, 4);
		}
		return data;
	}

	aggregateToDaily(data, days) {
		// Simulate daily data (in real app, would come from stored history)
		const result = [];
		for (let i = 0; i < days; i++) {
			const dayData = data.slice(i * 24, (i + 1) * 24);
			if (dayData.length > 0) {
				const avg = dayData.reduce((a, b) => a + b, 0) / dayData.length;
				result.push(avg);
			} else {
				// Generate simulated daily data
				result.push(50 + Math.random() * 40);
			}
		}
		return result;
	}

	aggregateToWeekly(data, weeks) {
		// Simulate weekly data
		const result = [];
		for (let i = 0; i < weeks; i++) {
			result.push(45 + Math.random() * 45);
		}
		return result;
	}

	initVerticalSliders() {
		const sliders = document.querySelectorAll('.vertical-slider');

		sliders.forEach(slider => {
			let isDragging = false;
			const fill = slider.querySelector('.slider-fill');
			const thumb = slider.querySelector('.slider-thumb');
			const valueDisplay = thumb.querySelector('.thumb-value');
			const sliderId = slider.id;

			// Get corresponding header value element
			let headerValueId;
			if (sliderId === 'slider-nutri-a') headerValueId = 'nutri-a-pct';
			else if (sliderId === 'slider-nutri-b') headerValueId = 'nutri-b-pct';
			else if (sliderId === 'slider-ph-down') headerValueId = 'ph-down-pct';

			const headerValue = document.getElementById(headerValueId);

			const updateSlider = (clientY) => {
				const rect = slider.getBoundingClientRect();
				const y = clientY - rect.top;
				const height = rect.height;

				// Calculate percentage (inverted because 0 is at bottom)
				let percent = Math.round(100 - (y / height) * 100);
				percent = Math.max(0, Math.min(100, percent));

				// Update slider
				slider.dataset.value = percent;
				fill.style.height = `${percent}%`;
				thumb.style.bottom = `${percent}%`;
				valueDisplay.textContent = percent;

				// Update header
				if (headerValue) {
					headerValue.textContent = `${percent}%`;
				}

				// Log the change
				const pumpName = sliderId.replace('slider-', '').toUpperCase();
				console.log(`${pumpName} speed: ${percent}%`);
			};

			// Mouse events
			slider.addEventListener('mousedown', (e) => {
				isDragging = true;
				updateSlider(e.clientY);
				e.preventDefault();
			});

			document.addEventListener('mousemove', (e) => {
				if (isDragging) {
					updateSlider(e.clientY);
				}
			});

			document.addEventListener('mouseup', () => {
				if (isDragging) {
					isDragging = false;
					// Send to backend
					const pumpId = sliderId.replace('slider-', '');
					this.setPumpSpeed(pumpId, parseInt(slider.dataset.value));
				}
			});

			// Touch events for mobile/touch devices
			slider.addEventListener('touchstart', (e) => {
				isDragging = true;
				updateSlider(e.touches[0].clientY);
				e.preventDefault();
			}, { passive: false });

			slider.addEventListener('touchmove', (e) => {
				if (isDragging) {
					updateSlider(e.touches[0].clientY);
					e.preventDefault();
				}
			}, { passive: false });

			slider.addEventListener('touchend', () => {
				if (isDragging) {
					isDragging = false;
					const pumpId = sliderId.replace('slider-', '');
					this.setPumpSpeed(pumpId, parseInt(slider.dataset.value));
				}
			});
		});
	}

	toggleWaterPump() {
		const btn = document.getElementById('water-pump-toggle');
		const status = document.getElementById('water-pump-status');

		if (!btn) return;

		const isActive = btn.classList.toggle('active');

		if (status) {
			status.textContent = isActive ? 'ON' : 'OFF';
			status.classList.toggle('active', isActive);
		}

		const stateText = isActive ? 'ACTIVATED' : 'DEACTIVATED';
		this.addLogEntry(`Water Pump ${stateText}`);

		// Send to backend
		fetch('/api/actuator', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				name: 'water_pump',
				value: isActive,
				action: 'set'
			})
		}).catch(e => console.error('Water pump toggle failed:', e));
	}

	async setPumpSpeed(pumpId, speed) {
		const nameMap = {
			'nutri-a': 'nutrient_a',
			'nutri-b': 'nutrient_b',
			'ph-down': 'ph_down_pump'
		};

		const actuatorName = nameMap[pumpId];
		if (!actuatorName) return;

		this.addLogEntry(`${pumpId.toUpperCase()} Speed set to ${speed}%`);

		try {
			// Convert speed to a value (sim might expect boolean or float)
			// For now, if speed > 0, we can also ensure the pump is ON
			const response = await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: actuatorName,
					value: speed, // Sending speed as numeric value
					action: 'set'
				})
			});
			const result = await response.json();
			if (result.status === 'success' && result.bcc) {
				this.addLogEntry(`${pumpId.toUpperCase()} Speed set to ${speed}% [BCC: ${result.bcc}]`);
			}
		} catch (e) {
			console.error('Failed to set pump speed:', e);
		}
	}

	generateInitialHistory() {
		// Generate realistic-looking initial data
		for (let i = 0; i < this.maxHistoryPoints; i++) {
			this.history.lux.push(70 + Math.random() * 30);
			this.history.humidity.push(55 + Math.random() * 20);
			this.history.temperature.push(20 + Math.random() * 10);
			this.history.watering.push(Math.random() > 0.7 ? 1 : 0);
			this.history.nutriA.push(75 + Math.random() * 20);
			this.history.nutriB.push(50 + Math.random() * 30);
			this.history.phDown.push(60 + Math.random() * 30);
		}
	}

	initGraphs() {
		// Initialize all canvas graphs
		this.drawLineGraph('lux-graph', this.history.lux, '#66FCF1');
		this.drawLineGraph('humidity-graph', this.history.humidity, '#66FCF1');
		this.drawLineGraph('nutrition-graph', this.history.temperature, '#66FCF1');
		this.drawLineGraph('watering-graph', this.history.watering, '#00FF41', true);

		// Mini bar charts
		this.drawBarChart('nutri-a-chart', this.history.nutriA.slice(-7), '#00FF41');
		this.drawBarChart('nutri-b-chart', this.history.nutriB.slice(-7), '#00FF41');
		this.drawLineGraph('ph-chart', this.history.phDown.slice(-7), '#FF3131');
	}

	drawLineGraph(canvasId, data, color, isStep = false) {
		const canvas = document.getElementById(canvasId);
		if (!canvas) return;

		const ctx = canvas.getContext('2d');
		const rect = canvas.getBoundingClientRect();
		canvas.width = rect.width * 2;
		canvas.height = rect.height * 2;
		ctx.scale(2, 2);

		const width = rect.width;
		const height = rect.height;
		const paddingLeft = 30;  // Space for Y-axis labels
		const paddingRight = 10;
		const paddingTop = 10;
		const paddingBottom = 18; // Space for X-axis labels

		ctx.clearRect(0, 0, width, height);

		if (data.length < 2) return;

		const maxVal = Math.max(...data) * 1.1 || 100;
		const minVal = Math.min(...data) * 0.9 || 0;
		const range = maxVal - minVal || 1;
		const graphWidth = width - paddingLeft - paddingRight;
		const graphHeight = height - paddingTop - paddingBottom;

		// Detect theme for colors
		const isLight = document.body.classList.contains('light-theme');
		const gridColor = isLight ? 'rgba(45, 106, 106, 0.35)' : 'rgba(102, 252, 241, 0.2)';
		const labelColor = isLight ? 'rgba(85, 85, 85, 0.9)' : 'rgba(102, 252, 241, 0.6)';
		const lineColor = isLight ? '#2D6A6A' : color;

		// Draw dotted grid lines (horizontal)
		ctx.setLineDash([2, 3]);
		ctx.strokeStyle = gridColor;
		ctx.lineWidth = 0.5;
		ctx.font = '8px JetBrains Mono';
		ctx.fillStyle = labelColor;

		for (let i = 0; i <= 4; i++) {
			const y = paddingTop + graphHeight * (i / 4);
			const value = Math.round(maxVal - (range * i / 4));

			ctx.beginPath();
			ctx.moveTo(paddingLeft, y);
			ctx.lineTo(width - paddingRight, y);
			ctx.stroke();

			// Y-axis labels
			ctx.fillText(value.toString(), 2, y + 3);
		}

		// Draw vertical dotted grid lines
		for (let i = 0; i <= 6; i++) {
			const x = paddingLeft + graphWidth * (i / 6);
			ctx.beginPath();
			ctx.moveTo(x, paddingTop);
			ctx.lineTo(x, height - paddingBottom);
			ctx.stroke();
		}

		ctx.setLineDash([]); // Reset to solid

		// Draw X-axis labels (time)
		ctx.fillStyle = labelColor;
		const xLabels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'];
		xLabels.forEach((label, i) => {
			const x = paddingLeft + graphWidth * (i / 6) - 12;
			ctx.fillText(label, x, height - 4);
		});

		// Draw line
		ctx.strokeStyle = lineColor;
		ctx.lineWidth = 1.5;
		ctx.beginPath();

		data.forEach((val, i) => {
			const x = paddingLeft + graphWidth * (i / (data.length - 1));
			const y = paddingTop + graphHeight * (1 - (val - minVal) / range);

			if (i === 0) {
				ctx.moveTo(x, y);
			} else if (isStep) {
				ctx.lineTo(x, ctx.currentY || y);
				ctx.lineTo(x, y);
			} else {
				ctx.lineTo(x, y);
			}
			ctx.currentY = y;
		});

		ctx.stroke();

		// Draw fill gradient
		const gradient = ctx.createLinearGradient(0, paddingTop, 0, height - paddingBottom);
		gradient.addColorStop(0, 'rgba(69, 162, 158, 0.4)');
		gradient.addColorStop(1, 'rgba(69, 162, 158, 0.05)');

		ctx.lineTo(width - paddingRight, height - paddingBottom);
		ctx.lineTo(paddingLeft, height - paddingBottom);
		ctx.closePath();
		ctx.fillStyle = gradient;
		ctx.fill();
	}

	drawBarChart(canvasId, data, color) {
		const canvas = document.getElementById(canvasId);
		if (!canvas) return;

		const ctx = canvas.getContext('2d');
		const rect = canvas.getBoundingClientRect();
		canvas.width = rect.width * 2;
		canvas.height = rect.height * 2;
		ctx.scale(2, 2);

		const width = rect.width;
		const height = rect.height;
		const paddingLeft = 20;
		const paddingRight = 5;
		const paddingTop = 8;
		const paddingBottom = 16;
		const graphWidth = width - paddingLeft - paddingRight;
		const graphHeight = height - paddingTop - paddingBottom;
		const barWidth = (graphWidth / data.length) - 4;

		ctx.clearRect(0, 0, width, height);

		const maxVal = 100;

		// Detect theme for colors
		const isLight = document.body.classList.contains('light-theme');
		const gridColor = isLight ? 'rgba(45, 106, 106, 0.30)' : 'rgba(102, 252, 241, 0.15)';
		const labelColor = isLight ? 'rgba(85, 85, 85, 0.9)' : 'rgba(102, 252, 241, 0.5)';

		// Draw dotted horizontal grid
		ctx.setLineDash([2, 2]);
		ctx.strokeStyle = gridColor;
		ctx.lineWidth = 0.5;
		ctx.font = '7px JetBrains Mono';
		ctx.fillStyle = labelColor;

		for (let i = 0; i <= 4; i++) {
			const y = paddingTop + graphHeight * (i / 4);
			const value = Math.round(100 - (25 * i));
			ctx.beginPath();
			ctx.moveTo(paddingLeft, y);
			ctx.lineTo(width - paddingRight, y);
			ctx.stroke();
			ctx.fillText(value.toString(), 2, y + 3);
		}
		ctx.setLineDash([]);

		// Bar colors based on theme
		const barColors = isLight
			? { c1: '#1B4040', c2: '#2D6A6A', c3: '#3A8888' }
			: { c1: '#1B4D4D', c2: '#2A7A7A', c3: '#45A29E' };

		// Draw bars with shine
		data.forEach((val, i) => {
			const barHeight = graphHeight * (val / maxVal);
			const x = paddingLeft + i * (graphWidth / data.length) + 2;
			const y = paddingTop + graphHeight - barHeight;

			// Bar gradient (dulled teal)
			const gradient = ctx.createLinearGradient(0, y + barHeight, 0, y);
			gradient.addColorStop(0, barColors.c1);
			gradient.addColorStop(0.5, barColors.c2);
			gradient.addColorStop(1, barColors.c3);

			ctx.fillStyle = gradient;
			ctx.fillRect(x, y, barWidth, barHeight);

			// Shine effect
			const shineGradient = ctx.createLinearGradient(0, y, 0, y + barHeight * 0.3);
			shineGradient.addColorStop(0, 'rgba(255,255,255,0.25)');
			shineGradient.addColorStop(1, 'transparent');
			ctx.fillStyle = shineGradient;
			ctx.fillRect(x, y, barWidth, barHeight * 0.3);

			// X-axis label (day)
			ctx.fillStyle = labelColor;
			const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
			ctx.fillText(days[i] || (i + 1).toString(), x, height - 3);
		});
	}

	updateAllDisplays() {
		// Update metric values
		this.updateElement('lux-value', `${this.values.lux}%`);
		this.updateElement('humidity-value', `${this.values.humidity}%`);
		this.updateElement('temp-in', `$${this.values.tempIn}°C`);
		this.updateElement('temp-out', `$${this.values.tempOut}°C`);
		this.updateElement('nutri-a-pct', `${this.values.nutriA}%`);
		this.updateElement('nutri-b-pct', `${this.values.nutriB}%`);
		this.updateElement('ph-down-pct', `${this.values.phDown}%`);

		// Update vertical bars
		this.updateBar('nutri-a-fill', this.values.nutriA);
		this.updateBar('nutri-b-fill', this.values.nutriB);
		this.updateBar('ph-down-fill', this.values.phDown);

		// Update pump button state
		const pumpBtn = document.getElementById('pump-toggle');
		if (pumpBtn) {
			pumpBtn.classList.toggle('active', this.values.pumpActive);
		}
	}

	updateElement(id, value) {
		const el = document.getElementById(id);
		if (el) el.textContent = value;
	}

	updateBar(id, percent) {
		const el = document.getElementById(id);
		if (el) {
			const value = Math.min(100, Math.max(0, Math.round(percent)));
			el.style.height = `${value}%`;
			// Update the bar-value text if it exists
			const valueEl = el.querySelector('.bar-value');
			if (valueEl) {
				valueEl.textContent = value.toString();
			}
		}
	}

	async togglePump() {
		try {
			const response = await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: 'pump_active',
					action: 'toggle'
				})
			});
			const result = await response.json();
			this.values.pumpActive = result.value;
			this.updateAllDisplays();
			this.addLogEntry(`Pump ${result.value ? 'STARTED' : 'STOPPED'} (User Override)`);
		} catch (e) {
			console.error('Pump toggle failed:', e);
		}
	}

	async toggleLightBtn() {
		const btn = document.getElementById('light-toggle');
		const status = document.getElementById('light-status');

		const isActive = btn.classList.contains('active');
		const newState = !isActive;

		if (newState) {
			btn.classList.add('active');
			if (status) {
				status.textContent = 'ON';
				status.classList.add('active');
			}
		} else {
			btn.classList.remove('active');
			if (status) {
				status.textContent = 'OFF';
				status.classList.remove('active');
			}
		}

		// Use existing backend logic
		this.toggleLights(newState);
	}

	async toggleLights(on) {
		try {
			const response = await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: 'lights',
					value: on,
					action: 'set'
				})
			});
			this.values.lightsOn = on;
			this.addLogEntry(`Lights ${on ? 'ON' : 'OFF'}`);
		} catch (e) {
			console.error('Lights toggle failed:', e);
		}
	}

	async toggleNutrient(type, on) {
		const nameMap = {
			'nutri-a': 'nutrient_a',
			'nutri-b': 'nutrient_b',
			'ph-down': 'ph_down_pump'
		};

		try {
			await fetch('/api/actuator', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: nameMap[type],
					value: on,
					action: 'set'
				})
			});
			this.addLogEntry(`${type.toUpperCase()} ${on ? 'DOSING' : 'STOPPED'}`);
		} catch (e) {
			console.error('Nutrient toggle failed:', e);
		}
	}

	setTheme(mode) {
		const isDark = mode === 'dark';

		// Apply theme class
		document.body.classList.toggle('light-theme', !isDark);

		// Update button states
		const sunBtn = document.getElementById('day-mode');
		const moonBtn = document.getElementById('night-mode');

		if (sunBtn) sunBtn.classList.toggle('active', !isDark);
		if (moonBtn) moonBtn.classList.toggle('active', isDark);

		// Log the change
		this.addLogEntry(`Theme: ${isDark ? 'Night Mode' : 'Day Mode'}`);

		// Redraw graphs with new colors
		setTimeout(() => this.initGraphs(), 100);
	}

	addLogEntry(message) {
		const log = document.getElementById('system-log');
		if (!log) return;

		const entry = document.createElement('div');
		entry.className = 'log-entry';
		entry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
		log.insertBefore(entry, log.firstChild);

		// Keep only last 10 entries
		while (log.children.length > 10) {
			log.removeChild(log.lastChild);
		}
	}

	startClock() {
		const updateClock = () => {
			const now = new Date();
			const el = document.getElementById('clock');
			if (el) {
				el.textContent = now.toLocaleTimeString('en-US', {
					hour: '2-digit',
					minute: '2-digit',
					hour12: true
				});
			}
		};
		updateClock();
		setInterval(updateClock, 1000);
	}

	async startTelemetryPolling() {
		setInterval(async () => {
			await this.fetchTelemetry();
		}, 2000);
	}

	async fetchTelemetry() {
		try {
			const response = await fetch('/api/status');
			const data = await response.json();

			// Update from simulation data if available
			// This will be expanded when connected to the backend telemetry
		} catch (e) {
			// Simulate data changes for demo
			this.simulateChanges();
		}
	}

	simulateChanges() {
		// Small random fluctuations for demo
		this.values.lux = Math.max(0, Math.min(100, this.values.lux + (Math.random() - 0.5) * 2));
		this.values.humidity = Math.max(0, Math.min(100, this.values.humidity + (Math.random() - 0.5) * 1));

		// Update history
		this.history.lux.push(this.values.lux);
		this.history.humidity.push(this.values.humidity);

		if (this.history.lux.length > this.maxHistoryPoints) {
			this.history.lux.shift();
			this.history.humidity.shift();
		}

		// Redraw graphs
		this.drawLineGraph('lux-graph', this.history.lux, '#66FCF1');
		this.drawLineGraph('humidity-graph', this.history.humidity, '#66FCF1');

		this.updateAllDisplays();
	}
}

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', () => {
	window.hmiDashboard = new HMIDashboard();
});
