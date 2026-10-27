// Check 10: Home-mode title, the aside landmark, and axe (default rules plus
// wcag2a/wcag2aa/wcag21aa) on every page, both modes, 1280 and 375 px.
// Usage: node c10_axe.js <build>...
"use strict";
const { chromium } = require("playwright");
const { AxeBuilder } = require("/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/tools/node/node_modules/@axe-core/playwright");
const L = require("./lib");

async function run(buildName, browser) {
  const out = { build: buildName, pages: 0, runs: 0, violations: {}, titles: {}, aside: {} };
  const dataDir = L.newDataDir(buildName + "-c10");
  L.addAlerts(buildName, dataDir, ["critical", "high", "medium", "low", "info"]);
  const server = await L.startServer(buildName, { dataDir });
  try {
    await L.upload(server.port, "telnet");
    const id = await L.telnetId(server.port);
    const a = (await L.api(server.port, "GET", "/api/alerts/" + id)).body;
    await L.patchAlert(server.port, id, { actor: "Ahmad", assignee: "Fiona" });
    const paths = ["/", "/upload", "/alerts/" + id, "/alerts/0000000000000000", "/?status=bogus",
      "/timeline", `/timeline?ip=172.18.0.3&end=${Math.floor(a.last_seen) + 1}`, "/assets"];
    for (const mode of ["analyst", "home"]) {
      for (const actor of [null, "Ahmad"]) {
        for (const width of [1280, 375]) {
          const ctx = await L.newContext(browser, { viewport: { width, height: 900 } });
          const cookies = [{ name: "mg_mode", value: mode, url: server.origin }];
          if (actor) cookies.push({ name: "mg_actor", value: actor, url: server.origin });
          await ctx.addCookies(cookies);
          const page = await ctx.newPage();
          for (const p of paths) {
            await page.goto(server.origin + p);
            out.pages++;
            const title = await page.title();
            if (p.startsWith("/alerts/" + id)) out.titles[mode] = title;
            if (width === 1280 && !actor) {
              out.aside[`${mode} ${p}`] = await page.evaluate(() => {
                const aside = document.querySelector("aside[aria-label]");
                const privacy = document.querySelector(".privacy");
                return aside ? `aside[aria-label=${aside.getAttribute("aria-label")}]` : (privacy ? "p.privacy with no landmark" : "none");
              });
            }
            const results = [await new AxeBuilder({ page }).analyze(),
              await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()];
            out.runs += 2;
            for (const r of results) {
              for (const v of r.violations) {
                const key = `${v.id} (${v.impact})`;
                const where = `${mode}${actor ? "+name" : ""} ${width}px ${p}: ${v.nodes.map((n) => n.target.join(" ")).join(", ")}`;
                (out.violations[key] = out.violations[key] || new Set()).add(where);
              }
            }
          }
          await ctx.close();
        }
      }
    }
  } finally {
    await server.stop();
  }
  for (const k of Object.keys(out.violations)) {
    const v = [...out.violations[k]];
    out.violations[k] = { count: v.length, sample: v.slice(0, 4) };
  }
  out.asideSummary = [...new Set(Object.values(out.aside))].join(" / ");
  out.pass = Object.keys(out.violations).length === 0 && out.titles.home && !out.titles.home.includes("Telnet session in cleartext") && out.asideSummary === "aside[aria-label=Privacy]";
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
