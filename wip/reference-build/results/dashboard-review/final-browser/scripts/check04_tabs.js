// Check 4: 8 queue tabs in one context use ONE /api/stream; a 9th tab (/upload) loads in
// under 2 s; one PATCH reaches all 8 tabs within 3 s; closing the stream's tab hands the
// stream to another tab and a second PATCH reaches all remaining tabs. Console errors kept.
// Usage: node check04_tabs.js <buildKey...>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");

// page.evaluate on a tab whose navigation never finished can wait forever: give up after ms.
const within = (promise, ms, fallback) => Promise.race([promise.catch(() => fallback), L.sleep(ms).then(() => fallback)]);

async function reach(base, tabs, id, name, limitMs) {
  const t0 = Date.now();
  await L.api(base, "PATCH", "/api/alerts/" + id, { actor: "x", assignee: name });
  const when = new Array(tabs.length).fill(null);
  while (Date.now() - t0 < limitMs && when.some((w) => w === null)) {
    await Promise.all(tabs.map(async (t, i) => {
      if (when[i] !== null) return;
      const shows = await within(t.evaluate((n) => [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((c) => c.textContent === n), name), 400, false);
      if (shows) when[i] = Date.now() - t0;
    }));
    await L.sleep(100);
  }
  return when;
}

async function run(browser, srv) {
  const tid = await L.telnetId(srv.base);
  const ctx = await browser.newContext();
  const pages = [];
  const streams = [];       // [tabIndex, time]
  const consoleErrors = [];
  ctx.on("request", (r) => {
    if (new URL(r.url()).pathname === "/api/stream") {
      let idx = -1;
      try { idx = pages.indexOf(r.frame().page()); } catch (e) { /* no frame */ }
      streams.push(idx + 1);
    }
  });
  ctx.on("page", (p) => {
    p.on("console", (m) => { if (m.type() === "error") consoleErrors.push(`tab${pages.indexOf(p) + 1}: ${m.text().slice(0, 160)}`); });
    p.on("pageerror", (e) => consoleErrors.push(`tab${pages.indexOf(p) + 1} pageerror: ${String(e).slice(0, 160)}`));
  });
  const loads = [];
  for (let i = 0; i < 8; i++) {
    const p = await ctx.newPage();
    pages.push(p);
    const t = Date.now();
    try {
      await p.goto(srv.base + "/", { timeout: 8000 });
      loads.push(Date.now() - t);
    } catch (e) {
      loads.push(`no load in 8 s`);
    }
  }
  await L.sleep(1500);
  const streamsAfter8 = streams.length;
  const streamTabs = [...streams];
  const ninth = await ctx.newPage();
  const t9 = Date.now();
  let ninthMs;
  try { await ninth.goto(srv.base + "/upload", { timeout: 10000 }); ninthMs = Date.now() - t9; }
  catch (e) { ninthMs = "no load in 10 s"; }
  const loaded = [];
  for (const p of pages) loaded.push(await within(p.evaluate(() => !!document.getElementById("alerts")), 1000, false));
  const reach1 = await reach(srv.base, pages, tid, "Tabs1", 3000);
  // Close the tab whose request opened the stream.
  const holder = streamTabs[0];
  const holderPage = pages[holder - 1];
  await holderPage.close();
  const rest = pages.filter((p) => p !== holderPage);
  await L.sleep(1500);
  const newStreams = streams.slice(streamsAfter8);
  const reach2 = await reach(srv.base, rest, tid, "Tabs2", 3000);
  await within(ctx.close(), 10000, null);
  const ok1 = reach1.filter((x) => x !== null).length;
  const ok2 = reach2.filter((x) => x !== null).length;
  return {
    queueTabLoadMs: loads, queueTabsShowingTable: loaded.filter(Boolean).length,
    streamRequestsAfter8Tabs: streamsAfter8, streamRequestTabs: streamTabs,
    ninthTabUploadMs: ninthMs,
    patch1ReachedTabs: `${ok1}/8`, patch1Ms: reach1, closedTab: holder,
    newStreamRequestsAfterClose: newStreams.length, newStreamFromTab: newStreams,
    patch2ReachedTabs: `${ok2}/${rest.length}`, patch2Ms: reach2,
    consoleErrors,
    pass: streamsAfter8 === 1 && typeof ninthMs === "number" && ninthMs < 2000 && ok1 === 8 &&
          newStreams.length === 1 && ok2 === 7,
  };
}

(async () => {
  const browser = await chromium.launch();
  for (const key of process.argv.slice(2)) {
    const r = await L.withServer(key, "c04", (srv) => run(browser, srv));
    console.log(`== ${key} check 4 (8 tabs): ${JSON.stringify(r)}`);
  }
  await browser.close();
})();
