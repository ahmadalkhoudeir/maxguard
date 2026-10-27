// Live refresh across a server restart, instrumented. Usage: node pw_restart2.js <py> <serve.py> <repo> <data> <port>
"use strict";
const { spawn } = require("child_process");
const { chromium } = require("playwright");
const [PY, SERVE, REPO, DATA, PORT] = process.argv.slice(2);
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const T0 = Date.now();
const t = () => ((Date.now() - T0) / 1000).toFixed(1).padStart(5);
async function start() {
  const proc = spawn(PY, [SERVE, REPO, DATA, PORT, "basic"], { stdio: "ignore", env: process.env });
  for (let i = 0; i < 80; i++) { try { if ((await fetch(BASE + "/api/alerts")).ok) return proc; } catch (e) { /* not up */ } await sleep(250); }
  throw new Error("server did not start");
}
(async () => {
  const hard = setTimeout(() => { console.log(t(), "hard timeout"); process.exit(2); }, 150000);
  let server = await start();
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on("request", (r) => { const u = new URL(r.url()); if (u.pathname === "/api/stream" || (u.pathname === "/" && u.search)) console.log(t(), "request ", u.pathname + u.search); });
  page.on("requestfailed", (r) => { const u = new URL(r.url()); if (u.pathname === "/api/stream" || u.pathname === "/") console.log(t(), "failed  ", u.pathname + u.search, r.failure() && r.failure().errorText); });
  page.on("console", (m) => console.log(t(), "console ", m.text().slice(0, 120)));
  await page.goto(BASE + "/"); await sleep(2000);
  server.kill("SIGTERM"); await new Promise((r) => server.on("exit", r));
  console.log(t(), "server stopped");
  await sleep(6000);
  server = await start();
  console.log(t(), "server started again");
  await sleep(10000);
  const id = (await (await fetch(BASE + "/api/alerts")).json())[0].finding_id;
  await fetch(BASE + "/api/alerts/" + id, { method: "PATCH", headers: { "content-type": "application/json" },
    body: JSON.stringify({ actor: "review", assignee: "AfterRestart" }) });
  console.log(t(), "change saved");
  try {
    await page.waitForFunction(() => document.body.textContent.includes("AfterRestart"), null, { timeout: 40000, polling: 250 });
    console.log(t(), "change shown in the queue");
  } catch (e) { console.log(t(), "change not shown within 40 s"); }
  server.kill("SIGTERM");
  clearTimeout(hard);
  await Promise.race([browser.close(), sleep(5000)]);
  process.exit(0);
})();
