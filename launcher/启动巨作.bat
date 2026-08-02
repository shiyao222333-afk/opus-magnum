@echo off
REM ============================================================
REM   OpusMagnum launcher (system tray version)
REM   ASCII-only on purpose: Chinese comments break cmd parsing
REM   when the file is UTF-8 but the system codepage is GBK.
REM ============================================================
set "PYW=D:\opus-magnum\venv\Scripts\pythonw.exe"
set "SCRIPT=%~dp0launcher.pyw"

REM double-click probe (diagnostic; safe to remove later)
echo [%date% %time%] double-click >> "%~dp0_doubleclick.log"

if not exist "%PYW%" goto MISSING
if not exist "%SCRIPT%" goto MISSING

start "" "%PYW%" "%SCRIPT%"
exit /b 0

:MISSING
echo ERROR: file not found. PYW=%PYW% SCRIPT=%SCRIPT%
pause
exit /b 1
