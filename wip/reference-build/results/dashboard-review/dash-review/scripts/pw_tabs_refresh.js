"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
const shows = (page, name) => page.evaluate((n) => [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((t) => t.textContent === n), name);
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  let streams = 0;
  ctx.on("request", (r) => { if (new URL(r.url()).pathname === "/api/stream") streams += 1; });
  const tabs = [];
  for (let i = 0; i < 3; i++) { const p = await ctx.newPage(); await p.goto(BASE + "/"); tabs.push(p); }
  await sleep(1500);
  console.log("/api/stream requests made by 3 queue tabs:", streams);
  const id = (await api("GET", "/api/alerts"))[1][0].finding_id;
  await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: "TabTest1" });
  await sleep(2500);
  console.log("change 1 shown in tabs:", JSON.stringify(await Promise.all(tabs.map((t) => shows(t, "TabTest1")))));
  await tabs[0].close();
  await sleep(1500);
  console.log("after closing tab 1, /api/stream requests so far:", streams);
  await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: "TabTest2" });
  await sleep(2500);
  console.log("change 2 shown in tabs 2,3:", JSON.stringify(await Promise.all(tabs.slice(1).map((t) => shows(t, "TabTest2")))));
  await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: "" });
  await browser.close();
})();
