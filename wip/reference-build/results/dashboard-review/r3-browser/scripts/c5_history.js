// Check 5: choose status, then severity, press Back: selects, rows and address agree
// and it is a full page load; the Analyst/Home switch keeps the filter; Back while the
// server is unreachable shows the browser's own error page, not a half page.
// Usage: node c5_history.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const state = (page) => page.evaluate(() => ({
  url: location.pathname + location.search,
  document: window.__marker === 1 ? "same document (no full load)" : "new document (full page load)",
  status: document.getElementById("status") && document.getElementById("status").value,
  severity: document.getElementById("severity") && document.getElementById("severity").value,
  rows: [...new Set([...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent.trim()))].join("+") || "(none)",
  statuses: [...new Set([...document.querySelectorAll('#alerts td[data-label="Status"]')].map((t) => t.textContent.trim()))].join("+") || "(none)",
  next: document.querySelector(".mode-switch input[name=next]") && document.querySelector(".mode-switch input[name=next]").value,
  mode: document.body.className,
  sessionCache: (() => { try { return sessionStorage.getItem("htmx-history-cache") ? "present" : "none"; } catch (e) { return "n/a"; } })(),
}));

async function run(buildName, browser) {
  const out = { build: buildName };
  const dataDir = L.newDataDir(buildName + "-c5");
  L.addAlerts(buildName, dataDir, ["critical", "high", "medium", "low", "info"], 2);
  const server = await L.startServer(buildName, { dataDir });
  try {
    await L.upload(server.port, "telnet");
    const list = await L.alerts(server.port);
    const medium = list.find((a) => a.severity === "medium");
    await L.patchAlert(server.port, medium.finding_id, { actor: "setup", status: "investigating" });
    const ctx = await L.newContext(browser);
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    await page.evaluate(() => { window.__marker = 1; });
    await page.selectOption("#status", "new");
    await page.waitForURL(/status=new/);
    await L.sleep(300);
    await page.selectOption("#severity", "medium");
    await page.waitForURL(/severity=medium/);
    await L.sleep(300);
    out.beforeBack = await state(page);
    await page.goBack();
    await L.sleep(1500);
    out.afterBack = await state(page);
    const s = out.afterBack;
    // Back goes from ?status=new&severity=medium to ?status=new&severity= : the selects must
    // say New / All, the rows must be New alerts of every severity, and it is a new document.
    out.backPass = s.url === "/?status=new&severity=" && s.status === "new" && s.severity === ""
      && s.rows === "Critical+High+Medium+Low+Info" && s.statuses === "New" && s.document.startsWith("new document");
    // the Analyst/Home switch keeps the filter
    await page.click(".mode-switch button[value=home]");
    await page.waitForLoadState("load");
    await L.sleep(500);
    out.afterHomeSwitch = await state(page);
    out.switchPass = out.afterHomeSwitch.url === "/?status=new&severity=" && out.afterHomeSwitch.status === "new" && out.afterHomeSwitch.mode === "mode-home";
    await page.click(".mode-switch button[value=analyst]");
    await page.waitForLoadState("load");
    // Back while the server is unreachable
    await page.selectOption("#severity", "high");
    await page.waitForURL(/severity=high/);
    await L.sleep(500);
    await page.evaluate(() => { window.__marker = 1; });
    await server.stop();
    let err = null;
    try { await page.goBack({ timeout: 10000 }); } catch (e) { err = e.message.split("\n")[0]; }
    await L.sleep(1500);
    out.backWhileDown = await page.evaluate(() => ({
      href: location.href, title: document.title,
      alertsTable: !!document.getElementById("alerts"),
      marker: window.__marker === 1 ? "same document" : "new document",
      text: document.body.innerText.replace(/\s+/g, " ").trim().slice(0, 120),
    })).catch((e) => ({ evaluateError: e.message.split("\n")[0] }));
    out.backWhileDown.gobackError = err;
    const d = out.backWhileDown;
    out.downPass = !d.alertsTable && (/(reached|refused|connect)/i.test(d.text || "") || /chrome-error/.test(d.href || ""));
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
