// Check 13: open the alert page, stop the server, change the status and Save: the form must
// say "Not saved: the MaxGuard server could not be reached." (never "Saved."); start the
// server again and confirm the store did not change.
// A: exactly those steps.  B: the same after one successful save (an earlier "Saved." on screen).
// Usage: node check13_down.js <buildKey>   (AHM-03 builds)
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");
const KEY = process.argv[2];

async function formText(page) {
  return page.evaluate(() => {
    const m = document.querySelector("#status-form .message");
    return { message: m ? m.textContent.trim() : null, messageRole: m ? m.getAttribute("role") : null,
             select: document.getElementById("alert-status").value };
  });
}

(async () => {
  const browser = await chromium.launch();
  const build = L.BUILDS[KEY];
  const data = L.newDataDir(`c13-${KEY}`);
  const port = await L.freePort();
  let srv = await L.startServer(build, data, port, `c13-${KEY}`);
  await L.upload(srv.base, L.ZIP);
  const tid = await L.telnetId(srv.base);
  const out = {};
  try {
    for (const variant of ["A", "B"]) {
      const ctx = await browser.newContext();
      const page = await ctx.newPage();
      const errors = [];
      page.on("console", (m) => { if (m.type() === "error") errors.push(m.text().slice(0, 120)); });
      await page.goto(srv.base + "/alerts/" + tid);
      await page.fill("#actor", "Ahmad");
      let first = null;
      if (variant === "B") {
        await page.selectOption("#alert-status", "investigating");
        await page.click("#status-form button[type=submit]");
        await page.waitForSelector("#status-form .message");
        first = await formText(page);
      }
      const storeBefore = (await L.api(srv.base, "GET", "/api/alerts/" + tid)).json;
      const auditBefore = (await L.api(srv.base, "GET", "/api/audit")).json;
      const stopped = await L.stopServer(srv);
      await page.selectOption("#alert-status", "resolved");
      await page.click("#status-form button[type=submit]");
      await L.sleep(2000);
      const down = await formText(page);
      const section = await page.evaluate(() => document.querySelector("section[aria-labelledby=status-heading]").innerText.replace(/\s+/g, " ").trim());
      srv = await L.startServer(build, data, port, `c13-${KEY}`);
      const storeAfter = (await L.api(srv.base, "GET", "/api/alerts/" + tid)).json;
      const auditAfter = (await L.api(srv.base, "GET", "/api/audit")).json;
      // Save again now that the server is back: does the form recover?
      await page.click("#status-form button[type=submit]");
      await L.sleep(1500);
      const backUp = await formText(page);
      const storeFinal = (await L.api(srv.base, "GET", "/api/alerts/" + tid)).json;
      await ctx.close();
      out[variant] = {
        firstSave: first, serverStop: stopped, whileDown: down, statusSectionText: section,
        storeBeforeStop: storeBefore.status, storeAfterRestart: storeAfter.status,
        auditRowsBefore: auditBefore.length, auditRowsAfterRestart: auditAfter.length,
        saveAfterRestart: backUp, storeAfterSecondSave: storeFinal.status, consoleErrors: errors,
        pass: down.message === "Not saved: the MaxGuard server could not be reached." &&
              storeAfter.status === storeBefore.status && auditAfter.length === auditBefore.length,
      };
      // reset for the next variant
      await L.api(srv.base, "PATCH", "/api/alerts/" + tid, { actor: "reset", status: "new" });
    }
  } finally {
    await L.stopServer(srv);
    await browser.close();
  }
  console.log(`== ${KEY} check 13 (server down):`);
  for (const [v, r] of Object.entries(out)) console.log(`   ${v}: ${JSON.stringify(r)}`);
})();
