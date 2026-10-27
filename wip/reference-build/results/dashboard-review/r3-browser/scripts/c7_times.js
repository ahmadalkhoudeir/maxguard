// Check 7: a Telnet log with ts=1e12, then 1e400 (inf): every page answers 200 in both
// modes, the alert page's timeline links carry no end=, the time says "(not a valid time)".
// Usage: node c7_times.js <build>...   (zips from make_hostile_zips.py in ../zips)
"use strict";
const { chromium } = require("playwright");
const path = require("path");
const L = require("./lib");

async function run(buildName, browser) {
  const out = { build: buildName, cases: {} };
  const stage = buildName.slice(-2);
  for (const literal of ["1e12", "1e400"]) {
    const server = await L.startServer(buildName);
    const c = out.cases[literal] = {};
    try {
      const up = await L.upload(server.port, "telnet-ts-" + literal, path.join(L.ZIPS, `telnet-ts-${literal}.zip`));
      c.upload = up.status;
      const list = await L.alerts(server.port);
      if (!list.length) { c.error = "no alert stored: " + JSON.stringify(up.body); continue; }
      const a = list[0];
      c.storedLastSeen = String(a.last_seen);
      const paths = ["/", "/alerts/" + a.finding_id];
      if (stage === "06") paths.push("/timeline?ip=172.18.0.3", "/assets");
      c.pages = {};
      for (const mode of ["analyst", "home"]) {
        const ctx = await L.newContext(browser);
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin }]);
        const page = await ctx.newPage();
        for (const p of paths) {
          const resp = await page.goto(server.origin + p);
          c.pages[`${mode} ${p}`] = resp.status();
          if (p.startsWith("/alerts/") && resp.status() === 200) {
            const info = await page.evaluate(() => ({
              timelineLinks: [...document.querySelectorAll('a[href^="/timeline?ip="]')].map((l) => l.getAttribute("href")),
              timeText: [...document.querySelectorAll("dd, p.muted")].map((e) => e.textContent.replace(/\s+/g, " ").trim()).filter((t) => /last|Last seen/i.test(t)),
            }));
            c[mode + "Alert"] = info;
          }
        }
        await ctx.close();
      }
      c.all200 = Object.values(c.pages).every((s) => s === 200);
      const links = (c.analystAlert && c.analystAlert.timelineLinks) || [];
      c.noEndParam = links.length > 0 && links.every((h) => !/[?&]end=/.test(h));
      c.notValidTime = [...((c.analystAlert && c.analystAlert.timeText) || []), ...((c.homeAlert && c.homeAlert.timeText) || [])].some((t) => t.includes("(not a valid time)"));
      c.pass = c.all200 && (stage === "02" || (c.noEndParam && c.notValidTime));
    } finally {
      await server.stop();
      const log = server.log();
      const err = log.split("\n").filter((l) => /Error|Traceback|500/.test(l));
      if (err.length) c.serverLog = err.slice(0, 3).join(" | ").slice(0, 300);
    }
  }
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
