// T11: the CSS change (.status-form, #upload-form get grid-template-columns: minmax(0, 1fr)).
// Measure both forms in the original and fixed builds: widths of every child, overflow
// past the form, and horizontal page scroll; several widths, fonts and long names.
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));
const FONTS = [null, "DejaVu Sans", "Liberation Sans", "Roboto", "Noto Sans"];
const WIDTHS = [1280, 375, 320];
const LONG = "Wolfeschlegelsteinhausenbergerdorffwelchevoralternwarengewissenhaftschaferswessenschafewarenwohlgepflegeundsorgfaltigkeitbeschutzenvorangreifendurchihrraubgierigfeindewelchevoralternzwolfhundert";

async function measure(page, formSel) {
  return page.evaluate((sel) => {
    const f = document.querySelector(sel);
    const cs = getComputedStyle(f);
    const fr = f.getBoundingClientRect();
    const contentRight = fr.right - parseFloat(cs.paddingRight) - parseFloat(cs.borderRightWidth);
    const kids = [...f.children].filter((k) => getComputedStyle(k).display !== "none").map((k) => {
      const r = k.getBoundingClientRect();
      return {
        el: k.tagName.toLowerCase() + (k.id && k.id !== "status-save" ? "#" + k.id : ""),
        w: Math.round(r.width),
        overflowPx: Math.max(0, Math.round(r.right - contentRight)),
        contentOverflowPx: Math.max(0, Math.round(k.scrollWidth - k.clientWidth)),
      };
    });
    return {
      tracks: cs.gridTemplateColumns,
      formW: Math.round(fr.width),
      kids,
      pageHScroll: document.scrollingElement.scrollWidth - document.scrollingElement.clientWidth,
      culprits: [...document.querySelectorAll("main *")].filter((e) => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1).slice(0, 3).map((e) => e.tagName.toLowerCase() + (e.className ? "." + e.className : "") + (e.id ? "#" + e.id : "")).join(" "),
    };
  }, formSel);
}

async function run(buildName, browser) {
  const server = await L.startServer(buildName);
  const results = {};
  try {
    await L.upload(server.port, "telnet");
    const [alert] = await L.alerts(server.port);
    await L.patchAlert(server.port, alert.finding_id, { actor: "t", assignee: LONG.slice(0, 100) });
    const ctx = await browser.newContext({ bypassCSP: true });  // only so the test can inject a font rule
    const page = await ctx.newPage();
    const cases = [
      ["upload", "/upload", "#upload-form", null],
      ["status-no-actor", `/alerts/${alert.finding_id}`, "#status-form", null],
      ["status-long-actor", `/alerts/${alert.finding_id}`, "#status-form", LONG.slice(0, 100)],
    ];
    for (const [name, url, sel, actor] of cases) {
      await ctx.clearCookies();
      if (actor) await ctx.addCookies([{ name: "mg_actor", value: encodeURIComponent(actor), url: server.origin }]);
      for (const w of WIDTHS) {
        await page.setViewportSize({ width: w, height: 800 });
        await page.goto(server.origin + url);
        for (const font of FONTS) {
          if (font) {
            await page.addStyleTag({ content: `html, body, input, button, select, label { font-family: "${font}" !important }` });
          }
          results[`${name} ${w}px ${font || "default"}`] = await measure(page, sel);
        }
      }
    }
    await ctx.close();
  } finally {
    await server.stop();
  }
  return results;
}

(async () => {
  const browser = await chromium.launch();
  try {
    const all = {};
    const names = builds.length ? builds : ["orig-03", "fixed-03"];
    for (const b of names) all[b] = await run(b, browser);
    const [a, b] = names;
    for (const key of Object.keys(all[a])) {
      const x = all[a][key], y = all[b][key];
      const same = JSON.stringify(x.kids) === JSON.stringify(y.kids) && x.pageHScroll === y.pageHScroll;
      const fmt = (m) => `form ${m.formW}px tracks[${m.tracks}] hscroll ${m.pageHScroll}px${m.pageHScroll ? " (" + m.culprits + ")" : ""} | ` +
        m.kids.map((k) => `${k.el}:${k.w}${k.overflowPx ? " OVER+" + k.overflowPx : ""}${k.contentOverflowPx ? " text+" + k.contentOverflowPx : ""}`).join(" ");
      if (same) console.log(`SAME     ${key}: ${fmt(y)}`);
      else console.log(`DIFFERS  ${key}\n   ${a}: ${fmt(x)}\n   ${b}: ${fmt(y)}`);
    }
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
