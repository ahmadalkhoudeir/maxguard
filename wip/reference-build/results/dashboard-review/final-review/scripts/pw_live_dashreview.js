// Live-refresh and form checks (dash-review). Usage: node pw_live.js <base-url> <scenario...>
"use strict";
const { chromium } = require("playwright");

const BASE = process.argv[2];
const WANT = new Set(process.argv.slice(3));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(method, path, body) {
  const res = await fetch(BASE + path, {
    method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  return [res.status, await res.json()];
}
const alerts = async () => (await api("GET", "/api/alerts"))[1];
const assignees = (page) => page.evaluate(() =>
  [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].map((t) => t.textContent));

const scenarios = {
  // J: two changes close together; the second "refresh" arrives while the first
  // refresh request is still running (its answer is held back 1.5 s, as on a busy Pi).
  async refresh_during_refresh(browser) {
    const list = await alerts();
    const [a, b] = [list[0].finding_id, list[1].finding_id];
    const page = await browser.newPage();
    await page.goto(BASE + "/");
    await sleep(1500); // the stream's first event already caused one refresh
    const refreshes = [];
    await page.route((url) => url.pathname === "/" && url.search.startsWith("?status="), async (route) => {
      const response = await route.fetch(); // rendered by the server NOW
      refreshes.push(Date.now());
      await sleep(3000); // ... but delivered 3 s later (a slow Pi, a big queue)
      try { await route.fulfill({ response }); } catch (e) { /* request was aborted */ }
    });
    await api("PATCH", "/api/alerts/" + a, { actor: "review", assignee: "First" });
    while (refreshes.length === 0) await sleep(50); // refresh 1 rendered, still in flight
    await api("PATCH", "/api/alerts/" + b, { actor: "review", assignee: "Second" });
    await sleep(8000);
    console.log("refresh requests sent after the two changes:", refreshes.length);
    console.log("assignee column shown:", JSON.stringify(await assignees(page)));
    console.log("assignees stored:     ", JSON.stringify((await alerts()).map((x) => x.assignee || "—")));
    await api("PATCH", "/api/alerts/" + a, { actor: "review", assignee: "" });
    await api("PATCH", "/api/alerts/" + b, { actor: "review", assignee: "" });
    await page.close();
  },

  // K: a refresh that started before a filter change answers after it.
  async refresh_vs_filter(browser) {
    const page = await browser.newPage();
    await page.goto(BASE + "/");
    await sleep(1500);
    await page.route((url) => url.pathname === "/" && url.search === "?status=&severity=", async (route) => {
      const response = await route.fetch();
      await sleep(1500);
      await route.fulfill({ response });
    });
    const id = (await alerts())[0].finding_id;
    await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: "x" }); // -> refresh (slow)
    await sleep(300);
    await page.selectOption("#severity", "medium"); // -> filtered request (fast)
    await page.waitForURL(/severity=medium/);
    await sleep(200);
    const mid = await page.evaluate(() => document.querySelectorAll('#alerts td[data-label="Severity"]').length);
    await sleep(3000);
    const end = await page.evaluate(() => ({
      url: location.search, select: document.getElementById("severity").value,
      severities: [...document.querySelectorAll('#alerts td[data-label="Severity"]')].map((t) => t.textContent),
      refresh_url: document.getElementById("alerts").getAttribute("hx-get"),
      alerts_divs: document.querySelectorAll("#alerts").length,
    }));
    console.log("rows right after the filter answer:", mid);
    console.log("after the late refresh answer:", JSON.stringify(end));
    await api("PATCH", "/api/alerts/" + id, { actor: "review", assignee: "" });
    await page.close();
  },

  // A (browser): two analysts, two cookie jars, the same alert page open.
  async two_analysts(browser) {
    const id = (await alerts()).find((x) => x.rule_id === "cleartext.telnet").finding_id;
    await api("PATCH", "/api/alerts/" + id, { actor: "review", status: "new", assignee: "" });
    const pages = [];
    for (const name of ["Ahmad", "Fiona"]) {
      const ctx = await browser.newContext();
      const page = await ctx.newPage();
      await page.goto(BASE + "/alerts/" + id);
      await page.fill("#actor", name);
      pages.push(page);
    }
    const [ahmad, fiona] = pages;
    await ahmad.selectOption("#alert-status", "investigating");
    await ahmad.click("#status-form button");
    await ahmad.waitForSelector("#status-form .message");
    await fiona.fill("#assignee", "Fiona");  // she only sets the assignee
    await fiona.click("#status-form button");
    await fiona.waitForSelector("#status-form .message");
    const sent = await fiona.evaluate(() => document.getElementById("alert-status").value);
    const stored = (await alerts()).find((x) => x.finding_id === id);
    console.log(`Fiona's form showed status "${sent}" and said: ${await fiona.textContent("#status-form .message")}`);
    console.log("stored now:", stored.status, "/", stored.assignee);
    const [, audit] = await api("GET", "/api/audit?limit=2");
    console.log("audit:", JSON.stringify(audit.map((r) => [r.actor, r.details])));
    for (const p of pages) await p.context().close();
  },

  // P: upload with the keyboard; where is focus afterwards?
  async upload_focus(browser) {
    const page = await browser.newPage();
    await page.goto(BASE + "/upload");
    await page.setInputFiles("#file", process.env.UPLOAD_ZIP);
    await page.focus("#upload-form button");
    await page.keyboard.press("Enter");
    await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "");
    console.log("result:", await page.textContent("#upload-result"));
    console.log("focus after upload:", await page.evaluate(() => document.activeElement.tagName));
    await page.close();
  },

  // O: six queue tabs hold six /api/stream connections; open a seventh page.
  async seven_tabs(browser) {
    const ctx = await browser.newContext();
    const tabs = [];
    for (let i = 0; i < 6; i++) {
      const p = await ctx.newPage();
      await p.goto(BASE + "/");
      tabs.push(p);
    }
    await sleep(1000);
    const seventh = await ctx.newPage();
    const t0 = Date.now();
    try {
      await seventh.goto(BASE + "/upload", { timeout: 10000 });
      console.log(`7th page loaded in ${Date.now() - t0} ms`);
    } catch (e) {
      console.log(`7th page (/upload) did not load within 10 s: ${e.message.split("\n")[0]}`);
    }
    await tabs[0].close();
    try {
      await seventh.waitForLoadState("load", { timeout: 10000 });
      console.log(`after closing one queue tab, it loaded (${Date.now() - t0} ms after the request)`);
    } catch (e) {
      console.log("still not loaded after closing one tab");
    }
    await ctx.close();
  },
};

(async () => {
  const browser = await chromium.launch();
  for (const [name, fn] of Object.entries(scenarios)) {
    if (WANT.size && !WANT.has(name)) continue;
    console.log(`--- ${name}`);
    try { await fn(browser); } catch (e) { console.log("ERROR", e.message.split("\n")[0]); }
  }
  await browser.close();
})();
