// One /api/stream for all queue tabs (Web Locks + BroadcastChannel).
// Usage: node pw_stream.js <port> <scenario...>
"use strict";
const { chromium } = require("playwright");
const PORT = process.argv[2];
const BASE = `http://127.0.0.1:${PORT}`;
const WANT = new Set(process.argv.slice(3));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
let counter = 0;
// Change one alert's assignee and report which pages show it within 5 s.
async function changeAndCheck(pages) {
  const id = (await api("GET", "/api/alerts"))[1][0].finding_id;
  const name = `Live-${++counter}`;
  await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: name });
  const seen = await Promise.all(pages.map((p) => p.waitForFunction((n) =>
    [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((t) => t.textContent === n),
    name, { timeout: 5000 }).then(() => true, () => false)));
  return seen;
}
function countStreams(ctx) {
  ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
  const urls = [];
  ctx.on("request", (r) => { if (r.url().includes("/api/stream")) urls.push(r.url()); });
  return urls;
}
const S = {
  async tabs_and_navigation(browser) {
    const ctx = await browser.newContext();
    const streams = countStreams(ctx);
    const pages = [];
    for (let i = 0; i < 3; i++) { const p = await ctx.newPage(); await p.goto(BASE + "/"); pages.push(p); }
    await sleep(1000);
    console.log("3 queue tabs, stream requests:", streams.length, "| shown in tabs:", JSON.stringify(await changeAndCheck(pages)));
    await pages[0].goto(BASE + "/upload");  // the leader leaves the queue
    await sleep(1500);
    console.log("leader went to /upload, stream requests so far:", streams.length,
      "| shown in the 2 queue tabs:", JSON.stringify(await changeAndCheck(pages.slice(1))));
    await pages[0].goBack();
    await sleep(500);
    console.log("Back in tab 1: restored from the back/forward cache:", await pages[0].evaluate(() => window.__persisted));
    const reasons = await pages[0].evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      const nrr = nav && nav.notRestoredReasons;
      return nrr ? JSON.stringify(nrr.reasons || nrr) : String(nrr);
    });
    console.log("notRestoredReasons:", reasons);
    await sleep(1000);
    const held = await pages[0].evaluate(async () => JSON.stringify(await navigator.locks.query()));
    console.log("locks seen from tab 1:", held);
    console.log("stream requests so far:", streams.length, "| shown in 3 tabs:", JSON.stringify(await changeAndCheck(pages)));
    await ctx.close();
  },
  async bfcache_nonleader(browser) {
    const ctx = await browser.newContext();
    const streams = countStreams(ctx);
    const a = await ctx.newPage(); await a.goto(BASE + "/");
    const b = await ctx.newPage(); await b.goto(BASE + "/");
    await sleep(800);
    await b.goto(BASE + "/upload");          // the waiting tab leaves
    await a.close();                          // the leader closes while b is away
    await sleep(1000);
    await b.goBack();
    await sleep(500);
    console.log("non-leader came back from the cache:", await b.evaluate(() => window.__persisted), "| stream requests:", streams.length);
    await sleep(1000);
    console.log("shown in tab b:", JSON.stringify(await changeAndCheck([b])),
      "| locks:", await b.evaluate(async () => JSON.stringify(await navigator.locks.query())));
    await ctx.close();
  },
  async two_origins(browser) {
    const ctx = await browser.newContext();
    const streams = countStreams(ctx);
    const pages = [];
    for (const host of ["127.0.0.1", "localhost", "127.0.0.1", "localhost"]) {
      const p = await ctx.newPage(); await p.goto(`http://${host}:${PORT}/`); pages.push(p);
    }
    await sleep(1000);
    console.log("2 tabs on 127.0.0.1 + 2 on localhost: stream requests:", JSON.stringify(streams.map((u) => new URL(u).host)),
      "| shown in 4 tabs:", JSON.stringify(await changeAndCheck(pages)));
    await ctx.close();
  },
  async two_windows(browser) {
    // two browser windows of one profile share one context; a second context is a second profile
    const c1 = await browser.newContext(), c2 = await browser.newContext();
    const s1 = countStreams(c1), s2 = countStreams(c2);
    const pages = [];
    for (const c of [c1, c1, c2, c2]) { const p = await c.newPage(); await p.goto(BASE + "/"); pages.push(p); }
    await sleep(1000);
    console.log("2 profiles x 2 tabs: stream requests", s1.length, "+", s2.length,
      "| shown in 4 tabs:", JSON.stringify(await changeAndCheck(pages)));
    await c1.close(); await c2.close();
  },
  async fallback(browser) {
    const ctx = await browser.newContext();
    await ctx.addInitScript(() => { delete Navigator.prototype.locks; });
    const streams = countStreams(ctx);
    const pages = [];
    for (let i = 0; i < 3; i++) { const p = await ctx.newPage(); await p.goto(BASE + "/"); pages.push(p); }
    await sleep(1000);
    console.log("no navigator.locks:", await pages[0].evaluate(() => typeof navigator.locks),
      "| stream requests:", streams.length, "| shown in 3 tabs:", JSON.stringify(await changeAndCheck(pages)));
    await ctx.close();
  },
};
(async () => {
  const browser = await chromium.launch();
  console.log("Chromium", browser.version());
  for (const [name, fn] of Object.entries(S)) {
    if (WANT.size && !WANT.has(name)) continue;
    console.log(`--- ${name}`);
    try { await fn(browser); } catch (e) { console.log("ERROR", e.message.split("\n")[0]); }
  }
  await browser.close();
})();
