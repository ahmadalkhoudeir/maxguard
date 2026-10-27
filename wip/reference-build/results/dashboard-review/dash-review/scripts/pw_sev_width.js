"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
  await ctx.addCookies([{ name: "mg_mode", value: "home", url: BASE }]);
  const page = await ctx.newPage();
  await page.goto(BASE + "/");
  console.log(await page.evaluate(() => JSON.stringify({
    scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth,
    badges: [...document.querySelectorAll("#alerts .sev")].map((e) => [e.textContent, Math.round(e.getBoundingClientRect().width)]),
    td_value_column: (() => { const td = document.querySelector('#alerts td[data-label="Severity"]');
      return getComputedStyle(td).gridTemplateColumns; })() }, null, 1)));
  await browser.close();
})();
