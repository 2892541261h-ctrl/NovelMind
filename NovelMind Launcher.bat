@echo off
setlocal

set "ROOT=%~dp0"
set "LAUNCHER=%ROOT%scripts\launch-novelmind.ps1"

if not exist "%LAUNCHER%" (
  echo Missing launcher script: "%LAUNCHER%"
  pause
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%"
if errorlevel 1 (
  echo.
  echo NovelMind launcher failed.
  pause
  exit /b 1
)

endlocal
