// Check 3 (d): two PATCHes about 200 ms apart while a slow (800 ms) table answer is in
// flight: both changes show without waiting for the 30 s poll.
// Usage: node c3d_midswap.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const DELAY = 800;

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    await L.upload(server.port, "ftp");
    const [a, b] = await L.alerts(server.port);
    const ctx = await L.newContext(browser);
    const page = await ctx.newPage();
    const gets = [];
    page.on("request", (r) => { if (r.url().includes("/?status=")) gets.push(Date.now()); });
    await page.goto(server.origin + "/");
    await L.sleep(1500);                                 // the stream's first event already refreshed once
    await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
      const response = await route.fetch();              // rendered by the server now ...
      await L.sleep(DELAY);                               // ... delivered 800 ms later
      try { await route.fulfill({ response }); } catch (e) { /* aborted by the page */ }
    });
    const g0 = gets.length;
    const t0 = Date.now();
    await L.patchAlert(server.port, a.finding_id, { actor: "r3", assignee: "P1" });
    // the second PATCH 200 ms later, but only once the first refresh request is in flight
    await L.sleep(200);
    const inFlight = await L.waitFor(() => gets.length > g0, 2000, 10);
    const t1 = Date.now();
    await L.patchAlert(server.port, b.finding_id, { actor: "r3", assignee: "P2" });
    out.patchGapMs = t1 - t0;
    out.firstGetInFlightWhenPatch2Sent = inFlight.ok;
    const shown = () => page.evaluate(() => [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].map((t) => t.textContent.trim()).sort().join(","));
    const r = await L.waitFor(async () => (await shown()) === "P1,P2", 35000, 50);
    out.bothShownAfterMs = r.ok ? `${Date.now() - t1} ms after the second PATCH` : `NOT within 35 s (shows ${await shown()})`;
    out.tableRequests = gets.length - g0;
    out.pass = r.ok && Date.now() - t1 < 5000;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
