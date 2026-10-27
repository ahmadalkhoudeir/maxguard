// Follow an AI citation chip with the keyboard only: Tab to it, Enter, see where we land.
"use strict";
const { chromium } = require("playwright");
const { DESCRIBE } = require("./lib.js");
const [BASE, FINDING, SHOT] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 700 } });
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  let tabs = 0, now = "";
  for (; tabs < 30; tabs++) {
    await page.keyboard.press("Tab");
    now = await page.evaluate(`(${DESCRIBE})(document.activeElement)`);
    if (now.includes("a#") || now.includes("href=#ev-")) break;
  }
  const chipStyle = await page.evaluate(() => { const cs = getComputedStyle(document.activeElement);
    return cs.outlineStyle + " " + cs.outlineWidth + " " + cs.outlineColor; });
  await page.keyboard.press("Enter");
  await page.waitForTimeout(400);
  const landed = await page.evaluate(() => {
    const row = document.querySelector(location.hash);
    const r = row.getBoundingClientRect();
    return { hash: location.hash, active: document.activeElement.id || document.activeElement.tagName,
             rowBackground: getComputedStyle(row).backgroundColor, rowInView: r.top >= 0 && r.bottom <= innerHeight };
  });
  await page.screenshot({ path: SHOT });
  console.log(JSON.stringify({ tabsToFirstChip: tabs + 1, chip: now, chipFocusOutline: chipStyle, afterEnter: landed }, null, 1));
  await browser.close();
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
