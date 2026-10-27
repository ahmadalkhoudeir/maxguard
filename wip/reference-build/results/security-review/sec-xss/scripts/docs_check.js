// Open FastAPI's /docs and /redoc with every outside request aborted; record what they ask for.
"use strict";
const { chromium } = require("playwright");
const base = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const outside = [];
  await context.route("**/*", r => {
    const u = r.request().url();
    if (u.startsWith(base)) return r.continue();
    outside.push(r.request().resourceType() + " " + u);
    return r.abort();
  });
  const page = await context.newPage();
  for (const p of ["/docs", "/redoc"]) {
    const resp = await page.goto(base + p, { waitUntil: "load" });
    await page.waitForTimeout(800);
    const h = resp.headers();
    console.log(p, resp.status(), "CSP:", h["content-security-policy"] || "NONE",
                "| inline scripts:", await page.$$eval("script:not([src])", s => s.length),
                "| external script tags:", JSON.stringify(await page.$$eval("script[src]", s => s.map(x => x.src))));
  }
  console.log("outside requests the pages tried (all aborted here):");
  for (const o of [...new Set(outside)]) console.log("  ", o);
  await browser.close();
})();
