@echo off
title WhatsApp Bot - Windows
cd /d "%~dp0"

echo [bot] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo [bot] Installing dependencies...
pip install -r requirements.txt -q

echo [bot] Starting Flask webhook server...
start "Flask Bot" cmd /k "python server_windows.py"

timeout /t 3 /nobreak >nul

echo [bot] Starting wacli sync...
start "wacli sync" cmd /k "wacli.exe sync --follow --webhook http://127.0.0.1:5000/webhook"

echo.
echo ========================================
echo  Bot is running! ComfyUI starts only
echo  when someone sends @imagine command.
echo  Close BOTH windows to stop the bot.
echo ========================================
pause
