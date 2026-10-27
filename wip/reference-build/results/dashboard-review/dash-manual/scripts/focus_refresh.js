// Keyboard focus on an alert link in the queue: what happens when the table refreshes?
// (1) a change made elsewhere (alerts-changed on /api/stream), (2) the 30 s fallback poll
// with nothing changed. usage: node focus_refresh.js <base url> <finding id> <wait poll: yes|no>
"use strict";
const { chromium } = require("playwright");
const { DESCRIBE } = require("./lib.js");
const [BASE, FINDING, WAIT_POLL] = process.argv.slice(2);
async function active(page) { return page.evaluate(`(${DESCRIBE})(document.activeElement)`); }
async function tabToLink(page) {
  for (let i = 0; i < 20; i++) {
    await page.keyboard.press("Tab");
    if ((await active(page)).includes(`href=/alerts/${FINDING}`)) return;
  }
  throw new Error("alert link not reached");
}
(async () => {
  const out = {};
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto(BASE + "/", { waitUntil: "load" });
  await page.waitForTimeout(1500);

  // (1) someone else changes the alert: the server sends alerts-changed, the table reloads
  await tabToLink(page);
  out.before = await active(page);
  const swapped = page.waitForResponse((r) => r.url().startsWith(BASE + "/?") && r.request().headers()["hx-request"] === "true");
  const t0 = Date.now();
  const res = await fetch(`${BASE}/api/alerts/${FINDING}`, {   // like another analyst's change
    method: "PATCH", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actor: "dash-manual focus test", assignee: "Another Analyst" }) });
  await swapped;
  await page.waitForTimeout(300);
  out.sseRefresh = { patchStatus: res.status, msToRefresh: Date.now() - t0, focusAfter: await active(page) };
  await page.keyboard.press("Tab");
  out.sseRefresh.nextTab = await active(page);

  // (2) nothing changes; just wait for the every-30-s poll
  if (WAIT_POLL === "yes") {
    await page.goto(BASE + "/", { waitUntil: "load" });
    await page.waitForTimeout(1500);
    await tabToLink(page);
    const polled = page.waitForResponse((r) => r.url().startsWith(BASE + "/?") && r.request().headers()["hx-request"] === "true",
                                        { timeout: 40000 });
    const t1 = Date.now();
    await polled;
    await page.waitForTimeout(300);
    out.pollRefresh = { secondsUntilPoll: ((Date.now() - t1) / 1000).toFixed(1), focusAfter: await active(page) };
  }
  // put the assignee back
  await fetch(`${BASE}/api/alerts/${FINDING}`, { method: "PATCH", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actor: "dash-manual focus test", assignee: "" }) });
  await browser.close();
  console.log(JSON.stringify(out, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
