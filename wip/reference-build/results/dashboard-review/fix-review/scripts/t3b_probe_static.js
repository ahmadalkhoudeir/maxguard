// Is bfcache working at all in this Playwright Chromium? Two static pages, no scripts.
"use strict";
const { chromium } = require("playwright");
const http = require("http");
(async () => {
  const srv = http.createServer((req, res) => {
    res.writeHead(200, { "content-type": "text/html" });
    res.end(`<!doctype html><title>${req.url}</title><a id="next" href="/b">next</a>`);
  }).listen(0, "127.0.0.1");
  await new Promise((r) => srv.once("listening", r));
  const port = srv.address().port;
  for (const opts of [{}, { channel: "chromium" }]) {
    const browser = await chromium.launch({ ...opts, ignoreDefaultArgs: ["--disable-back-forward-cache"] });
    const page = await (await browser.newContext()).newPage();
    await page.goto(`http://127.0.0.1:${port}/a`);
    await page.evaluate(() => { window.__marker = "kept"; });
    await page.click("#next");
    await page.waitForURL(/\/b$/);
    await page.goBack({ waitUntil: "commit" });
    await page.waitForTimeout(500);
    const info = await page.evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      const flat = [];
      const walk = (r) => { if (!r) return; for (const x of r.reasons || []) flat.push(x.reason); for (const c of r.children || []) walk(c); };
      walk(nav.notRestoredReasons);
      return { marker: window.__marker || "lost", notRestored: flat.join(",") };
    });
    console.log(JSON.stringify(opts), browser.version(), JSON.stringify(info));
    await browser.close();
  }
  srv.close();
})();
