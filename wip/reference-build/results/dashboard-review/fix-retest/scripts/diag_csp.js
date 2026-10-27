// Which step makes htmx set an inline style (CSP error) on the alert page?
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

(async () => {
  const buildName = process.argv[2] || "fixed-AHM-03";
  const s = await L.startServer(buildName, "diagcsp");
  const browser = await chromium.launch();
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    for (const variant of ["keyboard-no-screenshot", "click-no-screenshot", "screenshot-then-click"]) {
      const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
      const page = await ctx.newPage();
      const log = [];
      page.on("console", (m) => { if (m.type() === "error") log.push(m.text().slice(0, 60) + " @" + ((m.location() || {}).url || "").split("/").pop()); });
      const styled = () => page.evaluate(() => [...document.querySelectorAll("[style]")].map((e) => `${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""} style="${e.getAttribute("style")}"`));
      await page.goto(`${s.base}/alerts/${id}`);
      const steps = [["loaded", await styled(), log.length]];
      if (variant === "screenshot-then-click") {
        await page.locator("#status-form").screenshot({ path: `${L.W}/shots/diag-csp.png` });
        steps.push(["after element screenshot", await styled(), log.length]);
      }
      if (variant.startsWith("keyboard")) {
        await page.focus("#actor");
        await page.keyboard.type("Ahmad");
        await page.keyboard.press("Tab");
        await page.keyboard.press("ArrowDown");
        await page.keyboard.press("Tab");
        await page.keyboard.type("Fiona");
        await page.keyboard.press("Tab");
        steps.push(["before Enter", await styled(), log.length]);
        await page.keyboard.press("Enter");
      } else {
        await page.fill("#actor", "Ahmad");
        await page.selectOption("#alert-status", "investigating");
        await page.fill("#assignee", "Fiona");
        steps.push(["before click", await styled(), log.length]);
        await page.click("#status-form button[type=submit]");
      }
      await page.waitForSelector("#status-form .message");
      await page.waitForTimeout(300);
      steps.push(["after save", await styled(), log.length]);
      console.log(`\n== ${buildName} ${variant}`);
      for (const st of steps) console.log("  ", st[0], "| [style] elements:", JSON.stringify(st[1]), "| console errors so far:", st[2]);
      console.log("   errors:", log);
      await ctx.close();
    }
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
