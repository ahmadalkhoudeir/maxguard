// axe-core on every page, both modes, with and without a saved name. Usage: node pw_axe.js <base-url>
"use strict";
const { chromium } = require("playwright");
const { AxeBuilder } = require("/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/tools/node/node_modules/@axe-core/playwright");
const BASE = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const alerts = await (await fetch(BASE + "/api/alerts")).json();
  const info = alerts.find((a) => a.severity === "info") || alerts[0];
  let total = 0;
  for (const mode of ["analyst", "home"]) {
    for (const actor of [null, "Ahmad"]) {
      for (const width of [375, 1280]) {
        const ctx = await browser.newContext({ viewport: { width, height: 900 } });
        const cookies = [{ name: "mg_mode", value: mode, url: BASE }];
        if (actor) cookies.push({ name: "mg_actor", value: actor, url: BASE });
        await ctx.addCookies(cookies);
        const page = await ctx.newPage();
        for (const path of ["/", "/upload", "/alerts/" + info.finding_id]) {
          await page.goto(BASE + path);
          const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
          total += r.violations.length;
          if (r.violations.length) console.log(mode, actor, width, path, JSON.stringify(r.violations.map((v) => [v.id, v.nodes.length])));
        }
        await ctx.close();
      }
    }
  }
  console.log("axe violations in total:", total);
  await browser.close();
})();
