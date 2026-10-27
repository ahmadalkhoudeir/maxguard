// T6: a non-holder queue page sits in bfcache with its lock request still pending,
// then the holder tab closes. Who gets the lock? Does a new queue tab get live refresh?
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    let rows = 1;
    const ctx = await browser.newContext();
    const streams = [];
    ctx.on("request", (r) => {
      if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label);
    });
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
    const extra = Number(process.env.WAIT_S || 0) * 1000;
    if (extra) {
      await L.sleep(extra);
      out.waitedExtraSeconds = extra / 1000;
    }
    out.streams = streams.join(",");
    out.locksFromX = await X.evaluate(async () => {
      const q = await navigator.locks.query();
      return `held=${q.held.length} pending=${q.pending.length}`;
    });
    await L.upload(server.port, "ftp"); rows++;
    const r = await L.waitFor(async () => (await L.rowCount(X)) === rows, 5000);
    out.newTabLiveRefresh = r.ok ? `yes ${r.ms} ms` : `NO after ${r.ms} ms (rows ${await L.rowCount(X)}, server ${rows})`;
    // N comes back
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
    out.nRows = `${await L.rowCount(N)} (server ${rows})`;
    out.streamsEnd = streams.join(",");
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("chromium", browser.version(), "full Chromium, bfcache on");
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
