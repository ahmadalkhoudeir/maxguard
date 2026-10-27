// Check 14: axe-core 4.14.0 (default rules, plus a run limited to wcag2a/wcag2aa/wcag21aa; the
// two result sets are merged) on every page, both modes, 1280 and 375 px.
// The store: the Telnet alert (uploaded) plus one alert of each severity, so every badge color is on the queue.
// Usage: node check14_axe.js <buildKey>
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const { AxeBuilder } = require(L_AXE());
const L = require("./lib.js");
function L_AXE() { return "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/tools/node/node_modules/@axe-core/playwright"; }
const KEY = process.argv[2];

(async () => {
  const browser = await chromium.launch();
  const results = await L.withServer(KEY, "c14", async (srv) => {
    L.addAlerts(srv.build, srv.data, ["critical", "high", "medium", "low", "info"], 140);
    const tid = await L.telnetId(srv.base);
    const pages = [["queue", "/"], ["upload", "/upload"], ["alert", "/alerts/" + tid],
                   ["404", "/alerts/0000000000000000"], ["400", "/?status=bogus"]];
    const out = [];
    for (const mode of ["analyst", "home"]) {
      for (const width of [1280, 375]) {
        const ctx = await browser.newContext({ viewport: { width, height: 900 } });
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
        const page = await ctx.newPage();
        const states = [...pages];
        for (const [name, p] of states) {
          await page.goto(srv.base + p);
          await L.sleep(700);  // the queue refreshes itself once after loading
          const seen = new Map();
          let version = null;
          let passes = 0;
          for (const builder of [new AxeBuilder({ page }), new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"])]) {
            const r = await builder.analyze();
            version = r.testEngine.version;
            passes = Math.max(passes, r.passes.length);
            for (const v of r.violations) {
              const prev = seen.get(v.id);
              if (!prev || prev.nodes < v.nodes.length) {
                seen.set(v.id, { id: v.id, impact: v.impact, nodes: v.nodes.length,
                  targets: v.nodes.slice(0, 4).map((n) => n.target.join(" ")),
                  summary: (v.nodes[0] && v.nodes[0].failureSummary || "").split("\n").slice(0, 2).join(" ").slice(0, 200) });
              }
            }
          }
          out.push({ page: name, path: p.replace(tid, "<telnet>"), mode, width, axe: version, rulesPassed: passes, violations: [...seen.values()] });
        }
        // Extra state: the alert page after a Save ("Saved.") in Analyst mode.
        if (mode === "analyst") {
          await page.goto(srv.base + "/alerts/" + tid);
          await page.fill("#actor", "Ahmad");
          await page.click("#status-form button[type=submit]");
          await page.waitForSelector("#status-form .message");
          const seen = new Map();
          for (const builder of [new AxeBuilder({ page }), new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"])]) {
            for (const v of (await builder.analyze()).violations) {
              seen.set(v.id, { id: v.id, impact: v.impact, nodes: v.nodes.length, targets: v.nodes.slice(0, 4).map((n) => n.target.join(" ")) });
            }
          }
          out.push({ page: "alert-after-save", path: "/alerts/<telnet>", mode, width, violations: [...seen.values()] });
        }
        await ctx.close();
      }
    }
    return out;
  });
  fs.writeFileSync(`${L.W}/results/check14-${KEY}.json`, JSON.stringify(results, null, 1));
  console.log(`== ${KEY} check 14 (axe ${results[0].axe}): ${results.length} page states`);
  for (const r of results) {
    console.log(`   ${r.mode} ${r.width} ${r.page}: ${r.violations.length ? r.violations.map((v) => `${v.id} (${v.impact}, ${v.nodes} nodes: ${v.targets.join(" ; ")})`).join(" | ") : "no violations"}`);
  }
  await browser.close();
})();
