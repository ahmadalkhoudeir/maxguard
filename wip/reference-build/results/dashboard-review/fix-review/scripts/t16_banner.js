// T16: the alert page at 320/375 px when the local AI is unreachable (pre-existing):
// horizontal scroll from the banner's reason text, and with .banner { overflow-wrap: anywhere }.
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
(async () => {
  const browser = await chromium.launch();
  const server = await L.startServer("fixed-03");
  try {
    await L.upload(server.port, "telnet");
    const [alert] = await L.alerts(server.port);
    for (const w of [375, 320]) {
      const ctx = await browser.newContext({ viewport: { width: w, height: 800 }, bypassCSP: true });
      const page = await ctx.newPage();
      await page.goto(`${server.origin}/alerts/${alert.finding_id}`);
      const banner = (await page.textContent(".banner")).replace(/\s+/g, " ").trim().slice(0, 120);
      const before = await page.evaluate(() => document.scrollingElement.scrollWidth - document.documentElement.clientWidth);
      await page.addStyleTag({ content: ".banner { overflow-wrap: anywhere; }" });
      const after = await page.evaluate(() => document.scrollingElement.scrollWidth - document.documentElement.clientWidth);
      console.log(JSON.stringify({ width: w, banner, hscrollPx: before, withOverflowWrap: after }));
      await ctx.close();
    }
  } finally {
    await server.stop(); await browser.close(); await L.stopAll();
  }
})();
