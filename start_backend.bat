@echo off
cd /d "E:\DEV\git\soultext"
echo [Soultext] Starting backend on port 18732...
python -m uvicorn backend.app:app --host 0.0.0.0 --port 18732 --reload
if errorlevel 1 (
    echo [Soultext] Backend exited with error code %errorlevel%
    pause
)
