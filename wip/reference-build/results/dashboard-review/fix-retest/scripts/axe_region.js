"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");
const { AxeBuilder } = require(L.SP + "/tools/node/node_modules/@axe-core/playwright");
(async () => {
  const s = await L.startServer("fixed-AHM-03", "axeregion");
  const browser = await chromium.launch();
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    const ctx = await browser.newContext({ viewport: { width: 375, height: 900 } });
    const page = await ctx.newPage();
    for (const p of ["/", "/upload", `/alerts/${id}`]) {
      await page.goto(s.base + p);
      await page.waitForTimeout(600);
      const before = (await new AxeBuilder({ page }).analyze()).violations.map((x) => x.id);
      await page.evaluate(() => {
        const note = document.querySelector(".privacy");
        const aside = document.createElement("aside");
        aside.setAttribute("aria-label", "Privacy");
        note.replaceWith(aside);
        aside.append(note);
      });
      const after = (await new AxeBuilder({ page }).analyze()).violations.map((x) => x.id);
      console.log(p.replace(id, "<id>"), "| as built:", before.join(",") || "none", "| privacy note in <aside aria-label=\"Privacy\">:", after.join(",") || "none");
    }
    await ctx.close();
  } finally { await browser.close(); await L.stopAll(); }
})();
