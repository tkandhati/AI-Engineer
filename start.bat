@echo off
:: Free ports first
call "%~dp0stop.bat"
timeout /t 1 /nobreak >nul

:: Read API key from apikey.txt, or prompt
if exist "%~dp0apikey.txt" (
    set /p ANTHROPIC_KEY=<"%~dp0apikey.txt"
) else (
    set /p ANTHROPIC_KEY=Enter Anthropic API key:
)

:: Start proxy
start "AI Proxy" cmd /k "set ANTHROPIC_KEY=%ANTHROPIC_KEY% && python "%~dp0proxy.py""
timeout /t 2 /nobreak >nul

:: Start page server
start "AI Page Server" cmd /k "cd /d "%~dp0" && python -m http.server 8080"
timeout /t 1 /nobreak >nul

:: Open browser
start http://localhost:8080/index.html
