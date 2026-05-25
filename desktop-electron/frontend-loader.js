// NovelMind Frontend Loader
//
// Checks if the frontend is built (frontend/dist/index.html exists).
// If not, attempts to run `npm install && npm run build` in the frontend directory.
// Shows a loading window during the build process.

const { execSync, spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const os = require("os");

// ── Check & Build Frontend ───────────────────────────────────────────────────
async function ensureFrontendBuilt(repoRoot) {
  const frontendDir = path.join(repoRoot, "frontend");
  const distIndex = path.join(frontendDir, "dist", "index.html");

  if (fs.existsSync(distIndex)) {
    return; // Already built
  }

  console.log("[frontend-loader] Frontend build not found. Building...");

  const isWindows = os.platform() === "win32";
  const npmCmd = isWindows ? "npm.cmd" : "npm";

  // Install deps if node_modules is missing
  const nodeModules = path.join(frontendDir, "node_modules");
  if (!fs.existsSync(nodeModules)) {
    console.log("[frontend-loader] Installing frontend dependencies...");
    execSync(`"${npmCmd}" install`, {
      cwd: frontendDir,
      timeout: 120_000,
      windowsHide: true,
    });
  }

  // Build
  console.log("[frontend-loader] Building frontend...");
  execSync(`"${npmCmd}" run build`, {
    cwd: frontendDir,
    timeout: 120_000,
    windowsHide: true,
  });

  if (!fs.existsSync(distIndex)) {
    throw new Error(
      `Frontend build completed but ${distIndex} was not created. ` +
      `Check frontend/ for build errors.`
    );
  }

  console.log("[frontend-loader] Frontend build complete.");
}

// ── Get Frontend Status ─────────────────────────────────────────────────────
function getFrontendStatus(repoRoot) {
  const frontendDir = path.join(repoRoot, "frontend");
  const distIndex = path.join(frontendDir, "dist", "index.html");
  const nodeModules = path.join(frontendDir, "node_modules");

  return {
    built: fs.existsSync(distIndex),
    nodeModulesInstalled: fs.existsSync(nodeModules),
    distIndex,
    frontendDir,
  };
}

// ── Exports ──────────────────────────────────────────────────────────────────
module.exports = {
  ensureFrontendBuilt,
  getFrontendStatus,
};
