// S5: where does overflow-wrap: anywhere break a word (an IP address, a record ID, a
// UID, a MAC) in the middle? Queue, alert page (evidence table), timeline and devices,
// at 375, 768 and 1280 px, original build vs fixed. Usage: node s5_css.js <build>...
"use strict";
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const path = require("path");
const L = require("./lib");

const PY = path.join(L.VENV, "python");

// For every cell matching `selector`: the words (split on spaces) that span more than one
// line, i.e. were broken in the middle. Returns [{cell, lines, brokenWords}] for cells with any.
const BROKEN = (selector) => {
  const out = [];
  for (const cell of document.querySelectorAll(selector)) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    const broken = [];
    let tops = new Set();
    let node;
    while ((node = walker.nextNode())) {
      const text = node.data;
      const re = /\S+/g;
      let m;
      while ((m = re.exec(text))) {
        const range = document.createRange();
        range.setStart(node, m.index);
        range.setEnd(node, m.index + m[0].length);
        const wordTops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        wordTops.forEach((t) => tops.add(t));
        if (wordTops.size > 1) broken.push(`${m[0]} (${wordTops.size} lines)`);
      }
    }
    if (broken.length) out.push({ cell: (cell.getAttribute("data-label") || cell.className || cell.tagName) + ": " + cell.textContent.trim().slice(0, 40), lines: tops.size, broken });
  }
  return out;
};

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const v6 = execFileSync(PY, ["-I", path.join(__dirname, "add_ipv6.py"), server.build, server.dataDir, path.join(L.W, "tmp")]).toString().trim();
    const alerts = await L.alerts(server.port);
    const v6alert = alerts.find((a) => a.src_ip.includes(":"));
    const telnet = alerts.find((a) => a.dst_port === 23);
    for (const width of [375, 768, 1280]) {
      const ctx = await browser.newContext({ viewport: { width, height: 1000 } });
      const page = await ctx.newPage();
      const res = {};
      await page.goto(server.origin + "/");
      res.queue = await page.evaluate(BROKEN, "#alerts td");
      res.queueScrollWidth = await page.evaluate(() => document.documentElement.scrollWidth + " vs " + innerWidth);
      for (const [name, a] of [["alertTelnet", telnet], ["alertV6", v6alert]]) {
        await page.goto(server.origin + "/alerts/" + a.finding_id);
        res[name + "_facts"] = await page.evaluate(BROKEN, ".facts dd");
        res[name + "_evidence"] = await page.evaluate(BROKEN, "section[aria-labelledby='ev-heading'] td");
        res[name + "_evidenceTableScroll"] = await page.evaluate(() => { const w = document.querySelector(".table-wrap"); return w.scrollWidth + " in " + w.clientWidth; });
      }
      await page.goto(server.origin + "/timeline?ip=" + encodeURIComponent(v6alert.src_ip) + "&end=" + (Math.floor(v6alert.last_seen) + 1));
      res.timeline = await page.evaluate(BROKEN, "table td");
      await page.goto(server.origin + "/assets");
      res.assets = await page.evaluate(BROKEN, "table td");
      out[width] = res;
      await ctx.close();
    }
    out.v6 = v6;
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2).length ? process.argv.slice(2) : ["orig-all", "fixed-06"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
