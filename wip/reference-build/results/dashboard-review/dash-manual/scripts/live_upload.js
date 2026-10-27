// AHM-02 step 8, part 1: queue open in tab A, upload in tab B (keyboard only),
// the Telnet alert must appear in tab A without a reload. Timed.
// usage: node live_upload.js <base url> <zip path> <out dir> <label>
"use strict";
const { chromium } = require("playwright");
const { recordContext, watchPage } = require("./lib.js");

const [BASE, ZIP, OUT, LABEL] = process.argv.slice(2);

(async () => {
  const log = { requests: [], console: [], pageErrors: [] };
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  recordContext(context, log);

  // ---- tab A: the queue
  const tabA = await context.newPage();
  tabA.__name = "A";
  watchPage(tabA, log);
  let mainNavs = 0;
  tabA.on("framenavigated", (f) => { if (f === tabA.mainFrame()) mainNavs++; });
  await tabA.goto(BASE + "/", { waitUntil: "load" });
  const before = await tabA.locator("#alerts").innerText();
  await tabA.waitForTimeout(1500); // let the EventSource connect and its first refresh finish
  const navsBefore = mainNavs;
  await tabA.evaluate(() => {
    window.__marker = "tab A, never reloaded";
    window.__appearedAt = null;
    const check = () => {
      if (!window.__appearedAt && document.querySelector('#alerts a[href^="/alerts/"]')) {
        window.__appearedAt = Date.now();
      }
    };
    new MutationObserver(check).observe(document.body, { childList: true, subtree: true });
  });

  // ---- tab B: the upload page, keyboard only
  const tabB = await context.newPage();
  tabB.__name = "B";
  watchPage(tabB, log);
  await tabB.goto(BASE + "/upload", { waitUntil: "load" });
  const stops = [];
  for (let i = 0; i < 15; i++) {
    await tabB.keyboard.press("Tab");
    const id = await tabB.evaluate(() => document.activeElement.id || document.activeElement.tagName);
    stops.push(id);
    if (id === "file") break;
  }
  const [chooser] = await Promise.all([
    tabB.waitForEvent("filechooser", { timeout: 5000 }),
    tabB.keyboard.press("Space"),        // Space on the focused file input opens the file picker
  ]);
  await chooser.setFiles(ZIP);
  await tabB.keyboard.press("Tab");
  const onButton = await tabB.evaluate(() => document.activeElement.outerHTML);
  const t0 = Date.now();
  const [response] = await Promise.all([
    tabB.waitForResponse((r) => r.url().endsWith("/api/analyses") && r.request().method() === "POST",
                         { timeout: 120000 }),
    tabB.keyboard.press("Enter"),
  ]);
  const t1 = Date.now();
  const uploadStatus = response.status();
  const uploadBody = await response.text();
  await tabB.waitForFunction(() => document.getElementById("upload-result").textContent.trim() !== "",
                             null, { timeout: 10000 });
  const resultText = await tabB.locator("#upload-result").innerText();
  await tabB.screenshot({ path: `${OUT}/upload${LABEL}.png`, fullPage: true });

  // ---- back to tab A: did the alert appear by itself?
  let appeared = null;
  try {
    await tabA.waitForFunction(() => window.__appearedAt !== null, null, { timeout: 45000, polling: 50 });
    appeared = await tabA.evaluate(() => window.__appearedAt);
  } catch (e) { appeared = null; }
  const marker = await tabA.evaluate(() => window.__marker);
  const rowText = await tabA.locator("#alerts").innerText();
  await tabA.bringToFront();
  await tabA.screenshot({ path: `${OUT}/queue-telnet${LABEL}.png`, fullPage: true });

  const tableFetches = log.requests.filter((r) => r.page === "A" && r.url.startsWith(BASE + "/?"));
  console.log(JSON.stringify({
    queueBefore: before,
    tabStopsToFileInput: stops,
    focusedAfterFileTab: onButton,
    uploadHttpStatus: uploadStatus, uploadBody, uploadResultText: resultText,
    msFromEnterToResponse: t1 - t0,
    msFromResponseToAlertInTabA: appeared ? appeared - t1 : "NOT WITHIN 45 s",
    msFromEnterToAlertInTabA: appeared ? appeared - t0 : null,
    tabAMainFrameNavigationsDuringUpload: mainNavs - navsBefore,
    tabAMarkerStillThere: marker,
    tabAQueueAfter: rowText,
    tabATableFetches: tableFetches,
    pageErrors: log.pageErrors, console: log.console,
    allRequestUrls: [...new Set(log.requests.map((r) => r.method + " " + r.url))],
  }, null, 1));
  await browser.close();
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
