// Check 3 (shared stream): 8 queue tabs in one context use one /api/stream; a 9th tab
// (/upload) loads; one PATCH reaches all 8 within 3 s; closing the holder hands over;
// a second PATCH reaches all. Fallback: navigator.locks deleted -> one stream per tab.
// Usage: node c3_stream.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

let counter = 0;
async function patchAndSee(server, pages, timeout = 3000) {
  const id = (await L.alerts(server.port))[0].finding_id;
  const name = `Live-${++counter}-${Date.now() % 10000}`;
  const t0 = Date.now();
  await L.patchAlert(server.port, id, { actor: "review", assignee: name });
  const seen = await Promise.all(pages.map((p) => p.waitForFunction((n) =>
    [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((t) => t.textContent === n),
    name, { timeout }).then(() => Date.now() - t0, () => null)));
  return seen;
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    await L.upload(server.port, "ftp");
    const ctx = await L.newContext(browser);
    const streams = [];
    ctx.on("request", (r) => { if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label); });
    const pages = [];
    const loadMs = [];
    for (let i = 1; i <= 8; i++) {
      const p = await ctx.newPage(); p._label = "T" + i;
      const t = Date.now();
      try { await p.goto(server.origin + "/", { timeout: 15000 }); loadMs.push(Date.now() - t); }
      catch (e) { loadMs.push("timeout"); }
      pages.push(p);
    }
    await L.sleep(1500);
    out.queueTabLoadMs = loadMs.join(",");
    out.streamRequestsAfter8Tabs = streams.length + " (" + streams.join(",") + ")";
    const ninth = await ctx.newPage(); ninth._label = "T9";
    const t9 = Date.now();
    try {
      await ninth.goto(server.origin + "/upload", { timeout: 10000 });
      out.ninthTabUpload = `loaded in ${Date.now() - t9} ms, h1="${await ninth.textContent("h1")}"`;
    } catch (e) { out.ninthTabUpload = "FAILED to load within 10 s: " + e.message.split("\n")[0]; }
    const seen1 = await patchAndSee(server, pages);
    out.patch1ReachedMs = seen1.map((x) => (x === null ? "NO" : x)).join(",");
    out.patch1AllWithin3s = seen1.every((x) => x !== null);
    // close the holder: the tab whose page made the (first) stream request
    const holderLabel = streams[0];
    const holder = pages.find((p) => p._label === holderLabel) || pages[0];
    const before = streams.length;
    await holder.close();
    const rest = pages.filter((p) => p !== holder);
    const handover = await L.waitFor(() => streams.length > before, 5000, 50);
    out.handoverAfterHolderClosed = handover.ok ? `new stream by ${streams[streams.length - 1]} after ${handover.ms} ms` : "NO new stream within 5 s";
    await L.sleep(500);
    const seen2 = await patchAndSee(server, rest);
    out.patch2ReachedMs = seen2.map((x) => (x === null ? "NO" : x)).join(",");
    out.patch2AllWithin3s = seen2.every((x) => x !== null);
    out.streamRequestsTotal = streams.length + " (" + streams.join(",") + ")";
    await ctx.close();

    // fallback: no navigator.locks -> one stream per tab, and the PATCH still reaches all
    const ctx2 = await L.newContext(browser);
    await ctx2.addInitScript(() => { delete Navigator.prototype.locks; });
    const streams2 = [];
    ctx2.on("request", (r) => { if (r.url().includes("/api/stream")) streams2.push(1); });
    const pages2 = [];
    for (let i = 0; i < 3; i++) { const p = await ctx2.newPage(); await p.goto(server.origin + "/"); pages2.push(p); }
    await L.sleep(1000);
    const seen3 = await patchAndSee(server, pages2);
    out.fallback = { locks: await pages2[0].evaluate(() => typeof navigator.locks), streamRequestsFor3Tabs: streams2.length,
      patchReachedMs: seen3.map((x) => (x === null ? "NO" : x)).join(",") };
    await ctx2.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  console.log("Chromium", browser.version());
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
