// F3: keyboard-only Save keeps focus on the Save button. F5: the alert page <title>.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

const desc = (page) => page.evaluate(() => {
  const e = document.activeElement;
  if (!e || e === document.body) return "BODY (focus lost)";
  let s = e.tagName.toLowerCase();
  if (e.id) s += "#" + e.id;
  const href = e.getAttribute("href");
  return `${s}${href ? " href=" + href : ""} "${(e.textContent || e.value || "").trim().slice(0, 30)}"`;
});
const onSave = (page) => page.evaluate(() => {
  const e = document.activeElement;
  return { onSave: !!e && e.tagName === "BUTTON" && e.type === "submit" && !!e.closest("#status-form") && e.isConnected,
    focusVisible: !!e && e !== document.body && e.matches(":focus-visible") };
});

async function tabUntil(page, pred, max = 60) {
  for (let n = 1; n <= max; n++) {
    await page.keyboard.press("Tab");
    if (await page.evaluate(pred)) return n;
  }
  throw new Error("Tab target not reached");
}

async function save(page, res, prefix, withName) {
  if (withName) {
    res[prefix + "tabsToName"] = await tabUntil(page, () => document.activeElement.id === "actor");
    await page.keyboard.type("Ahmad");
    await page.keyboard.press("Tab");
  } else {
    res[prefix + "tabsToStatus"] = await tabUntil(page, () => document.activeElement.id === "alert-status");
  }
  res[prefix + "onStatus"] = await desc(page);
  const v0 = await page.evaluate(() => document.getElementById("alert-status").value);
  await page.keyboard.press("ArrowDown");
  res[prefix + "statusChange"] = `${v0} -> ${await page.evaluate(() => document.getElementById("alert-status").value)}`;
  await page.keyboard.press("Tab");
  res[prefix + "onAssignee"] = await desc(page);
  await page.keyboard.press("Control+A");
  await page.keyboard.type(withName ? "Fiona" : "Jakub");
  await page.keyboard.press("Tab");
  res[prefix + "beforeEnter"] = await desc(page);
  const t0 = Date.now();
  await page.keyboard.press("Enter");
  await page.waitForFunction(() => {
    const m = document.querySelector("#status-form .message");
    return m && m.textContent.includes("Saved.");
  }, null, { timeout: 10000 });
  res[prefix + "savedMs"] = Date.now() - t0;
  await page.waitForTimeout(300);
  res[prefix + "afterSaved"] = await desc(page);
  Object.assign(res, Object.fromEntries(Object.entries(await onSave(page)).map(([k, v]) => [prefix + k, v])));
  await page.keyboard.press("Shift+Tab");
  res[prefix + "shiftTabAfter"] = await desc(page);
  await page.keyboard.press("Tab");  // back to Save (or wherever) for the next round
}

async function runBuild(browser, buildName, records) {
  const s = await L.startServer(buildName, "f3f5");
  const res = { build: buildName };
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    // F3
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage();
    const rec = L.instrument(page, `${buildName} f3`, records);
    await page.goto(`${s.base}/alerts/${id}`);
    await save(page, res, "first_", true);
    await page.evaluate(() => document.activeElement && document.activeElement.blur());
    await page.evaluate(() => window.scrollTo(0, 0));
    // second save: the name is now in the cookie, so the form has no name field
    await page.goto(`${s.base}/alerts/${id}`);
    await save(page, res, "second_", false);
    const api = await (await fetch(`${s.base}/api/alerts/${id}`)).json();
    res.serverState = `${api.status} / ${api.assignee}`;
    const audit = await (await fetch(`${s.base}/api/audit`)).json();
    res.audit = audit.map((a) => `${a.actor} ${a.action} ${a.target || ""}`.trim()).slice(0, 6);
    res.f3ConsoleErrors = rec.consoleErrors.length + rec.pageErrors.length;
    res.f3pass = res.first_onSave && res.second_onSave;
    await page.screenshot({ path: `${L.W}/shots/${buildName}-f3-after-second-save-1280.png` });
    await ctx.close();
    // F5
    for (const mode of ["analyst", "home"]) {
      const c = await browser.newContext();
      if (mode === "home") await c.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
      const p = await c.newPage();
      L.instrument(p, `${buildName} f5 ${mode}`, records);
      await p.goto(`${s.base}/alerts/${id}`);
      res[`title_${mode}`] = await p.title();
      res[`h1_${mode}`] = await p.evaluate(() => document.querySelector("h1").textContent.trim());
      await c.close();
    }
    const headline = "A device used Telnet, which sends everything you type, even passwords, without encryption.";
    res.f5pass = res.title_home === `${headline} · MaxGuard` && res.title_analyst === "Telnet session in cleartext · MaxGuard";
  } finally {
    await L.stopServer(s);
  }
  return res;
}

(async () => {
  const builds = process.argv.slice(2).length ? process.argv.slice(2) : ["fixed-AHM-03", "orig-AHM-03"];
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
  L.writeJSON("f3f5.json", { results, console: sum });
})();
