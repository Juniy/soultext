@echo off
start "Soultext-Backend" cmd /k "cd /d E:\DEV\git\soultext && python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3
start "Soultext-Frontend" cmd /k "cd /d E:\DEV\git\soultext\frontend && npx vite --host 0.0.0.0 --port 5173 --strictPort"
echo Done.
