import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from backend.core.memory.vector_db import vector_db
    print(f"--- 🗄️ CHROMA CONNECTION AUDIT ---")
    print(f"Agent Connection Logic: {vector_db.backend_type}")

    # Check if we can reach the ports
    import socket
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    print(f"Port 8001 (Core): {'ACTIVE' if check_port(8001) else 'OFFLINE'}")
    print(f"Port 8000 (Proxy): {'ACTIVE' if check_port(8000) else 'OFFLINE'}")
    print(f"Port 8888 (Web UI): {'ACTIVE' if check_port(8888) else 'OFFLINE'}")

    print("\n[RECOMMENDATION]")
    print("If your UI/Extension says 'Cannot connect to 8888', change its config to 8000.")
    print("-----------------------------------")

except Exception as e:
    print(f"Error during audit: {e}")
