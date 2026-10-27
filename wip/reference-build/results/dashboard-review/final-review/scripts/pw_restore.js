// Does the browser put back old form values when the analyst returns to an alert page
// (Back, or reopening a closed tab) after someone else changed the alert?
// Usage: node pw_restore.js <base-url> [bfcache]
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const BF = process.argv[3] === "bfcache";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
const form = (p) => p.evaluate(() => {
  const f = document.getElementById("status-form");
  return { select: f.querySelector("#alert-status").value, shown_status: f.elements.shown_status.value,
    assignee: f.querySelector("#assignee").value, shown_assignee: f.elements.shown_assignee.value,
    persisted: window.__persisted, nav: performance.getEntriesByType("navigation")[0].type };
});
(async () => {
  const browser = await chromium.launch(BF ? { ignoreDefaultArgs: ["--disable-back-forward-cache"] } : {});
  const id = (await api("GET", "/api/alerts"))[1][0].finding_id;
  for (const touch of [false, true]) {
    await api("PATCH", "/api/alerts/" + id, { actor: "setup", status: "new", assignee: "" });
    const ctx = await browser.newContext();
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: BASE }]);
    await ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
    const page = await ctx.newPage();
    await page.goto(BASE + "/alerts/" + id);
    if (touch) { await page.selectOption("#alert-status", "investigating"); await page.selectOption("#alert-status", "new"); }
    console.log(`--- Ahmad ${touch ? "opened the Status list and left it at New" : "did not touch the form"}`);
    console.log("Ahmad's form:", JSON.stringify(await form(page)));
    await page.goto(BASE + "/upload");                       // he looks at something else
    await api("PATCH", "/api/alerts/" + id, { actor: "Fiona", status: "resolved" });  // she resolves it
    if (process.env.FRESH) await page.route("**/alerts/*", (r) => r.continue());  // routing bypasses the HTTP cache
    await page.goBack(); await sleep(800);
    console.log("after Back:  ", JSON.stringify(await form(page)));
    await page.fill("#assignee", "Ahmad");                   // he only takes the alert
    await page.click("#status-save");
    await sleep(800);
    const a = (await api("GET", "/api/alerts/" + id))[1];
    console.log("he saved his name; stored now:", a.status, "/", a.assignee);
    await ctx.close();
  }
  await browser.close();
})();
