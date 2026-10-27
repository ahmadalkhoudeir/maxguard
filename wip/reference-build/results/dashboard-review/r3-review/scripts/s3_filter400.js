// S3: the filter answer is a 400 page (no #alerts in it). What is left of the page, and
// what do the live refresh and the next filter change do then? Usage: node s3_filter400.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
const M = require("./more");

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await browser.newContext();
    await ctx.addInitScript(M.INIT);
    const page = await ctx.newPage();
    const pageErrors = [];
    page.on("pageerror", (e) => pageErrors.push(e.message));
    const gets = [];
    page.on("response", (r) => { if (r.url().includes("/?status=")) gets.push(`${new URL(r.url()).search} -> ${r.status()}`); });
    await page.goto(server.origin + "/");
    await L.sleep(1000);
    // a value the server does not know (what a hand-edited URL or an old page would send)
    await page.evaluate(() => { document.querySelector('#status option[value="new"]').value = "bogus"; });
    await page.selectOption("#status", "bogus");
    await L.sleep(1500);
    const state = () => page.evaluate(() => ({
      url: location.search, alertsDiv: !!document.getElementById("alerts"),
      rows: document.querySelectorAll("#alerts tbody tr").length,
      mainText: document.querySelector("main").innerText.replace(/\s+/g, " ").slice(0, 160),
    }));
    out.afterBadFilter = await state();
    out.afterBadFilter_gets = gets.join(" ; ");
    out.afterBadFilter_errors = pageErrors.splice(0);
    await L.upload(server.port, "ftp");          // the server says alerts changed
    await L.sleep(2500);
    out.afterChange = await state();
    out.afterChange_errors = pageErrors.splice(0);
    out.afterChange_gets = gets.join(" ; ");
    await page.selectOption("#status", "");       // the person picks "All" again
    await L.sleep(1500);
    out.afterAllAgain = await state();
    out.afterAllAgain_errors = pageErrors.splice(0);
    out.afterAllAgain_gets = gets.join(" ; ");
    out.windowErrors = await page.evaluate(() => window.__errors);
    await ctx.close();
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
