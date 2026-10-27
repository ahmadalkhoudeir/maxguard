// S2: a non-holder tab N goes through several bfcache cycles (alert page, Back), then
// the holder closes. Does N end up with exactly one stream, and no stale lock requests?
// Usage: node s2_cycles.js <build>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
const M = require("./more");

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    let rows = 1;
    const ctx = await browser.newContext();
    await ctx.addInitScript(M.INIT);
    const streams = [], gets = [];
    ctx.on("request", (r) => {
      const label = r.frame().page()._label;
      if (r.url().includes("/api/stream")) streams.push(label);
      if (r.url().includes("/?status=")) gets.push(label);
    });
    const H = await ctx.newPage(); H._label = "H";
    await H.goto(server.origin + "/");
    await L.sleep(700);
    const N = await ctx.newPage(); N._label = "N";
    await N.goto(server.origin + "/");
    await L.sleep(700);
    const cycles = [];
    for (let i = 0; i < 5; i++) {
      await N.click("#alerts tbody a");
      await N.waitForURL(/\/alerts\//);
      await L.sleep(400);
      await N.goBack({ waitUntil: "commit" });
      await N.waitForSelector("#alerts");
      await L.sleep(600);
      cycles.push(`${await M.navInfo(N)} / ${await M.locks(N)}`);
    }
    out.cycles = cycles;
    out.nShows = await N.evaluate(() => window.__shows.join(","));
    out.streamsBeforeHolderClosed = streams.join(",");
    const getsBefore = gets.length;
    await H.close();
    await L.sleep(2000);
    out.locksAfterHolderClosed = await M.locks(N);
    out.streamsAfterHolderClosed = streams.join(",") + ` | established=${M.established(server.port)}`;
    out.getsByNWhileTakingOver = gets.slice(getsBefore).join(",");
    const g0 = gets.length;
    await L.upload(server.port, "ftp"); rows++;
    const r1 = await L.waitFor(async () => (await L.rowCount(N)) === rows, 5000);
    await L.sleep(1500);
    out.nLive = r1.ok ? `yes ${r1.ms} ms` : `NO (rows ${await L.rowCount(N)} / ${rows})`;
    out.getsForOneChange = gets.slice(g0).join(",") + " (1 expected: one stream, one refresh)";
    const X = await ctx.newPage(); X._label = "X";
    await X.goto(server.origin + "/");
    await L.sleep(700);
    out.locksWithX = await M.locks(X);
    await L.upload(server.port, "imap"); rows++;
    const r2 = await L.waitFor(async () => (await L.rowCount(N)) === rows && (await L.rowCount(X)) === rows, 5000);
    out.nAndXLive = r2.ok ? `yes ${r2.ms} ms` : `NO (N ${await L.rowCount(N)}, X ${await L.rowCount(X)} / ${rows})`;
    out.streamsEnd = streams.join(",") + ` | established=${M.established(server.port)}`;
    out.errorsN = await N.evaluate(() => window.__errors);
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("chromium", browser.version(), "bfcache on");
  try {
    for (const b of process.argv.slice(2).length ? process.argv.slice(2) : ["fixed-06"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
