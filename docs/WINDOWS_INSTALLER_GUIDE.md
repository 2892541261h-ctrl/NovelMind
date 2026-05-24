# NovelMind Windows Installer Guide

This guide describes the V1 Windows MSI installer preview.

## What This Installer Is

The MSI is a local development environment installer preview. It is designed to make NovelMind easier to launch on Windows, but it is not a fully standalone offline desktop application.

The installed launcher starts the local backend and frontend, then opens:

```text
http://localhost:5173
```

## Requirements On The Target Machine

The current installer preview expects the machine to already have:

- Windows PowerShell.
- Python 3.11+.
- Node.js and npm.

The launcher reuses the existing local startup scripts. If `.venv` or `node_modules` are missing, the existing scripts may ask the user to create Python virtual environment dependencies or run npm installation as part of startup.

## Build The MSI

Install WiX Toolset v4 on the build machine, then run from the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-msi.ps1
```

The build script first runs:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

If the final release check fails, the MSI build stops. If WiX is not installed, the script reports that WiX is missing and does not generate an MSI.

Expected output when WiX is available:

```text
installer/dist/NovelMind-V1-Setup.msi
```

Do not commit this file.

## Install And Launch

1. Run `NovelMind-V1-Setup.msi`.
2. Confirm the Desktop shortcut `NovelMind` exists.
3. Confirm the Start Menu shortcut `NovelMind` exists.
4. Double-click `NovelMind`.
5. Wait for the backend and frontend windows to start.
6. The launcher opens `http://localhost:5173`.

If startup fails, the launcher keeps the window open so the error can be read.

## API Key Safety

Do not put real API keys into the MSI.

NovelMind stores AI provider configuration as environment variable names such as `OPENAI_API_KEY`, not raw key values. Real keys should stay in the user's local environment variables.

The MSI source and build scripts must not include:

- `.env`
- API Key
- Token
- Private key
- Database files

## Build Artifacts

MSI, EXE, ZIP, `.wixobj`, `.wixpdb`, and `installer/dist/` artifacts are ignored by Git. They are local build outputs only.

If a future release needs to distribute an MSI, create it locally after checks and upload the artifact manually to GitHub Releases. Do not commit installer binaries to the repository.

## Uninstall Notes

The MSI is configured to remove the install directory and shortcuts on uninstall. User-created `.env` or database files should not be packaged in the installer. If a user manually creates local data inside the install directory, Windows Installer may remove files it owns during uninstall; keep important user data outside the install directory.
