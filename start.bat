@echo off
setlocal enabledelayedexpansion

set DIR=%~dp0

echo Stopping any existing servers...
call "%DIR%stop.bat"
timeout /t 1 /nobreak >nul

:: Read or save API key
if not exist "%DIR%apikey.txt" (
    set /p ANTHROPIC_KEY=Enter Anthropic API key:
    echo !ANTHROPIC_KEY!> "%DIR%apikey.txt"
    echo Key saved.
)
set /p ANTHROPIC_KEY=<"%DIR%apikey.txt"

if "!ANTHROPIC_KEY!"=="" (
    echo ERROR: apikey.txt is empty. Delete it and run again.
    pause
    exit /b 1
)

:: Write a temp launcher for the proxy (avoids quoting issues)
echo @echo off > "%DIR%_proxy_launch.bat"
echo set ANTHROPIC_KEY=!ANTHROPIC_KEY!>> "%DIR%_proxy_launch.bat"
echo cd /d %DIR%>> "%DIR%_proxy_launch.bat"
echo python proxy.py>> "%DIR%_proxy_launch.bat"

echo Starting proxy on port 5001...
start "AI Proxy" cmd /k "%DIR%_proxy_launch.bat"
timeout /t 2 /nobreak >nul

echo Starting page server on port 8080...
start "AI Page Server" cmd /k "cd /d %DIR% && python -m http.server 8080"
timeout /t 1 /nobreak >nul

echo Opening browser...
start http://localhost:8080/index.html

echo.
echo Done. Keep the two terminal windows open.
echo Run stop.bat to shut down.
pause
