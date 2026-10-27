// S14: a refresh whose answer never comes (held 40 s) while changes happen; the 30 s
// poll (hx-sync replace) must abort it and show the newest state; the remembered
// refresh ("again") must not cause a storm. Usage: node s14_sync.js <build>
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
    const page = await ctx.newPage();
    const t0 = Date.now();
    const log = [];
    page.on("request", (r) => { if (r.url().includes("/?status=")) log.push(`sent +${Date.now() - t0}`); });
    page.on("requestfailed", (r) => { if (r.url().includes("/?status=")) log.push(`aborted +${Date.now() - t0}`); });
    page.on("response", (r) => { if (r.url().includes("/?status=")) log.push(`answered +${Date.now() - t0}`); });
    await page.goto(server.origin + "/");
    await L.sleep(1500);
    let held = 0;
    await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
      if (held++ === 0) {               // the first refresh: the answer never arrives in time
        await L.sleep(40000);
        try { await route.fulfill({ status: 200, body: "late", contentType: "text/html" }); } catch (e) { /* aborted */ }
        return;
      }
      return route.continue();
    });
    log.push(`t0 = page loaded +1500; trigger refresh now`);
    await page.evaluate(() => htmx.trigger("#alerts", "refresh"));
    await L.sleep(1000);
    out.classesDuringHeld = await page.evaluate(() => document.getElementById("alerts").className);
    await L.upload(server.port, "ftp"); rows++;      // a change while the refresh hangs
    await L.sleep(2000);
    out.rowsWhileHeld = `${await L.rowCount(page)} (server ${rows})`;
    await L.upload(server.port, "imap"); rows++;     // and another one
    const r = await L.waitFor(async () => (await L.rowCount(page)) === rows, 45000, 250);
    out.caughtUp = r.ok ? `yes after ${r.ms} ms (the 30 s poll replaced the hung refresh)` : `NO after ${r.ms} ms, rows ${await L.rowCount(page)} / ${rows}`;
    await L.sleep(3000);
    out.log = log;
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
