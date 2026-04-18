@echo off
setlocal enabledelayedexpansion

:: Free ports first
call "%~dp0stop.bat"
timeout /t 1 /nobreak >nul

:: Read key from apikey.txt — prompt once and save if missing
if not exist "%~dp0apikey.txt" (
    set /p ANTHROPIC_KEY=Enter Anthropic API key (saved for future runs):
    echo !ANTHROPIC_KEY!> "%~dp0apikey.txt"
    echo Key saved to apikey.txt
)
set /p ANTHROPIC_KEY=<"%~dp0apikey.txt"

:: Start proxy
start "AI Proxy" cmd /k "set ANTHROPIC_KEY=%ANTHROPIC_KEY% && python "%~dp0proxy.py""
timeout /t 2 /nobreak >nul

:: Start page server
start "AI Page Server" cmd /k "cd /d "%~dp0" && python -m http.server 8080"
timeout /t 1 /nobreak >nul

:: Open browser
start http://localhost:8080/index.html
