// Generates a 16x16 and 32x32 tray icon PNG from the NovelMind .ico file.
// Uses nativeImage from Electron to convert .ico → .png.
// Run: node make-tray-icon.js

const { nativeImage } = require("electron");
const path = require("path");
const fs = require("fs");

const assetsDir = __dirname;
const icoPath = path.join(assetsDir, "assets", "NovelMind.ico");

if (!fs.existsSync(icoPath)) {
  console.error("NovelMind.ico not found at", icoPath);
  process.exit(1);
}

const image = nativeImage.createFromPath(icoPath);
if (image.isEmpty()) {
  console.error("Failed to load icon from", icoPath);
  process.exit(1);
}

// Generate tray-sized PNG (16x16 for sharp tray rendering)
for (const size of [16, 32]) {
  const resized = image.resize({ width: size, height: size });
  const pngPath = path.join(assetsDir, "assets", `tray-${size}.png`);
  fs.writeFileSync(pngPath, resized.toPNG());
  console.log(`Created ${pngPath}`);
}

console.log("Tray icons generated.");
