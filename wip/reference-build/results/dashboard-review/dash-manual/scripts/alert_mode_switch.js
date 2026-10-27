"use strict";
const { chromium } = require("playwright");
const { DESCRIBE } = require("./lib.js");
const [BASE, FINDING] = process.argv.slice(2);
async function active(page) { return page.evaluate(`(${DESCRIBE})(document.activeElement)`); }
async function tabTo(page, wanted) {
  for (let i = 0; i < 20; i++) { await page.keyboard.press("Tab"); if ((await active(page)).includes(wanted)) return; }
  throw new Error("no " + wanted);
}
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  const out = { start: await page.locator("main h1").innerText() };
  await tabTo(page, "button[name=mode][value=home]");
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Enter")]);
  out.afterEnterOnHome = { url: page.url(), h1: await page.locator("main h1").innerText(),
                           badge: await page.locator("main .sev").innerText() };
  await tabTo(page, "button[name=mode][value=analyst]");
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Space")]);
  out.afterSpaceOnAnalyst = { url: page.url(), h1: await page.locator("main h1").innerText() };
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
