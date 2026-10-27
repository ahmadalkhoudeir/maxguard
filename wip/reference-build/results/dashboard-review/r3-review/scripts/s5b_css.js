// S5b: mid-word breaks, before and after an IPv6 alert joins the queue, with screenshots.
// Usage: node s5b_css.js <build>...   (writes logs/s5b-<build>.json and shots/*.png)
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const L = require("./lib");

const PY = path.join(L.VENV, "python");
const SHOTS = path.join(L.W, "shots");
fs.mkdirSync(SHOTS, { recursive: true });

const BROKEN = (selector) => {
  const out = [];
  for (const cell of document.querySelectorAll(selector)) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    const broken = [];
    let node;
    while ((node = walker.nextNode())) {
      const re = /\S+/g;
      let m;
      while ((m = re.exec(node.data))) {
        const range = document.createRange();
        range.setStart(node, m.index);
        range.setEnd(node, m.index + m[0].length);
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) broken.push(m[0]);
      }
    }
    if (broken.length) out.push((cell.getAttribute("data-label") || cell.className || cell.tagName) + " -> " + broken.join(" | "));
  }
  return out;
};

async function measure(browser, origin, label, alerts) {
  const res = {};
  for (const width of [375, 768, 1024, 1280]) {
    const ctx = await browser.newContext({ viewport: { width, height: 1000 } });
    const page = await ctx.newPage();
    await page.goto(origin + "/");
    const r = { queue: await page.evaluate(BROKEN, "#alerts td") };
    if (width >= 768) await page.screenshot({ path: path.join(SHOTS, `${label}-queue-${width}.png`), fullPage: true });
    const telnet = alerts.find((a) => a.dst_port === 23);
    await page.goto(origin + "/alerts/" + telnet.finding_id);
    r.evidenceTelnet = await page.evaluate(BROKEN, "section[aria-labelledby='ev-heading'] td");
    if (width === 375) await page.screenshot({ path: path.join(SHOTS, `${label}-alert-375.png`), fullPage: true });
    await page.goto(origin + "/assets");
    r.assets = await page.evaluate(BROKEN, "table td");
    await page.goto(origin + "/timeline?ip=172.18.0.3&end=" + (Math.floor(telnet.last_seen) + 1));
    r.timeline = await page.evaluate(BROKEN, "table td");
    res[width] = r;
    await ctx.close();
  }
  return res;
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    for (const name of ["telnet", "ftp", "plain_http", "cert_self_signed"]) await L.upload(server.port, name);
    let alerts = await L.alerts(server.port);
    out.ipv4only = await measure(browser, server.origin, buildName + "-v4", alerts);
    execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.W, "tmp")]);
    alerts = await L.alerts(server.port);
    out.withIpv6 = await measure(browser, server.origin, buildName + "-v6", alerts);
  } finally {
    await server.stop();
  }
  fs.writeFileSync(path.join(L.W, "logs", `s5b-${buildName}.json`), JSON.stringify(out, null, 1));
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2).length ? process.argv.slice(2) : ["orig-all", "fixed-06"]) {
      const out = await run(b, browser);
      console.log(JSON.stringify(out, null, 1));
    }
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
