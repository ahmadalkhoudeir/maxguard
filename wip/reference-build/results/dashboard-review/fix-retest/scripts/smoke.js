"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

(async () => {
  const s = await L.startServer("fixed-AHM-03", "smoke");
  try {
    for (const f of ["telnet", "ftp"]) console.log(f, await L.upload(s, f));
    const list = await L.alerts(s);
    console.log(list.map((a) => [a.rule_id, a.severity, a.title, a.last_seen, a.finding_id]));
    const browser = await chromium.launch();
    const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
    const page = await ctx.newPage();
    const recs = [];
    const rec = L.instrument(page, "smoke", recs);
    await page.goto(s.base + "/upload");
    const fam = () => page.evaluate(() => getComputedStyle(document.body).fontFamily);
    const used = () => page.evaluate(() => document.documentElement.scrollWidth);
    console.log("default", await fam(), await used());
    let tagErr = null;
    try {
      await page.addStyleTag({ content: 'html, body, input, button, select, label { font-family: "Liberation Sans" !important }' });
    } catch (e) { tagErr = String(e).split("\n")[0]; }
    console.log("addStyleTag error:", tagErr, "body font after addStyleTag:", await fam());
    await L.setFont(page, "Liberation Sans");
    console.log("after adoptedStyleSheets:", await fam(), await used());
    console.log("console errors:", rec.consoleErrors);
    await browser.close();
  } finally {
    await L.stopAll();
  }
})();
