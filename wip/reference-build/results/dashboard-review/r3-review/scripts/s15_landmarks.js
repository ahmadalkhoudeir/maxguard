// S15: landmark order as a screen reader sees it, plus axe on the queue and alert pages.
// Usage: node s15_landmarks.js <build>
"use strict";
const { chromium } = require("playwright");
const { AxeBuilder } = require("/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/tools/node/node_modules/@axe-core/playwright");
const L = require("./lib");

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const alerts = await L.alerts(server.port);
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    const snap = await page.locator("body").ariaSnapshot();
    out.landmarks = snap.split("\n").filter((l) => /^- (banner|navigation|complementary|main|contentinfo|region|aside)/.test(l.trim()) || /^- (banner|navigation|complementary|main)/.test(l));
    out.topLevel = snap.split("\n").filter((l) => /^- /.test(l)).map((l) => l.slice(2, 70));
    let violations = [];
    for (const path of ["/", "/alerts/" + alerts[0].finding_id, "/upload", "/timeline?ip=172.18.0.3", "/assets"]) {
      await page.goto(server.origin + path);
      const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
      violations.push(`${path}: ${r.violations.map((v) => v.id + "x" + v.nodes.length).join(",") || "none"}`);
    }
    out.axe = violations;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2).length ? process.argv.slice(2) : ["fixed-06"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
