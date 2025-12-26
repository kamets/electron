# _SUDOTEER - User Manual 📘

Welcome to **_SUDOTEER**, the premium forensic and financial intelligence desktop application for industrial agriculture and automated agent orchestration.

---

## 🚀 Getting Started

### 1. Launching the Application

To start the system, navigate to the project directory and run:

```powershell
cd c:\Users\NAMAN\electron\_SUDOTEER
npm start
```

This will launch the **Electron Frontend** and automatically spawn the **Python Agency Backend**.

### 2. The Dashboard Overview

Once the application loads, you will see several key panels:

* **System Health Monitor (Top Right)**: Shows a pulsing LED status. 🟢 Green means the backend is alive and processing telemetry.
* **Architect Hub (Center)**: Where you input high-level goals for the agent team.
* **Workflow Visualizer (Bottom Center)**: A real-time animation of the agent chain (Architect → Coder → Tester → Documenter → Validator).
* **Greenhouse Monitor (Bottom Left)**: Live telemetry from your industrial simulation or hardware.

---

## 🤖 Working with Agents

### Sending a Goal

1. Locate the input field in the **Architect Hub**.
2. Type a command like: *"Check greenhouse temperature and optimize growth settings"* or *"Audit the latest code in the knowledge base."*
3. Press **Enter**.
4. Watch the **Workflow Visualizer** - agents will light up blue as they begin working and turn green as they successfully complete their tasks.

### Dynamic Agent Spawning

The system supports a scalable workforce. To add or remove agents:

1. Open the **Agent Factory** panel (under the main hub).
2. Select a role (e.g., "Coder").
3. Enter a unique ID (e.g., `coder_debug_01`).
4. Click **Spawn Agent**.
5. The new agent will immediately register on the A2A bus and be available for tasks.

---

## 🌿 Greenhouse Management

The **Industrial Bridge** provides real-time control over your environment.

### Monitoring Telemetry

* **Temperature**: Tracked with a live sine-wave gauge representing daily cycles.
* **Humidity**: Inverse relationship to temperature, monitored for plant transpiration.
* **pH Level**: Critical for nutrient uptake. The bar will turn red if levels drift into dangerous zones.
* **Water Pressure**: Shows the load on your irrigation system.

### Manual Control

* **Pump Control**: Click the **START PUMP** button to manually activate irrigation.
* **Emergency Stop**: Click the **🚨 STOP ALL** button in the health monitor to shut down all actuators immediately.

---

## 🧠 Memory & Knowledge Base

### Vector Database Viewer (Vex Extension)

To inspect what your agents are "remembering":

1. Open the **Vex** sidebar in VS Code.
2. Connect to `localhost:8000`.
3. Expand **Collections** → **agent_memories**.
4. You can see individual "reasoning traces" and observation vectors stored by the agents.

### Graph Visualization (Neo4j)

For complex relationships between tasks and entities, use the **Neo4j** dashboard to see how agents are collaborating and which documents depend on which code modules.

---

## 🛠️ Troubleshooting

* **Heartbeat STALLED (Yellow LED)**: The backend is busy with a heavy calculation or the main thread is blocked. Wait a few seconds for it to recover.
* **Backend DISCONNECTED (Red LED)**: The Python process has crashed. Restart the app using `npm start`.
* **No Data in Vex**: Ensure you ran the `chroma run` command in a separate terminal.

---

**_SUDOTEER - Architecting the Future of Intelligent Automation.**
