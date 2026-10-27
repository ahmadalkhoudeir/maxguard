// axe on every AHM-03 page, both modes, 1280 and 375 px: default rules, then the
// wcag2a + wcag2aa + wcag21aa tags; violations are the union of the two runs.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");
const { AxeBuilder } = require(L.SP + "/tools/node/node_modules/@axe-core/playwright");

async function runBuild(browser, buildName, records) {
  const s = await L.startServer(buildName, "axe");
  const rows = [];
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    const pages = ["/", "/upload", `/alerts/${id}`, "/alerts/0000000000000000", "/?status=bogus", "SAVED"];
    for (const mode of ["analyst", "home"]) {
      for (const width of [1280, 375]) {
        const ctx = await browser.newContext({ viewport: { width, height: 900 } });
        if (mode === "home") await ctx.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
        const page = await ctx.newPage();
        L.instrument(page, `${buildName} axe ${mode} ${width}`, records);
        for (const p of pages) {
          if (p === "SAVED" && mode === "home") continue;  // Home mode has no status form
          let label = p.replace(id, "<telnet id>");
          if (p === "SAVED") {
            label = "/alerts/<telnet id> after Save";
            await page.goto(`${s.base}/alerts/${id}`);
            if (await page.$("#actor")) await page.fill("#actor", "Ahmad");
            await page.selectOption("#alert-status", "investigating");
            await page.click("#status-form button[type=submit]");
            await page.waitForSelector("#status-form .message");
          } else {
            const first = p === "/" ? page.waitForResponse((r) => r.url().includes("/?status="), { timeout: 4000 }).catch(() => null) : null;
            await page.goto(s.base + p);
            if (first) await first;
          }
          await page.waitForTimeout(300);
          const def = await new AxeBuilder({ page }).analyze();
          const tagged = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
          const v = new Map();
          for (const [run, r] of [["default", def], ["tags", tagged]]) {
            for (const x of r.violations) {
              const prev = v.get(x.id) || { id: x.id, impact: x.impact, nodes: 0, runs: [], targets: [] };
              prev.nodes = Math.max(prev.nodes, x.nodes.length);
              prev.runs.push(run);
              prev.targets = x.nodes.map((n) => n.target.join(" ")).slice(0, 4);
              prev.help = x.help;
              v.set(x.id, prev);
            }
          }
          rows.push({ build: buildName, page: label, mode, width, violations: [...v.values()],
            passes: def.passes.length, incomplete: def.incomplete.map((x) => x.id), rulesRunTags: tagged.passes.length + tagged.violations.length + tagged.incomplete.length + tagged.inapplicable.length });
        }
        await ctx.close();
      }
    }
  } finally {
    await L.stopServer(s);
  }
  return rows;
}

(async () => {
  const browser = await chromium.launch();
  const records = [];
  let all = [];
  try {
    const res = await Promise.all(["fixed-AHM-03", "orig-AHM-03"].map((b) => runBuild(browser, b, records)));
    all = res.flat();
  } finally {
    await browser.close();
    await L.stopAll();
  }
  L.writeJSON("axe.json", all);
  for (const r of all) {
    const v = r.violations.map((x) => `${x.id} (${x.impact}, ${x.nodes} node${x.nodes === 1 ? "" : "s"}${x.runs.length === 1 ? ", " + x.runs[0] + " only" : ""})`).join("; ");
    console.log(`${r.build} | ${r.page} | ${r.mode} | ${r.width} | ${v || "none"} | incomplete: ${r.incomplete.join(",") || "-"}`);
  }
  const key = (r) => `${r.page}|${r.mode}|${r.width}`;
  const orig = new Map(all.filter((r) => r.build === "orig-AHM-03").map((r) => [key(r), r]));
  const newOnes = [];
  for (const r of all.filter((x) => x.build === "fixed-AHM-03")) {
    const o = orig.get(key(r));
    for (const x of r.violations) {
      const ox = o && o.violations.find((y) => y.id === x.id);
      if (!ox || ox.nodes < x.nodes) newOnes.push(`${key(r)} ${x.id} fixed ${x.nodes} vs orig ${ox ? ox.nodes : 0}`);
    }
  }
  console.log("NEW in fixed build:", newOnes.length ? newOnes : "none");
  const sum = L.summarizeRecords(records);
  console.log("console errors:", sum.consoleErrors.length, sum.consoleErrors.filter((e) => !/status of (404|400)/.test(e)).slice(0, 5), "outside:", sum.outside, "requests:", sum.requests);
})();
