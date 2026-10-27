// L: the status form after the server went away (dash-review).
// Usage: node pw_server_down.js <python> <serve.py> <repo> <data_dir> <port>
"use strict";
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const [PY, SERVE, REPO, DATA, PORT] = process.argv.slice(2);
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function start() {
  const proc = spawn(PY, [SERVE, REPO, DATA, PORT, "basic"], { stdio: "ignore",
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" } });
  for (let i = 0; i < 60; i++) {
    try { if ((await fetch(BASE + "/api/alerts")).ok) return proc; } catch (e) { /* not up yet */ }
    await sleep(250);
  }
  throw new Error("server did not start");
}

(async () => {
  let server = await start();
  const id = (await (await fetch(BASE + "/api/alerts")).json())
    .find((a) => a.rule_id === "cleartext.telnet").finding_id;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(BASE + "/alerts/" + id);
  await page.fill("#actor", "Ahmad");
  await page.selectOption("#alert-status", "investigating");
  await page.click("#status-form button");
  await page.waitForSelector("#status-form .message");
  console.log("1st save, form says:", await page.textContent("#status-form .message"));

  server.kill("SIGTERM");
  await new Promise((r) => server.on("exit", r));
  console.log("server stopped");
  await page.selectOption("#alert-status", "resolved");
  await page.click("#status-form button");
  await sleep(2000);
  console.log("2nd save, select shows:", await page.inputValue("#alert-status"),
              "| form says:", await page.textContent("#status-form .message"));
  console.log("any other visible text near the form:",
              JSON.stringify(await page.evaluate(() => document.querySelector("section[aria-labelledby=status-heading]").innerText)));

  server = await start();
  const stored = (await (await fetch(BASE + "/api/alerts/" + id)).json()).status;
  console.log("server restarted; stored status is:", stored);
  await browser.close();
  server.kill("SIGTERM");
})();
