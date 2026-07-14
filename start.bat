@echo off
cd /d "E:\DEV\git\soultext"
echo [Soultext] Starting backend on port 18732...
start "Soultext-Backend" cmd /k "python -m uvicorn backend.app:app --host 0.0.0.0 --port 18732 --reload"
timeout /t 3 /nobreak >nul
echo [Soultext] Starting frontend on port 18733...
start "Soultext-Frontend" cmd /k "cd /d "E:\DEV\git\soultext\frontend" && npx vite --host 0.0.0.0 --port 18733 --strictPort"
echo [Soultext] Both services started.
echo [Soultext] Backend: http://localhost:18732
echo [Soultext] Frontend: http://localhost:18733
