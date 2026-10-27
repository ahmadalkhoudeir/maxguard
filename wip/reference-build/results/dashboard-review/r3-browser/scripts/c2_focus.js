// Check 2: keyboard focus survives (a) a live refresh of the queue caused by a PATCH
// from another client while an alert link has focus, and (b) Save on the alert page
// pressed with the keyboard only.  Usage: node c2_focus.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const active = (page) => page.evaluate(() => {
  const a = document.activeElement;
  if (!a || a === document.body) return "<body> (focus lost)";
  return `${a.tagName}${a.id ? "#" + a.id : ""}${a.getAttribute("href") ? " href=" + a.getAttribute("href") : ""} focus-visible=${a.matches(":focus-visible")}`;
});

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "ftp");
    await L.upload(server.port, "imap");
    await L.upload(server.port, "telnet");
    const ctx = await L.newContext(browser);
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    await L.sleep(1000);
    const hrefs = await page.evaluate(() => [...document.querySelectorAll("#alerts tbody a")].map((a) => a.getAttribute("href")));
    out.rows = hrefs.length;
    const target = hrefs[hrefs.length - 1];           // the last alert's link, reached with Tab
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press("Tab");
      const h = await page.evaluate(() => document.activeElement && document.activeElement.getAttribute("href"));
      if (h === target) break;
    }
    out.focusBefore = await active(page);
    // another client changes an alert: the stream sends alerts-changed, the table reloads
    const other = (await L.alerts(server.port)).find((a) => "/alerts/" + a.finding_id !== target);
    const t0 = Date.now();
    await L.patchAlert(server.port, other.finding_id, { actor: "Fiona", assignee: "Fiona-" + t0 });
    const r = await L.waitFor(() => page.evaluate((n) => [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((t) => t.textContent === n), "Fiona-" + t0), 6000);
    out.refreshShown = r.ok ? `after ${r.ms} ms` : "NOT within 6 s";
    await L.sleep(300);
    out.focusAfterRefresh = await active(page);
    out.a_pass = r.ok && out.focusAfterRefresh === out.focusBefore && out.focusBefore.includes("href=" + target);

    // (b) the alert page: Tab to Status, ArrowDown, Tab to Save, Enter
    await page.goto(server.origin + target);
    for (let i = 0; i < 80; i++) {
      await page.keyboard.press("Tab");
      if ((await page.evaluate(() => document.activeElement.id)) === "alert-status") break;
    }
    out.statusFocused = await active(page);
    await page.keyboard.press("ArrowDown");
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press("Tab");
      if ((await page.evaluate(() => document.activeElement.tagName)) === "BUTTON") break;
    }
    out.saveFocused = await page.evaluate(() => document.activeElement.outerHTML);
    await page.keyboard.press("Enter");
    await page.waitForSelector("#status-form .message", { timeout: 8000 });
    await L.sleep(300);
    out.message = (await page.textContent("#status-form .message")).trim();
    out.focusAfterSave = await active(page);
    out.b_pass = out.focusAfterSave.startsWith("BUTTON#status-save") && out.message === "Saved.";
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
