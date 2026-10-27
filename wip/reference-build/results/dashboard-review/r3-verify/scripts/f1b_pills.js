// F1 (overflow-wrap: anywhere): do the severity pills and other short words break mid-word
// on the queue page? Shipped CSS only, default font, Analyst and Home mode.
// Phase "ipv4": telnet, ftp, plain_http, cert_self_signed. Phase "ipv6": one IPv6 alert added.
// Usage: node f1b_pills.js <build>...
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const path = require("path");
const L = require("./lib");
const PY = path.join(L.VENV, "python");
const WIDTHS = [701, 768, 1024, 1280, 1440];

const PROBE = () => {
  const broken = [];
  for (const cell of document.querySelectorAll("#alerts td")) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const re = /\S+/g; let m;
      while ((m = re.exec(node.data))) {
        if (/[-\/]/.test(m[0]) || m[0].length > 30) continue;
        const range = document.createRange(); range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) broken.push(`${cell.dataset.label}:${m[0]}`);
      }
    }
  }
  const pills = [...document.querySelectorAll("#alerts .sev")].map((p) => {
    const range = document.createRange(); range.selectNodeContents(p);
    const lines = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top))).size;
    return `${p.textContent}:${lines}line${lines === 1 ? "" : "s"}`;
  });
  const sevCol = document.querySelector("#alerts td[data-label=Severity]");
  return { broken: [...new Set(broken)], pills, sevColWidth: sevCol ? Math.round(sevCol.getBoundingClientRect().width) : null,
    font: getComputedStyle(document.body).fontFamily, scroll: document.documentElement.scrollWidth,
    tableWidth: Math.round(document.querySelector("#alerts table").getBoundingClientRect().width) };
};

async function run(buildName, browser) {
  const server = await L.startServer(buildName);
  try {
    for (const name of ["telnet", "ftp", "plain_http", "cert_self_signed"]) await L.upload(server.port, name);
    for (const phase of ["ipv4", "ipv6"]) {
      if (phase === "ipv6") {
        const r = execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.R, "tmp")], { encoding: "utf8" });
        console.log(`  added IPv6 alert: ${r.trim()}`);
      }
      for (const mode of ["analyst", "home"]) {
        for (const width of WIDTHS) {
          const ctx = await browser.newContext({ viewport: { width, height: 900 } });
          await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin }]);
          const page = await ctx.newPage();
          await page.goto(server.origin + "/");
          await page.waitForSelector("#alerts table");
          const r = await page.evaluate(PROBE);
          const flag = r.broken.length ? "  <-- MID-WORD BREAK" : "";
          console.log(`${buildName} ${phase} ${mode.padEnd(7)} ${String(width).padEnd(4)} pills=${r.pills.join(",")} sevCol=${r.sevColWidth}px table=${r.tableWidth}px scroll=${r.scroll} broken=${JSON.stringify(r.broken)}${flag}`);
          if (mode === "analyst" && (width === 768 || width === 1280 || width === 1024)) {
            await page.screenshot({ path: path.join(L.R, "shots", `${buildName}-${phase}-${mode}-${width}.png`), fullPage: false });
          }
          await ctx.close();
        }
      }
    }
  } finally { await server.stop(); }
}

(async () => {
  const browser = await chromium.launch();
  console.log("Chromium", browser.version());
  try {
    for (const b of process.argv.slice(2)) await run(b, browser);
  } finally { await browser.close(); await L.stopAll(); }
})();
