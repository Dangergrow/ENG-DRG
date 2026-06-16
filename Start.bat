@echo off
title LinguaMate
cd /d "%~dp0"
echo   LinguaMate - English AI Tutor
echo   Starting...
echo.
start "" http://127.0.0.1:5000
python main.py
pause
