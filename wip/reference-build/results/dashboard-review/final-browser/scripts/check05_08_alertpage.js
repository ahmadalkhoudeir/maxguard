// Check 5: the Home-mode <title> of the Telnet alert is the Home headline; Analyst-mode is the rule title.
// Check 8: two analysts. Tab B opened the alert (New) before Ahmad set Investigating in tab A;
// B types an assignee and saves without touching the status.
// Usage: node check05_08_alertpage.js <buildKey...>   (AHM-03 builds)
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");

async function check5(browser, srv) {
  const tid = await L.telnetId(srv.base);
  const out = {};
  for (const mode of ["home", "analyst"]) {
    const ctx = await browser.newContext();
    await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
    const page = await ctx.newPage();
    await page.goto(srv.base + "/alerts/" + tid);
    out[mode] = { title: await page.title(), h1: (await page.textContent("h1")).trim() };
    await ctx.close();
  }
  const headline = "A device used Telnet, which sends everything you type, even passwords, without encryption.";
  out.pass = out.home.title === `${headline} · MaxGuard` && out.home.h1 === headline &&
             out.analyst.title === "Telnet session in cleartext · MaxGuard";
  return out;
}

async function check8(browser, srv) {
  const tid = await L.telnetId(srv.base);
  const auditBefore = (await L.api(srv.base, "GET", "/api/audit?limit=50")).json.length;
  const [ctxA, ctxB] = [await browser.newContext(), await browser.newContext()];
  const [a, b] = [await ctxA.newPage(), await ctxB.newPage()];
  await b.goto(srv.base + "/alerts/" + tid);           // B opens the page first: it shows New
  await a.goto(srv.base + "/alerts/" + tid);
  const bShowedBefore = await b.inputValue("#alert-status");
  await a.fill("#actor", "Ahmad");
  await a.selectOption("#alert-status", "investigating");
  await a.click("#status-form button[type=submit]");
  await a.waitForSelector("#status-form .message");
  const aSaid = (await a.textContent("#status-form .message")).trim();
  const afterA = (await L.api(srv.base, "GET", "/api/alerts/" + tid)).json;
  // B: name and assignee only; the status select is not touched (it still shows New).
  await b.fill("#actor", "Fiona");
  await b.fill("#assignee", "Fiona");
  const bStatusSent = await b.inputValue("#alert-status");
  await b.click("#status-form button[type=submit]");
  await b.waitForSelector("#status-form .message");
  const bSaid = (await b.textContent("#status-form .message")).trim();
  const bShowsAfter = await b.inputValue("#alert-status");
  const stored = (await L.api(srv.base, "GET", "/api/alerts/" + tid)).json;
  const audit = (await L.api(srv.base, "GET", "/api/audit?limit=50")).json;
  const newRows = audit.slice(0, audit.length - auditBefore).reverse().map((r) => ({ actor: r.actor, action: r.action, details: r.details }));
  await ctxA.close(); await ctxB.close();
  const bRows = newRows.filter((r) => r.actor === "Fiona");
  const pass = stored.status === "investigating" && stored.assignee === "Fiona" && bRows.length === 1 &&
               JSON.stringify(Object.keys(bRows[0].details)) === '["assignee"]';
  return { bShowedBefore, aSaid, afterA: [afterA.status, afterA.assignee], bStatusSelectWhenSaving: bStatusSent,
           bSaid, bSelectAfterSave: bShowsAfter, stored: [stored.status, stored.assignee], auditRowsAdded: newRows, pass };
}

(async () => {
  const browser = await chromium.launch();
  for (const key of process.argv.slice(2)) {
    const r5 = await L.withServer(key, "c05", (srv) => check5(browser, srv));
    console.log(`== ${key} check 5 (title): ${JSON.stringify(r5)}`);
    const r8 = await L.withServer(key, "c08", (srv) => check8(browser, srv));
    console.log(`== ${key} check 8 (two analysts): ${JSON.stringify(r8)}`);
  }
  await browser.close();
})();
