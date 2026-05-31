// NovelMind Electron Desktop — Build Script
//
// Wraps electron-builder to produce a distributable Windows installer.
// Run: node build.js
//
// Prerequisites:
//   1. npm install in desktop-electron/
//   2. Frontend built: cd ../frontend && npm run build
//   3. Python 3.11+ with backend deps installed
//
// Output: desktop-electron/dist/NovelMind-Setup-*.exe (NSIS installer)
//
// NOTE: NSIS builds require Windows symlink permission (Developer Mode or
// admin).  If winCodeSign fails with "Cannot create symbolic link", run as
// Administrator or enable Developer Mode in Windows Settings.
// For development / testing, use `electron .` (npm run start) instead.

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");
const os = require("os");

const REPO_ROOT = path.resolve(__dirname, "..");
const FRONTEND_DIST = path.join(REPO_ROOT, "frontend", "dist", "index.html");
const BACKEND_REQS = path.join(REPO_ROOT, "backend", "requirements.txt");

function check(name, condition, help) {
  if (!condition) {
    console.error(`[build] ERROR: ${name} check failed. ${help}`);
    process.exit(1);
  }
  console.log(`[build] ${name}: OK`);
}

async function main() {
  console.log("NovelMind Desktop Builder\n");

  // ── Pre-flight checks ──────────────────────────────────────────────────
  console.log("--- Pre-flight Checks ---\n");

  check(
    "Node.js",
    true,
    "Node.js is required to run this build script."
  );

  check(
    "Frontend dist",
    fs.existsSync(FRONTEND_DIST),
    `Frontend build not found at ${FRONTEND_DIST}. ` +
    `Run: cd frontend && npm install && npm run build`
  );

  check(
    "Backend requirements.txt",
    fs.existsSync(BACKEND_REQS),
    `Backend requirements not found at ${BACKEND_REQS}.`
  );

  check(
    "Electron installed",
    (() => {
      try {
        require.resolve("electron");
        return true;
      } catch (_) {
        return false;
      }
    })(),
    "Electron not installed. Run: cd desktop-electron && npm install"
  );

  check(
    "electron-builder installed",
    (() => {
      try {
        require.resolve("electron-builder");
        return true;
      } catch (_) {
        return false;
      }
    })(),
    "electron-builder not installed. Run: cd desktop-electron && npm install"
  );

  // ── Build ──────────────────────────────────────────────────────────────
  console.log("\n--- Building Desktop Client ---\n");

  const builder = require("electron-builder");

  try {
    await builder.build({
      targets: builder.Platform.WINDOWS.createTarget(["nsis"]),
      config: {
        appId: "com.novelmind.desktop",
        productName: "NovelMind",
        directories: {
          output: "dist",
        },
        files: [
          "main.js",
          "preload.js",
          "backend.js",
          "tray.js",
          "frontend-loader.js",
          "package.json",
          "assets/**/*",
        ],
        extraResources: [
          {
            from: "../backend",
            to: "backend",
            filter: [
              "**/*",
              "!__pycache__/**",
              "!*.db",
              "!*.sqlite3",
              "!*.pyc",
            ],
          },
          {
            from: "../frontend/dist",
            to: "frontend/dist",
          },
        ],
        win: {
          target: "nsis",
          icon: "assets/NovelMind.ico",
        },
        nsis: {
          oneClick: false,
          allowToChangeInstallationDirectory: true,
          createDesktopShortcut: true,
          createStartMenuShortcut: true,
          shortcutName: "NovelMind",
        },
      },
    });

    console.log("\n[build] Build completed successfully!");
    console.log("[build] Output: desktop-electron/dist/");
  } catch (err) {
    console.error(`\n[build] Build failed: ${err.message}`);
    console.error(
      "\nHINT: winCodeSign symlink failures require Developer Mode or admin.\n" +
      "For development, use `npm run start` (electron .) instead of npm run build."
    );
    process.exit(1);
  }
}

main();
