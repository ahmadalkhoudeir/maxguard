// Shared helpers for the final-browser checks: start/stop a real uvicorn server from a
// build folder, call the API, upload the Telnet zip, add synthetic alerts.
"use strict";
const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const net = require("net");
const path = require("path");

const SP = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad";
const W = SP + "/agentwork/final-browser";
const VENV = SP + "/ref/.venv/bin";
const BUILDS = {
  O2: W + "/orig-AHM-02", F2: W + "/fixed-AHM-02",
  O3: W + "/orig-AHM-03", F3: W + "/fixed-AHM-03",
};
const ZIP = W + "/tmp/telnet_logs.zip";
const FAR_ZIP = W + "/tmp/telnet_far_future.zip";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let dataCounter = 0;

function freePort() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.unref();
    s.on("error", reject);
    s.listen(0, "127.0.0.1", () => {
      const { port } = s.address();
      s.close(() => resolve(port));
    });
  });
}

function newDataDir(label) {
  dataCounter += 1;
  const dir = `${W}/data/${label}-${process.pid}-${Date.now()}-${dataCounter}`;
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

// Start "uvicorn maxguard.api.app:create_app --factory" in the build folder, the way
// the guide does, with MAXGUARD_DATA_DIR set. Resolves when GET /upload answers 200.
async function startServer(build, data, port, logLabel) {
  port = port || (await freePort());
  const logPath = `${W}/logs/${logLabel || path.basename(build)}-${port}.log`;
  const out = fs.openSync(logPath, "a");
  const proc = spawn(VENV + "/uvicorn",
    ["maxguard.api.app:create_app", "--factory", "--host", "127.0.0.1", "--port", String(port)],
    { cwd: build, stdio: ["ignore", out, out],
      env: { ...process.env, MAXGUARD_DATA_DIR: data, PYTHONDONTWRITEBYTECODE: "1", TMPDIR: W + "/tmp" } });
  let exited = false;
  proc.on("exit", () => { exited = true; });
  const base = `http://127.0.0.1:${port}`;
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    if (exited) throw new Error(`server exited early, see ${logPath}`);
    try {
      const r = await fetch(base + "/upload");
      if (r.status === 200) break;
    } catch (e) { /* not up yet */ }
    await sleep(200);
  }
  return { proc, base, port, data, build, logPath, startMs: Date.now() - t0 };
}

async function stopServer(srv) {
  if (!srv || srv.proc.exitCode !== null || srv.proc.signalCode) return "already stopped";
  const done = new Promise((r) => srv.proc.once("exit", (code, sig) => r(`exit code=${code} signal=${sig}`)));
  srv.proc.kill("SIGTERM");
  const res = await Promise.race([done, sleep(10000).then(() => null)]);
  if (res) return res;
  srv.proc.kill("SIGKILL");
  return (await done) + " (needed SIGKILL after 10 s)";
}

async function api(base, method, p, body) {
  const res = await fetch(base + p, {
    method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch (e) { /* not JSON */ }
  return { status: res.status, json, text };
}

async function upload(base, zipPath) {
  const form = new FormData();
  form.append("file", new Blob([fs.readFileSync(zipPath)], { type: "application/zip" }), path.basename(zipPath));
  const res = await fetch(base + "/api/analyses", { method: "POST", body: form });
  return { status: res.status, text: await res.text() };
}

// add_alerts.py: copies of the Telnet finding with the given severities, written
// straight into the data folder's state.db (the running server reads it per request).
function addAlerts(build, data, sevs, octet) {
  const r = spawnSync(VENV + "/python", [W + "/scripts/add_alerts.py", build, data, sevs.join(","), String(octet || 9)],
    { cwd: W, encoding: "utf8", env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1", TMPDIR: W + "/tmp" } });
  if (r.status !== 0) throw new Error("add_alerts failed: " + r.stderr);
  return r.stdout.trim();
}

async function alerts(base) {
  return (await api(base, "GET", "/api/alerts?limit=1000")).json;
}

async function telnetId(base) {
  const list = await alerts(base);
  const t = list.find((a) => a.rule_id === "cleartext.telnet" && a.dst_ip === "172.18.0.2");
  return t ? t.finding_id : null;
}

// One server per (build, check): fresh data folder, the Telnet zip uploaded through the
// real server, then fn(srv). The server is always stopped.
async function withServer(buildKey, label, fn, opts = {}) {
  const build = BUILDS[buildKey];
  const data = newDataDir(`${label}-${buildKey}`);
  const srv = await startServer(build, data, null, `${label}-${buildKey}`);
  srv.key = buildKey;
  try {
    if (opts.upload !== false) {
      const up = await upload(srv.base, ZIP);
      if (up.status !== 200) throw new Error("telnet upload failed: " + up.status + " " + up.text);
      srv.uploadAnswer = up.text;
    }
    return await fn(srv);
  } finally {
    srv.stopResult = await stopServer(srv);
  }
}

async function activeDesc(page) {
  return page.evaluate(() => {
    const e = document.activeElement;
    if (!e || e === document.body) return e ? "BODY" : "null";
    return `${e.tagName}${e.id ? "#" + e.id : ""} "${(e.textContent || e.value || "").trim().slice(0, 40)}"`;
  });
}

module.exports = { SP, W, VENV, BUILDS, ZIP, FAR_ZIP, sleep, freePort, newDataDir, startServer, stopServer,
  api, upload, addAlerts, alerts, telnetId, withServer, activeDesc };
