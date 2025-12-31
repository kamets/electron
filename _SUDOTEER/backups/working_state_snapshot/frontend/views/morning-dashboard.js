// Morning Dashboard - What Foreman Sees First Thing
// Simple, clear, actionable

function createMorningDashboard() {
	const container = document.createElement('div');
	container.className = 'morning-summary';
	container.id = 'morning-dashboard';

	async function updateMorningStatus() {
		try {
			const response = await fetch('/api/status');
			const status = await response.json();

			const statusBanner = document.querySelector('.status-banner');
			const dashboard = document.getElementById('morning-dashboard');
			if (!statusBanner || !dashboard) return;

			const isDegraded = status.status === 'degraded';
			const isOffline = status.status === 'offline';

			if (isOffline) {
				statusBanner.className = 'status-banner needs-attention offline';
				statusBanner.textContent = '❌ SYSTEM OFFLINE';
			} else if (isDegraded) {
				statusBanner.className = 'status-banner needs-attention';
				statusBanner.textContent = '⚠ SYSTEM DEGRADED';

				// Add detail if not already there
				if (!document.getElementById('status-detail')) {
					const detail = document.createElement('div');
					detail.id = 'status-detail';
					detail.style.fontSize = '10px';
					detail.style.marginTop = '5px';
					detail.style.color = 'rgba(255,100,100,0.8)';
					detail.textContent = 'Graph Memory: CONNECTION FAILURE';
					statusBanner.appendChild(detail);
				}
			} else {
				statusBanner.className = 'status-banner all-good';
				statusBanner.textContent = '✓ ALL SYSTEMS NORMAL';
				const detail = document.getElementById('status-detail');
				if (detail) detail.remove();
			}

			// Update stat cards if they exist in simple mode
			const uptimeEl = document.getElementById('dashboard-uptime');
			if (uptimeEl) {
				const hours = Math.floor(status.uptime / 3600);
				const mins = Math.floor((status.uptime % 3600) / 60);
				uptimeEl.textContent = `${hours}h ${mins}m`;
			}
		} catch (e) {
			console.error("Dashboard Status Poll Failed:", e);
		}
	}

	container.innerHTML = `
		<h2>Today's Status</h2>

		<div class="status-banner ${statusClass}">
			${statusText}
		</div>

		<h3 style="margin: 15px 0 10px 0; font-size: 14px; color: rgba(255,255,255,0.7);">Action Items:</h3>
		<ul class="task-list">
			${getTasksForToday()}
		</ul>

		<div class="quick-stats">
			<div class="quick-stat">
				<div class="quick-stat-label">Temp</div>
				<div class="quick-stat-value">24°C</div>
			</div>
			<div class="quick-stat">
				<div class="quick-stat-label">Humidity</div>
				<div class="quick-stat-value">62%</div>
			</div>
			<div class="quick-stat">
				<div class="quick-stat-label">Health</div>
				<div class="quick-stat-value">95%</div>
			</div>
			<div class="quick-stat">
				<div class="quick-stat-label">Uptime</div>
				<div class="quick-stat-value" id="dashboard-uptime">0h</div>
			</div>
		</div>
	`;

	const rightPanel = document.querySelector('.right-panel');
	if (rightPanel) {
		rightPanel.prepend(container);
	} else {
		document.body.appendChild(container);
	}

	// Start polling
	setInterval(updateMorningStatus, 5000);
	updateMorningStatus();

	// Update uptime every minute
	setInterval(updateDashboardUptime, 60000);
	updateDashboardUptime();
}

function checkSystemStatus() {
	// Simple logic: all good if no critical alerts
	// In real implementation, check actual sensor data
	return true; // Default: everything OK
}

function getTasksForToday() {
	// Sample tasks - in production, pull from actual task system
	const tasks = [
		{ text: '9:00 AM - Nutrient delivery expected', type: 'normal' },
		{ text: 'Check water levels in Zone B', type: 'normal' },
		{ text: 'pH adjustment needed (Zone A)', type: 'warning' }
	];

	return tasks.map(task =>
		`<li class="task-item ${task.type}">${task.text}</li>`
	).join('');
}

function updateDashboardUptime() {
	const uptimeEl = document.getElementById('dashboard-uptime');
	if (uptimeEl) {
		const hours = Math.floor((Date.now() - startTime) / (1000 * 60 * 60));
		uptimeEl.textContent = `${hours}h`;
	}
}

// Initialize on page load
if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', createMorningDashboard);
} else {
	createMorningDashboard();
}
