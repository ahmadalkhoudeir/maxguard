// Check 11: every control reachable with Tab, in DOM order, on every page.
// Usage: node c11_tab_order.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const SEL = 'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
const expected = (page) => page.evaluate((sel) => [...document.querySelectorAll(sel)]
  .filter((e) => !e.disabled && e.type !== "hidden" && e.tabIndex >= 0 && !(e.getAttribute("tabindex") === "-1"))
  .map((e) => `${e.tagName}${e.id ? "#" + e.id : ""}${e.getAttribute("href") ? "[" + e.getAttribute("href") + "]" : ""}${e.name ? "(" + e.name + ")" : ""}`), SEL);
const describe = (page) => page.evaluate(() => {
  const e = document.activeElement;
  if (!e || e === document.body) return "<body>";
  return `${e.tagName}${e.id ? "#" + e.id : ""}${e.getAttribute("href") ? "[" + e.getAttribute("href") + "]" : ""}${e.name ? "(" + e.name + ")" : ""}`;
});

async function run(buildName, browser) {
  const out = { build: buildName, pages: {} };
  const stage = buildName.slice(-2);
  const dataDir = L.newDataDir(buildName + "-c11");
  L.addAlerts(buildName, dataDir, ["critical", "high", "medium", "low", "info"]);
  const server = await L.startServer(buildName, { dataDir });
  try {
    await L.upload(server.port, "telnet");
    const id = await L.telnetId(server.port);
    const a = (await L.api(server.port, "GET", "/api/alerts/" + id)).body;
    const paths = ["/", "/upload"];
    if (stage !== "02") paths.push("/alerts/" + id, "/alerts/0000000000000000", "/?status=bogus");
    if (stage === "06") paths.push("/timeline", `/timeline?ip=172.18.0.3&end=${Math.floor(a.last_seen) + 1}`, "/assets");
    for (const mode of ["analyst", "home"]) {
      const ctx = await L.newContext(browser, { viewport: { width: 1280, height: 900 } });
      await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin }]);
      const page = await ctx.newPage();
      for (const p of paths) {
        await page.goto(server.origin + p);
        await L.sleep(200);
        const want = await expected(page);
        const got = [];
        for (let i = 0; i < want.length + 2; i++) {
          await page.keyboard.press("Tab");
          const d = await describe(page);
          if (d === "<body>" && got.length) break;      // wrapped around to the browser UI
          got.push(d);
        }
        const same = JSON.stringify(want) === JSON.stringify(got);
        out.pages[`${mode} ${p}`] = same ? `ok (${want.length} controls)` : { want, got };
      }
      await ctx.close();
    }
  } finally {
    await server.stop();
  }
  out.pass = Object.values(out.pages).every((v) => typeof v === "string");
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
