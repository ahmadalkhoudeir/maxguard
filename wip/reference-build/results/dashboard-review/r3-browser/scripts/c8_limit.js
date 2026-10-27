// Check 8: 201 alerts -> 200 rows and the "More alerts match" caption; with both filters
// set the caption ends "are not shown."; 3 alerts -> "3 alerts, most severe first".
// Usage: node c8_limit.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const WANT_201 = "The 200 most severe alerts, most recent first. More alerts match and are not shown: choose a status and a severity to see them.";
const WANT_BOTH = "The 200 most severe alerts, most recent first. More alerts match and are not shown.";

const read = (page) => page.evaluate(() => ({
  rows: document.querySelectorAll("#alerts tbody tr").length,
  caption: (document.querySelector("#alerts caption") || {}).textContent || null,
}));

async function run(buildName, browser) {
  const out = { build: buildName };
  const ctx = await L.newContext(browser);
  const page = await ctx.newPage();
  try {
    let dataDir = L.newDataDir(buildName + "-c8-201");
    out.added201 = L.addAlerts(buildName, dataDir, ["low"], 201);
    let server = await L.startServer(buildName, { dataDir });
    out.apiCount = (await L.alerts(server.port)).length + " (API default limit)";
    await page.goto(server.origin + "/");
    out.noFilter = await read(page);
    await page.goto(server.origin + "/?status=new&severity=low");
    out.bothFilters = await read(page);
    await server.stop();
    dataDir = L.newDataDir(buildName + "-c8-3");
    out.added3 = L.addAlerts(buildName, dataDir, ["high", "medium", "low"], 1);
    server = await L.startServer(buildName, { dataDir });
    await page.goto(server.origin + "/");
    out.three = await read(page);
    await server.stop();
    out.pass = out.noFilter.rows === 200 && out.noFilter.caption === WANT_201
      && out.bothFilters.rows === 200 && out.bothFilters.caption === WANT_BOTH
      && out.three.rows === 3 && out.three.caption === "3 alerts, most severe first";
  } finally {
    await ctx.close();
    await L.stopAll();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
