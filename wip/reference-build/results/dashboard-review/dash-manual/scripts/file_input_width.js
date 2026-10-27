// Why is the file input 365 px wide? Measure its font and its width with other fonts.
"use strict";
const { chromium } = require("playwright");
const [BASE] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const out = { chromium: browser.version(), runs: [] };
  for (const family of [null, "Liberation Sans", "DejaVu Sans Condensed", "Liberation Sans Narrow"]) {
    const context = await browser.newContext({ viewport: { width: 375, height: 700 }, bypassCSP: true });
    const page = await context.newPage();
    await page.goto(BASE + "/upload", { waitUntil: "load" });
    if (family) await page.addStyleTag({ content: `#file { font-family: "${family}" !important; }` });
    out.runs.push(await page.evaluate((family) => {
      const input = document.getElementById("file");
      const cs = getComputedStyle(input);
      const ctx = document.createElement("canvas").getContext("2d");
      ctx.font = cs.fontSize + " " + cs.fontFamily;
      const zero = ctx.measureText("0").width;
      return { fontOverride: family, fontFamily: cs.fontFamily, fontSize: cs.fontSize,
               widthOfZero: +zero.toFixed(2), thirtyFourZeros: +(34 * zero).toFixed(1),
               inputWidth: input.getBoundingClientRect().width,
               scrollWidth: document.documentElement.scrollWidth };
    }, family));
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out, null, 1));
})();
