"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  for (const [mode, path] of [["home", "/"], ["analyst", "/upload"]]) {
    const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
    await ctx.addCookies([{ name: "mg_mode", value: mode, url: BASE }]);
    const page = await ctx.newPage();
    await page.goto(BASE + path);
    const leaves = await page.evaluate(() => {
      const cw = document.documentElement.clientWidth;
      return [...document.querySelectorAll("body *")]
        .filter((e) => e.getBoundingClientRect().right > cw + 0.5 && e.children.length === 0)
        .map((e) => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
          return `${e.tagName}.${e.className} "${(e.textContent || "").trim().slice(0, 40)}" ` +
                 `left=${Math.round(r.left)} width=${Math.round(r.width)} right=${Math.round(r.right)} white-space=${cs.whiteSpace}`; });
    });
    console.log(`${mode} ${path} overflowing leaf elements:\n  ` + leaves.join("\n  "));
    await page.screenshot({ path: `../shot_${mode}_${path === "/" ? "queue" : "upload"}_375.png`, fullPage: true });
    await ctx.close();
  }
  await browser.close();
})();
