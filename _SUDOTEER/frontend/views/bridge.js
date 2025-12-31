/**
 * _SUDOTEER WebBridge
 * Connects the legacy Electron-style UI to the FastAPI WebSocket backend.
 * Implements the window.sudoteerAPI interface.
 */

(function () {
	const wsUrl = `ws://${window.location.host}/ws`;
	let socket = null;
	const listeners = [];

	console.log("🔗 Connecting to _SUDOTEER WebBridge...");

	function connect() {
		socket = new WebSocket(wsUrl);

		socket.onopen = () => {
			console.log("✅ WebBridge Active: Heartbeat Synced.");
		};

		socket.onmessage = (event) => {
			try {
				const payload = JSON.parse(event.data);
				// Dispatch to all registered listeners
				listeners.forEach(cb => cb(payload));
			} catch (e) {
				console.error("❌ WebBridge Parse Error:", e);
			}
		};

		socket.onclose = () => {
			console.warn("⚠️ WebBridge Lost. Reconnecting in 2s...");
			setTimeout(connect, 2000);
		};

		socket.onerror = (err) => {
			console.error("❌ WebBridge Error:", err);
		};
	}

	// Define the interface that the dashboards expect
	window.sudoteerAPI = {
		/**
		 * Register a callback for agent/telemetry updates.
		 * @param {Function} callback (payload) => void
		 */
		onAgentUpdate: (callback) => {
			if (typeof callback === 'function') {
				listeners.push(callback);
			}
		},

		/**
		 * Send a command to the backend.
		 * @param {string} command
		 * @param {Object} payload
		 */
		sendCommand: (command, payload) => {
			if (socket && socket.readyState === WebSocket.OPEN) {
				socket.send(JSON.stringify({
					command: command,
					payload: payload
				}));
			} else {
				console.error("❌ Cannot send command: WebBridge is offline.");
			}
		}
	};

	connect();
})();
