@echo off
echo ============================================================
echo   _SUDOTEER Vector Database (ChromaDB + Proxy)
echo ============================================================
echo.
echo 1. Starting ChromaDB Core on port 8001...
start /min "Chroma Core" "%~dp0..\.venv\Scripts\chroma.exe" run --path "%~dp0..\data\vector_db" --port 8001 --host 0.0.0.0

echo 2. Giving Chroma 5 seconds to warm up...
timeout /t 5 /nobreak > nul

echo 3. Starting Compatibility Proxy on port 8888...
echo (Translates v1 -> v2 for Vex Extension)
"%~dp0..\.venv\Scripts\python.exe" "%~dp0chroma_proxy.py" --port 8888
