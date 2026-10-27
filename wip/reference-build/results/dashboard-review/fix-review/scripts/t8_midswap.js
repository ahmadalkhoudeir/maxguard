// T8: htmx.trigger("#alerts", "refresh") while #alerts is mid-request / mid-swap.
// (a) a refresh fired while a refresh request is in flight; (b) one fired right after
// the swap, before htmx has processed the new #alerts (settle delay 20 ms).
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const gets = [];
    page.on("request", (r) => { if (r.url().includes("/?status=")) gets.push(Date.now()); });
    await page.goto(server.origin + "/");
    await L.sleep(1000);

    // (a) hold the first refresh's answer for 1.5 s (rendered by the server now, delivered late)
    let held = 0;
    await page.route(/\/\?status=/, async (route) => {
      if (held++ === 0) {
        const resp = await route.fetch();        // rendered now: 1 alert
        await L.sleep(1500);
        return route.fulfill({ response: resp });
      }
      return route.continue();
    });
    const g0 = gets.length;
    await page.evaluate(() => htmx.trigger("#alerts", "refresh"));
    await L.sleep(300);
    await L.upload(server.port, "ftp");          // a change while that answer is on its way
    await L.sleep(4000);                          // the stream event arrives within ~0.5 s
    out.a_requestsIssued = gets.length - g0;
    out.a_rowsShown = `${await L.rowCount(page)} (server has 2)`;
    await page.unroute(/\/\?status=/);

    // (b) a refresh fired synchronously right after a swap
    const g1 = gets.length;
    await page.evaluate(() => {
      document.body.addEventListener("htmx:afterSwap", function once(e) {
        document.body.removeEventListener("htmx:afterSwap", once);
        window.__settling = document.getElementById("alerts").classList.contains("htmx-settling");
        htmx.trigger("#alerts", "refresh");
      });
      htmx.trigger("#alerts", "refresh");
    });
    await L.sleep(1500);
    out.b_settlingAtSecondTrigger = await page.evaluate(() => window.__settling);
    out.b_requestsIssued = `${gets.length - g1} (2 expected if the second trigger was honoured)`;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
