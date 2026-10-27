// Find what makes a page wider than the viewport: text-node ranges and elements whose
// scrollWidth exceeds their clientWidth. Usage: node diag_overflow.js <buildKey> <width> <mode>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");
const [KEY, WIDTH, MODE] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  await L.withServer(KEY, "diag", async (srv) => {
    const tid = await L.telnetId(srv.base);
    const ctx = await browser.newContext({ viewport: { width: +WIDTH, height: 800 } });
    await ctx.addCookies([{ name: "mg_mode", value: MODE, url: srv.base }]);
    const page = await ctx.newPage();
    await page.goto(srv.base + "/alerts/" + tid);
    const r = await page.evaluate(() => {
      const cw = document.documentElement.clientWidth;
      const out = { scrollWidth: document.documentElement.scrollWidth, clientWidth: cw, texts: [], scrollers: [] };
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let n;
      while ((n = walker.nextNode())) {
        if (!n.textContent.trim()) continue;
        const range = document.createRange(); range.selectNodeContents(n);
        const right = Math.max(...[...range.getClientRects()].map((x) => x.right), 0);
        if (right > cw + 0.5) {
          let p = n.parentElement, chain = [];
          while (p && p !== document.body) { chain.unshift(p.tagName.toLowerCase() + (p.className ? "." + p.className : "") + (p.id ? "#" + p.id : "")); p = p.parentElement; }
          out.texts.push({ text: n.textContent.trim().slice(0, 90), right: Math.round(right), path: chain.join(" > "),
            ws: getComputedStyle(n.parentElement).whiteSpace, wrap: getComputedStyle(n.parentElement).overflowWrap });
        }
      }
      for (const e of document.querySelectorAll("body *")) {
        if (e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX === "visible" && e.clientWidth > 0)
          out.scrollers.push(`${e.tagName.toLowerCase()}${e.className ? "." + e.className : ""} scrollWidth=${e.scrollWidth} clientWidth=${e.clientWidth}`);
      }
      out.scrollers = out.scrollers.slice(0, 12);
      return out;
    });
    console.log(JSON.stringify(r, null, 1));
    await ctx.close();
  });
  await browser.close();
})();
