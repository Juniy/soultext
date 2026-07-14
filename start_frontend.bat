@echo off
chcp 65001 >nul
title Soultext - 前端服务
cd /d "%~dp0frontend"
npx vite --host 0.0.0.0 --port 5173 --strictPort
pause
