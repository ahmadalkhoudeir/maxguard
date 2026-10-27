// S11: the filter race the other way round. A refresh for the unfiltered table is in
// flight (its answer is slow); the analyst picks a filter, whose answer comes first;
// then the old unfiltered answer arrives. The table must stay filtered.
// Then the original race (refresh answers first) once more, on this build.
// Usage: node s11_reverse_race.js <build>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
const M = require("./more");

const state = (page) => page.evaluate(() => ({
  url: location.search,
  select: document.getElementById("severity").value,
  rows: [...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent.trim()).join("/"),
  refreshUrl: document.getElementById("alerts").getAttribute("hx-get"),
  caption: (document.querySelector("#alerts caption") || {}).textContent,
}));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    for (const name of ["telnet", "ftp", "plain_http"]) await L.upload(server.port, name);
    const alerts = await L.alerts(server.port);
    out.severities = alerts.map((a) => a.severity).join("/");
    const ctx = await browser.newContext();
    await ctx.addInitScript(M.INIT);
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    await L.sleep(1500);
    const log = [];
    let t0 = Date.now();
    // A: the UNFILTERED answer is slow (held 1500 ms); the filtered one is immediate
    await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
      const search = new URL(route.request().url()).search;
      const response = await route.fetch();
      if (search === "?status=&severity=") await L.sleep(1500);
      log.push(`${search} answered +${Date.now() - t0} ms`);
      try { await route.fulfill({ response }); } catch (e) { log.push("  (dropped by the page)"); }
    });
    await page.evaluate(() => htmx.trigger("#alerts", "refresh"));
    await L.sleep(150);
    await page.selectOption("#severity", "medium");
    await L.sleep(3000);
    out.A_log = log.splice(0);
    out.A_afterBoth = await state(page);
    await page.unroute((u) => true);
    await page.evaluate(() => htmx.trigger("#alerts", "refresh"));
    await L.sleep(1200);
    out.A_afterNextRefresh = await state(page);

    // B: the original race: both take 800 ms, the refresh was sent first
    await page.selectOption("#severity", "");
    await L.sleep(1200);
    t0 = Date.now();
    await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
      const search = new URL(route.request().url()).search;
      const response = await route.fetch();
      await L.sleep(800);
      log.push(`${search} answered +${Date.now() - t0} ms`);
      try { await route.fulfill({ response }); } catch (e) { log.push("  (dropped by the page)"); }
    });
    await page.evaluate(() => htmx.trigger("#alerts", "refresh"));
    await L.sleep(100);
    await page.selectOption("#severity", "high");
    await L.sleep(3000);
    out.B_log = log.splice(0);
    out.B_afterBoth = await state(page);
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
