// F1 screenshots: status form at 375 px (fixed vs original), upload page at 320 px,
// and the two overflow cases that remain in both builds.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");
const SHOTS = L.W + "/shots";

async function formGeometry(page) {
  return page.evaluate(() => {
    const f = document.getElementById("status-form");
    const fr = f.getBoundingClientRect();
    const items = [...f.children].map((c) => {
      const r = c.getBoundingClientRect();
      return `${c.tagName.toLowerCase()}${c.id ? "#" + c.id : ""} x${Math.round(r.left)} w${Math.round(r.width)} h${Math.round(r.height)}`;
    });
    return { form: `x${Math.round(fr.left)} w${Math.round(fr.width)} h${Math.round(fr.height)}`, gridColumns: getComputedStyle(f).gridTemplateColumns, items,
      scrollWidth: document.documentElement.scrollWidth };
  });
}

(async () => {
  require("fs").mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch();
  const records = [];
  const out = {};
  try {
    for (const b of ["fixed-AHM-03", "orig-AHM-03"]) {
      const s = await L.startServer(b, "shots");
      try {
        await L.upload(s, "telnet");
        const id = await L.telnetId(s);
        const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
        const page = await ctx.newPage();
        L.instrument(page, `${b} shots`, records);
        await page.goto(`${s.base}/alerts/${id}`);
        const form = page.locator("#status-form");
        await form.scrollIntoViewIfNeeded();
        out[`${b} status form before save`] = await formGeometry(page);
        await form.screenshot({ path: `${SHOTS}/${b}-status-form-375.png` });
        // save once, so the form shows "Saved." and no name field
        await page.fill("#actor", "Ahmad");
        await page.selectOption("#alert-status", "investigating");
        await page.fill("#assignee", "Fiona");
        await page.click("#status-form button[type=submit]");
        await page.waitForSelector("#status-form .message");
        out[`${b} status form after save`] = await formGeometry(page);
        await page.locator("#status-form").screenshot({ path: `${SHOTS}/${b}-status-form-375-saved.png` });
        await page.screenshot({ path: `${SHOTS}/${b}-alert-analyst-375-full.png`, fullPage: true });
        // the upload page at 320 px
        await page.setViewportSize({ width: 320, height: 700 });
        await page.goto(`${s.base}/upload`);
        out[`${b} upload 320 scrollWidth`] = await page.evaluate(() => document.documentElement.scrollWidth);
        await page.screenshot({ path: `${SHOTS}/${b}-upload-320-full.png`, fullPage: true });
        await ctx.close();
        if (b.startsWith("fixed")) {
          // the remaining overflows, fixed build only
          const c2 = await browser.newContext({ viewport: { width: 320, height: 700 } });
          await c2.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
          const p2 = await c2.newPage();
          L.instrument(p2, `${b} shots home`, records);
          await p2.goto(`${s.base}/`);
          await p2.waitForTimeout(600);
          await L.setFont(p2, "DejaVu Sans");
          out[`${b} home queue 320 DejaVu scrollWidth`] = await p2.evaluate(() => document.documentElement.scrollWidth);
          await p2.screenshot({ path: `${SHOTS}/${b}-home-queue-320-dejavu-full.png`, fullPage: true });
          await c2.close();
          const c3 = await browser.newContext({ viewport: { width: 375, height: 700 } });
          const p3 = await c3.newPage();
          L.instrument(p3, `${b} shots banner`, records);
          await p3.goto(`${s.base}/alerts/${id}`);
          await p3.locator(".banner").scrollIntoViewIfNeeded();
          await p3.evaluate(() => window.scrollTo(10000, window.scrollY));
          out[`${b} alert 375 scrollX after scrolling right`] = await p3.evaluate(() => window.scrollX);
          await p3.screenshot({ path: `${SHOTS}/${b}-alert-banner-375-scrolled-right.png` });
          await c3.close();
        }
      } finally {
        await L.stopServer(s);
      }
    }
  } finally {
    await browser.close();
    await L.stopAll();
  }
  console.log(JSON.stringify(out, null, 1));
  console.log("console errors:", L.summarizeRecords(records).consoleErrors);
  L.writeJSON("f1-shots.json", out);
})();
