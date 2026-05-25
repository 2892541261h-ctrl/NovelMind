@echo off
REM ============================================================
REM NovelMind V1 Web Launcher (LEGACY)
REM
REM This launcher opens NovelMind in a native WebView window via
REM pywebview. It is the original desktop launcher from V1.
REM
REM For the Electron-based V2 desktop client candidate, see:
REM   desktop-electron/
REM   docs/DESKTOP_CLIENT_GUIDE.md
REM
REM This file is preserved for backward compatibility.
REM ============================================================

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
