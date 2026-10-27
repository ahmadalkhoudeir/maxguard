// Check 3 (b): a queue page parked in the back/forward cache (full Chromium, bfcache
// on) must not hold the stream lock while a new tab gets no stream.
// Usage: node c3b_bfcache.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    let rows = 1;
    const ctx = await L.newContext(browser);
    const streams = [];
    ctx.on("request", (r) => { if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label); });
    const H = await ctx.newPage(); H._label = "H";
    await H.goto(server.origin + "/");
    await L.sleep(500);
    const N = await ctx.newPage(); N._label = "N";
    await N.goto(server.origin + "/");
    await L.sleep(500);
    await N.click("nav a[href='/upload']");      // N's queue page goes into bfcache
    await N.waitForURL(/\/upload/);
    await L.sleep(800);
    await H.close();                              // the holder goes away
    await L.sleep(1000);
    const X = await ctx.newPage(); X._label = "X";
    await X.goto(server.origin + "/");            // a new queue tab
    await L.sleep(1500);
    out.streams = streams.join(",");
    out.locksFromX = await X.evaluate(async () => {
      if (!navigator.locks) return "no navigator.locks";
      const q = await navigator.locks.query();
      return `held=${q.held.length} pending=${q.pending.length}`;
    });
    await L.upload(server.port, "ftp"); rows++;
    const r = await L.waitFor(async () => (await L.rowCount(X)) === rows, 5000);
    out.newTabLiveRefresh = r.ok ? `yes, ${r.ms} ms` : `NO after ${r.ms} ms (rows ${await L.rowCount(X)}, server ${rows})`;
    await N.goBack({ waitUntil: "commit" });
    await N.waitForSelector("#alerts");
    await L.sleep(1500);
    out.nBack = await N.evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      const flat = [];
      const walk = (x) => { if (!x) return; for (const y of x.reasons || []) flat.push(y.reason); for (const c of x.children || []) walk(c); };
      walk(nav.notRestoredReasons);
      return flat.join(",") || "restored from bfcache";
    });
    out.nRowsAfterBack = `${await L.rowCount(N)} (server ${rows})`;
    await L.upload(server.port, "imap"); rows++;
    const r2 = await L.waitFor(async () => (await L.rowCount(N)) === rows && (await L.rowCount(X)) === rows, 5000);
    out.bothTabsLiveAfterBack = r2.ok ? `yes, ${r2.ms} ms` : `NO after ${r2.ms} ms (N ${await L.rowCount(N)}, X ${await L.rowCount(X)}, server ${rows})`;
    out.streamsEnd = streams.join(",");
    out.pass = r.ok && r2.ok;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("Chromium", browser.version(), "full Chromium, bfcache on");
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
