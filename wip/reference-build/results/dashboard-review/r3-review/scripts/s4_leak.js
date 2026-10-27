// S4: 300 table refreshes in one tab. Do listeners, timers, streams or heap grow?
// Usage: node s4_leak.js <build>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
const M = require("./more");

async function listenerCounts(cdp) {
  const counts = {};
  for (const expr of ["window", "document", "document.body", "document.getElementById('alerts')"]) {
    const { result } = await cdp.send("Runtime.evaluate", { expression: expr, objectGroup: "probe" });
    const { listeners } = await cdp.send("DOMDebugger.getEventListeners", { objectId: result.objectId, depth: 0 });
    const byType = {};
    for (const l of listeners) byType[l.type] = (byType[l.type] || 0) + 1;
    counts[expr] = { total: listeners.length, ...byType };
  }
  await cdp.send("Runtime.releaseObjectGroup", { objectGroup: "probe" });
  return counts;
}

async function heap(cdp) {
  const { usedSize } = await cdp.send("Runtime.getHeapUsage");
  return Math.round(usedSize / 1024) + " KiB";
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await browser.newContext();
    await ctx.addInitScript(M.INIT);
    const page = await ctx.newPage();
    const gets = [];
    page.on("request", (r) => { if (r.url().includes("/?status=")) gets.push(Date.now()); if (r.url().includes("/api/stream")) gets.push("stream"); });
    await page.goto(server.origin + "/");
    await L.sleep(1500);
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("HeapProfiler.collectGarbage");
    out.before = { listeners: await listenerCounts(cdp), heap: await heap(cdp), established: M.established(server.port) };
    const N = 300;
    const t0 = Date.now();
    let settled = 0;
    for (let i = 0; i < N; i++) {
      const ok = await page.evaluate(() => new Promise((resolve) => {
        const timer = setTimeout(() => resolve(false), 4000);
        document.addEventListener("htmx:afterSettle", function once(e) {
          if (e.target.id !== "alerts") return;
          document.removeEventListener("htmx:afterSettle", once);
          clearTimeout(timer);
          resolve(true);
        });
        htmx.trigger("#alerts", "refresh");
      }));
      if (ok) settled++;
    }
    out.refreshes = `${N} triggered, ${settled} settled in ${Date.now() - t0} ms`;
    await L.sleep(500);
    await cdp.send("HeapProfiler.collectGarbage");
    out.after = { listeners: await listenerCounts(cdp), heap: await heap(cdp), established: M.established(server.port),
      alertsDivs: await page.evaluate(() => document.querySelectorAll("#alerts").length) };
    // polling: in the next 40 s only the one "every 30s" poll should fire
    const g0 = gets.length;
    await L.sleep(40000);
    out.requestsIn40s = `${gets.length - g0} (about 1 expected: the 30 s poll)`;
    await L.upload(server.port, "ftp");
    const g1 = gets.length;
    await L.sleep(3000);
    out.requestsForOneChange = `${gets.length - g1} (1 expected)`;
    out.rowsNow = await L.rowCount(page);
    out.errors = await page.evaluate(() => window.__errors);
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2).length ? process.argv.slice(2) : ["fixed-06"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
