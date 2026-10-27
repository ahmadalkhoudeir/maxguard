// Each open queue tab keeps one /api/stream connection open. Chromium allows 6 HTTP/1.1
// connections per host. With N queue tabs open, can one more tab still load a page?
// usage: node sse_limit.js <base url> <N>
"use strict";
const { chromium } = require("playwright");
const [BASE, N] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();   // one browser profile, like one person's Chrome
  const queues = [];
  for (let i = 0; i < Number(N); i++) {
    const page = await context.newPage();
    await Promise.all([page.waitForResponse((r) => r.url().includes("/api/stream"), { timeout: 15000 }),
                       page.goto(BASE + "/", { waitUntil: "load", timeout: 15000 })]);
    queues.push(page);
  }
  const extra = await context.newPage();
  const t0 = Date.now();
  let loaded, error = null;
  try {
    await extra.goto(BASE + "/upload", { waitUntil: "load", timeout: 10000 });
    loaded = true;
  } catch (e) { loaded = false; error = e.message.split("\n")[0]; }
  const result = { queueTabsOpen: queues.length, extraTabLoadedUploadPage: loaded,
                   msWaited: Date.now() - t0, error };
  if (!loaded) {
    await queues[0].close();   // close one queue tab: does the stuck tab load now?
    const t1 = Date.now();
    try {
      await extra.waitForFunction(() => document.readyState === "complete" && !!document.getElementById("upload-form"),
                                  null, { timeout: 10000 });
      result.afterClosingOneQueueTab = { loaded: true, ms: Date.now() - t1 };
    } catch (e) { result.afterClosingOneQueueTab = { loaded: false }; }
  }
  console.log(JSON.stringify(result));
  await browser.close();
})().catch((e) => { console.error("SCRIPT ERROR", e.message); process.exit(1); });
