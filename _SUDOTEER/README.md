# _SUDOTEER: Industrial Forensic & Financial Agency

_SUDOTEER is a premium desktop application for industrial-grade forensic analysis and financial intelligence.

## Architecture

For detailed service relationships and layered design, see:
- [Architecture Diagrams Documentation (v11.1.0+)](./docs/ARCHITECTURE_DIAGRAMS.md)


## Directory Structure

- `backend/`: DSPy logic and agent services.
- `sandbox/`: Workstations and simulations (LangGraph).
- `frontend/`: Electron (VS Code base) with iOS-inspired UI.
- `assets/`: UI assets and generated charts.

## Setup

1. `cd backend`
2. `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
3. `pip install -r requirements.txt`
