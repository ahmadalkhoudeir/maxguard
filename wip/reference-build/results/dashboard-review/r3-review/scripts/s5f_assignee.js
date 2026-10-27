// S5f: with an IPv6 alert in the table, does a short assignee ("Fiona") break mid-word
// when the Assignee column has overflow-wrap: anywhere (V7)? And what does V8 (Assignee
// break-word too) do with a 100-character name?
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const path = require("path");
const L = require("./lib");
const PY = path.join(L.VENV, "python");
const VARIANTS = {
  V7: `@media (min-width: 701px) { .stack td { overflow-wrap: break-word !important } .stack td.mono, .stack td[data-label="Assignee"] { overflow-wrap: anywhere !important } }`,
  V8: `@media (min-width: 701px) { .stack td { overflow-wrap: break-word !important } .stack td.mono { overflow-wrap: anywhere !important } }`,
};
const PROBE = () => {
  const out = [];
  for (const cell of document.querySelectorAll("#alerts td")) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const re = /\S+/g; let m;
      while ((m = re.exec(node.data))) {
        if (/[-\/]/.test(m[0]) || m[0].length > 30) continue;
        const range = document.createRange(); range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) out.push(m[0]);
      }
    }
  }
  return { broken: [...new Set(out)], scroll: document.documentElement.scrollWidth };
};
(async () => {
  const browser = await chromium.launch();
  const server = await L.startServer(process.argv[2] || "fixed-06");
  try {
    for (const name of ["telnet", "ftp", "plain_http", "cert_self_signed"]) await L.upload(server.port, name);
    execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.W, "tmp")]);
    const alerts = await L.alerts(server.port);
    const telnet = alerts.find((a) => a.dst_port === 23);
    const ftp = alerts.find((a) => a.dst_port === 21);
    for (const [phase, names] of [["short names", ["Fiona", "Jonattan"]], ["one 100-char name", ["N".repeat(100), "Fiona"]]]) {
      await L.patchAlert(server.port, telnet.finding_id, { actor: "test", assignee: names[0] });
      await L.patchAlert(server.port, ftp.finding_id, { actor: "test", assignee: names[1] });
      for (const font of ["default", "DejaVu Sans"]) for (const [variant, css] of Object.entries(VARIANTS)) {
        const scrolls = [], breaks = [];
        for (const width of [701, 720, 768, 834, 900, 1024, 1280]) {
          const ctx = await browser.newContext({ viewport: { width, height: 800 } });
          const page = await ctx.newPage();
          await page.goto(server.origin + "/");
          let text = css;
          if (font !== "default") text += ` html, body, input, button, select, label, .stack td::before { font-family: "${font}" !important }`;
          await page.evaluate((t) => { const s = new CSSStyleSheet(); s.replaceSync(t); document.adoptedStyleSheets = [...document.adoptedStyleSheets, s]; }, text);
          await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
          const r = await page.evaluate(PROBE);
          if (r.scroll > width) scrolls.push(`${width}->${r.scroll}`);
          if (r.broken.length) breaks.push(`${width}:${r.broken.join("/")}`);
          await ctx.close();
        }
        console.log(`${phase.padEnd(18)} ${font.padEnd(11)} ${variant} sideways: ${scrolls.join(" ") || "none"}; mid-word: ${breaks.join(" ") || "none"}`);
      }
    }
  } finally { await server.stop(); await browser.close(); await L.stopAll(); }
})();
