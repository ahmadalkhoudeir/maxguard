// F1: no sideways scrolling at phone widths, every page, both modes, four fonts.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

const WIDTHS = [320, 360, 375, 390, 414];
const FONTS = [null, ...L.FONTS];  // null = no override (system-ui -> Noto Sans here)
// --candidate: also apply a CSS change that would close the two remaining gaps
const CANDIDATE = process.argv.includes("--candidate")
  ? " .banner { overflow-wrap: anywhere; } .stack td .sev { white-space: normal; }" : "";

async function measure(page) {
  return page.evaluate(() => {
    const describe = (el) => {
      let s = el.tagName.toLowerCase();
      if (el.id) s += "#" + el.id;
      if (el.classList.length) s += "." + [...el.classList].join(".");
      if (el.type && el.tagName === "INPUT") s += `[type=${el.type}]`;
      return s;
    };
    const de = document.documentElement;
    window.scrollTo(0, 0);
    const vw = de.clientWidth;
    const res = { scrollWidth: de.scrollWidth, clientWidth: vw, innerWidth: window.innerWidth };
    window.scrollTo(100000, 0);
    res.scrollX = window.scrollX;  // how far the page really scrolls sideways
    window.scrollTo(0, 0);
    res.over = [];
    res.clipped = [];
    res.innerScrollers = [];
    for (const el of document.querySelectorAll("body *")) {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      if ((cs.overflowX === "auto" || cs.overflowX === "scroll") && el.scrollWidth > el.clientWidth) {
        res.innerScrollers.push({ el: describe(el), scrollWidth: el.scrollWidth, clientWidth: el.clientWidth });
      }
      if (r.right > vw + 0.5) {
        let clip = null;
        for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
          if (getComputedStyle(a).overflowX !== "visible") { clip = a; break; }
        }
        const item = { el: describe(el), right: Math.round(r.right * 10) / 10, width: Math.round(r.width * 10) / 10 };
        if (clip && clip.getBoundingClientRect().right <= vw + 0.5) {
          item.clippedBy = describe(clip);
          res.clipped.push(item);
        } else {
          res.over.push(item);
        }
      }
    }
    // text that runs out of its box (the box itself can be inside the viewport)
    res.textOver = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    let node;
    while ((node = walker.nextNode())) {
      if (!node.textContent.trim()) continue;
      const pcs = getComputedStyle(node.parentElement);
      if (pcs.display === "none" || pcs.visibility === "hidden") continue;
      range.selectNodeContents(node);
      let right = 0;
      for (const r of range.getClientRects()) right = Math.max(right, r.right);
      if (right > vw + 0.5) {
        let clipped = false;
        for (let a = node.parentElement; a && a !== document.body; a = a.parentElement) {
          if (getComputedStyle(a).overflowX !== "visible" && a.getBoundingClientRect().right <= vw + 0.5) { clipped = true; break; }
        }
        if (!clipped) res.textOver.push({ in: describe(node.parentElement), right: Math.round(right), text: node.textContent.trim().slice(0, 70) });
      }
    }
    res.font = getComputedStyle(document.body).fontFamily;
    return res;
  });
}

async function runBuild(browser, buildName, out, records) {
  const s = await L.startServer(buildName, "f1");
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    const pages = ["/", "/upload"];
    if (buildName.endsWith("AHM-03")) pages.push(`/alerts/${id}`, "/alerts/0000000000000000", "/?status=bogus");
    for (const mode of ["analyst", "home"]) {
      const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
      if (mode === "home") await ctx.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
      const page = await ctx.newPage();
      L.instrument(page, `${buildName} ${mode}`, records);
      for (const p of pages) {
        for (const w of WIDTHS) {
          await page.setViewportSize({ width: w, height: 800 });
          const refreshed = p === "/" ? page.waitForResponse((r) => r.url().includes("/?status="), { timeout: 4000 }).catch(() => null) : null;
          const resp = await page.goto(s.base + p, { waitUntil: "load" });
          if (refreshed) await refreshed;
          await page.waitForTimeout(150);
          for (const font of FONTS) {
            await L.setFont(page, font, CANDIDATE);
            const m = await measure(page);
            out.push({ build: buildName, page: p.replace(id, "<telnet id>"), status: resp.status(), mode, width: w,
              font: font || "default", ...m });
          }
          await L.setFont(page, null);
        }
      }
      await ctx.close();
    }
  } finally {
    await L.stopServer(s);
  }
}

(async () => {
  const args = process.argv.slice(2).filter((a) => !a.startsWith("--"));
  const builds = args.length ? args : Object.keys(L.BUILDS);
  const tag = CANDIDATE ? "f1-candidate" : "f1";
  const browser = await chromium.launch();
  const out = [];
  const records = [];
  try {
    for (const b of builds) await runBuild(browser, b, out, records);
  } finally {
    await browser.close();
    await L.stopAll();
  }
  L.writeJSON(`${tag}-raw.json`, out);
  const sum = L.summarizeRecords(records);
  L.writeJSON(`${tag}-console.json`, sum);
  // compact table: build x page x mode
  const groups = new Map();
  for (const r of out) {
    const k = `${r.build} | ${r.page} (${r.status}) | ${r.mode}`;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(r);
  }
  for (const [k, rows] of groups) {
    const bad = rows.filter((r) => r.scrollWidth > r.clientWidth || r.scrollX > 0 || r.over.length || r.textOver.length);
    const inner = rows.filter((r) => r.innerScrollers.length);
    const worst = rows.reduce((a, r) => (r.scrollWidth - r.clientWidth > a.scrollWidth - a.clientWidth ? r : a), rows[0]);
    const culprits = new Set();
    for (const r of bad) for (const o of r.over) if (!["table", "caption", "tbody", "tr", "td"].includes(o.el.split(/[#.]/)[0])) culprits.add(o.el);
    for (const r of bad) for (const o of r.textOver) culprits.add(`text in ${o.in} "${o.text.slice(0, 40)}"`);
    const badList = bad.map((r) => `${r.width}/${r.font === "default" ? "def" : r.font.split(" ")[0]}=${r.scrollWidth}`).join(" ");
    console.log(`${k} | combos ${rows.length} | sideways ${bad.length} | worst scrollWidth ${worst.scrollWidth} @${worst.width}px ${worst.font} (scrollX ${worst.scrollX}) | inner scrollers ${inner.length} | culprits ${[...culprits].slice(0, 4).join("; ")}${bad.length ? " | failing " + badList : ""}`);
  }
  console.log("console errors:", sum.consoleErrors.length, sum.consoleErrors.slice(0, 5));
  console.log("requests:", sum.requests, "outside app:", sum.outside);
})();
