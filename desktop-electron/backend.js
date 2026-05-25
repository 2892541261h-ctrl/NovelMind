// NovelMind Backend Sidecar Manager
//
// Manages the Python FastAPI backend as a child process:
//   - Finds Python executable (.venv or system)
//   - Spawns uvicorn with windowsHide (no console window)
//   - Redirects stdout/stderr to log file
//   - Polls /health endpoint with timeout
//   - Graceful shutdown (terminate → kill)

const { spawn, execSync } = require("child_process");
const path = require("path");
const fs = require("fs");
const os = require("os");
const http = require("http");

// ── Find Python ──────────────────────────────────────────────────────────────
function findPython(repoRoot, log) {
  const isWindows = os.platform() === "win32";

  // 1. Repo .venv
  const repoVenv = path.join(repoRoot, ".venv", "Scripts", "python.exe");
  if (fs.existsSync(repoVenv)) {
    log(`using repo .venv Python: ${repoVenv}`);
    return repoVenv;
  }

  // 2. System Python via `where` (Windows) or `which` (Unix)
  try {
    const cmd = isWindows ? "where python" : "which python3 || which python";
    const result = execSync(cmd, { encoding: "utf-8", timeout: 5000 }).trim();
    const pythonPath = result.split("\n")[0].trim();
    if (pythonPath) {
      log(`using system Python: ${pythonPath}`);
      return pythonPath;
    }
  } catch (_) {
    // fall through
  }

  // 3. Default: just "python" and hope it's on PATH
  log("falling back to 'python' on PATH");
  return "python";
}

// ── Start Backend ────────────────────────────────────────────────────────────
function startBackend({ repoRoot, backendUrl, logDir, log }) {
  const pythonExe = findPython(repoRoot, log);
  const backendDir = path.join(repoRoot, "backend");

  if (!fs.existsSync(backendDir)) {
    throw new Error(`backend directory not found: ${backendDir}`);
  }

  const requirementsFile = path.join(backendDir, "requirements.txt");
  if (!fs.existsSync(requirementsFile)) {
    throw new Error(`requirements.txt not found: ${requirementsFile}`);
  }

  // Ensure deps installed
  try {
    log("installing/checking backend dependencies...");
    execSync(`"${pythonExe}" -m pip install -r "${requirementsFile}" --quiet`, {
      cwd: backendDir,
      timeout: 120_000,
      windowsHide: true,
    });
  } catch (err) {
    log(`pip install warning: ${err.message}`);
    // Continue — deps might already be installed
  }

  // Parse port from backendUrl for uvicorn
  const url = new URL(backendUrl);
  const host = url.hostname;
  const port = url.port;

  // Ensure log dir
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const backendLogStream = fs.createWriteStream(
    path.join(logDir, "backend.log"),
    { flags: "a" }
  );

  backendLogStream.write(
    `\n${"=".repeat(60)}\n` +
    `NovelMind backend started at ${new Date().toISOString()}\n` +
    `${"=".repeat(60)}\n\n`
  );

  const child = spawn(
    pythonExe,
    [
      "-m", "uvicorn",
      "main:app",
      "--host", host,
      "--port", String(port),
      "--log-level", "info",
    ],
    {
      cwd: backendDir,
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
      env: {
        ...process.env,
        NOVELMIND_DATABASE_PATH:
          process.env.NOVELMIND_DATABASE_PATH ||
          path.join(process.env.APPDATA || process.env.LOCALAPPDATA, "NovelMind", "data", "novelmind.db"),
      },
    }
  );

  child.stdout.pipe(backendLogStream);
  child.stderr.pipe(backendLogStream);

  child.on("error", (err) => {
    log(`backend process error: ${err.message}`);
  });

  child.on("exit", (code, signal) => {
    const msg = signal
      ? `backend exited with signal ${signal}`
      : `backend exited with code ${code}`;
    log(msg);
    backendLogStream.end();
  });

  return child;
}

// ── Stop Backend ─────────────────────────────────────────────────────────────
async function stopBackend(child, log) {
  if (!child) return;

  log(`stopping backend (PID ${child.pid})...`);

  return new Promise((resolve) => {
    // Try graceful terminate first
    // On Windows, spawn taskkill for the process tree
    const isWindows = os.platform() === "win32";

    if (isWindows) {
      try {
        execSync(`taskkill /PID ${child.pid} /T /F`, {
          windowsHide: true,
          timeout: 5000,
        });
      } catch (_) {
        // process may already be dead
      }
    } else {
      child.kill("SIGTERM");
    }

    // Give it a moment
    setTimeout(() => {
      if (child.exitCode === null && child.signalCode === null) {
        log("backend still alive, force killing...");
        try {
          child.kill("SIGKILL");
        } catch (_) {
          // already dead
        }
      }
      log("backend stopped");
      resolve();
    }, 2000);
  });
}

// ── Health Check ─────────────────────────────────────────────────────────────
function checkHealth(url) {
  return new Promise((resolve, reject) => {
    const req = http.get(url, { timeout: 2000 }, (res) => {
      if (res.statusCode === 200) {
        res.resume();
        resolve(true);
      } else {
        res.resume();
        reject(new Error(`health returned ${res.statusCode}`));
      }
    });
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("health check timed out"));
    });
  });
}

async function waitForHealth(healthUrl, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;

  while (Date.now() < deadline) {
    try {
      await checkHealth(healthUrl);
      return true;
    } catch (err) {
      lastError = err;
    }
    await sleep(500);
  }

  throw new Error(
    `health check failed after ${timeoutMs / 1000}s: ${lastError?.message || "unknown error"}`
  );
}

// ── Utilities ────────────────────────────────────────────────────────────────
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ── Exports ──────────────────────────────────────────────────────────────────
module.exports = {
  startBackend,
  stopBackend,
  waitForHealth,
  checkHealth,
  findPython,
};
