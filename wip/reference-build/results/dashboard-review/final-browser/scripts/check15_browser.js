// Check 15 (browser part): every request the pages make stays on 127.0.0.1, and every control
// is reachable with Tab, on every page, both modes, 1280 and 375 px.
// Usage: node check15_browser.js <buildKey>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");
const KEY = process.argv[2];

async function tabReach(page) {
  // Number every control a keyboard user must reach, then Tab from the top and see which come up.
  const total = await page.evaluate(() => {
    const sel = "a[href], button, select, input:not([type=hidden]), textarea, [tabindex]";
    const els = [...document.querySelectorAll(sel)].filter((e) => !e.disabled && e.tabIndex >= 0 &&
      (e.getClientRects().length > 0 || e.classList.contains("skip")));
    els.forEach((e, i) => e.setAttribute("data-k", String(i)));
    return els.map((e) => `${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""} "${(e.textContent || e.value || "").trim().slice(0, 25)}"`);
  });
  await page.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
  await page.focus("body").catch(() => {});
  const reached = new Set();
  for (let i = 0; i < total.length + 4; i++) {
    await page.keyboard.press("Tab");
    const k = await page.evaluate(() => document.activeElement && document.activeElement.getAttribute("data-k"));
    if (k !== null && k !== undefined) reached.add(+k);
  }
  const missing = total.filter((_, i) => !reached.has(i));
  return { controls: total.length, reached: reached.size, missing };
}

(async () => {
  const browser = await chromium.launch();
  const r = await L.withServer(KEY, "c15", async (srv) => {
    L.addAlerts(srv.build, srv.data, ["critical", "medium", "low"], 150);
    const tid = await L.telnetId(srv.base);
    const ahm03 = KEY.endsWith("3");
    const pages = ["/", "/upload", "/?status=bogus"].concat(ahm03 ? ["/alerts/" + tid, "/alerts/0000000000000000"] : []);
    const urls = new Map();
    const tab = [];
    for (const mode of ["analyst", "home"]) {
      for (const width of [1280, 375]) {
        const ctx = await browser.newContext({ viewport: { width, height: 900 } });
        ctx.on("request", (q) => { const k = `${q.method()} ${q.url()}`; urls.set(k, (urls.get(k) || 0) + 1); });
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: srv.base }]);
        const page = await ctx.newPage();
        page.on("websocket", (ws) => urls.set("WEBSOCKET " + ws.url(), 1));
        for (const p of pages) {
          await page.goto(srv.base + p);
          await L.sleep(800);
          const t = await tabReach(page);
          tab.push({ mode, width, path: p.replace(tid, "<telnet>"), ...t });
        }
        // Interactions that make requests: a filter, the mode switch, an upload, a Save.
        await page.goto(srv.base + "/");
        await page.selectOption("#severity", "high");
        await page.waitForURL(/severity=high/);
        await Promise.all([page.waitForNavigation(), page.click(`.mode-switch button[value="${mode === "home" ? "analyst" : "home"}"]`)]);
        await page.goto(srv.base + "/upload");
        await page.setInputFiles("#file", L.ZIP);
        await page.click("#upload-form button");
        await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "", null, { timeout: 60000 });
        if (ahm03) {
          await ctx.addCookies([{ name: "mg_mode", value: "analyst", url: srv.base }]);
          await page.goto(srv.base + "/alerts/" + tid);
          if (await page.$("#actor")) await page.fill("#actor", "Ahmad");
          await page.click("#status-form button[type=submit]");
          await page.waitForSelector("#status-form .message");
        }
        await ctx.close();
      }
    }
    return { urls: [...urls.entries()], tab, base: srv.base };
  });
  const off = r.urls.filter(([k]) => !k.split(" ")[1].startsWith(r.base + "/"));
  const paths = [...new Set(r.urls.map(([k]) => k.split(" ")[0] + " " + new URL(k.split(" ")[1]).pathname))].sort();
  console.log(`== ${KEY} check 15 (browser): ${r.urls.reduce((s, [, n]) => s + n, 0)} requests, ${r.urls.length} distinct, ` +
              `${off.length} not to ${r.base}: ${JSON.stringify(off)}`);
  console.log(`   request paths: ${paths.join(", ")}`);
  const bad = r.tab.filter((t) => t.missing.length || t.reached !== t.controls);
  console.log(`   Tab reachability: ${r.tab.length} page views, ${bad.length} with a control Tab never reached`);
  for (const t of r.tab) console.log(`      ${t.mode} ${t.width} ${t.path}: ${t.reached}/${t.controls}${t.missing.length ? " missing " + JSON.stringify(t.missing) : ""}`);
  await browser.close();
})();
