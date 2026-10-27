// Check 1: no sideways scrolling at phone width.
// Usage: node check01_width.js <buildKey...>   (O2 F2 O3 F3)
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const L = require("./lib.js");

const FONTS = ["default", "DejaVu Sans", "Liberation Sans", "Roboto", "Noto Sans"];
const WIDTHS = [320, 375];
const MODES = ["analyst", "home"];

async function measure(page) {
  return page.evaluate(() => {
    const cw = document.documentElement.clientWidth;
    const wide = [...document.querySelectorAll("body *")]
      .filter((e) => e.getBoundingClientRect().right > cw + 0.5 && e.children.length === 0)
      .map((e) => { const r = e.getBoundingClientRect();
        return `${e.tagName.toLowerCase()}${e.className ? "." + String(e.className).replace(/ /g, ".") : ""} "${(e.textContent || "").trim().slice(0, 40)}" right=${Math.round(r.right)}`; });
    return { scrollWidth: document.documentElement.scrollWidth, clientWidth: cw,
             innerWidth: window.innerWidth, wide: wide.slice(0, 4) };
  });
}

async function run(browser, srv, paths, label) {
  const rows = [];
  for (const mode of MODES) {
    for (const width of WIDTHS) {
      const ctx = await browser.newContext({ viewport: { width, height: 800 } });
      await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
      const page = await ctx.newPage();
      for (const p of paths) {
        for (const font of FONTS) {
          const resp = await page.goto(srv.base + p);
          if (font !== "default") {
            // page.addStyleTag is refused by the page's CSP (style-src 'self'); a constructed
            // stylesheet (CSSOM) applies the same rule with the CSP still on.
            await page.evaluate((f) => {
              const sheet = new CSSStyleSheet();
              sheet.replaceSync(`html, body, input, button, select, label { font-family: "${f}" !important }`);
              document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
            }, font);
          }
          await page.evaluate(() => document.fonts.ready);
          await page.waitForTimeout(150);
          const usedFont = await page.evaluate(() => getComputedStyle(document.body).fontFamily);
          const m = await measure(page);
          rows.push({ phase: label, mode, width, font, path: p, http: resp.status(), usedFont,
                      ...m, pass: m.scrollWidth === width && m.clientWidth === width });
        }
      }
      await ctx.close();
    }
  }
  return rows;
}

(async () => {
  const browser = await chromium.launch();
  const all = {};
  for (const key of process.argv.slice(2)) {
    all[key] = await L.withServer(key, "c01", async (srv) => {
      const tid = await L.telnetId(srv.base);
      const ahm03 = key.endsWith("3");
      const paths = ahm03
        ? ["/", "/upload", "/alerts/" + tid, "/alerts/0000000000000000", "/?status=bogus"]
        : ["/", "/upload", "/?status=bogus"];
      const rows = await run(browser, srv, paths, "A: Telnet alert only");
      // B: many alerts of every severity (4 of each, plus the Telnet alert).
      const sevs = [];
      for (const s of ["critical", "high", "medium", "low", "info"]) for (let i = 0; i < 4; i++) sevs.push(s);
      L.addAlerts(srv.build, srv.data, sevs, 20);
      const list = await L.alerts(srv.base);
      const rowsB = await run(browser, srv, ["/"], "B: queue with 21 alerts of every severity");
      // C (extra): the alert page of one alert per severity, in Home mode the badge is
      // bigger (.home-view .sev) and the words are the longest.
      let rowsC = [];
      if (ahm03) {
        const perSev = ["critical", "high", "medium", "low", "info"].map((s) => list.find((a) => a.severity === s && a.dst_ip.startsWith("10.9.20.")));
        rowsC = await run(browser, srv, perSev.map((a) => "/alerts/" + a.finding_id), "C (extra): alert page per severity");
        rowsC.forEach((r) => { r.severity = perSev.find((a) => r.path.endsWith(a.finding_id)).severity; });
      }
      // Screenshots: the Home queue at 375 px with all severities, the upload page at 320 px.
      for (const [mode, width, p, name] of [["home", 375, "/", "home-queue-375"], ["analyst", 320, "/upload", "upload-320"], ["home", 320, "/upload", "upload-320-home"]]) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 } });
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
        const page = await ctx.newPage();
        await page.goto(srv.base + p);
        await page.waitForTimeout(800);
        await page.screenshot({ path: `${L.W}/shots/${key}-${name}.png`, fullPage: true });
        await ctx.close();
      }
      return { rows: rows.concat(rowsB, rowsC), telnet: tid };
    });
    const rs = all[key].rows;
    const fails = rs.filter((r) => !r.pass);
    console.log(`== ${key}: ${rs.length} page loads, ${fails.length} with sideways scrolling`);
    const byPhase = {};
    for (const r of rs) { byPhase[r.phase] = byPhase[r.phase] || [0, 0]; byPhase[r.phase][0] += 1; if (!r.pass) byPhase[r.phase][1] += 1; }
    for (const [ph, [n, f]] of Object.entries(byPhase)) console.log(`   ${ph}: ${n} loads, ${f} fail`);
    const seen = new Set();
    for (const r of fails) {
      const k = `${r.phase}|${r.mode}|${r.path}`;
      if (seen.has(k + r.width + r.font)) continue;
      seen.add(k + r.width + r.font);
      console.log(`   FAIL ${r.phase.split(":")[0]} ${r.mode} ${r.width}px font=${r.font} ${r.path}${r.severity ? " (" + r.severity + ")" : ""}: scrollWidth=${r.scrollWidth} ` +
                  `(${r.wide.join(" | ")})`);
    }
    const maxSW = {};
    for (const r of rs) { const k = `${r.width}`; maxSW[k] = Math.max(maxSW[k] || 0, r.scrollWidth); }
    console.log(`   max scrollWidth per viewport width: ${JSON.stringify(maxSW)}; HTTP codes: ${JSON.stringify([...new Set(rs.map((r) => r.path.replace(/[0-9a-f]{16}/, "<id>") + "=" + r.http))])}`);
    console.log(`   fonts in use: ${JSON.stringify([...new Set(rs.map((r) => r.usedFont))])}`);
  }
  fs.writeFileSync(`${L.W}/results/check01-${process.argv.slice(2).join("-")}.json`, JSON.stringify(all, null, 1));
  await browser.close();
})();
