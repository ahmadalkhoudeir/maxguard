// Home-mode queue and alert page: sideways scroll across widths (default font, DejaVu Sans).
// Usage: node pw_home_widths.js <base-url>
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const alerts = await (await fetch(BASE + "/api/alerts")).json();
  const info = alerts.find((a) => a.severity === "info");
  for (const font of ["default", "DejaVu Sans"]) {
    for (const [label, path] of [["queue /", "/"], ["alert page (info)", "/alerts/" + info.finding_id]]) {
      const bad = [];
      for (const width of [320, 340, 360, 375, 414, 700, 701, 720, 768, 800, 820, 834, 850, 900, 1024]) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 }, bypassCSP: true });
        await ctx.addCookies([{ name: "mg_mode", value: "home", url: BASE }]);
        const page = await ctx.newPage();
        await page.goto(BASE + path);
        if (font !== "default") await page.addStyleTag({ content: `html, body, input, button, select, label { font-family: "${font}" !important }` });
        const sw = await page.evaluate(() => document.documentElement.scrollWidth);
        if (sw > width) bad.push(`${width}px->${sw}`);
        await ctx.close();
      }
      console.log(`[${font}] Home ${label}: sideways scroll at ${bad.length ? bad.join(", ") : "no width tested"}`);
    }
  }
  await browser.close();
})();
