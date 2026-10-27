// Screenshot just the AI section of the alert page (for the bad-citation result).
"use strict";
const { chromium } = require("playwright");
const [BASE, FINDING, SHOT] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  await page.locator('section[aria-labelledby="ai-heading"]').screenshot({ path: SHOT });
  await browser.close();
})();
