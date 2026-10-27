// Check 3 (a): with two queue tabs open, Back after Save (alert page) and Back after
// Upload shows the new state within 2 s, not after the 30 s poll.
// Usage: node c3a_back.js [bfcache] <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const bf = process.argv.includes("bfcache");
const builds = process.argv.slice(2).filter((a) => a !== "bfcache");

const statusCell = (page) => page.evaluate(() => {
  const td = document.querySelector('#alerts tbody td[data-label="Status"]');
  return td ? td.textContent.trim() : null;
});
const navInfo = (page) => page.evaluate(() => {
  const nav = performance.getEntriesByType("navigation")[0];
  return `${nav.type}${window.__persisted ? " (bfcache)" : ""} transfer=${nav.transferSize}`;
});

async function run(buildName, browser) {
  const out = { build: buildName, bfcache: bf };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await L.newContext(browser);
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    await ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
    const H = await ctx.newPage();
    await H.goto(server.origin + "/");            // first queue tab (the stream holder in the fixed build)
    await L.sleep(500);
    const N = await ctx.newPage();
    await N.goto(server.origin + "/");            // second queue tab
    await L.sleep(500);
    // --- Back after Save
    await N.click("#alerts tbody a");
    await N.waitForURL(/\/alerts\//);
    await N.selectOption("#alert-status", "investigating");
    await N.click("#status-form button[type=submit]");
    await N.waitForSelector("#status-form .message");
    out.saved = (await N.textContent("#status-form .message")).trim();
    await L.sleep(800);
    out.otherTabShows = await statusCell(H);
    let t0 = Date.now();
    await N.goBack({ waitUntil: "commit" });
    await N.waitForSelector("#alerts");
    out.backNav = await navInfo(N);
    out.rightAfterBack = await statusCell(N);
    let r = await L.waitFor(async () => (await statusCell(N)) === "Investigating", 8000, 50);
    out.backAfterSave = r.ok ? `Investigating after ${Date.now() - t0} ms` : `NOT within 8 s (shows "${await statusCell(N)}")`;
    out.backAfterSavePass = r.ok && Date.now() - t0 <= 2000;
    // --- Back after Upload (a new alert appears)
    await N.goto(server.origin + "/upload");
    await L.sleep(300);
    await L.upload(server.port, "ftp");
    await L.sleep(800);
    out.otherTabRows = await L.rowCount(H);
    t0 = Date.now();
    await N.goBack({ waitUntil: "commit" });
    await N.waitForSelector("#alerts");
    out.backNav2 = await navInfo(N);
    out.rightAfterBack2 = await L.rowCount(N);
    r = await L.waitFor(async () => (await L.rowCount(N)) === 2, 8000, 50);
    out.backAfterUpload = r.ok ? `2 rows after ${Date.now() - t0} ms` : `NOT within 8 s (${await L.rowCount(N)} rows)`;
    out.backAfterUploadPass = r.ok && Date.now() - t0 <= 2000;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const opts = bf ? { channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] } : {};
  const browser = await chromium.launch(opts);
  console.log("Chromium", browser.version(), bf ? "bfcache on" : "Playwright default (bfcache off)");
  try {
    for (const b of builds) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
