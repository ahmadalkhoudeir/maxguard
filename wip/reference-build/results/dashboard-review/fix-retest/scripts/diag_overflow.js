// Find what makes a page wider than the viewport: element boxes AND text runs.
"use strict";
const L = require("./lib.js");
const { chromium } = require("playwright");

async function textOverflow(page) {
  return page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const out = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    let node;
    while ((node = walker.nextNode())) {
      if (!node.textContent.trim()) continue;
      range.selectNodeContents(node);
      let maxRight = 0;
      for (const r of range.getClientRects()) maxRight = Math.max(maxRight, r.right);
      if (maxRight > vw + 0.5) {
        const p = node.parentElement;
        let d = p.tagName.toLowerCase() + (p.id ? "#" + p.id : "") + (p.classList.length ? "." + [...p.classList].join(".") : "");
        const pr = p.getBoundingClientRect();
        out.push({ parent: d, parentRight: Math.round(pr.right), textRight: Math.round(maxRight), text: node.textContent.trim().slice(0, 160) });
      }
    }
    return { vw, scrollWidth: document.documentElement.scrollWidth, out };
  });
}

(async () => {
  const buildName = process.argv[2] || "fixed-AHM-03";
  const s = await L.startServer(buildName, "diag");
  const browser = await chromium.launch();
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    for (const [mode, p, w, font] of [["analyst", `/alerts/${id}`, 320, null], ["analyst", `/alerts/${id}`, 414, null],
      ["analyst", `/alerts/${id}`, 414, "DejaVu Sans"], ["home", "/", 320, "DejaVu Sans"], ["home", "/", 320, null],
      ["home", "/", 320, "Liberation Sans"], ["home", "/", 320, "Roboto"], ["home", "/", 360, "DejaVu Sans"]]) {
      const ctx = await browser.newContext({ viewport: { width: w, height: 800 } });
      if (mode === "home") await ctx.addCookies([{ name: "mg_mode", value: "home", url: s.base }]);
      const page = await ctx.newPage();
      await page.goto(s.base + p);
      await page.waitForTimeout(600);
      await L.setFont(page, font);
      const r = await textOverflow(page);
      console.log(`\n== ${buildName} ${mode} ${p.replace(id, "<id>")} ${w}px font=${font || "default"} scrollWidth=${r.scrollWidth} vw=${r.vw}`);
      for (const o of r.out.slice(0, 8)) console.log("  ", JSON.stringify(o));
      if (mode === "home" && p === "/") {
        const cells = await page.evaluate(() => [...document.querySelectorAll(".stack td")].map((td) => {
          const r = td.getBoundingClientRect();
          return `${td.dataset.label}: td ${Math.round(r.left)}-${Math.round(r.right)} ` + [...td.children].map((c) => `${c.tagName.toLowerCase()}${c.className ? "." + c.className.replace(/ /g, ".") : ""} w${Math.round(c.getBoundingClientRect().width)} r${Math.round(c.getBoundingClientRect().right)}`).join(" ");
        }));
        console.log("   cells:", cells.join(" | "));
      }
      await ctx.close();
    }
    const banner = await (await fetch(`${s.base}/alerts/${id}`)).text();
    const m = banner.match(/<div class="banner"[\s\S]*?<\/div>/);
    console.log("\nbanner HTML:", m ? m[0] : "(none)");
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
