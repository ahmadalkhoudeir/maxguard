// Back/Forward with "historyCacheSize": 0, and the Analyst/Home switch after Back.
// Usage: node pw_history.js <base-url>
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const state = (page) => page.evaluate(() => ({
  url: location.pathname + location.search,
  marker: window.__marker === 1 ? "same document (no full reload)" : "new document (full reload)",
  status: document.getElementById("status") && document.getElementById("status").value,
  severity: document.getElementById("severity") && document.getElementById("severity").value,
  rows: [...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent.trim()).join(","),
  next: document.querySelector(".mode-switch input[name=next]").value,
  sessionCache: sessionStorage.getItem("htmx-history-cache") ? "present" : "none",
}));
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const restoreRequests = [];
  page.on("request", (r) => { if (r.headers()["hx-history-restore-request"]) restoreRequests.push(r.url().replace(BASE, "")); });
  let navigations = 0;
  page.on("framenavigated", (f) => { if (f === page.mainFrame()) navigations += 1; });
  await page.goto(BASE + "/");
  await page.evaluate(() => { window.__marker = 1; });
  await page.selectOption("#severity", "medium");
  await page.waitForURL(/severity=medium/);
  await page.selectOption("#status", "new");
  await page.waitForURL(/status=new/);
  await sleep(300);
  console.log("before Back:", JSON.stringify(await state(page)));
  await page.goBack();
  await sleep(1500);
  console.log("after Back: ", JSON.stringify(await state(page)));
  console.log("history-restore requests:", JSON.stringify(restoreRequests), "| main-frame navigations since goto:", navigations - 1);
  // The analyst now narrows the list again and switches to Home.
  await page.selectOption("#severity", "high");
  await page.waitForURL(/severity=high/);
  await sleep(300);
  console.log("filter changed after Back:", JSON.stringify(await state(page)));
  await page.click(".mode-switch button[value=home]");
  await page.waitForLoadState("load");
  await sleep(500);
  console.log("after the Home switch:", JSON.stringify(await state(page)));
  await page.click(".mode-switch button[value=analyst]");  // put the cookie back
  await browser.close();
})();
