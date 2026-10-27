// Check 10: status filter, then severity filter, then Back: selects and rows match the address.
// Check 11: after an upload finishes, focus is on Analyze.
// Check 12: a severity filter (address changes without a page load), then Home: still filtered.
// Usage: node check10_11_12.js <buildKey...>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");

const LABELS = { new: "New", investigating: "Investigating", resolved: "Resolved", false_positive: "False positive" };

async function seed(srv) {
  L.addAlerts(srv.build, srv.data, ["critical", "high", "high", "medium", "low"], 40);
  const list = await L.alerts(srv.base);
  // Two alerts Investigating (one High, one Critical), the rest New.
  const hi = list.find((a) => a.severity === "high" && a.dst_ip.startsWith("10.9.40."));
  const cr = list.find((a) => a.severity === "critical");
  for (const a of [hi, cr]) await L.api(srv.base, "PATCH", "/api/alerts/" + a.finding_id, { actor: "seed", status: "investigating" });
  return L.alerts(srv.base);
}

// What the page shows vs what the address asks for (and what the server holds for it).
async function state(page, srv) {
  const s = await page.evaluate(() => ({
    url: location.pathname + location.search,
    statusSelect: document.getElementById("status").value,
    severitySelect: document.getElementById("severity").value,
    rows: [...document.querySelectorAll("#alerts tbody tr")].map((tr) => [
      tr.querySelector('td[data-label="Status"]').textContent.trim(),
      tr.querySelector('td[data-label="Severity"]').textContent.trim().toLowerCase(),
      tr.querySelector("a").getAttribute("href").split("/").pop()]),
  }));
  const q = new URLSearchParams(s.url.split("?")[1] || "");
  const want = { status: q.get("status") || "", severity: q.get("severity") || "" };
  const api = await L.alerts(srv.base + "");
  const expected = api.filter((a) => (!want.status || a.status === want.status) && (!want.severity || a.severity === want.severity))
    .map((a) => a.finding_id).sort();
  const shown = s.rows.map((r) => r[2]).sort();
  s.matches = s.statusSelect === want.status && s.severitySelect === want.severity &&
              JSON.stringify(shown) === JSON.stringify(expected);
  s.rowsSummary = `${s.rows.length} rows: ${[...new Set(s.rows.map((r) => r[0] + "/" + r[1]))].join(", ")}`;
  s.expectedRows = expected.length;
  delete s.rows;
  return s;
}

async function check10(browser, srv) {
  await seed(srv);
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(srv.base + "/");
  await L.sleep(800);
  await page.selectOption("#status", "new");
  await page.waitForURL(/status=new/);
  await L.sleep(500);
  const afterStatus = await state(page, srv);
  await page.selectOption("#severity", "high");
  await page.waitForURL(/severity=high/);
  await L.sleep(500);
  const afterSeverity = await state(page, srv);
  await page.goBack();
  await page.waitForURL((u) => !u.search.includes("severity=high"));
  await L.sleep(1200);
  const afterBack = await state(page, srv);
  await page.goBack();
  await page.waitForURL((u) => u.search === "");
  await L.sleep(1200);
  const afterBack2 = await state(page, srv);
  await page.goForward();
  await page.waitForURL(/status=new/);
  await L.sleep(1200);
  const afterForward = await state(page, srv);
  await ctx.close();
  return { afterStatus, afterSeverity, afterBack, afterBack2, afterForward,
           pass: afterBack.matches && afterBack2.matches && afterForward.matches };
}

async function check11(browser, srv) {
  const page = await browser.newPage();
  await page.goto(srv.base + "/upload");
  await page.setInputFiles("#file", L.ZIP);       // the file chooser itself is not keyboard-testable
  await page.focus("#file");
  await page.keyboard.press("Tab");                // keyboard from here: Tab to Analyze, Enter
  const before = await L.activeDesc(page);
  const t0 = Date.now();
  await page.keyboard.press("Enter");
  await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "", null, { timeout: 60000 });
  const ms = Date.now() - t0;
  await L.sleep(200);
  const result = await page.textContent("#upload-result");
  const after = await L.activeDesc(page);
  const pass = await page.evaluate(() => document.activeElement === document.querySelector("#upload-form button"));
  await page.keyboard.press("Tab");
  const nextTab = await L.activeDesc(page);
  await page.close();
  return { focusBeforeEnter: before, uploadMs: ms, result, focusAfter: after, nextTab, pass };
}

async function check12(browser, srv) {
  await seed(srv);
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(srv.base + "/");
  await L.sleep(800);
  await page.evaluate(() => { window.__samePage = true; });
  await page.selectOption("#severity", "high");
  await page.waitForURL(/severity=high/);
  await L.sleep(500);
  const before = await state(page, srv);
  before.noPageLoad = await page.evaluate(() => window.__samePage === true);
  before.switchNext = await page.evaluate(() => document.querySelector('.mode-switch input[name="next"]').value);
  await Promise.all([page.waitForNavigation(), page.click('.mode-switch button[value="home"]')]);
  await L.sleep(800);
  const after = await state(page, srv);
  after.mode = await page.evaluate(() => document.body.className);
  after.badges = await page.evaluate(() => [...new Set([...document.querySelectorAll("#alerts .sev")].map((e) => e.textContent.trim()))]);
  await ctx.close();
  return { before, after, pass: before.noPageLoad && after.matches && /severity=high/.test(after.url) && after.mode === "mode-home" };
}

(async () => {
  const browser = await chromium.launch();
  for (const key of process.argv.slice(2)) {
    const r10 = await L.withServer(key, "c10", (srv) => check10(browser, srv));
    console.log(`== ${key} check 10 (Back button): ${JSON.stringify(r10)}`);
    const r11 = await L.withServer(key, "c11", (srv) => check11(browser, srv), { upload: false });
    console.log(`== ${key} check 11 (upload focus): ${JSON.stringify(r11)}`);
    const r12 = await L.withServer(key, "c12", (srv) => check12(browser, srv));
    console.log(`== ${key} check 12 (mode switch keeps filters): ${JSON.stringify(r12)}`);
  }
  await browser.close();
})();
