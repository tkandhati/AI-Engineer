@echo off
setlocal enabledelayedexpansion

set DIR=%~dp0

:: Free ports
call "%DIR%stop.bat"
timeout /t 1 /nobreak >nul

:: Read or save API key
if not exist "%DIR%apikey.txt" (
    set /p ANTHROPIC_KEY=Enter Anthropic API key (saved for future runs):
    echo !ANTHROPIC_KEY!> "%DIR%apikey.txt"
)
set /p ANTHROPIC_KEY=<"%DIR%apikey.txt"

if "!ANTHROPIC_KEY!"=="" (
    echo ERROR: apikey.txt is empty. Delete it and run start.bat again.
    pause
    exit /b 1
)

:: Start proxy
set PROXY_CMD=set ANTHROPIC_KEY=!ANTHROPIC_KEY! && cd /d %DIR% && python proxy.py
start "AI Proxy" cmd /k "%PROXY_CMD%"
timeout /t 2 /nobreak >nul

:: Start page server
start "AI Page Server" cmd /k "cd /d %DIR% && python -m http.server 8080"
timeout /t 1 /nobreak >nul

:: Open browser
start http://localhost:8080/index.html

echo Started. Close the two terminal windows or run stop.bat to shut down.
