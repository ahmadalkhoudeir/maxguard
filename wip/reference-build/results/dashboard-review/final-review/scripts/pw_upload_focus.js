// Where is keyboard focus when an upload finishes, if the person moved on while it ran?
// Usage: node pw_upload_focus.js <base-url> <zip>
"use strict";
const { chromium } = require("playwright");
const [BASE, ZIP] = [process.argv[2], process.argv[3]];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(BASE + "/upload");
  await page.setInputFiles("#file", ZIP);
  await page.route("**/api/analyses", async (route) => { await sleep(2500); await route.continue(); });
  await page.focus("#upload-form button");
  await page.keyboard.press("Enter");
  await sleep(300);
  const during = await page.evaluate(() => document.activeElement.tagName);
  // the person moves on while the analysis runs: Tab to "Go to the alert queue"
  await page.focus("text=Go to the alert queue");
  const moved = await page.evaluate(() => document.activeElement.textContent.trim());
  await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "", null, { timeout: 30000 });
  await sleep(200);
  const after = await page.evaluate(() => `${document.activeElement.tagName} "${document.activeElement.textContent.trim()}"`);
  console.log(`during the upload: ${during}; the person moved focus to: "${moved}"; when the answer came: ${after}`);
  console.log("result:", await page.textContent("#upload-result"));
  await browser.close();
})();
