@echo off
setlocal
title _SUDOTEER Agency - MASTER START

echo ============================================================
echo   🧬 _SUDOTEER: FORENSIC INTELLIGENCE AGENCY
echo ============================================================
echo.

:: 1. Environment Check
if not exist "%~dp0.venv" (
    echo [!] Warning: .venv folder not found at %~dp0.venv
    pause
    exit /b
)

:: 2. Start ChromaDB (Vector Core)
echo [1/3] Starting ChromaDB Core (Port 8001)...
start /min "SUDOTEER-Chroma-Core" "%~dp0.venv\Scripts\chroma.exe" run --path "%~dp0data\vector_db" --port 8001 --host 0.0.0.0

:: 3. Start Agency Web Server (UI + Proxy)
echo [2/3] Launching Agency Web Server (Port 8000)...
echo.
echo ============================================================
echo   AGENCY ACTIVE. Access UI at: http://localhost:8000
echo ============================================================
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0scripts\webserver.py"

pause
