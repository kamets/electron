# 🎨 _SUDOTEER UI Architecture

## Overview
The _SUDOTEER frontend is built on a modern Electron foundation, inspired by the VS Code aesthetic. It prioritizes high-fidelity "Wow" aesthetics, real-time feedback, and industrial-grade monitoring.

## Core Principles
- **Glassmorphism**: Use of translucent, blurred backgrounds for a premium feel.
- **Real-Time Bidirectional Communication**: Seamless data flow between the Python backend and the Javascript frontend via a secure Electron bridge (`sudoteerAPI`).
- **Reactive Components**: UI elements update instantly in response to agent events and telemetry.
- **GPU-Accelerated Animations**: Smooth transitions and pulsing indicators for active processes.

## Components

### 1. Workflow Visualizer (`workflow.js`)
- **Purpose**: Visualizes the agent validation chain in real-time.
- **States**: `idle`, `active`, `success`, `error`.
- **Animations**: `node-breathe` (active), `pulse-expand` (aura), `flow` (data connector).

### 2. Greenhouse Monitor (`greenhouse-monitor.js`)
- **Purpose**: A "Digital Twin" of the industrial greenhouse simulation.
- **Features**:
  - Real-time gauge updates (Temp, Humidity, pH, Health).
  - Bidirectional controls (Pump Start/Stop).
  - Dynamic color-coding for plant health and stress.

### 3. Central UI Bridge (`ui.js`)
- **Purpose**: Initializes the overall layout and handles global events.
- **Interface**: Exposes methods to update the agent log and terminal.

## Data Flow (Telemetry & Commands)

### Backend -> Frontend (Telemetry)
1. Python backend sends a message via `ui_bridge.py`.
2. The Electron main process catches it and forwards it to the renderer.
3. The `sudoteerAPI.onAgentUpdate` hook in the frontend receives the payload.
4. Component (e.g., `GreenhouseMonitor`) updates its internal state and DOM.

### Frontend -> Backend (Commands)
1. User interacts with a UI element (e.g., clicks "START PUMP").
2. Frontend calls `window.sudoteerAPI.sendCommand`.
3. The Electron main process routes the command to the Python command server.
4. The appropriate agent or simulation handles the request.

## Styling System (`index.css`)
- **Theme**: Premium Dark (Grey/Slate base with vibrant accents).
- **Typography**: Inter (Modern, readable).
- **Animations**: Defined in `index.css` and `workflow.css` using standard CSS `@keyframes`.

## Development Standards
- **Wait for DOM**: Components should auto-initialize on `DOMContentLoaded`.
- **Error Boundaries**: Check for container existence before rendering to avoid script crashes.
- **Mock Support**: Components should have fallback behavior (Dev Mode) when `sudoteerAPI` is missing.
