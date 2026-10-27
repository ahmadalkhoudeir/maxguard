// T9: keyboard user, single queue tab (the stream holder): focus an alert link with
// Tab, open it with Enter, come back with Back. Where is focus after Back?
// Full Chromium with bfcache on (like a normal Chrome).
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    for (const z of ["telnet", "ftp", "imap"]) await L.upload(server.port, z);
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    await L.sleep(800);
    // Tab to the third alert link
    const target = await page.evaluate(() => document.querySelectorAll("#alerts tbody a")[2].getAttribute("href"));
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press("Tab");
      const href = await page.evaluate(() => document.activeElement && document.activeElement.getAttribute("href"));
      if (href === target) break;
    }
    out.focusedBefore = await page.evaluate(() => document.activeElement.outerHTML.slice(0, 60));
    await page.keyboard.press("Enter");
    await page.waitForURL(/\/alerts\//);
    await L.sleep(700);
    await page.goBack({ waitUntil: "commit" });
    await page.waitForSelector("#alerts");
    await L.sleep(1200);
    out.back = await page.evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      const flat = [];
      const walk = (x) => { if (!x) return; for (const y of x.reasons || []) flat.push(y.reason); for (const c of x.children || []) walk(c); };
      walk(nav.notRestoredReasons);
      return flat.join(",") || "restored from bfcache";
    });
    out.focusedAfterBack = await page.evaluate(() => {
      const a = document.activeElement;
      return a === document.body ? "<body> (focus lost)" : a.outerHTML.slice(0, 60);
    });
    // one Tab press after Back: where does it land?
    await page.keyboard.press("Tab");
    out.afterOneTab = await page.evaluate(() => document.activeElement.textContent.trim().slice(0, 40));
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("chromium", browser.version(), "full Chromium, bfcache on");
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
