# NovelMind Windows MSI Installer Preview

This directory contains the source configuration for a Windows MSI preview installer.

## Status

- Installer approach: WiX Toolset.
- Build output: `installer/dist/NovelMind-V1-Setup.msi`.
- Build output must not be committed to Git.
- This is a local development environment installer preview, not a fully offline desktop app.

## Requirements

The installed launcher still expects the target machine to have:

- Windows PowerShell.
- Python 3.11+.
- Node.js and npm.
- WiX Toolset v4 only when building the MSI.

NovelMind does not package real API keys. If real AI providers are configured, keys must stay in local environment variables.

## Build

From the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-msi.ps1
```

The build script first runs:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\final-release-check.ps1
```

If WiX is missing, the script stops with a clear message and does not generate an MSI.

## Installed Launcher

The MSI config creates:

- Desktop shortcut: `NovelMind`
- Start Menu shortcut: `NovelMind`

Both shortcuts use `installer/assets/NovelMind.ico` as the NovelMind application icon. The MSI also sets the ARP product icon so Windows Apps & Features / Control Panel can show the same icon where supported.

Both shortcuts point to `NovelMind Launcher.bat`, which runs:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\launch-novelmind.ps1
```

The launcher starts the local backend and frontend, then opens:

```text
http://localhost:5173
```

## Security Notes

The installer source excludes `.env`, `.venv`, `node_modules`, `frontend/dist`, `*.db`, Git internals, and installer build artifacts.

Do not upload the MSI to the repository. If publishing later, upload the MSI manually as a GitHub Release artifact after final checks.
