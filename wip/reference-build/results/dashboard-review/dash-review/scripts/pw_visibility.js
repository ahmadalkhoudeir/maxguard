"use strict";
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  const a = await ctx.newPage(); await a.goto(process.argv[2] + "/upload");
  const b = await ctx.newPage(); await b.goto(process.argv[2] + "/upload");
  console.log("page A:", await a.evaluate(() => document.visibilityState), "| page B:", await b.evaluate(() => document.visibilityState));
  await a.bringToFront();
  console.log("after A.bringToFront -> A:", await a.evaluate(() => document.visibilityState), "| B:", await b.evaluate(() => document.visibilityState));
  await browser.close();
})();
