@echo off
echo Freeing ports 5001 and 8080...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5001 "') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080 "') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Done. Ports 5001 and 8080 are free.
