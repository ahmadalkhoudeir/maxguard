// Back while the server cannot be reached (the history-restore request fails).
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const state = (page) => page.evaluate(() => ({
  url: location.search, severity: document.getElementById("severity").value,
  rows: [...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent.trim()).join(","),
  refreshUrl: document.getElementById("alerts").getAttribute("hx-get") }));
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(BASE + "/");
  await page.selectOption("#severity", "medium");
  await page.waitForURL(/severity=medium/);
  await page.selectOption("#severity", "high");
  await page.waitForURL(/severity=high/);
  await sleep(300);
  await page.route((u) => u.pathname === "/", (r) => r.abort("connectionrefused"));
  await page.goBack();
  await sleep(1000);
  console.log("Back, server unreachable:", JSON.stringify(await state(page)));
  await page.unroute((u) => u.pathname === "/");
  await page.evaluate(() => htmx.trigger("#alerts", "refresh"));
  await sleep(1000);
  console.log("server back, next refresh:", JSON.stringify(await state(page)));
  await browser.close();
})();
