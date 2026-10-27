// Check 2: Tab to an alert link, another client changes that alert: focus stays on the link.
// Check 3 (AHM-03 builds): keyboard-only Save on the alert page: focus is on Save afterwards.
// Usage: node check02_03_focus.js <buildKey...>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");

async function tabTo(page, predicateSrc, max = 40) {
  for (let i = 1; i <= max; i++) {
    await page.keyboard.press("Tab");
    if (await page.evaluate(predicateSrc)) return i;
  }
  return -1;
}

async function check2(browser, srv) {
  const tid = await L.telnetId(srv.base);
  L.addAlerts(srv.build, srv.data, ["critical", "medium", "low"], 30);  // a few more links around it
  const page = await browser.newPage();
  const settles = [];
  await page.exposeFunction("__settled", (t) => settles.push(t));
  await page.addInitScript(() => document.addEventListener("htmx:afterSettle",
    (e) => { if (e.target && e.target.id === "alerts") window.__settled(Date.now()); }));
  await page.goto(srv.base + "/");
  // The stream's first event refreshes the table once right after loading: let it happen.
  const t0 = Date.now();
  while (settles.length === 0 && Date.now() - t0 < 5000) await L.sleep(50);
  await L.sleep(300);
  const presses = await tabTo(page, `document.activeElement && document.activeElement.getAttribute("href") === "/alerts/${tid}"`);
  const before = await L.activeDesc(page);
  const nSettled = settles.length;
  const tPatch = Date.now();
  const res = await L.api(srv.base, "PATCH", "/api/alerts/" + tid, { actor: "x", assignee: "Someone" });
  // Wait for the refresh that shows the change.
  let shown = false;
  while (Date.now() - tPatch < 8000) {
    shown = await page.evaluate((id) => {
      const a = document.querySelector(`#alerts a[href="/alerts/${id}"]`);
      return !!a && a.closest("tr").querySelector('td[data-label="Assignee"]').textContent === "Someone";
    }, tid);
    if (shown && settles.length > nSettled) break;
    await L.sleep(50);
  }
  const refreshMs = Date.now() - tPatch;
  await L.sleep(200);
  const after = await L.activeDesc(page);
  const onLink = await page.evaluate((id) => document.activeElement.getAttribute("href") === `/alerts/${id}`, tid);
  await page.keyboard.press("Tab");
  const nextTab = await L.activeDesc(page);
  await page.close();
  return { tabPresses: presses, patch: res.status, changeShownAfterMs: shown ? refreshMs : null,
           focusBefore: before, focusAfter: after, pass: onLink, nextTabGoesTo: nextTab };
}

async function check3(browser, srv) {
  const tid = await L.telnetId(srv.base);
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(srv.base + "/alerts/" + tid);
  const steps = [];
  steps.push(["Tab to the name field", await tabTo(page, `document.activeElement && document.activeElement.id === "actor"`)]);
  await page.keyboard.type("Ahmad");
  await page.keyboard.press("Tab");
  steps.push(["Tab ->", await L.activeDesc(page)]);
  await page.keyboard.press("ArrowDown");  // New -> Investigating, keyboard only
  steps.push(["status after ArrowDown", await page.inputValue("#alert-status")]);
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");
  const beforeEnter = await L.activeDesc(page);
  await page.keyboard.press("Enter");
  await page.waitForFunction(() => { const m = document.querySelector("#status-form .message"); return m && m.textContent.trim(); });
  await L.sleep(300);
  const message1 = (await page.textContent("#status-form .message")).trim();
  const after1 = await L.activeDesc(page);
  const pass1 = await page.evaluate(() => document.activeElement.tagName === "BUTTON" && document.activeElement.textContent.trim() === "Save");
  // A second keyboard save (the name is now remembered): Shift+Tab to the assignee, type, Tab, Enter.
  await page.keyboard.press("Shift+Tab");
  const back = await L.activeDesc(page);
  await page.keyboard.type("Fiona");
  await page.keyboard.press("Tab");
  const beforeEnter2 = await L.activeDesc(page);
  await page.keyboard.press("Enter");
  let after2, pass2 = false;
  try {
    await page.waitForFunction(() => document.querySelector("#assignee") && document.querySelector("#assignee").value === "Fiona" &&
      document.querySelector("#status-form .message"), null, { timeout: 5000 });
    await L.sleep(300);
    after2 = await L.activeDesc(page);
    pass2 = await page.evaluate(() => document.activeElement.tagName === "BUTTON" && document.activeElement.textContent.trim() === "Save");
  } catch (e) {
    after2 = `no second save: "Fiona" was typed into ${back}, Enter pressed on ${beforeEnter2}; now at ${await L.activeDesc(page)} (url ${page.url().replace(srv.base, "")})`;
  }
  const stored = (await L.api(srv.base, "GET", "/api/alerts/" + tid)).json;
  await ctx.close();
  return { steps, focusBeforeEnter: beforeEnter, message: message1, focusAfterSave1: after1,
           shiftTabFromThere: back, focusAfterSave2: after2, stored: [stored.status, stored.assignee],
           pass: pass1 && pass2 };
}

(async () => {
  const browser = await chromium.launch();
  for (const key of process.argv.slice(2)) {
    const r2 = await L.withServer(key, "c02", (srv) => check2(browser, srv));
    console.log(`== ${key} check 2 (focus through a live refresh): ${JSON.stringify(r2)}`);
    if (key.endsWith("3")) {
      const r3 = await L.withServer(key, "c03", (srv) => check3(browser, srv));
      console.log(`== ${key} check 3 (focus after keyboard Save): ${JSON.stringify(r3)}`);
    }
  }
  await browser.close();
})();
