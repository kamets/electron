const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess = null;

function createWindow() {
	mainWindow = new BrowserWindow({
		width: 1400,
		height: 900,
		frame: false, // Frameless for premium design
		titleBarStyle: 'hidden',
		backgroundColor: '#0a0f1e',
		webPreferences: {
			preload: path.join(__dirname, 'preload.js'),
			contextIsolation: true,
			nodeIntegration: false
		}
	});

	mainWindow.loadFile(path.join(__dirname, '../views/index.html'));

	// Open DevTools in development
	mainWindow.webContents.openDevTools();

	// Start Python backend with real-time communication
	startPythonBackend();
}

function startPythonBackend() {
	const pythonPath = path.join(__dirname, '../../.venv/Scripts/python.exe');
	const scriptPath = path.join(__dirname, '../../backend/agency.py');

	// Spawn Python process with unbuffered output
	pythonProcess = spawn(pythonPath, ['-u', scriptPath], {
		cwd: path.join(__dirname, '../..')
	});

	console.log('[Electron] Python backend started');

	// Buffer for handling partial data across chunks
	let stdoutBuffer = '';

	pythonProcess.stdout.on('data', (data) => {
		stdoutBuffer += data.toString();

		// Split by delimiter
		if (stdoutBuffer.includes('::SUDO::')) {
			const parts = stdoutBuffer.split('::SUDO::');

			// The last part might be incomplete, keep it in buffer
			stdoutBuffer = parts.pop();

			parts.forEach((part) => {
				const cleanPart = part.trim();
				if (!cleanPart) return;

				if (cleanPart.startsWith('{') && cleanPart.endsWith('}')) {
					try {
						const jsonData = JSON.parse(cleanPart);
						if (mainWindow) {
							mainWindow.webContents.send('agent-update', jsonData);
						}
					} catch (e) {
						console.error('[Electron] IPC JSON Parse Failure:', e.message, 'Part:', cleanPart);
					}
				} else {
					// Fallback for non-JSON or malformed parts
					console.log(`[Python Log]: ${cleanPart}`);
				}
			});
		}
	});

	pythonProcess.stderr.on('data', (data) => {
		console.error(`[Python Error]: ${data.toString()}`);
	});

	pythonProcess.on('close', (code) => {
		console.log(`[Electron] Python process exited with code ${code}`);
		pythonProcess = null;
	});
}

// IPC Handler: Frontend Commands → Python stdin
ipcMain.on('frontend-command', (event, { command, payload }) => {
	if (pythonProcess && pythonProcess.stdin) {
		const packet = JSON.stringify({ command, payload });
		pythonProcess.stdin.write(packet + '\n');
		console.log(`[Electron → Python]: ${packet}`);
	} else {
		console.error('[Electron] Cannot send command: Python process not running');
	}
});

// SYSTEM: Health Check Handler
ipcMain.handle('system-ping', async () => {
	return { status: 'online', timestamp: Date.now() };
});

// AGENT: Run Task Handler (Forward to command server)
ipcMain.handle('run-agent-task', async (event, taskData) => {
	if (pythonProcess && pythonProcess.stdin) {
		const packet = JSON.stringify({ command: 'RUN_TASK', payload: taskData });
		pythonProcess.stdin.write(packet + '\n');
		return { status: 'queued', task: taskData.goal };
	}
	return { status: 'error', reason: 'Backend offline' };
});

// Graceful shutdown
app.on('will-quit', () => {
	if (pythonProcess) {
		pythonProcess.kill();
	}
});

app.whenReady().then(() => {
	createWindow();

	app.on('activate', () => {
		if (BrowserWindow.getAllWindows().length === 0) createWindow();
	});
});

app.on('window-all-closed', () => {
	if (pythonProcess) {
		pythonProcess.kill();
	}
	if (process.platform !== 'darwin') app.quit();
});
