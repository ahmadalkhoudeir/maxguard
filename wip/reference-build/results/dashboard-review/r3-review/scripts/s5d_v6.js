// S5d: the refined CSS fix (V6) in analyst and home mode, stress content and common content.
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const path = require("path");
const L = require("./lib");
const PY = path.join(L.VENV, "python");
const V6 = `@media (min-width: 701px) {
  .stack td { overflow-wrap: break-word !important }
  .stack td.mono, .stack td[data-label="Assignee"] { overflow-wrap: anywhere !important }
  .sev { white-space: nowrap !important }
}`;
const BROKEN = () => {
  const out = [];
  for (const cell of document.querySelectorAll("main td")) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const re = /\S+/g; let m;
      while ((m = re.exec(node.data))) {
        const range = document.createRange(); range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) out.push(m[0].length > 12 ? m[0].slice(0, 10) + "…" : m[0]);
      }
    }
  }
  return { broken: [...new Set(out)].join(" | ") || "none",
    widens: document.documentElement.scrollWidth > innerWidth ? `YES (${document.documentElement.scrollWidth})` : "no" };
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
        execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.W, "tmp")]);
        await L.patchAlert(server.port, telnet.finding_id, { actor: "test", assignee: "N".repeat(100) });
      }
      for (const mode of ["analyst", "home"]) {
        for (const variant of ["shipped", "V6"]) {
          const line = [];
          for (const width of [1280, 1024, 768, 375]) {
            const ctx = await browser.newContext({ viewport: { width, height: 1000 } });
            await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin }]);
            const page = await ctx.newPage();
            const results = {};
            for (const [label, url] of [["queue", "/"], ["timeline", "/timeline?ip=172.18.0.3&end=" + (Math.floor(telnet.last_seen) + 1)], ["assets", "/assets"]]) {
              await page.goto(server.origin + url);
              if (variant === "V6") {
                await page.evaluate((text) => { const s = new CSSStyleSheet(); s.replaceSync(text); document.adoptedStyleSheets = [...document.adoptedStyleSheets, s]; }, V6);
                await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
              }
              results[label] = await page.evaluate(BROKEN);
              if (label === "queue" && variant === "V6" && mode === "home" && (width === 768 || width === 375)) await page.screenshot({ path: path.join(L.W, "shots", `v6-home-${phase}-${width}.png`), fullPage: true });
            }
            line.push(`${width}: ` + Object.entries(results).map(([k, r]) => `${k}[${r.widens === "no" ? "" : "WIDENS "}${r.broken}]`).join(" "));
            await ctx.close();
          }
          console.log(`${phase} ${mode} ${variant}\n   ` + line.join("\n   "));
        }
      }
    }
  } finally { await server.stop(); await browser.close(); await L.stopAll(); }
})();
