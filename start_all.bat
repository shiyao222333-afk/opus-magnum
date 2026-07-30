@echo off
chcp 437 >nul
title Opus Magnum - Start All (One-Click Workshop Launcher)
setlocal enabledelayedexpansion

REM --- Self-resolve script directory (no hardcoded drive letter) ---
set "OPUS_DIR=%~dp0"
if "%OPUS_DIR:~-1%"=="\" set "OPUS_DIR=%OPUS_DIR:~0,-1%"
for %%I in ("%OPUS_DIR%.") do set "ROOT=%%~dpI"

set "NIGREDO=%ROOT%nigredo"
set "ALBEDO=%ROOT%albedo"
set "CITRINITAS=%ROOT%citrinitas"

set "RESTART=0"
if /i "%~1"=="--restart" set "RESTART=1"

if "%RESTART%"=="1" (
    echo [RESTART] Killing services on ports 8501/8080 ...
    call :kill_port 8501
    call :kill_port 8080
    timeout /t 2 /nobreak >nul
)

echo **************************************************
echo   Opus Magnum - Start All Workshop
echo   8501 Opus      8080 Citrinitas
echo   (Nigredo / Albedo run headless, PID-lock guarded)
echo **************************************************
echo.

REM --- Ensure Opus venv exists (shared by Opus dashboard) ---
set "VENV_PY=%OPUS_DIR%\venv\Scripts\python.exe"
if exist "%VENV_PY%" goto venv_ok
where python >nul 2>nul
if errorlevel 1 goto no_python
echo [SETUP] First run: creating Opus venv...
python -m venv "%OPUS_DIR%\venv"
if not exist "%VENV_PY%" goto venv_create_failed
:venv_ok
"%VENV_PY%" -c "import nicegui" >nul 2>&1
if errorlevel 1 "%VENV_PY%" -m pip install -r "%OPUS_DIR%\requirements.txt"
goto after_venv
:no_python
echo [ERROR] Python not found on PATH. Install Python 3.x, then re-run start_all.bat.
goto after_venv
:venv_create_failed
echo [ERROR] Failed to create Opus venv at %OPUS_DIR%\venv.
goto after_venv
:after_venv

REM --- Launch each service ---
if exist "%VENV_PY%" (
    echo [START] Opus Magnum : port 8501 ...
    start "Opus Magnum" "%VENV_PY%" "%OPUS_DIR%\app.py"
) else (
    echo [SKIP] Opus : venv missing.
)
call :start_headless "Nigredo" "%NIGREDO%\run.bat"
call :start_headless "Albedo" "%ALBEDO%\run.bat"
call :maybe_start 8080 "Citrinitas" "%CITRINITAS%\run.bat"

echo.
echo ==================================================
echo   Workshop launch complete.
echo   Opus:       http://127.0.0.1:8501
echo   Citrinitas: http://127.0.0.1:8080
echo   Nigredo / Albedo: headless (check Opus 摄入入口页状态灯)
echo   (PID-lock guarded: re-running won't double-launch.)
echo   Tip: run start_all.bat --restart to force restart port-based services.
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
start "%NAME%" "%CMD%"
timeout /t 2 /nobreak >nul
goto :eof


:start_headless
set "NAME=%~1"
set "CMD=%~2"
echo [START] %NAME% : headless ...
start "%NAME%" "%CMD%"
timeout /t 2 /nobreak >nul
goto :eof


:kill_port
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %1 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
goto :eof
