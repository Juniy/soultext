@echo off
cd /d "E:\DEV\git\soultext\frontend"
echo [Soultext] Starting frontend on port 18733...
npx vite --host 0.0.0.0 --port 18733 --strictPort
if errorlevel 1 (
    echo [Soultext] Frontend exited with error code %errorlevel%
    pause
)
