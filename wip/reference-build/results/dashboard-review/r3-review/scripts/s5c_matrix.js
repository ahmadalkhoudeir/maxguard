// S5c: candidate CSS fixes for the mid-word breaks, injected through CSSOM (the CSP
// refuses addStyleTag). Queue with IPv4 + one IPv6 alert + one 100-character assignee
// without spaces, at 1280/1024/768/375. Usage: node s5c_matrix.js <build>
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const path = require("path");
const L = require("./lib");

const PY = path.join(L.VENV, "python");
const DESKTOP = (css) => `@media (min-width: 701px) { ${css} }`;
const VARIANTS = {
  shipped: "",
  "V1 break-word on desktop": DESKTOP(".stack td { overflow-wrap: break-word !important }"),
  "V2 shipped + .sev nowrap on desktop": DESKTOP(".sev { white-space: nowrap !important }"),
  "V3 word-break: break-word on desktop": DESKTOP(".stack td { overflow-wrap: normal !important; word-break: break-word !important }"),
  "V4 break-word + assignee anywhere + .sev nowrap (desktop)": DESKTOP(
    ".stack td { overflow-wrap: break-word !important } .stack td[data-label=\"Assignee\"] { overflow-wrap: anywhere !important } .sev { white-space: nowrap !important }"),
  "V5 table-layout fixed (desktop)": DESKTOP(".stack { table-layout: fixed }"),
};

const BROKEN = () => {
  const out = [];
  for (const cell of document.querySelectorAll("#alerts td")) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const re = /\S+/g;
      let m;
      while ((m = re.exec(node.data))) {
        const range = document.createRange();
        range.setStart(node, m.index);
        range.setEnd(node, m.index + m[0].length);
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) out.push(m[0].length > 12 ? m[0].slice(0, 10) + "…" : m[0]);
      }
    }
  }
  const uniq = [...new Set(out)];
  return {
    brokenWords: uniq.join(" | ") || "none",
    pageWidens: document.documentElement.scrollWidth > innerWidth ? `YES (${document.documentElement.scrollWidth} > ${innerWidth})` : "no",
    tableHeight: document.querySelector("#alerts table").getBoundingClientRect().height,
  };
};

async function run(buildName, browser) {
  const server = await L.startServer(buildName);
  try {
    for (const name of ["telnet", "ftp", "plain_http", "cert_self_signed"]) await L.upload(server.port, name);
    execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.W, "tmp")]);
    const alerts = await L.alerts(server.port);
    const telnet = alerts.find((a) => a.dst_port === 23);
    await L.patchAlert(server.port, telnet.finding_id, { actor: "test", assignee: "N".repeat(100) });
    for (const [name, css] of Object.entries(VARIANTS)) {
      const row = {};
      for (const width of [1280, 1024, 768, 375]) {
        const ctx = await browser.newContext({ viewport: { width, height: 1000 } });
        const page = await ctx.newPage();
        await page.goto(server.origin + "/");
        if (css) {
          await page.evaluate((text) => {
            const s = new CSSStyleSheet();
            s.replaceSync(text);
            document.adoptedStyleSheets = [...document.adoptedStyleSheets, s];
          }, css);
          await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
        }
        row[width] = await page.evaluate(BROKEN);
        if (width === 1280 || width === 768) await page.screenshot({ path: path.join(L.W, "shots", `matrix-${name.slice(0, 2).trim()}-${width}.png`), fullPage: true });
        await ctx.close();
      }
      console.log(`${name}`);
      for (const [w, r] of Object.entries(row)) console.log(`   ${w.padStart(4)}px  widens=${r.pageWidens.padEnd(16)} broken: ${r.brokenWords}`);
    }
  } finally {
    await server.stop();
  }
}

(async () => {
  const browser = await chromium.launch();
  try {
    await run(process.argv[2] || "fixed-06", browser);
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
