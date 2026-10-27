"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const WANT = new Set(process.argv.slice(3));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
const S = {
  // J follow-up: how long does the queue stay stale?
  async catch_up(browser) {
    const list = (await api("GET", "/api/alerts"))[1];
    const [a, b] = [list[0].finding_id, list[1].finding_id];
    const page = await browser.newPage();
    await page.goto(BASE + "/"); await sleep(1500);
    let n = 0;
    await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
      const response = await route.fetch(); n += 1;
      if (n === 1) await sleep(3000);
      try { await route.fulfill({ response }); } catch (e) { /* aborted */ }
    });
    await api("PATCH", "/api/alerts/" + a, { actor: "review", assignee: "First" });
    while (n === 0) await sleep(50);
    const t0 = Date.now();
    await api("PATCH", "/api/alerts/" + b, { actor: "review", assignee: "Second" });
    await page.waitForFunction(() => [...document.querySelectorAll('#alerts td[data-label="Assignee"]')]
      .some((t) => t.textContent === "Second"), null, { timeout: 40000, polling: 200 });
    console.log(`"Second" appeared ${((Date.now() - t0) / 1000).toFixed(1)} s after it was saved (refresh requests: ${n})`);
    await api("PATCH", "/api/alerts/" + a, { actor: "review", assignee: "" });
    await api("PATCH", "/api/alerts/" + b, { actor: "review", assignee: "" });
    await page.close();
  },
  // O follow-up: is the server itself still answering while six queue tabs are open?
  async server_ok(browser) {
    const ctx = await browser.newContext();
    for (let i = 0; i < 6; i++) { const p = await ctx.newPage(); await p.goto(BASE + "/"); }
    await sleep(1000);
    const t0 = Date.now();
    const r = await fetch(BASE + "/upload");
    console.log(`same moment, a request from outside the browser: HTTP ${r.status} in ${Date.now() - t0} ms`);
    const seventh = await ctx.newPage();
    const t1 = Date.now();
    try { await seventh.goto(BASE + "/upload", { timeout: 5000 }); console.log(`7th tab loaded in ${Date.now() - t1} ms`); }
    catch (e) { console.log("7th tab: no answer within 5 s"); }
    await ctx.close();
  },
  // P follow-up: where is focus while the upload runs?
  async upload_focus_during(browser) {
    const page = await browser.newPage();
    await page.goto(BASE + "/upload");
    await page.setInputFiles("#file", process.env.UPLOAD_ZIP);
    await page.route("**/api/analyses", async (route) => { await sleep(1500); await route.continue(); });
    await page.focus("#upload-form button");
    await page.keyboard.press("Enter");
    await sleep(500);
    console.log("during the upload: button disabled =", await page.evaluate(() => document.querySelector("#upload-form button").disabled),
      "| focus on:", await page.evaluate(() => document.activeElement.tagName));
    await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "");
    console.log("after: focus on:", await page.evaluate(() => document.activeElement.tagName));
    await page.close();
  },
};
(async () => {
  const browser = await chromium.launch();
  for (const [name, fn] of Object.entries(S)) {
    if (WANT.size && !WANT.has(name)) continue;
    console.log(`--- ${name}`);
    try { await fn(browser); } catch (e) { console.log("ERROR", e.message.split("\n")[0]); }
  }
  await browser.close();
})();
