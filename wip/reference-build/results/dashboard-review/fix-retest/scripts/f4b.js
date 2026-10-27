// F4b: the stream-holder tab navigates away (clicks the alert) instead of closing.
// Run with Chrome's back/forward cache off (Playwright default) and on.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

async function run(bfcache, buildName, records) {
  const browser = await chromium.launch(bfcache ? { ignoreDefaultArgs: ["--disable-back-forward-cache"] } : {});
  const s = await L.startServer(buildName, "f4b");
  const res = { build: buildName, bfcache };
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    const ctx = await browser.newContext();
    const streams = [];
    const tabs = [];
    for (let n = 1; n <= 3; n++) {
      const page = await ctx.newPage();
      L.instrument(page, `${buildName} f4b bfcache=${bfcache} tab${n}`, records);
      page.on("request", (q) => { if (q.url().includes("/api/stream")) streams.push({ tab: n, t: Date.now() }); });
      await page.goto(s.base + "/");
      tabs.push(page);
    }
    await L.sleep(1500);
    res.streamsBefore = streams.map((x) => x.tab).join(",");
    const before = streams.length;
    const t0 = Date.now();
    await tabs[0].click(`a[href="/alerts/${id}"]`);
    await tabs[0].waitForLoadState("load");
    let took = null;
    for (let i = 0; i < 100 && took === null; i++) {
      const fresh = streams.slice(before).find((x) => x.tab !== 1);
      if (fresh) took = `tab ${fresh.tab} after ${fresh.t - t0} ms`;
      else await L.sleep(100);
    }
    res.takeoverAfterHolderNavigates = took || "no new stream within 10 s";
    res.patch = (await L.patchAlert(s, id, { actor: "x", assignee: "Moved" })).status;
    const t1 = Date.now();
    res.otherTabsUpdate = (await Promise.all(tabs.slice(1).map(async (p, i) => {
      try {
        await p.waitForFunction((i2) => document.querySelector(`a[href="/alerts/${i2}"]`).closest("tr").textContent.includes("Moved"), id, { timeout: 10000, polling: 50 });
        return `${i + 2}:${Date.now() - t1}`;
      } catch (e) { return `${i + 2}:never`; }
    }))).join(" ");
    // back to the queue in tab 1: restored from the cache or loaded again?
    await tabs[0].evaluate(() => { window.__left = true; });
    await tabs[0].evaluate(() => { window.addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
    const persisted = tabs[0].evaluate(() => 0);  // placeholder to keep the order clear
    await persisted;
    await tabs[0].goBack();
    await tabs[0].waitForLoadState("load");
    res.tab1BackRestoredFromCache = await tabs[0].evaluate(() => performance.getEntriesByType("navigation")[0].type + (window.__restored ? " (restored)" : ""));
    await L.sleep(1500);
    res.streamsAfterBack = streams.map((x) => x.tab).join(",");
    await ctx.close();
  } finally {
    await L.stopServer(s);
    await browser.close();
  }
  return res;
}

(async () => {
  const records = [];
  const out = [];
  try {
    for (const b of ["fixed-AHM-03"]) for (const bf of [false, true]) out.push(await run(bf, b, records));
  } finally {
    await L.stopAll();
  }
  for (const r of out) console.log(JSON.stringify(r));
  const sum = L.summarizeRecords(records);
  console.log("console errors:", sum.consoleErrors, "outside:", sum.outside);
  L.writeJSON("f4b.json", { out, console: sum });
})();
