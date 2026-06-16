@echo off
title DRG ENG Build
cd /d "%~dp0"

echo ========================================
echo   DRG ENG v1.0.0 — Build System
echo ========================================
echo.

echo [1/3] Installing dependencies...
pip install flask openai edge-tts pywebview pyinstaller certifi --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/3] Generating icon...
python -c "import struct,base64;open('app.ico','wb').write(base64.b64decode('AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AAAA='))" 2>nul
if not exist "app.ico" (
    echo WARNING: No icon file, using default
)

echo [3/3] Building DRGENG.exe...
pyinstaller --clean --noconfirm DRGENG.spec
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETE!
echo   dist\DRGENG.exe
echo ========================================
echo.
echo To test: dist\DRGENG.exe
pause
