@echo off
chcp 65001 >nul
title Soultext - 后端服务
cd /d "%~dp0"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
pause
