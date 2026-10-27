// F1 extra: a long unbroken assignee (an email address) in the queue card at phone widths.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

(async () => {
  const s = await L.startServer("fixed-AHM-03", "f1assignee");
  const browser = await chromium.launch();
  const out = [];
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    const assignee = "firstname.lastname@example-company.com";
    await L.patchAlert(s, id, { actor: "x", assignee });
    for (const extra of ["", " .stack td { overflow-wrap: anywhere; }"]) {
      for (const mode of ["analyst", "home"]) {
        const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
        if (mode === "home") await ctx.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
        const page = await ctx.newPage();
        for (const w of [320, 375, 414]) {
          await page.setViewportSize({ width: w, height: 800 });
          await page.goto(s.base + "/");
          await page.waitForTimeout(600);
          await L.setFont(page, null, extra + (mode === "home" ? " .stack td .sev { white-space: normal; }" : ""));
          const sw = await page.evaluate(() => document.documentElement.scrollWidth);
          out.push(`${extra ? "with overflow-wrap" : "as built"} | ${mode} | ${w}px | scrollWidth ${sw}`);
        }
        await ctx.close();
      }
    }
  } finally {
    await browser.close();
    await L.stopAll();
  }
  console.log(out.join("\n"));
})();
