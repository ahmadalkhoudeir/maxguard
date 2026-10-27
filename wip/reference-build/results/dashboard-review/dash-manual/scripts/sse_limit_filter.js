// With 6 queue tabs open, does a filter change inside one of them still get an answer?
"use strict";
const { chromium } = require("playwright");
const [BASE] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const queues = [];
  for (let i = 0; i < 6; i++) {
    const page = await context.newPage();
    await Promise.all([page.waitForResponse((r) => r.url().includes("/api/stream")), page.goto(BASE + "/")]);
    queues.push(page);
  }
  const page = queues[2];
  await page.focus("#status");
  const t0 = Date.now();
  let answered;
  try {
    await Promise.all([page.waitForResponse((r) => r.url().includes("status=new"), { timeout: 8000 }),
                       page.keyboard.press("ArrowDown")]);
    answered = `answered after ${Date.now() - t0} ms`;
  } catch (e) { answered = `NO ANSWER after ${Date.now() - t0} ms`; }
  console.log(JSON.stringify({ queueTabsOpen: 6, filterChangeInTab3: answered,
    tableCaption: (await page.locator("#alerts").innerText()).split("\n")[0] }));
  await browser.close();
})();
