// Screenshots for the guide: the Home queue at 375 px with one alert of every severity, and the
// upload page at 320 px (Analyst and Home). Also the page widths at the moment of the shot.
// Usage: node shots.js <buildKey...>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");

(async () => {
  const browser = await chromium.launch();
  for (const key of process.argv.slice(2)) {
    await L.withServer(key, "shots", async (srv) => {
      L.addAlerts(srv.build, srv.data, ["critical", "medium", "low", "info"], 160);  // + the Telnet alert (high)
      for (const [mode, width, p, name] of [["home", 375, "/", "home-queue-375-all-severities"],
                                            ["analyst", 320, "/upload", "upload-320-analyst"],
                                            ["home", 320, "/upload", "upload-320-home"]]) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 } });
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
        const page = await ctx.newPage();
        await page.goto(srv.base + p);
        await L.sleep(800);
        const m = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth,
          badges: [...document.querySelectorAll("#alerts .sev")].map((e) => e.textContent.trim()) }));
        const file = `${L.W}/shots/${key}-${name}.png`;
        await page.screenshot({ path: file, fullPage: true });
        console.log(`${key} ${name}: viewport ${width}, scrollWidth ${m.scrollWidth}${m.badges.length ? ", badges " + JSON.stringify(m.badges) : ""} -> ${file}`);
        await ctx.close();
      }
    });
  }
  await browser.close();
})();
