// NovelMind Electron preload script.
// This runs in a privileged context before the web page loads.
// Currently minimal — exposes a simple bridge for future use.

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("novelmind", {
  platform: process.platform,
  appVersion: process.env.npm_package_version || "2.0.0",
});
