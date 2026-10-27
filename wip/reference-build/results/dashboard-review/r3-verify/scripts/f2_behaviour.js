// F2: are the "NOT CAUGHT" mutations real behaviour changes (not no-ops)? Build two mutated
// copies of fixed-06 (test_web.py stays green on both, see mutate.py) and watch the browser:
//  lock-holder-no-stream: after an upload, does the queue table refresh by itself?
//  not-saved-handler-dead: with the server stopped, does Save show the "No answer" message?
// Usage: node f2_behaviour.js
"use strict";
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const L = require("./lib");

const SRC = L.BUILDS["fixed-06"];
const MUT = path.join(L.R, "mut");
const MUTATIONS = {
  "lock-holder-no-stream": ["maxguard/web/static/app.js", "return hold();", "return null;"],
  "not-saved-handler-dead": ["maxguard/web/static/app.js", 'if (!form || form.id !== "status-form") {', "if (true) {"],
};

function buildMutant(name) {
  const dest = path.join(MUT, name);
  fs.rmSync(dest, { recursive: true, force: true });
  execFileSync("cp", ["-r", SRC, dest]);
  const [file, oldS, newS] = MUTATIONS[name];
  const p = path.join(dest, file);
  const text = fs.readFileSync(p, "utf8");
  if (text.split(oldS).length !== 2) throw new Error(name + ": old string not found exactly once");
  fs.writeFileSync(p, text.replace(oldS, newS));
  return dest;
}

async function liveRefresh(build, browser, label) {
  const server = await L.startServer(build);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await L.newContext(browser);
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    await page.waitForSelector("#alerts table");
    const before = await L.rowCount(page);
    await L.upload(server.port, "ftp");
    const r = await L.waitFor(async () => (await L.rowCount(page)) === 2, 8000, 100);
    console.log(`${label.padEnd(24)} live refresh after upload: rows ${before} -> ${r.value === true ? 2 : await L.rowCount(page)} within ${r.ms} ms (${r.ok ? "refreshed" : "NO refresh in 8 s"})`);
    await ctx.close();
  } finally { await server.stop(); }
}

async function notSaved(build, browser, label) {
  const server = await L.startServer(build);
  try {
    await L.upload(server.port, "telnet");
    const id = await L.telnetId(server.port);
    const ctx = await L.newContext(browser);
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    const page = await ctx.newPage();
    await page.goto(server.origin + "/alerts/" + id);
    await server.stop();
    await page.selectOption("#alert-status", "resolved");
    await page.click("#status-save");
    await L.sleep(2000);
    const msg = await page.evaluate(() => (document.querySelector("#status-form .message") || {}).textContent || null);
    console.log(`${label.padEnd(24)} Save with the server stopped -> message: ${JSON.stringify(msg)}`);
    await ctx.close();
  } finally { await server.stop(); }
}

(async () => {
  const browser = await chromium.launch();
  try {
    await liveRefresh(SRC, browser, "fixed-06");
    await liveRefresh(buildMutant("lock-holder-no-stream"), browser, "lock-holder-no-stream");
    await notSaved(SRC, browser, "fixed-06");
    await notSaved(buildMutant("not-saved-handler-dead"), browser, "not-saved-handler-dead");
  } finally { await browser.close(); await L.stopAll(); }
})();
