// Shared helpers for the fix-retest checks: servers, uploads, page instrumentation.
"use strict";
const fs = require("fs");
const path = require("path");
const net = require("net");
const { spawn, execFileSync } = require("child_process");

const SP = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad";
const W = SP + "/agentwork/fix-retest";
const VENV = SP + "/ref/.venv/bin";
const BUILDS = {
  "fixed-AHM-02": W + "/fixed-AHM-02",
  "fixed-AHM-03": W + "/fixed-AHM-03",
  "orig-AHM-02": W + "/orig-AHM-02",
  "orig-AHM-03": W + "/orig-AHM-03",
};
const FONTS = ["DejaVu Sans", "Liberation Sans", "Roboto", "Noto Sans"];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function freePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.on("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const p = srv.address().port;
      srv.close(() => resolve(p));
    });
  });
}

let dataCounter = 0;
const running = new Set();

async function startServer(buildName, label) {
  const build = BUILDS[buildName];
  const port = await freePort();
  dataCounter += 1;
  const stamp = Date.now().toString(36) + "-" + dataCounter;
  const dataDir = `${W}/data/${label}-${buildName}-${stamp}`;
  fs.mkdirSync(dataDir, { recursive: true });
  const logFile = `${W}/logs/${label}-${buildName}-${stamp}.log`;
  fs.mkdirSync(path.dirname(logFile), { recursive: true });
  const out = fs.openSync(logFile, "w");
  const proc = spawn(VENV + "/uvicorn",
    ["maxguard.api.app:create_app", "--factory", "--host", "127.0.0.1", "--port", String(port)],
    { cwd: build, env: { ...process.env, MAXGUARD_DATA_DIR: dataDir }, stdio: ["ignore", out, out] });
  const server = { buildName, build, port, base: `http://127.0.0.1:${port}`, proc, logFile, dataDir };
  proc.on("exit", (code, signal) => {
    if (process.env.F_DEBUG) console.error(`[${new Date().toISOString()}] server ${buildName}:${port} exited code=${code} signal=${signal}`);
  });
  running.add(server);
  for (let i = 0; i < 150; i++) {
    try {
      const r = await fetch(server.base + "/docs");
      if (r.ok) return server;
    } catch (e) { /* not up yet */ }
    if (proc.exitCode !== null) break;
    await sleep(100);
  }
  throw new Error(`server ${buildName} did not start; see ${logFile}`);
}

async function stopServer(server) {
  if (!server || server.proc.exitCode !== null) { running.delete(server); return; }
  server.proc.kill("SIGTERM");
  for (let i = 0; i < 50 && server.proc.exitCode === null; i++) await sleep(100);
  if (server.proc.exitCode === null) server.proc.kill("SIGKILL");
  running.delete(server);
}

async function stopAll() {
  for (const s of [...running]) await stopServer(s);
}
process.on("exit", () => { for (const s of running) { try { s.proc.kill("SIGKILL"); } catch (e) { /* gone */ } } });

// Zip one fixture folder's files (flat, like shutil.make_archive does) into W/zips.
function fixtureZip(buildName, fixture) {
  const dir = `${BUILDS[buildName]}/tests/fixtures/zeek/${fixture}`;
  const zipPath = `${W}/zips/${buildName}-${fixture}.zip`;
  if (!fs.existsSync(zipPath)) {
    fs.mkdirSync(path.dirname(zipPath), { recursive: true });
    const files = fs.readdirSync(dir).sort();
    execFileSync("zip", ["-q", "-j", zipPath, ...files.map((f) => `${dir}/${f}`)]);
  }
  return zipPath;
}

async function upload(server, fixture) {
  const zipPath = fixtureZip(server.buildName, fixture);
  const form = new FormData();
  form.append("file", new Blob([fs.readFileSync(zipPath)], { type: "application/zip" }), `${fixture}.zip`);
  const r = await fetch(server.base + "/api/analyses", { method: "POST", body: form });
  const body = await r.json();
  if (!r.ok) throw new Error(`upload ${fixture}: ${r.status} ${JSON.stringify(body)}`);
  return body;
}

async function alerts(server) {
  const r = await fetch(server.base + "/api/alerts");
  return r.json();
}

async function telnetId(server) {
  const list = await alerts(server);
  const t = list.find((a) => a.rule_id === "cleartext.telnet");
  if (!t) throw new Error("no telnet alert: " + JSON.stringify(list.map((a) => a.rule_id)));
  return t.finding_id;
}

async function patchAlert(server, id, body) {
  const r = await fetch(`${server.base}/api/alerts/${id}`, {
    method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  return { status: r.status, body: await r.json() };
}

// Record console errors, page errors, failed requests and every request URL of a page.
function instrument(page, tag, sink) {
  const rec = { tag, consoleErrors: [], pageErrors: [], failed: [], requests: [] };
  sink.push(rec);
  page.on("console", (m) => {
    if (m.type() !== "error") return;
    const loc = m.location() || {};
    rec.consoleErrors.push(`${m.text()} [at ${loc.url || "?"}]`);
  });
  page.on("pageerror", (e) => rec.pageErrors.push(String(e)));
  page.on("request", (q) => rec.requests.push({ url: q.url(), method: q.method(), t: Date.now() }));
  page.on("requestfailed", (q) => rec.failed.push({ url: q.url(), err: (q.failure() || {}).errorText }));
  return rec;
}

// Summaries of instrument() records: console errors and requests outside the app.
function summarizeRecords(records, base) {
  const errs = [];
  const outside = new Set();
  let nreq = 0;
  const urls = new Set();
  for (const r of records) {
    for (const e of r.consoleErrors) errs.push(`${r.tag}: console: ${e}`);
    for (const e of r.pageErrors) errs.push(`${r.tag}: pageerror: ${e}`);
    for (const q of r.requests) {
      nreq += 1;
      const u = new URL(q.url);
      urls.add(u.origin + u.pathname);
      if (!(base && q.url.startsWith(base + "/")) && !(u.protocol === "data:" || u.protocol === "about:")) {
        if (!/^http:\/\/127\.0\.0\.1:\d+\//.test(q.url)) outside.add(q.url);
      }
    }
  }
  return { consoleErrors: errs, requests: nreq, distinctPaths: [...urls].sort(), outside: [...outside] };
}

function writeJSON(name, data) {
  const p = `${W}/results/${name}`;
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(data, null, 2));
  return p;
}

// The font override as a constructed stylesheet: the pages' CSP (style-src 'self')
// blocks an inline <style> element, but not CSSOM.
async function setFont(page, font, extraCss = "") {
  await page.evaluate(([f, extra]) => {
    window.__fontSheet = window.__fontSheet || new CSSStyleSheet();
    const css = (f ? `html, body, input, button, select, label, textarea, .stack td::before { font-family: "${f}" !important; }` : "") + extra;
    window.__fontSheet.replaceSync(css);
    if (!document.adoptedStyleSheets.includes(window.__fontSheet)) {
      document.adoptedStyleSheets = [...document.adoptedStyleSheets, window.__fontSheet];
    }
  }, [font, extraCss]);
  await page.evaluate(() => document.fonts.ready.then(() => true));
}

module.exports = {
  SP, W, VENV, BUILDS, FONTS, sleep, freePort, startServer, stopServer, stopAll, fixtureZip,
  upload, alerts, telnetId, patchAlert, instrument, summarizeRecords, writeJSON, setFont,
};
