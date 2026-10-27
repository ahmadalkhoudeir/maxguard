// Shared helpers for the fix-review Playwright checks: start/stop a MaxGuard
// server from a build folder, upload a zipped Zeek fixture, small waits.
"use strict";
const { spawn } = require("child_process");
const net = require("net");
const fs = require("fs");
const path = require("path");

const W = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/r3-review";
const VENV = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin";
const BUILDS = {
  "fixed-06": path.join(W, "fixed-06"), "verify": path.join(W, "verify"), "orig-all": path.join(W, "orig-all"), "fixed-02": path.join(W, "fixed-02"),
  "fixed-03": path.join(W, "fixed-03"),
  "orig-02": path.join(W, "orig-02"),
  "orig-03": path.join(W, "orig-03"),
  "patched-03": path.join(W, "patched-03"),
  "patched-02": path.join(W, "patched-02"),
  "patched1-03": path.join(W, "patched1-03"),
};
const ZIPS = path.join(W, "zips");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function freePort() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.listen(0, "127.0.0.1", () => {
      const p = s.address().port;
      s.close(() => resolve(p));
    });
    s.on("error", reject);
  });
}

let counter = 0;
const running = new Set();

async function startServer(buildName, opts = {}) {
  const build = BUILDS[buildName] || buildName;
  const port = opts.port || (await freePort());
  const dataDir = opts.dataDir ||
    path.join(W, "data", `${path.basename(build)}-${process.pid}-${Date.now()}-${counter++}`);
  fs.mkdirSync(dataDir, { recursive: true });
  const env = { ...process.env, MAXGUARD_DATA_DIR: dataDir, ...(opts.env || {}) };
  const args = ["-m", "uvicorn", "maxguard.api.app:create_app", "--factory", "--host", opts.host || "127.0.0.1",
    "--port", String(port), "--log-level", "warning"];
  const proc = spawn(path.join(VENV, "python"), args, { cwd: build, env, stdio: ["ignore", "pipe", "pipe"] });
  let log = "";
  proc.stdout.on("data", (d) => (log += d));
  proc.stderr.on("data", (d) => (log += d));
  const server = {
    port, dataDir, proc, build,
    origin: `http://127.0.0.1:${port}`,
    log: () => log,
    stop: () => new Promise((resolve) => {
      running.delete(server);
      if (proc.exitCode !== null || proc.signalCode !== null) return resolve();
      proc.once("exit", () => resolve());
      proc.kill("SIGKILL");
    }),
  };
  running.add(server);
  for (let i = 0; i < 150; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/api/alerts`);
      if (r.ok) return server;
    } catch (e) { /* not up yet */ }
    if (proc.exitCode !== null) break;
    await sleep(100);
  }
  await server.stop();
  throw new Error(`server ${buildName} did not start on ${port}:\n${log}`);
}

async function stopAll() {
  for (const s of [...running]) await s.stop();
}

async function upload(port, name, host = "127.0.0.1") {
  const buf = fs.readFileSync(path.join(ZIPS, name + ".zip"));
  const fd = new FormData();
  fd.append("file", new Blob([buf]), name + ".zip");
  const r = await fetch(`http://${host}:${port}/api/analyses`, { method: "POST", body: fd });
  return { status: r.status, body: await r.json() };
}

async function patchAlert(port, findingId, body) {
  const r = await fetch(`http://127.0.0.1:${port}/api/alerts/${findingId}`, {
    method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  return { status: r.status, body: await r.json() };
}

async function alerts(port) {
  const r = await fetch(`http://127.0.0.1:${port}/api/alerts`);
  return r.json();
}

// Count the alert rows a page shows right now.
async function rowCount(page) {
  return page.evaluate(() => document.querySelectorAll("#alerts tbody tr").length);
}

// Wait until fn() returns truthy, or time out; returns the last value and the time taken.
async function waitFor(fn, timeoutMs = 5000, stepMs = 50) {
  const t0 = Date.now();
  let v;
  while (Date.now() - t0 < timeoutMs) {
    v = await fn();
    if (v) return { ok: true, value: v, ms: Date.now() - t0 };
    await sleep(stepMs);
  }
  return { ok: false, value: v, ms: Date.now() - t0 };
}

process.on("exit", () => {
  for (const s of running) { try { s.proc.kill("SIGKILL"); } catch (e) { /* gone */ } }
});

module.exports = { W, VENV, BUILDS, sleep, freePort, startServer, stopAll, upload, patchAlert, alerts, rowCount, waitFor };
