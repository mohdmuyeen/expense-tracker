@echo off
cd /d "%~dp0"

start "Expense Tracker Server" /min "%~dp0.venv\Scripts\pythonw.exe" "%~dp0app.py"

timeout /t 2 /nobreak >nul

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:5000"