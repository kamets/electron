// Morning Dashboard - What Foreman Sees First Thing
// Simple, clear, actionable

function createMorningDashboard() {
	const container = document.createElement('div');
	container.className = 'morning-summary';
	container.id = 'morning-dashboard';

	// Check overall status
	const allGood = checkSystemStatus();
	const statusClass = allGood ? 'all-good' : 'needs-attention';
	const statusText = allGood ? '✓ ALL SYSTEMS NORMAL' : '⚠ NEEDS ATTENTION';

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
