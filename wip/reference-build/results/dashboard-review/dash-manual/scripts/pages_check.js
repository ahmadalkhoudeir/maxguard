// AHM-02 step 8 part 2: every page at 375 px (no sideways scroll) and keyboard reachability.
// usage: node pages_check.js <base url> <out dir> <label> '<json list of paths>'
"use strict";
const { chromium } = require("playwright");
const { recordContext, focusables, tabWalk, overflow } = require("./lib.js");

const [BASE, OUT, LABEL, PATHS] = process.argv.slice(2);
const paths = JSON.parse(PATHS);
const EXPECTED_OUTLINE = "solid 3px rgb(227, 98, 9)"; // app.css: 3px solid var(--focus) #e36209

(async () => {
  const log = { requests: [], console: [], pageErrors: [] };
  const browser = await chromium.launch();
  const results = { narrow: [], keyboard: [] };

  // ---- 375 px: a narrowed desktop window, and phone emulation (like the device toolbar)
  const viewports = [
    { name: "375 window", opts: { viewport: { width: 375, height: 812 } } },
    { name: "375 phone emulation", opts: { viewport: { width: 375, height: 812 }, isMobile: true,
                                            hasTouch: true, deviceScaleFactor: 3 } },
  ];
  for (const vp of viewports) {
    for (const mode of ["analyst", "home"]) {
      const context = await browser.newContext(vp.opts);
      recordContext(context, log);
      await context.addCookies([{ name: "mg_mode", value: mode, url: BASE }]);
      const page = await context.newPage();
      page.__name = `${vp.name}/${mode}`;
      for (const path of paths) {
        const resp = await page.goto(BASE + path, { waitUntil: "load" });
        await page.waitForTimeout(300);
        const o = await overflow(page);
        results.narrow.push({ viewport: vp.name, mode, path, http: resp.status(),
                              contentType: resp.headers()["content-type"], ...o,
                              pass: o.scrollWidth <= 375 });
        if (vp.name === "375 window" && path === "/") {
          await page.screenshot({ path: `${OUT}/queue-375${LABEL}-${mode}.png`, fullPage: true });
        }
        if (vp.name === "375 window" && path.startsWith("/alerts/")) {
          const tag = path.endsWith("0000000000000000") ? "unknown" : "telnet";
          await page.screenshot({ path: `${OUT}/alert-375${LABEL}-${tag}-${mode}.png`, fullPage: true });
        }
      }
      await context.close();
    }
  }

  // ---- keyboard: Tab and Shift+Tab reach every link, button, select and input; focus visible
  for (const width of [1280, 375]) {
    for (const mode of ["analyst", "home"]) {
      const context = await browser.newContext({ viewport: { width, height: 800 } });
      recordContext(context, log);
      await context.addCookies([{ name: "mg_mode", value: mode, url: BASE }]);
      const page = await context.newPage();
      page.__name = `kb ${width}/${mode}`;
      for (const path of paths) {
        const resp = await page.goto(BASE + path, { waitUntil: "load" });
        if (!(resp.headers()["content-type"] || "").startsWith("text/html")) {
          results.keyboard.push({ width, mode, path, http: resp.status(), skipped: "not an HTML page" });
          continue;
        }
        await page.waitForTimeout(200);
        const expected = await focusables(page);
        const forward = await tabWalk(page, { max: expected.length + 5 });
        await page.evaluate(() => document.activeElement && document.activeElement.blur());
        const backward = await tabWalk(page, { max: expected.length + 5, shift: true });
        const reached = forward.map((s) => s.el);
        const missing = expected.filter((e) => !reached.includes(e));
        const notVisible = forward.filter((s) => !s.focusVisible || s.outline !== EXPECTED_OUTLINE);
        const offscreen = forward.filter((s) => !s.inViewport);
        results.keyboard.push({
          width, mode, path, http: resp.status(), focusables: expected.length,
          tabStops: reached, missing,
          backwardIsReverse: JSON.stringify(backward.map((s) => s.el)) ===
                             JSON.stringify([...reached].reverse()),
          focusNotVisible: notVisible, notInViewportWhenFocused: offscreen.map((s) => s.el),
          pass: missing.length === 0 && notVisible.length === 0 && offscreen.length === 0,
        });
      }
      await context.close();
    }
  }
  await browser.close();
  results.pageErrors = log.pageErrors;
  results.consoleMessages = log.console;
  results.requestOrigins = [...new Set(log.requests.map((r) => new URL(r.url).origin))];
  results.allRequestUrls = [...new Set(log.requests.map((r) => r.method + " " + r.url))];
  console.log(JSON.stringify(results, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
