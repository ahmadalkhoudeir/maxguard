// S5e: sideways scroll and mid-word breaks across widths, fonts, modes; shipped vs V6 vs V7.
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const path = require("path");
const L = require("./lib");
const PY = path.join(L.VENV, "python");
const VARIANTS = {
  shipped: "",
  V6: `@media (min-width: 701px) { .stack td { overflow-wrap: break-word !important } .stack td.mono, .stack td[data-label="Assignee"] { overflow-wrap: anywhere !important } .sev { white-space: nowrap !important } }`,
  V7: `@media (min-width: 701px) { .stack td { overflow-wrap: break-word !important } .stack td.mono, .stack td[data-label="Assignee"] { overflow-wrap: anywhere !important } }`,
};
const WIDTHS = [320, 340, 360, 375, 414, 700, 701, 720, 768, 800, 834, 900, 1024, 1280];
const PROBE = () => {
  const out = [];
  for (const cell of document.querySelectorAll("#alerts td")) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const re = /\S+/g; let m;
      while ((m = re.exec(node.data))) {
        if (/[-\/]/.test(m[0]) || m[0].length > 30) continue;   // hyphen/slash breaks are ordinary; long tokens are meant to wrap
        const range = document.createRange(); range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) out.push(m[0]);
      }
    }
  }
  return { broken: [...new Set(out)], scroll: document.documentElement.scrollWidth, font: getComputedStyle(document.body).fontFamily };
};
(async () => {
  const browser = await chromium.launch();
  const server = await L.startServer(process.argv[2] || "fixed-06");
  try {
    for (const name of ["telnet", "ftp", "plain_http", "cert_self_signed"]) await L.upload(server.port, name);
    const alerts = await L.alerts(server.port);
    const telnet = alerts.find((a) => a.dst_port === 23);
    for (const phase of ["common", "stress"]) {
      if (phase === "stress") {
        execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.R, "tmp")]);
        await L.patchAlert(server.port, telnet.finding_id, { actor: "test", assignee: "N".repeat(100) });
      }
      for (const mode of ["analyst", "home"]) for (const font of ["default", "DejaVu Sans"]) for (const [variant, css] of Object.entries(VARIANTS)) {
        const scrolls = [], breaks = [];
        for (const width of WIDTHS) {
          const ctx = await browser.newContext({ viewport: { width, height: 800 } });
          await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin }]);
          const page = await ctx.newPage();
          await page.goto(server.origin + "/");
          let text = css;
          if (font !== "default") text += ` html, body, input, button, select, label, .stack td::before { font-family: "${font}" !important }`;
          if (text) {
            await page.evaluate((t) => { const s = new CSSStyleSheet(); s.replaceSync(t); document.adoptedStyleSheets = [...document.adoptedStyleSheets, s]; }, text);
            await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
          }
          const r = await page.evaluate(PROBE);
          if (font !== "default" && !r.font.includes("DejaVu")) throw new Error("font not applied: " + r.font);
          if (r.scroll > width) scrolls.push(`${width}->${r.scroll}`);
          if (r.broken.length) breaks.push(`${width}:${r.broken.join("/")}`);
          await ctx.close();
        }
        console.log(`${phase.padEnd(6)} ${mode.padEnd(7)} ${font.padEnd(11)} ${variant.padEnd(7)} sideways: ${scrolls.join(" ") || "none"}; mid-word: ${breaks.join(" ") || "none"}`);
      }
    }
  } finally { await server.stop(); await browser.close(); await L.stopAll(); }
})();
