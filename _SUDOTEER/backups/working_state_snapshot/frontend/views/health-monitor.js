// _SUDOTEER System Health Monitor
// Displays real-time backend connection status with Dead Man's Switch monitoring

class SystemHealthMonitor {
	constructor(containerId) {
		this.container = document.getElementById(containerId);
		this.status = 'CONNECTING'; // 'CONNECTED', 'STALLED', 'DISCONNECTED'
		this.lastPing = null;
		this.watchdogTimer = null;
		this.watchdogTimeout = 5000; // 5s timeout

		this.init();
	}

	init() {
		this.render();
		this.connectToBackend();
	}

	render() {
		const colors = {
			CONNECTED: '#4ade80',   // Green
			STALLED: '#facc15',     // Yellow (Warning)
			DISCONNECTED: '#ef4444', // Red
			CONNECTING: '#60a5fa'    // Blue
		};

		const messages = {
			CONNECTED: 'SYSTEM ONLINE',
			STALLED: 'SYSTEM UNRESPONSIVE',
			DISCONNECTED: 'CONNECTION LOST',
			CONNECTING: 'CONNECTING...'
		};

		this.container.innerHTML = `
			<div class="health-indicator" style="display: flex; align-items: center; gap: 12px;">
				<div class="health-led" style="
					width: 12px;
					height: 12px;
					border-radius: 50%;
					background-color: ${colors[this.status]};
					box-shadow: 0 0 12px ${colors[this.status]};
					animation: pulse-led 2s ease-in-out infinite;
				"></div>
				<div class="health-info" style="display: flex; flex-direction: column; gap: 2px;">
					<span class="health-status" style="
						color: ${colors[this.status]};
						font-weight: 600;
						font-size: 0.75rem;
						letter-spacing: 0.5px;
					">${messages[this.status]}</span>
					${this.lastPing ? `
						<span class="health-ping" style="
							font-size: 0.65rem;
							opacity: 0.5;
							font-family: 'JetBrains Mono', monospace;
						">Ping: ${this.lastPing.split('T')[1].split('.')[0]}</span>
					` : ''}
				</div>
			</div>
		`;
	}

	connectToBackend() {
		if (!window.sudoteerAPI) {
			console.warn('SystemHealthMonitor: sudoteerAPI not available');
			this.status = 'DISCONNECTED';
			this.render();
			return;
		}

		this.unsubscribe = window.sudoteerAPI.onAgentUpdate((payload) => {
			if (payload.event === 'SYSTEM_HEARTBEAT') {
				// Update ping time
				this.lastPing = payload.timestamp;

				// Check for stalled status from backend
				if (payload.data.status === 'stalled') {
					this.status = 'STALLED';
					console.warn('⚠️  Backend reports STALL:', payload.data);
				} else {
					this.status = 'CONNECTED';
				}

				// Reset watchdog timer
				this.resetWatchdog();
				this.render();
			}
		});

		// Start watchdog - if we don't hear heartbeat in 5s, mark as disconnected
		this.resetWatchdog();
	}

	resetWatchdog() {
		// Clear existing timer
		if (this.watchdogTimer) {
			clearTimeout(this.watchdogTimer);
		}

		// Set new timer
		this.watchdogTimer = setTimeout(() => {
			this.status = 'DISCONNECTED';
			console.error('🚨 HEARTBEAT LOST: Python backend is silent.');
			this.render();
		}, this.watchdogTimeout);
	}

	disconnect() {
		if (this.unsubscribe) {
			this.unsubscribe();
		}
		if (this.watchdogTimer) {
			clearTimeout(this.watchdogTimer);
		}
	}
}

// Export for use in main UI
window.SystemHealthMonitor = SystemHealthMonitor;
