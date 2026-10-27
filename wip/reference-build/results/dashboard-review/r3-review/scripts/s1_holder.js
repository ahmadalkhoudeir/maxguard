// S1: the tab holding the stream lock leaves the queue page (alert link) and comes
// Back. Does another tab take the stream over? Is the holder's page bfcached with the
// lock? How many streams are open at each step? Usage: node s1_holder.js <build>
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
    const streams = [];
    const t0 = Date.now();
    ctx.on("request", (r) => { if (r.url().includes("/api/stream")) streams.push(`${r.frame().page()._label}@${Date.now() - t0}ms`); });
    const H = await ctx.newPage(); H._label = "H";
    await H.goto(server.origin + "/");
    await L.sleep(700);
    const N = await ctx.newPage(); N._label = "N";
    await N.goto(server.origin + "/");
    await L.sleep(700);
    out.step1_locks = await M.locks(N);
    out.step1_streams = streams.join(",") + ` | established=${M.established(server.port)}`;

    await H.click("#alerts tbody a");                 // the holder leaves the queue page
    await H.waitForURL(/\/alerts\//);
    await L.sleep(1500);
    out.step2_locksAfterHolderLeft = await M.locks(N);
    out.step2_streams = streams.join(",") + ` | established=${M.established(server.port)}`;
    await L.upload(server.port, "ftp"); rows++;
    const r1 = await L.waitFor(async () => (await L.rowCount(N)) === rows, 5000);
    out.step2_nLiveAfterTakeover = r1.ok ? `yes ${r1.ms} ms` : `NO (rows ${await L.rowCount(N)} / ${rows})`;

    await H.goBack({ waitUntil: "commit" });          // the holder comes Back
    await H.waitForSelector("#alerts");
    await L.sleep(1500);
    out.step3_hBack = await M.navInfo(H);
    out.step3_hShows = await H.evaluate(() => window.__shows.join(","));
    out.step3_hRows = `${await L.rowCount(H)} (server ${rows})`;
    out.step3_locks = await M.locks(N);
    await L.upload(server.port, "imap"); rows++;
    const r2 = await L.waitFor(async () => (await L.rowCount(H)) === rows && (await L.rowCount(N)) === rows, 5000);
    out.step3_bothLive = r2.ok ? `yes ${r2.ms} ms` : `NO (H ${await L.rowCount(H)}, N ${await L.rowCount(N)} / ${rows})`;
    out.step3_streams = streams.join(",") + ` | established=${M.established(server.port)}`;

    await N.close();                                   // the new holder closes
    await L.sleep(1500);
    out.step4_locksAfterNClosed = await M.locks(H);
    await L.upload(server.port, "pop3"); rows++;
    const r3 = await L.waitFor(async () => (await L.rowCount(H)) === rows, 5000);
    out.step4_hLive = r3.ok ? `yes ${r3.ms} ms` : `NO (rows ${await L.rowCount(H)} / ${rows})`;
    out.step4_streams = streams.join(",") + ` | established=${M.established(server.port)}`;
    out.errors = await H.evaluate(() => window.__errors);
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
