// Does live refresh keep working after the server restarts? (original build)
"use strict";
const { spawn } = require("child_process");
const { chromium } = require("playwright");
const [PY, SERVE, REPO, DATA, PORT] = process.argv.slice(2);
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function start() {
  const proc = spawn(PY, [SERVE, REPO, DATA, PORT, "basic"], { stdio: "ignore", env: process.env });
  for (let i = 0; i < 80; i++) { try { if ((await fetch(BASE + "/api/alerts")).ok) return proc; } catch (e) { /* not up */ } await sleep(250); }
  throw new Error("server did not start");
}
(async () => {
  let server = await start();
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(BASE + "/"); await sleep(1000);
  server.kill("SIGTERM"); await new Promise((r) => server.on("exit", r));
  console.log("server stopped; waiting 6 s");
  await sleep(6000);
  server = await start();
  console.log("server started again");
  await sleep(5000); // EventSource retry
  const id = (await (await fetch(BASE + "/api/alerts")).json())[0].finding_id;
  const t0 = Date.now();
  await fetch(BASE + "/api/alerts/" + id, { method: "PATCH", headers: { "content-type": "application/json" },
    body: JSON.stringify({ actor: "review", assignee: "AfterRestart" }) });
  try {
    await page.waitForFunction(() => document.body.textContent.includes("AfterRestart"), null, { timeout: 15000 });
    console.log(`change shown ${((Date.now() - t0) / 1000).toFixed(1)} s after it was saved: live refresh survived the restart`);
  } catch (e) { console.log("change not shown within 15 s"); }
  await browser.close(); server.kill("SIGTERM");
})();
