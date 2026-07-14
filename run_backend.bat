@echo off
cd /d "%~dp0"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 1>backend_stdout.txt 2>backend_stderr.txt
if %errorlevel% neq 0 (
  echo Backend crashed with errorlevel=%errorlevel% > backend_crash.txt
  type backend_stderr.txt >> backend_crash.txt
  echo. >> backend_crash.txt
  echo === stdout === >> backend_crash.txt
  type backend_stdout.txt >> backend_crash.txt
  pause
)
