// NovelMind System Tray
//
// Creates a system tray icon with context menu:
//   - 打开 NovelMind — show/hide main window
//   - 重启服务 — kill and restart Python backend
//   - 退出 — quit the application
//
// Double-click tray icon shows the main window.

const { Tray, Menu, nativeImage } = require("electron");
const path = require("path");
const fs = require("fs");

// ── Create Tray ──────────────────────────────────────────────────────────────
function createTray({ iconPath, onShow, onRestart, onQuit, log }) {
  // Build tray icon from .ico or fallback to a blank 16x16 image
  let trayIcon;
  if (fs.existsSync(iconPath)) {
    trayIcon = nativeImage.createFromPath(iconPath);
  }

  if (!trayIcon || trayIcon.isEmpty()) {
    // Create a minimal 16x16 tray icon as fallback
    log("tray icon not found or invalid, using fallback");
    trayIcon = nativeImage.createEmpty();
  }

  // Resize for tray (16x16 is standard on Windows)
  const trayImage = trayIcon.resize({ width: 16, height: 16 });
  const tray = new Tray(trayImage);

  tray.setToolTip("NovelMind");

  // Double-click → show window
  tray.on("double-click", () => {
    log("tray double-click — show window");
    onShow();
  });

  // Context menu
  const contextMenu = Menu.buildFromTemplate([
    {
      label: "打开 NovelMind",
      click: () => {
        log("tray menu: open");
        onShow();
      },
    },
    { type: "separator" },
    {
      label: "重启服务",
      click: async () => {
        log("tray menu: restart");
        await onRestart();
      },
    },
    { type: "separator" },
    {
      label: "退出",
      click: () => {
        log("tray menu: quit");
        onQuit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
  log("tray created");

  return tray;
}

// ── Destroy Tray ─────────────────────────────────────────────────────────────
function destroyTray(tray) {
  if (tray) {
    try {
      tray.destroy();
    } catch (_) {
      // tray may already be destroyed
    }
  }
}

// ── Exports ──────────────────────────────────────────────────────────────────
module.exports = {
  createTray,
  destroyTray,
};
