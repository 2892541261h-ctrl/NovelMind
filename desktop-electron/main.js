// NovelMind Electron Desktop — Main Process
//
// Architecture:
//   1. Single-instance lock — only one NovelMind at a time
//   2. System tray — minimize to tray, not close
//   3. Backend sidecar — spawn/kill Python FastAPI process
//   4. Health polling — wait for backend before loading frontend
//   5. BrowserWindow — load backend-served SPA at http://127.0.0.1:8000/app
//
// No external browser is opened. The Python backend runs hidden (no console window).

const {
  app,
  BrowserWindow,
  nativeImage,
} = require("electron");
const path = require("path");
const fs = require("fs");

const { startBackend, stopBackend, waitForHealth } = require("./backend");
const { createTray, destroyTray } = require("./tray");
const { ensureFrontendBuilt } = require("./frontend-loader");

// ── Paths ────────────────────────────────────────────────────────────────────
const REPO_ROOT = path.resolve(__dirname, "..");
const LOG_DIR = path.join(app.getPath("userData"), "logs");
const ICON_PATH = path.join(__dirname, "assets", "NovelMind.ico");
const BACKEND_URL = "http://127.0.0.1:8000";
const APP_URL = `${BACKEND_URL}/app`;
const HEALTH_URL = `${BACKEND_URL}/health`;

// ── State ────────────────────────────────────────────────────────────────────
let mainWindow = null;
let tray = null;
let backendProcess = null;
let isQuitting = false;

// ── Logging ──────────────────────────────────────────────────────────────────
function ensureLogDir() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
}

function log(message) {
  ensureLogDir();
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] ${message}`;
  console.log(line);
  try {
    fs.appendFileSync(path.join(LOG_DIR, "desktop.log"), line + "\n", "utf-8");
  } catch (_) {
    // best-effort logging
  }
}

// ── Window ───────────────────────────────────────────────────────────────────
function createWindow() {
  const icon = fs.existsSync(ICON_PATH)
    ? nativeImage.createFromPath(ICON_PATH)
    : undefined;

  mainWindow = new BrowserWindow({
    title: "NovelMind",
    width: 1280,
    height: 840,
    minWidth: 980,
    minHeight: 680,
    icon,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.setMenuBarVisibility(false);

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    log("main window shown");
  });

  // Minimize to tray instead of closing
  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      log("window hidden to tray");
    }
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  log(`loading app at ${APP_URL}`);
  mainWindow.loadURL(APP_URL);
}

function showWindow() {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  }
}

// ── App Lifecycle ────────────────────────────────────────────────────────────
async function startApp() {
  log("NovelMind desktop starting...");
  ensureLogDir();

  // 1. Ensure frontend is built
  try {
    await ensureFrontendBuilt(REPO_ROOT);
  } catch (err) {
    log(`frontend build failed: ${err.message}`);
    // Show error and continue — backend will serve 404 for missing dist
  }

  // 2. Start Python backend
  try {
    backendProcess = startBackend({
      repoRoot: REPO_ROOT,
      backendUrl: BACKEND_URL,
      logDir: LOG_DIR,
      log,
    });
    log(`backend started (PID ${backendProcess.pid})`);
  } catch (err) {
    log(`backend start failed: ${err.message}`);
    showErrorDialog("后端启动失败", `无法启动 NovelMind 后端服务。\n\n${err.message}\n\n请确认 Python 3.11+ 已安装且 backend/requirements.txt 依赖已安装。`);
    app.quit();
    return;
  }

  // 3. Wait for /health
  try {
    log("waiting for backend health...");
    await waitForHealth(HEALTH_URL, 30_000);
    log("backend healthy");
  } catch (err) {
    log(`backend health check failed: ${err.message}`);
    stopBackend(backendProcess, log);
    showErrorDialog("后端启动超时", `NovelMind 后端服务在 30 秒内未就绪。\n\n${err.message}\n\n请检查日志: ${path.join(LOG_DIR, "backend.log")}`);
    app.quit();
    return;
  }

  // 4. Create window
  createWindow();
}

function showErrorDialog(title, message) {
  const { dialog } = require("electron");
  dialog.showErrorBox(title, message);
}

// ── Single Instance ──────────────────────────────────────────────────────────
const gotLock = app.requestSingleInstanceLock();

if (!gotLock) {
  log("another instance is already running — quitting");
  app.quit();
} else {
  app.on("second-instance", () => {
    log("second-instance event — showing existing window");
    showWindow();
  });

  app.whenReady().then(async () => {
    // Create tray
    tray = createTray({
      iconPath: ICON_PATH,
      onShow: showWindow,
      onRestart: async () => {
        log("restart requested from tray");
        if (backendProcess) {
          await stopBackend(backendProcess, log);
        }
        backendProcess = startBackend({
          repoRoot: REPO_ROOT,
          backendUrl: BACKEND_URL,
          logDir: LOG_DIR,
          log,
        });
        try {
          await waitForHealth(HEALTH_URL, 20_000);
          if (mainWindow) {
            mainWindow.loadURL(APP_URL);
          }
          log("backend restarted successfully");
        } catch (err) {
          log(`restart health check failed: ${err.message}`);
        }
      },
      onQuit: () => {
        isQuitting = true;
        log("quit requested from tray");
        if (backendProcess) {
          stopBackend(backendProcess, log);
        }
        destroyTray(tray);
        app.quit();
      },
      log,
    });

    await startApp();
  });

  app.on("window-all-closed", () => {
    // Don't quit — stay in tray
    log("all windows closed, staying in tray");
  });

  app.on("before-quit", () => {
    isQuitting = true;
    if (backendProcess) {
      stopBackend(backendProcess, log);
    }
    if (tray) {
      destroyTray(tray);
    }
  });

  app.on("quit", () => {
    log("NovelMind desktop exited");
  });
}
