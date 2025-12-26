// Live uptime counter for Master Grower status
// Shows continuous monitoring time

const startTime = Date.now();

function updateUptime() {
	const elapsed = Date.now() - startTime;

	// Convert to hours and minutes
	const hours = Math.floor(elapsed / (1000 * 60 * 60));
	const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));

	// Update display
	const uptimeEl = document.getElementById('uptime');
	if (uptimeEl) {
		uptimeEl.textContent = `${hours}h ${minutes.toString().padStart(2, '0')}m`;
	}

	// Calculate cycle day (resets every 30 days)
	const cycleDay = Math.floor(elapsed / (1000 * 60 * 60 * 24)) % 30 + 1;
	const cycleDayEl = document.getElementById('cycle-day');
	if (cycleDayEl) {
		cycleDayEl.textContent = `Day ${cycleDay}`;
	}
}

// Update every minute
setInterval(updateUptime, 60000);

// Initial update
updateUptime();
