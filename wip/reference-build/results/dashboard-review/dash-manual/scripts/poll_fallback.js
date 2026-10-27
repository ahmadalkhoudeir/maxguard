// The live stream is down (every /api/stream request fails): does the 30 s poll still
// bring a change into the open queue? usage: node poll_fallback.js <base url> <finding id>
"use strict";
const { chromium } = require("playwright");
const [BASE, FINDING] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  let streamAttempts = 0;
  await context.route("**/api/stream*", (route) => { streamAttempts++; route.abort(); });
  const page = await context.newPage();
  await page.goto(BASE + "/", { waitUntil: "load" });
  await page.waitForTimeout(500);
  const t0 = Date.now();
  await fetch(`${BASE}/api/alerts/${FINDING}`, { method: "PATCH", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actor: "dash-manual poll test", assignee: "Poll Check" }) });
  await page.waitForFunction(() => document.querySelector("#alerts").innerText.includes("Poll Check"),
                             null, { timeout: 45000, polling: 200 });
  const seconds = ((Date.now() - t0) / 1000).toFixed(1);
  await fetch(`${BASE}/api/alerts/${FINDING}`, { method: "PATCH", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actor: "dash-manual poll test", assignee: "" }) });
  console.log(JSON.stringify({ streamAttemptsBlocked: streamAttempts, secondsUntilChangeShown: seconds }));
  await browser.close();
})().catch((e) => { console.error("SCRIPT ERROR", e.message); process.exit(1); });
