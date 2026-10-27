// Shared helpers for the r3-browser checks: start/stop a MaxGuard server from a
// build folder, upload a zipped Zeek fixture, PATCH alerts, small waits, and a
// record of every host the browser talked to (nothing may leave 127.0.0.1).
"use strict";
const { spawn, spawnSync } = require("child_process");
const net = require("net");
const fs = require("fs");
const path = require("path");

const R = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/r3-verify";
const VENV = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin";
const BUILDS = {
  "fixed-02": path.join(R, "builds", "fixed-AHM-02"),
  "fixed-03": path.join(R, "builds", "fixed-AHM-03"),
  "fixed-06": path.join(R, "builds", "fixed-AHM-06"),
  "orig-02": "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/stages/AHM-02",
  "orig-03": path.join(R, "builds", "orig-AHM-03"),
  "orig-06": path.join(R, "builds", "orig-ALL"),
};
const ZIPS = path.join(R, "zips");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function freePort() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.listen(0, "127.0.0.1", () => { const p = s.address().port; s.close(() => resolve(p)); });
    s.on("error", reject);
  });
}

let counter = 0;
const running = new Set();

function newDataDir(label) {
  const dir = path.join(R, "data", `${label}-${process.pid}-${Date.now()}-${counter++}`);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

// Add synthetic alerts (copies of the Telnet finding) of the given severities to a data folder.
function addAlerts(buildName, dataDir, severities, per = 1) {
  const build = BUILDS[buildName] || buildName;
  const r = spawnSync(path.join(VENV, "python"), ["-I", path.join(R, "scripts", "add_alerts.py"),
    build, dataDir, severities.join(","), String(per)], { encoding: "utf8",
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1", TMPDIR: path.join(R, "tmp") } });
  if (r.status !== 0) throw new Error("add_alerts failed: " + r.stderr);
  return r.stdout.trim();
}

async function startServer(buildName, opts = {}) {
  const build = BUILDS[buildName] || buildName;
  const port = opts.port || (await freePort());
  const dataDir = opts.dataDir || newDataDir(path.basename(build));
  const env = { ...process.env, MAXGUARD_DATA_DIR: dataDir, PYTHONDONTWRITEBYTECODE: "1",
    TMPDIR: path.join(R, "tmp"), ...(opts.env || {}) };
  const args = ["maxguard.api.app:create_app", "--factory", "--host", "127.0.0.1",
    "--port", String(port), "--log-level", opts.logLevel || "warning"];
  const proc = spawn(path.join(VENV, "uvicorn"), args, { cwd: build, env, stdio: ["ignore", "pipe", "pipe"] });
  let log = "";
  proc.stdout.on("data", (d) => (log += d));
  proc.stderr.on("data", (d) => (log += d));
  const server = {
    port, dataDir, proc, build, name: buildName,
    origin: `http://127.0.0.1:${port}`,
    log: () => log,
    stop: (signal = "SIGKILL") => new Promise((resolve) => {
      running.delete(server);
      if (proc.exitCode !== null || proc.signalCode !== null) return resolve();
      proc.once("exit", () => resolve());
      proc.kill(signal);
    }),
  };
  running.add(server);
  for (let i = 0; i < 300; i++) {
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

async function upload(port, name, file) {
  const buf = fs.readFileSync(file || path.join(ZIPS, name + ".zip"));
  const fd = new FormData();
  fd.append("file", new Blob([buf]), name + ".zip");
  const r = await fetch(`http://127.0.0.1:${port}/api/analyses`, { method: "POST", body: fd });
  return { status: r.status, body: await r.json() };
}

async function api(port, method, p, body) {
  const r = await fetch(`http://127.0.0.1:${port}${p}`, {
    method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  let json = null;
  try { json = await r.json(); } catch (e) { /* not json */ }
  return { status: r.status, body: json };
}

async function patchAlert(port, findingId, body) {
  return api(port, "PATCH", `/api/alerts/${findingId}`, body);
}

async function alerts(port) {
  return (await api(port, "GET", "/api/alerts")).body;
}

async function telnetId(port) {
  const list = await alerts(port);
  const a = list.find((x) => x.rule_id === "cleartext.telnet" && x.dst_ip === "172.18.0.2") || list.find((x) => x.rule_id === "cleartext.telnet");
  return a && a.finding_id;
}

async function rowCount(page) {
  return page.evaluate(() => document.querySelectorAll("#alerts tbody tr").length);
}

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

// Every host any page asked for, across all contexts of this process.
const hosts = new Map();
function track(ctx) {
  ctx.on("request", (r) => {
    let host;
    try { host = new URL(r.url()).host; } catch (e) { host = r.url().split("/")[0]; }
    hosts.set(host, (hosts.get(host) || 0) + 1);
  });
  return ctx;
}
async function newContext(browser, opts = {}) {
  return track(await browser.newContext(opts));
}
function hostsSeen() {
  return Object.fromEntries([...hosts.entries()]);
}

// The CSP refuses page.addStyleTag; a constructed stylesheet is allowed.
async function setFont(page, font) {
  if (!font || font === "default") return page.evaluate(() => getComputedStyle(document.body).fontFamily);
  return page.evaluate((f) => {
    const s = new CSSStyleSheet();
    s.replaceSync('html, body, input, button, select, label, .stack td::before { font-family: "' + f + '" !important }');
    document.adoptedStyleSheets = [...document.adoptedStyleSheets, s];
    return getComputedStyle(document.body).fontFamily;
  }, font);
}

process.on("exit", () => {
  for (const s of running) { try { s.proc.kill("SIGKILL"); } catch (e) { /* gone */ } }
});

module.exports = { R, VENV, BUILDS, ZIPS, sleep, freePort, newDataDir, addAlerts, startServer, stopAll, upload,
  api, patchAlert, alerts, telnetId, rowCount, waitFor, track, newContext, hostsSeen, setFont };
