// T3: which pages Chrome keeps in bfcache here, and why not (notRestoredReasons).
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const INIT = () => {
  window.__shows = window.__shows || [];
  addEventListener("pageshow", (e) => window.__shows.push(e.persisted ? "persisted" : "fresh"));
};

async function navInfo(page) {
  return page.evaluate(() => {
    const nav = performance.getEntriesByType("navigation")[0];
    const flat = [];
    const walk = (r) => {
      if (!r) return;
      for (const x of r.reasons || []) flat.push(x.reason);
      for (const c of r.children || []) walk(c);
    };
    walk(nav && nav.notRestoredReasons);
    return { shows: window.__shows.join(","), notRestored: flat.join(",") };
  });
}

async function backForward(page, fromUrl, viaSelector) {
  await page.goto(fromUrl);
  await L.sleep(700);
  await page.click(viaSelector);
  await page.waitForLoadState("load");
  await L.sleep(700);
  await page.goBack({ waitUntil: "commit" });
  await L.sleep(1000);
  return navInfo(page);
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await browser.newContext();
    await ctx.addInitScript(INIT);
    const P = await ctx.newPage();
    out.uploadPage = await backForward(P, server.origin + "/upload", "nav a[href='/']");
    const Q = await ctx.newPage();
    out.queueHolder = await backForward(Q, server.origin + "/", "nav a[href='/upload']");
    // a second queue tab that is not the holder (fixed build: it waits for the lock)
    const R = await ctx.newPage();
    out.queueNonHolder = await backForward(R, server.origin + "/", "nav a[href='/upload']");
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("chromium", browser.version(), "(bfcache on)");
  try {
    for (const b of ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
