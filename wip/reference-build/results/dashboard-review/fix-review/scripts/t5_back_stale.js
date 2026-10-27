// T5: the analyst flow "queue -> alert -> change status -> Back" in a queue tab
// that is NOT the stream holder (another queue tab is open). Does the queue show
// the new status after Back?
//   node t5_back_stale.js [bfcache]        default: Playwright's own flags (bfcache off)
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const bf = process.argv.includes("bfcache");
const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function statusCell(page) {
  return page.evaluate(() => {
    const td = document.querySelector('#alerts tbody td[data-label="Status"]');
    return td ? td.textContent.trim() : null;
  });
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await browser.newContext();
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    const H = await ctx.newPage();
    await H.goto(server.origin + "/");          // first queue tab: holds the stream
    await L.sleep(500);
    const N = await ctx.newPage();
    await N.goto(server.origin + "/");          // second queue tab
    await L.sleep(500);
    await N.click("#alerts tbody a");
    await N.waitForURL(/\/alerts\//);
    await N.selectOption("#alert-status", "investigating");
    await N.click("#status-form button[type=submit]");
    await N.waitForSelector("#status-form .message");
    out.saved = (await N.textContent("#status-form .message")).trim();
    await L.sleep(1000);
    out.holderTabShows = await statusCell(H);
    const t0 = Date.now();
    await N.goBack({ waitUntil: "commit" });
    await N.waitForSelector("#alerts");
    out.backNavigation = await N.evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      return { type: nav.type, transferSize: nav.transferSize };
    });
    out.queueShowsRightAfterBack = await statusCell(N);
    const r = await L.waitFor(async () => (await statusCell(N)) === "Investigating", 8000, 100);
    out.queueShowsInvestigating = r.ok ? `after ${Date.now() - t0} ms` : `NO, still "${r.value === false ? await statusCell(N) : r.value}" ${Date.now() - t0} ms after Back`;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const opts = bf ? { channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] } : {};
  const browser = await chromium.launch(opts);
  console.log("chromium", browser.version(), bf ? "full Chromium, bfcache on" : "Playwright default launch (bfcache off)");
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
