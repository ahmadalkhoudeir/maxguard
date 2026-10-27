// The stream lock with the back/forward cache switched ON (Playwright switches it off).
// Usage: node pw_bfcache.js <port>
"use strict";
const { chromium } = require("playwright");
const PORT = process.argv[2];
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
let counter = 0;
async function changeAndCheck(pages) {
  const id = (await api("GET", "/api/alerts"))[1][0].finding_id;
  const name = `Live-${++counter}`;
  await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: name });
  return Promise.all(pages.map((p) => p.waitForFunction((n) =>
    [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((t) => t.textContent === n),
    name, { timeout: 5000 }).then(() => true, () => false)));
}
const info = (p) => p.evaluate(async () => {
  const nav = performance.getEntriesByType("navigation")[0];
  return { persisted: window.__persisted, reasons: nav.notRestoredReasons ? JSON.stringify(nav.notRestoredReasons.reasons) : null,
    locks: JSON.stringify(await navigator.locks.query(), (k, v) => (k === "clientId" ? undefined : v)) };
});
(async () => {
  const browser = await chromium.launch({ ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  // control: is the cache on at all? a plain page with nothing open
  {
    const ctx = await browser.newContext();
    await ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
    const p = await ctx.newPage();
    await p.goto(BASE + "/upload"); await p.goto(BASE + "/static/app.css"); await p.goBack(); await sleep(500);
    console.log("control (/upload, no stream): back from the cache:", await p.evaluate(() => window.__persisted));
    await ctx.close();
  }
  const ctx = await browser.newContext();
  await ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
  const streams = [];
  ctx.on("request", (r) => { if (r.url().includes("/api/stream")) streams.push(Date.now()); });
  const [a, b, c] = [await ctx.newPage(), await ctx.newPage(), await ctx.newPage()];
  for (const p of [a, b, c]) { await p.goto(BASE + "/"); }
  await sleep(1000);
  console.log("3 queue tabs: stream requests", streams.length);
  await a.goto(BASE + "/upload");   // leader leaves
  await sleep(1500);
  console.log("leader left: stream requests", streams.length, "| b, c show a change:", JSON.stringify(await changeAndCheck([b, c])));
  await a.goBack(); await sleep(1000);
  console.log("leader back:", JSON.stringify(await info(a)), "| stream requests", streams.length);
  await b.goto(BASE + "/upload");   // a waiting (or leading) tab leaves
  await sleep(1500);
  await b.goBack(); await sleep(1000);
  console.log("b back:", JSON.stringify(await info(b)), "| stream requests", streams.length);
  console.log("a, b, c show a change:", JSON.stringify(await changeAndCheck([a, b, c])));
  await ctx.close();
  await browser.close();
})();
