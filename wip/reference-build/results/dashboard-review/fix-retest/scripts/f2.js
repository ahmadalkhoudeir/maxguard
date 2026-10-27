// F2: keyboard focus on the Telnet link survives (a) a live refresh after a PATCH from
// another client and (b) the 30 s poll; the next Tab goes to the next control.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

const desc = (page) => page.evaluate(() => {
  const e = document.activeElement;
  if (!e || e === document.body) return "BODY (focus lost)";
  let s = e.tagName.toLowerCase();
  if (e.id) s += "#" + e.id;
  if (e.className && typeof e.className === "string") s += "." + e.className.replace(/ /g, ".");
  const href = e.getAttribute("href");
  return `${s}${href ? " href=" + href : ""} "${(e.textContent || "").trim().slice(0, 40)}"`;
});
const isLink = (page, id) => page.evaluate((i) => {
  const e = document.activeElement;
  return { isTelnetLink: !!e && e.getAttribute("href") === `/alerts/${i}`, connected: !!e && e.isConnected,
    focusVisible: !!e && e.matches(":focus-visible") };
}, id);

async function tabTo(page, id, max = 40) {
  for (let n = 1; n <= max; n++) {
    await page.keyboard.press("Tab");
    if ((await isLink(page, id)).isTelnetLink) return n;
  }
  throw new Error("could not Tab to the Telnet link");
}

async function runBuild(browser, buildName, records) {
  const s = await L.startServer(buildName, "f2");
  const res = { build: buildName };
  try {
    for (const f of ["telnet", "ftp", "plain_http"]) await L.upload(s, f);
    const list = await L.alerts(s);
    const id = list.find((a) => a.rule_id === "cleartext.telnet").finding_id;
    res.queueOrder = list.map((a) => a.title);
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();
    const rec = L.instrument(page, `${buildName} f2`, records);
    const refreshes = [];
    page.on("response", (r) => { if (r.url().includes("/?status=")) refreshes.push(Date.now()); });
    const first = page.waitForResponse((r) => r.url().includes("/?status="), { timeout: 5000 }).catch(() => null);
    await page.goto(s.base + "/");
    await first;  // the stream's first event refreshes the table once at start
    await page.waitForTimeout(400);
    res.tabsToTelnetLink = await tabTo(page, id);
    await page.keyboard.press("Tab");
    res.baselineNextTab = await desc(page);  // no refresh in between
    await page.keyboard.press("Shift+Tab");
    res.baselineBack = (await isLink(page, id)).isTelnetLink;

    // (a) another client changes the alert
    const before = refreshes.length;
    const t0 = Date.now();
    res.patch = (await L.patchAlert(s, id, { actor: "x", assignee: "Someone" })).status;
    await page.waitForFunction((i) => {
      const a = document.querySelector(`a[href="/alerts/${i}"]`);
      return a && a.closest("tr").textContent.includes("Someone");
    }, id, { timeout: 10000 });
    res.a_refreshMs = Date.now() - t0;
    res.a_refreshRequests = refreshes.length - before;
    await page.waitForTimeout(300);
    res.a_active = await desc(page);
    Object.assign(res, Object.fromEntries(Object.entries(await isLink(page, id)).map(([k, v]) => ["a_" + k, v])));
    await page.keyboard.press("Tab");
    res.a_nextTab = await desc(page);
    // put focus back on the Telnet link for (b)
    await page.keyboard.press("Shift+Tab");
    if (!(await isLink(page, id)).isTelnetLink) {
      await page.evaluate(() => document.activeElement && document.activeElement.blur());
      res.b_refocusTabs = await tabTo(page, id);
    }
    res.b_activeBeforePoll = await desc(page);

    // (b) the 30 s poll, nothing changed
    const lastSwap = refreshes[refreshes.length - 1];
    const tPoll = Date.now();
    const poll = await page.waitForResponse((r) => r.url().includes("/?status="), { timeout: 40000 });
    res.b_pollAfterLastRefreshS = Math.round((Date.now() - lastSwap) / 100) / 10;
    res.b_waitedS = Math.round((Date.now() - tPoll) / 100) / 10;
    res.b_pollStatus = poll.status();
    await page.waitForTimeout(400);
    res.b_active = await desc(page);
    Object.assign(res, Object.fromEntries(Object.entries(await isLink(page, id)).map(([k, v]) => ["b_" + k, v])));
    await page.keyboard.press("Tab");
    res.b_nextTab = await desc(page);
    res.consoleErrors = rec.consoleErrors.length + rec.pageErrors.length;
    res.pass = res.a_isTelnetLink && res.b_isTelnetLink && res.a_nextTab === res.baselineNextTab && res.b_nextTab === res.baselineNextTab;
    await ctx.close();
  } finally {
    await L.stopServer(s);
  }
  return res;
}

(async () => {
  const builds = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(L.BUILDS);
  const browser = await chromium.launch();
  const records = [];
  let results;
  try {
    results = await Promise.all(builds.map((b) => runBuild(browser, b, records)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
  for (const r of results) console.log(JSON.stringify(r, null, 1));
  const sum = L.summarizeRecords(records);
  console.log("console errors:", sum.consoleErrors, "outside:", sum.outside, "requests:", sum.requests);
  L.writeJSON("f2.json", { results, console: sum });
})();
