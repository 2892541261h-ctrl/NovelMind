# NovelMind Desktop Client Guide

## Overview

NovelMind offers two ways to run the application:

| Mode | Launcher | Requires Browser? | Technology |
|------|----------|-------------------|------------|
| **Web Dev** | `scripts/start-dev.ps1` | Yes (Chrome/Edge at localhost:5173) | Vite + FastAPI |
| **Desktop V1 (Legacy)** | `NovelMind Launcher.bat` | No (pywebview) | pywebview |
| **Desktop V2 (Candidate)** | `desktop-electron/` | No (Electron) | Electron + FastAPI |

## Technology Choice: Electron vs Tauri

### Why Electron (not Tauri)

1. **Frontend is React/TypeScript**: Electron can directly load the Vite-built SPA via `BrowserWindow.loadURL()`. Tauri requires building a Rust IPC bridge layer to communicate between the Rust backend and the React frontend.

2. **Existing backend is FastAPI (Python)**: The backend stays as-is regardless of Electron or Tauri. Tauri's Rust process would be an unnecessary third runtime alongside Python and Node.js.

3. **Sidecar management**: Electron's `child_process.spawn` API is straightforward for managing the Python FastAPI backend process. Tauri's sidecar support requires bundling platform-specific binaries.

4. **Development velocity**: Electron's larger ecosystem (electron-builder, electron-store, electron-log) means faster iteration for a candidate/prototype.

5. **No Rust build step**: Tauri compiles a Rust binary on every build, adding complexity. Electron packages JS files directly — the only "build" is `electron-builder` for distribution.

6. **pywebview → Electron is a natural upgrade**: The V1 desktop already uses a WebView approach. Electron adds system tray, single-instance lock, and proper window management on top of the same concept.

### Why Tauri Could Be Considered Later

- Smaller binary size (~5MB vs ~150MB)
- Lower memory footprint (Rust vs Chromium)
- Better security model (no Node.js in renderer)

Tauri is a better long-term goal if the Python backend can also be packaged (e.g., PyInstaller + Tauri sidecar). For the V2 candidate, Electron provides the fastest path to a stable prototype.

## Quick Start

### Web Development Mode

```powershell
# Terminal 1: Backend
.\scripts\start-backend.ps1

# Terminal 2: Frontend
.\scripts\start-frontend.ps1

# Or both at once:
.\scripts\start-dev.ps1
```

Then open `http://127.0.0.1:5173` in your browser.

### Desktop Client (Electron)

```powershell
cd desktop-electron
npm install
npm start
```

This:
1. Checks for Python (`.venv/Scripts/python.exe`, a compatible `py -0p` runtime, or system `python`)
2. Starts the FastAPI backend on `http://127.0.0.1:8765`
3. Waits for `/health` to return 200
4. Opens the Electron window at `http://127.0.0.1:8765/app`
5. Shows a system tray icon with context menu

## Dependencies

### Runtime Dependencies

| Dependency | Required? | Notes |
|-----------|-----------|-------|
| Python 3.11-3.13 | **Yes** | Backend is not yet packaged as standalone .exe; Python 3.14 is intentionally skipped for dependency compatibility |
| Node.js 18+ | Build/dev only | The installed Electron app bundles Chromium and frontend assets |
| npm | Build/dev only | For `npm install` and `npm run build` in `desktop-electron/` |
| Electron | Auto-installed | `npm install` in desktop-electron/ installs it |
| Google Chrome | No | Electron bundles Chromium |

### Python Backend Packaging Status

**The Python backend is NOT yet packaged as a standalone .exe.**

- **PyInstaller is not currently installed** on development machines.
- The Electron desktop client starts the backend via an app-local Python virtual environment in `%APPDATA%\novelmind-desktop\python-runtime`.
- On first launch, it creates that runtime from a compatible Python 3.11-3.13 installation and installs `backend/requirements.txt` there.
- Users need Python 3.11-3.13 available, but they do not need to pre-install backend dependencies into system Python.

**Next steps for standalone packaging:**
1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller --onefile --name novelmind-backend backend/main.py`
3. Configure Electron to use the .exe as a sidecar instead of calling Python directly
4. Remove the Python runtime requirement from user machines

## Tray Menu

Right-click the NovelMind tray icon for these options:

| Menu Item | Action |
|-----------|--------|
| **打开 NovelMind** | Show/hide the main window |
| **重启服务** | Kill and restart the Python backend, reload the page |
| **退出** | Close the backend and quit the application |

- **Double-click** the tray icon to show the window
- **Minimize to tray**: Clicking the window close button minimizes to tray instead of quitting

## Build Desktop Client

```powershell
cd desktop-electron
npm install
npm run build        # Electron-builder produces NSIS installer
```

Output: `desktop-electron/dist/NovelMind Setup 2.0.0.exe`

**Note:** This produces an NSIS installer, not MSI. The existing WiX MSI in `installer/` is preserved for V1.

## Logs

Logs are written to `%APPDATA%\novelmind-desktop\logs\`:

| File | Content |
|------|---------|
| `backend.log` | FastAPI backend stdout/stderr |
| `desktop.log` | Electron main process logs |

To view logs:

```powershell
# Open logs directory
explorer $env:APPDATA\novelmind-desktop\logs

# Or read latest lines
Get-Content $env:APPDATA\novelmind-desktop\logs\backend.log -Tail 50
Get-Content $env:APPDATA\novelmind-desktop\logs\desktop.log -Tail 50
```

## Exit Backend Services

### From the Desktop App

Right-click tray icon → **退出**

### Manually

```powershell
# Find and kill the uvicorn process
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Or kill by port
netstat -ano | findstr :8765
taskkill /PID <PID> /F
```

## Current Limitations

1. **Python runtime required**: The backend is not packaged as a standalone .exe. Users need Python 3.11-3.13.
2. **No code signing**: Windows SmartScreen will show a warning on first launch. Expected for dev/candidate builds.
3. **No auto-start**: The app does not start automatically with Windows.
4. **No MSI installer**: Uses NSIS (electron-builder default), not WiX MSI.
5. **One instance only**: Only one NovelMind instance can run at a time (by design).
6. **Frontend must be pre-built for packaging**: `npm run build` in `frontend/` must run before `npm run build` in `desktop-electron/`. The installed app serves the packaged frontend from `http://127.0.0.1:8765/app`.

## Next Steps

1. Package Python backend with PyInstaller
2. Switch from NSIS to WiX MSI for consistent installer format
3. Add auto-start with Windows option
4. Code signing certificate for SmartScreen trust
5. CI/CD pipeline for automated desktop builds
6. Evaluate Tauri for production (smaller binary, no Chromium overhead)
