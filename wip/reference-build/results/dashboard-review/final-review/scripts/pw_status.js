// The status form: errors, "Not saved", the 400 name path, saves in a row, two analysts.
// Usage: node pw_status.js <base-url>
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
const stored = async (id) => { const a = (await api("GET", "/api/alerts/" + id))[1]; return `${a.status}/${a.assignee || "-"}`; };
const formState = (page) => page.evaluate(() => {
  const f = document.getElementById("status-form");
  const m = f.querySelector(".message");
  return { message: m ? m.textContent : null, select: f.querySelector("#alert-status").value,
    assignee: f.querySelector("#assignee").value, shown_status: f.elements.shown_status.value,
    shown_assignee: f.elements.shown_assignee.value, focus: document.activeElement.id || document.activeElement.tagName };
});
async function save(page) {
  const before = await page.evaluate(() => { const f = document.getElementById("status-form"); f.dataset.old = "1"; });
  await page.focus("#status-save");
  await page.keyboard.press("Enter");
  // wait until the form was replaced (no data-old) or a message changed
  await page.waitForFunction(() => {
    const f = document.getElementById("status-form");
    return !f.dataset.old || (f.querySelector(".message") && f.querySelector(".message").textContent.startsWith("Not saved"));
  }, null, { timeout: 8000 }).catch(() => {});
  await sleep(200);
}
(async () => {
  const browser = await chromium.launch();
  const list = (await api("GET", "/api/alerts"))[1];
  const id = list[0].finding_id;
  await api("PATCH", "/api/alerts/" + id, { actor: "setup", status: "new", assignee: "" });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(BASE + "/alerts/" + id);

  console.log("--- 400: a name of spaces");
  await page.fill("#actor", "   ");
  await page.selectOption("#alert-status", "resolved");
  await save(page);
  console.log("form:", JSON.stringify(await formState(page)), "| stored:", await stored(id));
  console.log("--- retry with a name, choosing Resolved again");
  await page.fill("#actor", "Ahmad");
  await page.selectOption("#alert-status", "resolved");
  await save(page);
  console.log("form:", JSON.stringify(await formState(page)), "| stored:", await stored(id));

  console.log("--- second save from the swapped form: only the assignee");
  await page.fill("#assignee", "Fiona");
  await save(page);
  console.log("form:", JSON.stringify(await formState(page)), "| stored:", await stored(id));
  const [, audit] = await api("GET", "/api/audit?limit=3");
  console.log("audit:", JSON.stringify(audit.map((r) => [r.actor, r.details])));

  for (const [label, handler] of [
    ["500 answer", (route) => route.fulfill({ status: 500, body: "Internal Server Error" })],
    ["404 answer", (route) => route.fulfill({ status: 404, contentType: "text/html", body: "<p>gone</p>" })],
    ["network error", (route) => route.abort("connectionrefused")],
    ["saved on the server, answer lost", async (route) => { await route.fetch(); await route.abort("connectionreset"); }],
  ]) {
    console.log(`--- ${label}`);
    await page.route("**/alerts/*/status", handler);
    const want = (await page.inputValue("#assignee")) === "X1" ? "X2" : "X1";
    await page.fill("#assignee", want);
    await save(page);
    console.log("form:", JSON.stringify(await formState(page)), "| stored:", await stored(id), `(asked for ${want})`);
    await page.unroute("**/alerts/*/status");
  }
  console.log("--- a working save after the errors");
  await page.fill("#assignee", "Final");
  await save(page);
  console.log("form:", JSON.stringify(await formState(page)), "| stored:", await stored(id));
  await api("PATCH", "/api/alerts/" + id, { actor: "setup", status: "new", assignee: "" });
  await ctx.close();
  await browser.close();
})();
