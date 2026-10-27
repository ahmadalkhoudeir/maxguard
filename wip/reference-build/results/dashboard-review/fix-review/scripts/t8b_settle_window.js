// T8b: a cross-tab "alerts-changed" message that lands while #alerts is settling
// (the 20 ms after a swap, before htmx has wired up the new table). The message is
// posted from a second BroadcastChannel object in the same page, which the app's
// channel receives like a message from another tab.
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
    const g0 = gets.length;
    await page.evaluate(() => {
      const other = new BroadcastChannel("maxguard-alerts");
      window.__log = [];
      document.body.addEventListener("htmx:afterSwap", function once() {
        document.body.removeEventListener("htmx:afterSwap", once);
        other.postMessage("alerts-changed");     // arrives while the new table is settling
      });
      other.onmessage = null;
      new BroadcastChannel("maxguard-alerts").addEventListener("message", () => {
        window.__log.push(document.getElementById("alerts").classList.contains("htmx-settling") ? "arrived while settling" : "arrived after settle");
      });
      htmx.trigger("#alerts", "refresh");
    });
    await L.sleep(1500);
    out.messageTiming = await page.evaluate(() => window.__log.join(","));
    out.requests = `${gets.length - g0} (2 = the message's refresh happened)`;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of builds.length ? builds : ["fixed-03", "patched-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
