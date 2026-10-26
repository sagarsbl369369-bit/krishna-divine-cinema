@echo off
title Gita Production Studio Dashboard
echo ==================================================================
echo 🕉️ GITA PRODUCTION STUDIO - MISSION CONTROL DASHBOARD
echo ==================================================================
cd /d "%~dp0"
start http://127.0.0.1:8000
python dashboard.py
pause
