// S13: the stream answers 502 twice, then works. Exactly one stream must be open
// afterwards, and one change must cause one refresh (not two). Usage: node s13_streams.js <build>
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
    const streams = [], gets = [];
    page.on("request", (r) => { if (r.url().includes("/?status=")) gets.push(Date.now() - t0); });
    let failures = 0;
    await page.route("**/api/stream", async (route) => {
      streams.push(`+${Date.now() - t0}ms`);
      if (failures++ < 2) return route.fulfill({ status: 502, body: "bad gateway", contentType: "text/html" });
      return route.continue();
    });
    await page.goto(server.origin + "/");
    await L.sleep(13000);                       // two retries at 5 s each, then a good one
    out.streamRequests = streams.join(", ");
    out.established = M.established(server.port);
    out.locks = await M.locks(page);
    const g0 = gets.length;
    await L.upload(server.port, "ftp"); rows++;
    const r = await L.waitFor(async () => (await L.rowCount(page)) === rows, 5000);
    await L.sleep(1500);
    out.live = r.ok ? `yes ${r.ms} ms` : `NO (rows ${await L.rowCount(page)} / ${rows})`;
    out.getsForOneChange = `${gets.length - g0} (1 expected)`;
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
