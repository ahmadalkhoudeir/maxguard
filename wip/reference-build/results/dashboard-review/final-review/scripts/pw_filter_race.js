// A refresh is running when the analyst picks a filter; every table request takes the
// same time on the server (a slow Pi), so the refresh, sent first, answers first.
// Usage: node pw_filter_race.js <base-url> [delay-ms]
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const DELAY = Number(process.argv[3] || 800);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const state = (page) => page.evaluate(() => ({
  url: location.search,
  select: document.getElementById("severity").value,
  rows: [...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent.trim()),
  refreshUrl: document.getElementById("alerts").getAttribute("hx-get"),
  caption: (document.querySelector("#alerts caption") || {}).textContent,
}));
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const log = [];
  await page.goto(BASE + "/");
  await sleep(1500); // the stream's first event already caused one refresh
  await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
    const t = Date.now();
    const response = await route.fetch();   // the server renders it now ...
    await sleep(DELAY);                       // ... and the answer takes DELAY ms to arrive
    log.push(`${new URL(route.request().url()).search} sent +${t - t0} ms, answered +${Date.now() - t0} ms`);
    try { await route.fulfill({ response }); } catch (e) { log.push("  (aborted by the page)"); }
  });
  const t0 = Date.now();
  await page.evaluate(() => htmx.trigger("#alerts", "refresh"));  // what an alerts-changed event does
  await sleep(100);
  await page.selectOption("#severity", "medium");
  await sleep(DELAY * 2 + 1500);
  console.log(log.join("\n"));
  console.log("after both answers:", JSON.stringify(await state(page)));
  await page.unroute((u) => true).catch(() => {});
  await page.evaluate(() => htmx.trigger("#alerts", "refresh"));  // the next live refresh
  await sleep(1500);
  console.log("after the next refresh:", JSON.stringify(await state(page)));
  await browser.close();
})();
