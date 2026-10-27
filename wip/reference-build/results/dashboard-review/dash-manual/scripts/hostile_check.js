"use strict";
const { chromium } = require("playwright");
const [BASE, FINDING, SHOT] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const dialogs = [], csp = [], errors = [];
  page.on("dialog", (d) => { dialogs.push(d.message()); d.dismiss(); });
  page.on("console", (m) => { if (/Content Security Policy|Refused/.test(m.text())) csp.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  await page.waitForTimeout(1000);
  const r = await page.evaluate(() => {
    const li = document.querySelector(".ai-sentences li");
    return { pwned: window.__pwned === 1, scriptsInList: li.querySelectorAll("script, b, img").length,
             shownText: li.innerText, html: li.innerHTML.trim().slice(0, 200) };
  });
  await page.screenshot({ path: SHOT });
  console.log(JSON.stringify({ ...r, dialogs, cspMessages: csp, errors }, null, 1));
  await browser.close();
})();
