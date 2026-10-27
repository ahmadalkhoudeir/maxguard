"use strict";
const { chromium } = require("playwright");
const [BASE, W, FONT] = [process.argv[2], Number(process.argv[3]), process.argv[4]];
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: 800 }, bypassCSP: true });
  await ctx.addCookies([{ name: "mg_mode", value: "home", url: BASE }]);
  const page = await ctx.newPage();
  await page.goto(BASE + "/");
  if (FONT) await page.addStyleTag({ content: `html, body, input, button, select, label { font-family: "${FONT}" !important }` });
  console.log(await page.evaluate(() => JSON.stringify({ sw: document.documentElement.scrollWidth,
    cols: [...document.querySelectorAll("#alerts thead th")].map((th) => `${th.textContent}: ${Math.round(th.getBoundingClientRect().width)}`),
    widest: [...document.querySelectorAll("#alerts td")].map((td) => [td.dataset.label, Math.round(td.scrollWidth), td.textContent.trim().slice(0, 40)])
      .sort((a, b) => b[1] - a[1]).slice(0, 4) })));
  await browser.close();
})();
