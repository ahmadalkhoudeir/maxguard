// Investigate the /upload page at 375 px: widths, real sideways scroll, and a candidate CSS fix.
// usage: node upload_overflow.js <base url> <out dir> <label>
"use strict";
const { chromium } = require("playwright");
const [BASE, OUT, LABEL] = process.argv.slice(2);

const MEASURE = `(() => {
  const w = (sel) => { const e = document.querySelector(sel); if (!e) return null;
    const r = e.getBoundingClientRect(); return { left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width) }; };
  return { main: w("main"), card: w("#upload-form"), label: w("#upload-form label"), file: w("#file"),
           button: w("#upload-form button"), gridColumns: getComputedStyle(document.querySelector("#upload-form")).gridTemplateColumns,
           scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth };
})()`;

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const width of [320, 360, 375, 390, 414]) {
    const context = await browser.newContext({ viewport: { width, height: 700 } });
    const page = await context.newPage();
    await page.goto(BASE + "/upload", { waitUntil: "load" });
    out[width] = await page.evaluate(MEASURE);
    if (width === 375) {
      await page.screenshot({ path: `${OUT}/upload-375${LABEL}.png` });
      await page.evaluate(() => window.scrollTo(500, 0));
      out.scrollXAfterScrollTo500 = await page.evaluate(() => window.scrollX);
      await page.screenshot({ path: `${OUT}/upload-375${LABEL}-scrolled.png` });
    }
    await context.close();
  }
  // Candidate fix, tried in this browser only (bypassCSP lets the test inject one rule):
  const context = await browser.newContext({ viewport: { width: 375, height: 700 }, bypassCSP: true });
  const page = await context.newPage();
  await page.goto(BASE + "/upload", { waitUntil: "load" });
  await page.addStyleTag({ content: ".status-form, #upload-form { grid-template-columns: minmax(0, 1fr); }" });
  out.withCandidateFix = await page.evaluate(MEASURE);
  await page.screenshot({ path: `${OUT}/upload-375${LABEL}-candidate-fix.png` });
  await browser.close();
  console.log(JSON.stringify(out, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
