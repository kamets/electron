// _SUDOTEER Real-Time Workflow Visualization
// Displays the Sequential Validation Chain in real-time

class WorkflowVisualizer {
	constructor(containerId) {
		this.container = document.getElementById(containerId);
		this.agents = [
			{ id: 'architect_01', name: 'Architect', status: 'idle', color: '#007aff' },
			{ id: 'coder_01', name: 'Coder', status: 'idle', color: '#34c759' },
			{ id: 'tester_01', name: 'Tester', status: 'idle', color: '#ff9500' },
			{ id: 'documenter_01', name: 'Documenter', status: 'idle', color: '#af52de' },
			{ id: 'validator_01', name: 'Validator', status: 'idle', color: '#ff3b30' }
		];
		this.currentStep = -1;
		this.init();
	}

	init() {
		this.render();
	}

	render() {
		this.container.innerHTML = `
			<div class="workflow-chain">
				${this.agents.map((agent, index) => `
					<div class="workflow-node ${agent.status}" data-agent="${agent.id}" style="--agent-color: ${agent.color}">
						<div class="node-icon">
							<div class="node-pulse"></div>
							<div class="node-core"></div>
						</div>
						<div class="node-label">${agent.name}</div>
						<div class="node-status">${this.getStatusText(agent.status)}</div>
						${index < this.agents.length - 1 ? '<div class="connector"></div>' : ''}
					</div>
				`).join('')}
			</div>
		`;
	}

	getStatusText(status) {
		const statusMap = {
			idle: 'Ready',
			active: 'Processing',
			success: 'Complete',
			error: 'Failed'
		};
		return statusMap[status] || 'Ready';
	}

	setAgentStatus(agentId, status) {
		const agent = this.agents.find(a => a.id === agentId);
		if (agent) {
			agent.status = status;
			const node = this.container.querySelector(`[data-agent="${agentId}"]`);
			if (node) {
				node.className = `workflow-node ${status}`;
				node.querySelector('.node-status').textContent = this.getStatusText(status);
			}
		}
	}

	async runWorkflow() {
		for (let i = 0; i < this.agents.length; i++) {
			const agent = this.agents[i];

			// Activate current agent
			this.setAgentStatus(agent.id, 'active');

			// Simulate processing time
			await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

			// Mark as success
			this.setAgentStatus(agent.id, 'success');

			// Small pause before next agent
			if (i < this.agents.length - 1) {
				await new Promise(resolve => setTimeout(resolve, 300));
			}
		}
	}

	reset() {
		this.agents.forEach(agent => {
			agent.status = 'idle';
		});
		this.render();
	}

	updateFromBackend(workflowData) {
		// Parse backend workflow events
		if (workflowData.currentNode) {
			this.setAgentStatus(workflowData.currentNode, 'active');
		}
		if (workflowData.completedNodes) {
			workflowData.completedNodes.forEach(nodeId => {
				this.setAgentStatus(nodeId, 'success');
			});
		}
		if (workflowData.failedNodes) {
			workflowData.failedNodes.forEach(nodeId => {
				this.setAgentStatus(nodeId, 'error');
			});
		}
	}

	connectToBackend() {
		/**
		 * Connects to the Python backend via native WebSockets.
		 * Listens for agent status updates in real-time.
		 */
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const wsUrl = `${protocol}//${window.location.host}/ws`;

		console.log('WorkflowVisualizer: Connecting to WebSocket...', wsUrl);
		this.socket = new WebSocket(wsUrl);

		this.socket.onopen = () => {
			console.log('WorkflowVisualizer: ✓ Connected to Agency WebSocket');
		};

		this.socket.onmessage = (event) => {
			try {
				const payload = JSON.parse(event.data);
				console.log('WorkflowVisualizer received:', payload);

				// Handle different event types from webserver.py
				if (payload.type === 'AGENT_UPDATE' || payload.type === 'IPC_EVENT') {
					if (payload.event.startsWith('AGENT_')) {
						const status = payload.event.replace('AGENT_', '').toLowerCase();
						this.setAgentStatus(payload.agent_id, status);
					}

					if (payload.event === 'WORKFLOW_UPDATE') {
						this.updateFromBackend({
							currentNode: payload.data.current_node,
							status: payload.data.status
						});
					}

					if (payload.event === 'SYSTEM_HEARTBEAT') {
						this.handleHeartbeat(payload);
					}
				}

				// Handle greenhouse telemetry (if greenhouse-monitor.js isn't handling it)
				if (payload.type === 'GREENHOUSE_TELEMETRY') {
					window.dispatchEvent(new CustomEvent('greenhouse-update', { detail: payload.data }));
				}

			} catch (err) {
				console.error('WorkflowVisualizer: Failed to parse socket message', err);
			}
		};

		this.socket.onclose = () => {
			console.warn('WorkflowVisualizer: WebSocket closed. Retrying in 3s...');
			setTimeout(() => this.connectToBackend(), 3000);
		};

		this.socket.onerror = (err) => {
			console.error('WorkflowVisualizer: WebSocket error', err);
		};
	}

	handleHeartbeat(payload) {
		// Update system status indicator (could be exposed to UI)
		this.lastHeartbeat = payload.timestamp;
		this.systemStatus = payload.data.status; // "alive" or "stalled"

		// Dispatch event for health monitoring
		const healthEvent = new CustomEvent('system-health', {
			detail: {
				status: payload.data.status,
				uptime: payload.data.uptime,
				timestamp: payload.timestamp
			}
		});
		window.dispatchEvent(healthEvent);
	}

	disconnect() {
		if (this.unsubscribe) {
			this.unsubscribe();
			console.log('WorkflowVisualizer: Disconnected from backend');
		}
	}
}

// Export for use in main UI
window.WorkflowVisualizer = WorkflowVisualizer;
