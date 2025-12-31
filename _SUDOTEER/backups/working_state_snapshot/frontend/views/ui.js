// _SUDOTEER UI Logic

document.addEventListener('DOMContentLoaded', () => {
	const voiceIndicator = document.getElementById('voice-indicator');
	const userInput = document.getElementById('user-input');
	const stressOverlay = document.getElementById('global-stress');
	const chatHistory = document.getElementById('chat-history');

	// 0. Chat Helper
	function appendChatMessage(sender, message, type = 'agent') {
		if (!chatHistory) return;

		const msgDiv = document.createElement('div');
		msgDiv.className = `chat-msg ${type}`;
		msgDiv.innerHTML = `
			<span class="sender">${sender.toUpperCase()}</span>
			<span class="msg">${message}</span>
		`;

		chatHistory.appendChild(msgDiv);
		chatHistory.scrollTop = chatHistory.scrollHeight;
	}

	// 1. Voice Pulse Interaction
	// Simulates the indicator "listening" or "reponding"
	function setVoiceState(state) {
		const colors = {
			idle: '#007aff',
			listening: '#5856d6',
			responding: '#32ade6',
			stress: '#ff3b30'
		};
		const pulseSpeed = {
			idle: '3s',
			listening: '1s',
			responding: '1.5s',
			stress: '0.5s'
		};

		const aura = document.querySelector('.inner-circle');
		const wave = document.querySelector('.pulse-wave');

		aura.style.background = colors[state] || colors.idle;
		aura.style.boxShadow = `0 0 40px ${colors[state]}`;
		wave.style.borderColor = colors[state];
		wave.style.animationDuration = pulseSpeed[state];
	}

	// 2. Stress-Aware HUD (Therapeutic)
	// Switches background "aura" based on system stress
	function setSystemStress(level) {
		// level: 0.0 to 1.0
		const r = Math.floor(255 * level);
		const g = Math.floor(122 * (1 - level));
		const b = Math.floor(255 * (1 - level));
		stressOverlay.style.background = `radial-gradient(circle, rgba(${r}, ${g}, ${b}, 0.1) 0%, transparent 70%)`;

		if (level > 0.8) {
			setVoiceState('stress');
		} else {
			setVoiceState('idle');
		}
	}

	// 3. User Input Handling (Native Web Gateway)
	userInput.addEventListener('keypress', async (e) => {
		if (e.key === 'Enter') {
			// UI Feedback
			const goal = userInput.value;
			if (!goal) return;
			userInput.value = '';
			setVoiceState('listening');
			appendChatMessage('You', goal, 'user');

			console.log(`Sending goal to agency: ${goal}`);

			try {
				const response = await fetch('/api/goal', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ goal })
				});

				const result = await response.json();

				if (result.status === 'success') {
					setVoiceState('responding');
					const narrative = result.result?.narrative || "Goal acknowledged. Starting sequence.";
					appendChatMessage('Supervisor', narrative, 'agent');
					console.log('Agency responded:', result);
				} else {
					throw new Error(result.error || 'Unknown error');
				}
			} catch (err) {
				console.error('Goal submission failed:', err);
				setVoiceState('stress');
				appendChatMessage('System', `Mission Error: ${err.message}`, 'system');
			}
		}
	});

	// Initial State
	setVoiceState('idle');
	setSystemStress(0.0);

	// 3.1 Global Status Polling
	setInterval(async () => {
		try {
			const res = await fetch('/api/status');
			const status = await res.json();
			const architectStatus = document.querySelector('.architect-status');
			if (architectStatus) {
				if (status.status === 'degraded') {
					architectStatus.textContent = 'Master Grower - Degraded';
					architectStatus.style.color = 'var(--danger)';
				} else {
					architectStatus.textContent = 'Master Grower - Active';
					architectStatus.style.color = 'white';
				}
			}
		} catch (e) { }
	}, 5000);

	// 4. Voice Command Integration (functional)
	const voiceBtn = document.querySelector('.voice-btn');
	let isListening = false;

	if (voiceBtn && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
		const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
		const recognition = new SpeechRecognition();
		recognition.continuous = false;
		recognition.interimResults = false;
		recognition.lang = 'en-US';

		voiceBtn.addEventListener('click', () => {
			if (isListening) {
				recognition.stop();
			} else {
				recognition.start();
				setVoiceState('listening');
				isListening = true;
				voiceBtn.classList.add('listening');
			}
		});

		recognition.onresult = (event) => {
			const transcript = event.results[0][0].transcript;
			console.log('Voice transcript received:', transcript);
			userInput.value = transcript;
			// Trigger command execution
			const e = new KeyboardEvent('keypress', { key: 'Enter' });
			userInput.dispatchEvent(e);
		};

		recognition.onstart = () => {
			console.log('Speech recognition started...');
		};

		recognition.onend = () => {
			console.log('Speech recognition ended.');
			isListening = false;
			voiceBtn.classList.remove('listening');
		};

		recognition.onerror = (event) => {
			console.error('Speech recognition error:', event.error);
			setVoiceState('stress');
		};
	} else if (voiceBtn) {
		voiceBtn.title = 'Speech API not supported in this browser';
		voiceBtn.style.opacity = '0.5';
	}


	// Initialize Workflow Visualizer with animation
	const workflowContainer = document.querySelector('.workflow-container');
	if (workflowContainer && window.WorkflowVisualizer) {
		workflowContainer.classList.add('animate-slide-up', 'stagger-2');
		const visualizer = new WorkflowVisualizer('workflow-chain', 'workflow-status');
		visualizer.connectToBackend();
		window.workflowViz = visualizer;
	}

	// Animate stat cards on load
	const statCards = document.querySelectorAll('.stat-card');
	statCards.forEach((card, index) => {
		card.classList.add('animate-fade-in', `stagger-${index + 3}`);
		card.classList.add('hover-lift', 'transition-all');
	});

	// Animate greenhouse panel
	const greenhousePanel = document.getElementById('greenhouse-panel');
	if (greenhousePanel) {
		greenhousePanel.parentElement.classList.add('animate-slide-up', 'stagger-4');
	}

	// Add smooth transitions to all interactive elements
	const buttons = document.querySelectorAll('button');
	buttons.forEach(btn => {
		btn.classList.add('transition-fast', 'hover-lift');
	});

	// Mock Telemetry Update with smooth transitions
	setInterval(() => {
		const randomLoad = (Math.random() * 30 + 10).toFixed(1);
		const loadElement = document.querySelector('.stat-card .value');
		if (loadElement) {
			loadElement.classList.add('counter');
			loadElement.textContent = randomLoad + '%';
		}
	}, 3000);

	// Mock Telemetry Update
	setInterval(() => {
		const tempValue = document.querySelector('.value.hot');
		const currentTemp = 24.5 + (Math.random() - 0.5);
		tempValue.textContent = `${currentTemp.toFixed(1)}°C`;
	}, 2000);

	// Initialize Workflow Visualizer (if workflow.js is loaded)
	if (window.WorkflowVisualizer) {
		// Create workflow container inside architect-hub
		let workflowContainer = document.getElementById('workflow-container');
		if (!workflowContainer) {
			workflowContainer = document.createElement('div');
			workflowContainer.id = 'workflow-container';
			workflowContainer.style.marginTop = '40px';
			document.querySelector('.architect-hub').appendChild(workflowContainer);
		}

		const visualizer = new WorkflowVisualizer('workflow-container');

		// Update user input handler to show workflow
		const originalKeyHandler = userInput.onkeypress;
		userInput.addEventListener('keypress', async (e) => {
			if (e.key === 'Enter' && userInput.value) {
				// Show workflow visualization
				visualizer.reset();

				//Simulate workflow execution
				setTimeout(() => {
					visualizer.runWorkflow();
				}, 500);
			}
		});

		// Expose visualizer globally for debugging
		window.agencyWorkflow = visualizer;
	}
});
