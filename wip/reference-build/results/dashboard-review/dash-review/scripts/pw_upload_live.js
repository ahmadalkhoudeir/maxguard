"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  const queue = await ctx.newPage(); await queue.goto(BASE + "/");
  console.log("queue before:", (await queue.textContent("#alerts")).trim().replace(/\s+/g, " ").slice(0, 60));
  const up = await ctx.newPage(); await up.goto(BASE + "/upload");
  await up.setInputFiles("#file", process.env.UPLOAD_ZIP);
  const t0 = Date.now();
  await up.click("#upload-form button");
  await up.waitForFunction(() => document.getElementById("upload-result").textContent !== "");
  console.log("upload tab says:", await up.textContent("#upload-result"));
  await queue.waitForFunction(() => document.getElementById("alerts").textContent.includes("Telnet session in cleartext"), null, { timeout: 40000 });
  console.log(`queue tab shows the Telnet alert ${((Date.now() - t0) / 1000).toFixed(1)} s after Analyze, without reloading`);
  await browser.close();
})();
