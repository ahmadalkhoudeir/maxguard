"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const list = await (await fetch(BASE + "/api/alerts")).json();
  const telnet = list.find((a) => a.rule_id === "cleartext.telnet").finding_id;
  for (const mode of ["analyst", "home"]) {
    const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
    await ctx.addCookies([{ name: "mg_mode", value: mode, url: BASE }]);
    const page = await ctx.newPage();
    for (const path of ["/", "/upload", "/alerts/" + telnet, "/alerts/nope", "/?status=bogus"]) {
      await page.goto(BASE + path);
      await page.waitForTimeout(300);
      const r = await page.evaluate(() => {
        const unlabeled = [...document.querySelectorAll("input:not([type=hidden]), select, textarea")]
          .filter((e) => !(e.labels && e.labels.length) && !e.getAttribute("aria-label") && !e.getAttribute("aria-labelledby"))
          .map((e) => e.outerHTML.slice(0, 60));
        const nameless = [...document.querySelectorAll("button, a[href]")].filter((e) => !e.textContent.trim()).map((e) => e.outerHTML.slice(0, 60));
        const focusable = [...document.querySelectorAll("a[href], button, select, input:not([type=hidden]), [tabindex]:not([tabindex='-1'])")];
        const sevNoText = [...document.querySelectorAll(".sev")].filter((e) => !e.textContent.trim()).length;
        const live = [...document.querySelectorAll("[aria-live], [role=status], [role=alert]")].map((e) => (e.id || e.className || e.tagName) + ":" + (e.getAttribute("aria-live") || e.getAttribute("role")));
        return { unlabeled, nameless, focusable: focusable.length, sevNoText, live };
      });
      // Tab through the page and count distinct elements reached
      const reached = new Set();
      await page.evaluate(() => document.activeElement && document.activeElement.blur());
      for (let i = 0; i < r.focusable + 5; i++) {
        await page.keyboard.press("Tab");
        const k = await page.evaluate(() => { const e = document.activeElement; return e && e !== document.body ? e.outerHTML.slice(0, 80) : null; });
        if (k) reached.add(k);
      }
      console.log(`${mode} ${path}: unlabeled=${JSON.stringify(r.unlabeled)} nameless=${JSON.stringify(r.nameless)} ` +
                  `focusable=${r.focusable} reachedByTab=${reached.size} sevBadgesWithoutText=${r.sevNoText} live=${JSON.stringify(r.live)}`);
    }
    await ctx.close();
  }
  await browser.close();
})();
