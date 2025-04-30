@echo off
echo Starting LLM Readability Web App...
echo.
echo The application will be available at http://127.0.0.1:8000
echo Press Ctrl+C followed by Y to stop the server when done.
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0run_app.ps1"
