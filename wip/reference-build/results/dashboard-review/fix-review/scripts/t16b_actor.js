// T16b: long actor name (100 characters, no spaces) in the status form at 375 px, with and
// without overflow-wrap on the banner and the form's "recorded as" line.
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
const LONG = "Wolfeschlegelsteinhausenbergerdorffwelchevoralternwarengewissenhaftschaferswessenschafewarenwohlgepf";
(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of ["orig-03", "fixed-03"]) {
      const server = await L.startServer(b);
      try {
        await L.upload(server.port, "telnet");
        const [alert] = await L.alerts(server.port);
        const ctx = await browser.newContext({ viewport: { width: 375, height: 800 }, bypassCSP: true });
        await ctx.addCookies([{ name: "mg_actor", value: LONG, url: server.origin }]);
        const page = await ctx.newPage();
        await page.goto(`${server.origin}/alerts/${alert.finding_id}`);
        const hs = () => page.evaluate(() => document.scrollingElement.scrollWidth - document.documentElement.clientWidth);
        const r = { build: b, actorChars: LONG.length, hscroll: await hs() };
        await page.addStyleTag({ content: ".banner { overflow-wrap: anywhere; }" });
        r.withBannerRule = await hs();
        await page.addStyleTag({ content: ".status-form .muted { overflow-wrap: anywhere; }" });
        r.withBothRules = await hs();
        r.saveButtonWidth = await page.evaluate(() => Math.round(document.querySelector("#status-form button").getBoundingClientRect().width));
        console.log(JSON.stringify(r));
        await ctx.close();
      } finally { await server.stop(); }
    }
  } finally { await browser.close(); await L.stopAll(); }
})();
