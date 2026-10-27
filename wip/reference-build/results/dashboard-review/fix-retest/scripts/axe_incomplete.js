"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");
const { AxeBuilder } = require(L.SP + "/tools/node/node_modules/@axe-core/playwright");
(async () => {
  const s = await L.startServer("fixed-AHM-03", "axeinc");
  const browser = await chromium.launch();
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    for (const extra of ["", " .banner { overflow-wrap: anywhere; }"]) {
      const ctx = await browser.newContext({ viewport: { width: 375, height: 900 } });
      const page = await ctx.newPage();
      await page.goto(`${s.base}/alerts/${id}`);
      if (extra) await L.setFont(page, null, extra);
      const r = await new AxeBuilder({ page }).analyze();
      for (const x of r.incomplete) for (const n of x.nodes) console.log(extra ? "with banner fix:" : "as built:", x.id, n.target.join(" "), "|", (n.any[0] || {}).message);
      console.log(extra ? "with banner fix:" : "as built:", "incomplete ids:", r.incomplete.map((x) => x.id).join(",") || "none", "| violations:", r.violations.map((x) => x.id).join(","));
      await ctx.close();
    }
  } finally { await browser.close(); await L.stopAll(); }
})();
