@echo off
chcp 65001 >nul
REM ============================================================
REM   巨作 Opus Magnum — 一键启动器（系统托盘版，无黑框）
REM ============================================================
setlocal
set "PYW=C:\Users\Lenovo\.workbuddy\binaries\python\versions\3.13.12\pythonw.exe"
set "SCRIPT=%~dp0launcher.pyw"

if not exist "%PYW%" (
    echo 找不到 pythonw：%PYW%
    echo 请确认受管 Python 路径是否正确。
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo 找不到启动脚本：%SCRIPT%
    pause
    exit /b 1
)

REM 用 pythonw 启动（无控制台窗口），托盘出现图标即代表已运行
start "" "%PYW%" "%SCRIPT%"
exit /b 0
