// An assignee with a line break (set through the JSON API) and the stale-form rule.
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
(async () => {
  const browser = await chromium.launch();
  const id = (await api("GET", "/api/alerts"))[1][0].finding_id;
  console.log("API PATCH assignee 'Ali\\nBaba':", (await api("PATCH", "/api/alerts/" + id, { actor: "api-client", status: "new", assignee: "Ali\nBaba" }))[0]);
  const ctx = await browser.newContext();
  await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: BASE }]);
  const page = await ctx.newPage();
  await page.goto(BASE + "/alerts/" + id);
  console.log("form:", JSON.stringify(await page.evaluate(() => ({ assignee: document.getElementById("assignee").value,
    shown_assignee: document.getElementById("status-form").elements.shown_assignee.value }))));
  await page.selectOption("#alert-status", "investigating");  // he changes only the status
  await page.click("#status-save");
  await sleep(800);
  const [, audit] = await api("GET", "/api/audit?limit=1");
  console.log("audit:", JSON.stringify(audit.map((r) => [r.actor, r.details])));
  await ctx.close(); await browser.close();
})();
