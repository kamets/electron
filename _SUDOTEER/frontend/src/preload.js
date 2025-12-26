const { contextBridge, ipcRenderer } = require('electron');

/**
 * _SUDOTEER Secure Bridge
 * Exposes controlled API to renderer process via contextIsolation
 */

contextBridge.exposeInMainWorld('sudoteerAPI', {
	/**
	 * OUTGOING: Send commands to Python backend
	 * Usage: window.sudoteerAPI.sendCommand('SPAWN_AGENT', {role: 'coder', name: 'coder_02'})
	 */
	sendCommand: (command, payload) => {
		if (typeof command === 'string') {
			ipcRenderer.send('frontend-command', { command, payload });
			console.log(`[UI → Python]: ${command}`, payload);
		} else {
			console.error('sendCommand: command must be a string');
		}
	},

	/**
	 * INCOMING: Listen for updates from Python agents
	 * Returns cleanup function to unsubscribe
	 */
	onAgentUpdate: (callback) => {
		const subscription = (_event, data) => callback(data);
		ipcRenderer.on('agent-update', subscription);

		// Return cleanup function
		return () => {
			ipcRenderer.removeListener('agent-update', subscription);
		};
	},

	/**
	 * LEGACY: Run agent task (for backward compatibility)
	 */
	runTask: (taskData) => ipcRenderer.invoke('run-agent-task', taskData),

	/**
	 * SYSTEM: Ping backend for health check
	 */
	ping: () => ipcRenderer.invoke('system-ping')
});
