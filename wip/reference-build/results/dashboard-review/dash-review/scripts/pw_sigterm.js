// Does the server stop on SIGTERM while a queue page is open? Usage: node pw_sigterm.js <py> <serve.py> <repo> <data> <port> <page>
"use strict";
const { spawn } = require("child_process");
const { chromium } = require("playwright");
const [PY, SERVE, REPO, DATA, PORT, PAGE] = process.argv.slice(2);
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  let log = "";
  const server = spawn(PY, [SERVE, REPO, DATA, PORT, "basic"], { env: { ...process.env, LOG_LEVEL: "info" } });
  server.stderr.on("data", (d) => { log += d; });
  for (let i = 0; i < 80; i++) { try { if ((await fetch(BASE + "/api/alerts")).ok) break; } catch (e) { /* not up */ } await sleep(250); }
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const path = PAGE === "queue" ? "/" : "/alerts/" + (await (await fetch(BASE + "/api/alerts")).json())[0].finding_id;
  await page.goto(BASE + path);
  await sleep(2000);
  const t0 = Date.now();
  server.kill("SIGTERM");
  const exited = await Promise.race([new Promise((r) => server.on("exit", () => r(true))), sleep(15000).then(() => false)]);
  console.log(`page open: ${path} -> after SIGTERM the server ${exited ? `exited in ${Date.now() - t0} ms` : "was still running 15 s later"}`);
  console.log("uvicorn said:", JSON.stringify(log.split("\n").filter((l) => /Shutting down|Waiting|Finished|Application shutdown|Cancel/.test(l))));
  if (!exited) { server.kill("SIGKILL"); }
  await Promise.race([browser.close(), sleep(5000)]);
  process.exit(0);
})();
