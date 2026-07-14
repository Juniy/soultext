@echo off
chcp 65001 >nul
title Soultext - 一键启动
color 0B
echo ========================================
echo    Soultext - AI 长篇小说创作引擎
echo    v0.1.0
echo ========================================
echo.
echo  服务地址：
echo    后端 API:  http://localhost:8000
echo    前端页面:  http://localhost:5173
echo.
echo  双击 start_backend.bat 和 start_frontend.bat
echo  分别启动两个服务，或直接在此窗口运行。
echo ========================================
echo.
echo [1] 启动后端 + 前端（推荐）
echo [2] 仅启动后端
echo [3] 仅启动前端
echo [4] 退出
echo.
choice /c 1234 /n /m "请选择 (1-4): "
if errorlevel 4 exit /b
if errorlevel 3 goto frontend
if errorlevel 2 goto backend
if errorlevel 1 goto both

:both
start "Soultext-Backend" cmd /k "cd /d ""%~dp0"" && python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul
start "Soultext-Frontend" cmd /k "cd /d ""%~dp0frontend"" && npx vite --host 0.0.0.0 --port 5173 --strictPort"
echo.
echo 服务已启动！
echo 后端：http://localhost:8000
echo 前端：http://localhost:5173
echo.
pause
exit /b

:backend
cd /d "%~dp0"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
pause
exit /b

:frontend
cd /d "%~dp0frontend"
npx vite --host 0.0.0.0 --port 5173 --strictPort
pause
exit /b
