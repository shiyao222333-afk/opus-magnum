@echo off
chcp 437 >nul
title Opus Magnum - Start All (One-Click Workshop Launcher)
setlocal enabledelayedexpansion

set "OPUS=D:\opus-magnum"
set "NIGREDO=D:\nigredo"
set "ALBEDO=D:\albedo"
set "CITRINITAS=D:\citrinitas"
set "SUP=%OPUS%\front_half\supervisor"

set "RESTART=0"
if /i "%~1"=="--restart" set "RESTART=1"

if "%RESTART%"=="1" (
    echo [RESTART] Killing services on ports 8500/8503/8502/8501/8080 ...
    call :kill_port 8500
    call :kill_port 8503
    call :kill_port 8502
    call :kill_port 8501
    call :kill_port 8080
    timeout /t 2 /nobreak >nul
)

echo **************************************************
echo   Opus Magnum - Start All Workshop
echo   8500 Opus      8503 Supervisor
echo   8502 Nigredo   8501 Albedo   8080 Citrinitas
echo **************************************************
echo.

REM --- Ensure Opus venv exists (shared by Opus dashboard + Supervisor) ---
set "VENV_PY=%OPUS%\venv\Scripts\python.exe"
if exist "%VENV_PY%" goto venv_ok
where python >nul 2>nul
if errorlevel 1 goto no_python
echo [SETUP] First run: creating Opus venv...
python -m venv "%OPUS%\venv"
if not exist "%VENV_PY%" goto venv_create_failed
:venv_ok
"%VENV_PY%" -c "import streamlit" >nul 2>&1
if errorlevel 1 "%VENV_PY%" -m pip install -r "%OPUS%\requirements.txt"
"%VENV_PY%" -c "import nicegui" >nul 2>&1
if errorlevel 1 "%VENV_PY%" -m pip install -r "%SUP%\requirements.txt"
goto after_venv
:no_python
echo [ERROR] Python not found on PATH. Install Python 3.x, then re-run start_all.bat.
goto after_venv
:venv_create_failed
echo [ERROR] Failed to create Opus venv at %OPUS%\venv.
goto after_venv
:after_venv

REM --- Launch each service (skip if port already listening = reuse) ---
call :maybe_start 8500 "Opus Magnum" "D:\opus-magnum\run.bat"
if exist "%VENV_PY%" (
    call :maybe_start 8503 "Supervisor" "%VENV_PY% D:\opus-magnum\front_half\supervisor\app.py"
) else (
    echo [SKIP] Supervisor : Opus venv missing (Python not installed). Start it manually later.
)
call :maybe_start 8502 "Nigredo" "D:\nigredo\run.bat"
call :maybe_start 8501 "Albedo" "D:\albedo\run.bat"
call :maybe_start 8080 "Citrinitas" "D:\citrinitas\run.bat"

echo.
echo ==================================================
echo   Workshop launch complete.
echo   Opus:       http://127.0.0.1:8500
echo   Supervisor: http://127.0.0.1:8503
echo   Nigredo:    http://127.0.0.1:8502
echo   Albedo:     http://127.0.0.1:8501
echo   Citrinitas: http://127.0.0.1:8080
echo   (Services already running were reused, not restarted.)
echo   Tip: run start_all.bat as Administrator so Citrinitas
echo        can elevate/start Qdrant without a second window.
echo   Usage: start_all.bat           (reuse running services)
echo           start_all.bat --restart (force kill + fresh start)
echo ==================================================
echo.
pause
goto :eof


:maybe_start
set "PORT=%~1"
set "NAME=%~2"
set "CMD=%~3"
set "PORT_BUSY=0"
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $t=New-Object System.Net.Sockets.TcpClient; try { $t.Connect('127.0.0.1', %PORT%); $t.Close(); exit 0 } catch { exit 1 }"
if not errorlevel 1 set "PORT_BUSY=1"
if "%PORT_BUSY%"=="1" (
    echo [SKIP] %NAME% : port %PORT% already listening, reusing.
    goto :eof
)
echo [START] %NAME% : port %PORT% ...
start "%NAME%" cmd /k "%CMD%"
timeout /t 2 /nobreak >nul
goto :eof


:kill_port
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %1 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
goto :eof
