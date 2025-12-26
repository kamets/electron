# _SUDOTEER - Deployment Guide 🏗️

This guide outlines the steps to deploy **_SUDOTEER** in production environments, ranging from local industrial workstations to containerized cloud deployments.

---

## 💻 Local Workstation Deployment (Industrial)

For deployment on factory floors or greenhouse control rooms.

### 1. Prerequisites
*   **Python 3.10+**: Recommended for performance and stability.
*   **Node.js 18+**: For the Electron frontend.
*   **Hardware Interface**: USB-to-RS485 adapter (for Modbus/PLC communication).

### 2. Environment Setup
1.  **Clone & Install**:
    ```powershell
    git clone https://github.com/sudoteer/agency.git
    cd _SUDOTEER
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    npm install
    ```
2.  **Configuration**:
    Edit `.env` with production keys:
    *   `GEMINI_API_KEY`: For primary agent reasoning.
    *   `PLC_IP` / `COM_PORT`: For hardware bridge.
    *   `SUPABASE_URL`: For persistent long-term memory.

### 3. Running as a System Service (Windows)
To ensure the app restarts on boot, use **PM2** or a Windows Task:
```powershell
# Using PM2
pm2 start "npm start" --name "sudoteer-agency"
pm2 save
```

---

## 🐳 Containerized Deployment (Docker)

Ideal for cloud-based brain instances or multi-site management.

### 1. Docker Compose
Use the provided `docker-compose.yml` (located in root) to spin up the full stack:
```bash
docker-compose up -d
```

**Includes**:
*   **Backend**: Python Agency Container.
*   **Database**: ChromaDB (Vector) + Neo4j (Graph).
*   **Real-time Bridge**: WebSocket Proxy.

### 2. Networking
*   **Exposed Port**: 8000 (API & Telemetry).
*   **Local Access**: `http://localhost:8000`.

---

## ☁️ Cloud Persistence (Supabase + Pinecone)

To scale memory across multiple physical locations:

1.  **Database Migration**: Run the SQL scripts in `backend/data/schema.sql` on your Supabase instance.
2.  **Vector Store**: Create a Pinecone index with **1536 dimensions** (for OpenAI embeddings) or **384 dimensions** (for local MiniLM).
3.  **Cross-Region Sync**: Configure the `HybridMemoryManager` in `backend/core/memory/manager.py` to use `pinecone` as the backend instead of `chroma`.

---

## 🛡️ Security Best Practices

1.  **Isolation**: Run the agency in its own virtual environment or container to prevent library conflicts.
2.  **API Keys**: Never commit `.env` files. Use environment secrets in production.
3.  **Access Control**: The UIBridge broadcasts to localhost by default. Use an NGINX reverse proxy with Auth for remote access.
4.  **Hardware Safety**: Ensure `GreenhouseAgent` safety limits match your physical equipment specs.

---

**For deployment assistance, contact the _SUDOTEER DevOps Team.**
