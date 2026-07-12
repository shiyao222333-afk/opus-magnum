@echo off
chcp 437 >nul
title Opus Magnum - Front-Half Launcher
setlocal enabledelayedexpansion
set "OPUS_DIR=D:\opus-magnum"
set "SUP_DIR=%OPUS_DIR%\front_half\supervisor"
set "CIT_DIR=D:\citrinitas"

echo **************************************************
echo   * Opus Magnum Front-Half Launcher
echo   Step 1: start Citrinitas (data center / inbox)
echo   Step 2: start Supervisor (pipeline UI :8503)
echo **************************************************
echo.

REM Step 1: start Citrinitas in its own window (it elevates to admin and starts Qdrant)
echo [1/2] Starting Citrinitas (inbox listener)...
start "Citrinitas" cmd /k "%CIT_DIR%\run.bat"
echo   Waiting for Citrinitas to come up...
timeout /t 8 /nobreak >nul

REM Step 2: start Supervisor (pipeline UI)
echo [2/2] Starting Supervisor (pipeline UI)...
if exist "%OPUS_DIR%\venv\Scripts\python.exe" (
    set "PY=%OPUS_DIR%\venv\Scripts\python.exe"
) else (
    set "PY=python"
)
%PY% -c "import nicegui" >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Installing supervisor dependencies...
    %PY% -m pip install -r "%SUP_DIR%\requirements.txt"
)
start "Supervisor" cmd /k "%PY% %SUP_DIR%\app.py"
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8503

echo.
echo ==================================================
echo   Front-Half started:
echo   - Citrinitas (inbox): http://127.0.0.1:8080
echo   - Supervisor (pipeline): http://127.0.0.1:8503
echo   Close the two opened windows to stop.
echo ==================================================
pause
