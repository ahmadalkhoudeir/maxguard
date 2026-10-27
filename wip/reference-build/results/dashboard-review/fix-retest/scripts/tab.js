// Every control reachable with Tab, in DOM order, on every page, both modes, 1280 and 375 px.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

async function controls(page) {
  return page.evaluate(() => {
    const sel = 'a[href], button, input:not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])';
    let i = 0;
    const out = [];
    for (const el of document.querySelectorAll(sel)) {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden" || el.disabled) continue;
      if (el.closest("[hidden], [inert]")) continue;
      el.dataset.tabKey = "k" + (i++);
      out.push({ key: el.dataset.tabKey, label: `${el.tagName.toLowerCase()}${el.id ? "#" + el.id : ""} "${(el.textContent || el.value || el.name || "").trim().slice(0, 24)}"` });
    }
    return out;
  });
}

async function runBuild(browser, buildName, records) {
  const s = await L.startServer(buildName, "tab");
  const rows = [];
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    const pages = ["/", "/upload"];
    if (buildName.endsWith("AHM-03")) pages.push(`/alerts/${id}`, "/alerts/0000000000000000", "/?status=bogus");
    for (const mode of ["analyst", "home"]) {
      for (const width of [1280, 375]) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 } });
        if (mode === "home") await ctx.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
        const page = await ctx.newPage();
        L.instrument(page, `${buildName} tab ${mode} ${width}`, records);
        for (const p of pages) {
          const first = p === "/" ? page.waitForResponse((r) => r.url().includes("/?status="), { timeout: 4000 }).catch(() => null) : null;
          await page.goto(s.base + p);
          if (first) await first;
          await page.waitForTimeout(300);
          const list = await controls(page);
          const seen = [];
          for (let n = 0; n < list.length + 3; n++) {
            await page.keyboard.press("Tab");
            seen.push(await page.evaluate(() => {
              const e = document.activeElement;
              return e && e !== document.body ? (e.dataset.tabKey || `UNLISTED ${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""}`) : "BODY";
            }));
          }
          const firstPass = seen.slice(0, list.length);
          const missing = list.filter((c) => !seen.includes(c.key)).map((c) => c.label);
          const inOrder = firstPass.every((k, i) => k === list[i].key);
          rows.push({ build: buildName, page: p.replace(id, "<telnet id>"), mode, width, controls: list.length,
            reached: list.length - missing.length, missing, inDomOrder: inOrder, unlisted: seen.filter((k) => k.startsWith("UNLISTED")),
            order: list.map((c) => c.label).join(" > ") });
        }
        await ctx.close();
      }
    }
  } finally {
    await L.stopServer(s);
  }
  return rows;
}

(async () => {
  const builds = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(L.BUILDS);
  const browser = await chromium.launch();
  const records = [];
  let rows = [];
  try {
    rows = (await Promise.all(builds.map((b) => runBuild(browser, b, records)))).flat();
  } finally {
    await browser.close();
    await L.stopAll();
  }
  L.writeJSON("tab.json", rows);
  for (const r of rows) {
    console.log(`${r.build} | ${r.page} | ${r.mode} | ${r.width} | ${r.reached}/${r.controls} reached | DOM order ${r.inDomOrder} | missing ${r.missing.join(", ") || "-"} | unlisted ${r.unlisted.join(", ") || "-"}`);
  }
  const seenOrders = new Map();
  for (const r of rows.filter((x) => x.width === 375)) seenOrders.set(`${r.build} ${r.page} ${r.mode}`, r.order);
  for (const [k, v] of seenOrders) if (k.startsWith("fixed-AHM-03")) console.log("ORDER", k, ":", v);
  const sum = L.summarizeRecords(records);
  console.log("console errors (excluding the 404/400 documents):", sum.consoleErrors.filter((e) => !/status of (404|400)/.test(e)), "outside:", sum.outside, "requests:", sum.requests);
})();
