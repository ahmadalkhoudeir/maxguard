// The two overflows left in the fixed AHM-03 build, with and without a proposed two-rule CSS
// change (applied through a constructed stylesheet; the page's CSP stays on):
//   .banner { overflow-wrap: anywhere; }          the "AI not available" reason is one long token
//   .home-view .sev { white-space: normal; }      "Info: nothing to fix, good to know" in Home mode
// Usage: node residual_fix.js <buildKey>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");
const KEY = process.argv[2];
const FONTS = ["default", "DejaVu Sans", "Liberation Sans", "Roboto", "Noto Sans"];
const CSS = ".banner { overflow-wrap: anywhere; } .home-view .sev { white-space: normal; }";

async function apply(page, font, fix) {
  await page.evaluate(([f, css]) => {
    const sheets = [];
    if (f !== "default") { const s = new CSSStyleSheet(); s.replaceSync(`html, body, input, button, select, label { font-family: "${f}" !important }`); sheets.push(s); }
    if (css) { const s = new CSSStyleSheet(); s.replaceSync(css); sheets.push(s); }
    document.adoptedStyleSheets = [...document.adoptedStyleSheets, ...sheets];
  }, [font, fix ? CSS : ""]);
  await page.waitForTimeout(100);
  return page.evaluate(() => document.documentElement.scrollWidth);
}

(async () => {
  const browser = await chromium.launch();
  await L.withServer(KEY, "resid", async (srv) => {
    L.addAlerts(srv.build, srv.data, ["critical", "high", "medium", "low", "info"], 170);
    const list = await L.alerts(srv.base);
    const tid = await L.telnetId(srv.base);
    const targets = [["analyst", "/alerts/" + tid, "Telnet (AI banner)"]].concat(
      ["critical", "high", "medium", "low", "info"].map((s) => ["home", "/alerts/" + list.find((a) => a.severity === s && a.dst_ip.startsWith("10.9.170.")).finding_id, s]),
      [["home", "/alerts/" + tid, "Telnet (home)"]]);
    const rows = { without: 0, with: 0, total: 0, detail: [] };
    for (const width of [320, 375]) {
      for (const [mode, p, label] of targets) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 } });
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
        const page = await ctx.newPage();
        for (const font of FONTS) {
          await page.goto(srv.base + p);
          const before = await apply(page, font, false);
          await page.goto(srv.base + p);
          const after = await apply(page, font, true);
          rows.total += 1;
          if (before !== width) rows.without += 1;
          if (after !== width) rows.with += 1;
          if (before !== width || after !== width) rows.detail.push(`${width}px ${mode} ${label} font=${font}: without ${before}, with ${after}`);
        }
        await ctx.close();
      }
    }
    console.log(`== ${KEY}: ${rows.total} page loads; wider than the viewport without the CSS change: ${rows.without}; with it: ${rows.with}`);
    for (const d of rows.detail) console.log("   " + d);
  });
  await browser.close();
})();
