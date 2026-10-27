// Check 4: a refresh is running when the analyst picks Severity = Medium; every table
// answer takes 800 ms. The table must end filtered and the address must match.
// Usage: node c4_filter_race.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const DELAY = 800;
const state = (page) => page.evaluate(() => ({
  url: location.search,
  select: document.getElementById("severity").value,
  rows: [...new Set([...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent.trim()))].join("+"),
  nrows: document.querySelectorAll("#alerts tbody tr").length,
  refreshUrl: document.getElementById("alerts").getAttribute("hx-get"),
}));

async function run(buildName, browser) {
  const out = { build: buildName };
  const dataDir = L.newDataDir(buildName + "-c4");
  L.addAlerts(buildName, dataDir, ["critical", "high", "medium", "low", "info"], 2);
  const server = await L.startServer(buildName, { dataDir });
  try {
    await L.upload(server.port, "telnet");
    const ctx = await L.newContext(browser);
    const page = await ctx.newPage();
    const log = [];
    await page.goto(server.origin + "/");
    await L.sleep(1500);
    const t0 = Date.now();
    await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
      const t = Date.now();
      const response = await route.fetch();
      await L.sleep(DELAY);
      log.push(`${new URL(route.request().url()).search} sent +${t - t0} ms, answered +${Date.now() - t0} ms`);
      try { await route.fulfill({ response }); } catch (e) { log.push("  (aborted by the page)"); }
    });
    await page.evaluate(() => htmx.trigger("#alerts", "refresh"));   // what an alerts-changed event does
    await L.sleep(100);
    await page.selectOption("#severity", "medium");
    await L.sleep(DELAY * 2 + 1500);
    out.requests = log;
    out.afterBothAnswers = await state(page);
    const s = out.afterBothAnswers;
    out.pass = s.url === "?status=&severity=medium" && s.select === "medium" && s.rows === "Medium";
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
