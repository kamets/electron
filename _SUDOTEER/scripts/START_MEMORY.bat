@echo off
echo ============================================================
echo   _SUDOTEER Vector Database (ChromaDB + Proxy)
echo ============================================================
echo.
echo 1. Starting ChromaDB Core on port 8001...
start /min "Chroma Core" .\.venv\Scripts\chroma.exe run --path .\backend\data\vector_db --port 8001 --host 0.0.0.0

echo 2. Giving Chroma 5 seconds to warm up...
timeout /t 5 /nobreak > nul

echo 3. Starting Compatibility Proxy on port 8000...
echo (Translates v1 -> v2 for Vex Extension)
.\.venv\Scripts\python.exe chroma_proxy.py
