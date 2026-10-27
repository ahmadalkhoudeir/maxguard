// Browser checks for the AHM-03 dashboard (dash-review). Server: scripts/serve.py.
// Usage: node pw_a11y.js <base-url> <scenario...>
"use strict";
const { chromium } = require("playwright");

const BASE = process.argv[2];
const WANT = new Set(process.argv.slice(3));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  return [res.status, await res.json()];
}

async function active(page) {
  return page.evaluate(() => {
    const e = document.activeElement;
    return e ? `${e.tagName}${e.id ? "#" + e.id : ""} "${(e.textContent || "").trim().slice(0, 30)}"` : "null";
  });
}

async function alerts() {
  const [, list] = await api("GET", "/api/alerts");
  return list;
}

const scenarios = {
  // E: change a filter with htmx, then use the Analyst/Home switch.
  async mode_switch_keeps_filter(browser) {
    const page = await browser.newPage();
    await page.goto(BASE + "/");
    await page.selectOption("#severity", "medium");
    await page.waitForURL(/severity=medium/);
    const before = await page.evaluate(() => ({
      url: location.pathname + location.search,
      next: document.querySelector('.mode-switch input[name="next"]').value,
      rows: document.querySelectorAll('#alerts td[data-label="Alert"]').length,
    }));
    await Promise.all([page.waitForNavigation(), page.click('button[value="home"]')]);
    const after = await page.evaluate(() => ({
      url: location.pathname + location.search,
      severity_select: document.getElementById("severity").value,
      rows: document.querySelectorAll('#alerts td[data-label="Alert"]').length,
    }));
    console.log("before switch:", JSON.stringify(before));
    console.log("after switch: ", JSON.stringify(after));
    await page.close();
  },

  // F: save the status form with the keyboard; where is focus afterwards?
  async status_form_focus(browser) {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const id = (await alerts()).find((a) => a.rule_id === "cleartext.ftp").finding_id;
    await page.goto(BASE + "/alerts/" + id);
    await page.fill("#actor", "Ahmad");
    await page.focus("#alert-status");
    await page.keyboard.press("ArrowDown"); // keyboard-only change of the status
    await page.keyboard.press("Tab"); // -> assignee
    await page.keyboard.press("Tab"); // -> Save
    console.log("focus before Enter:", await active(page));
    await page.keyboard.press("Enter");
    await page.waitForSelector("#status-form .message");
    await sleep(300);
    console.log("message:", await page.textContent("#status-form .message"));
    console.log("focus after the swap:", await active(page));
    await page.keyboard.press("Tab");
    console.log("next Tab goes to:", await active(page));
    await ctx.close();
  },

  // G: keyboard focus on an alert link while the queue refreshes itself.
  async queue_refresh_focus(browser) {
    const page = await browser.newPage();
    await page.goto(BASE + "/");
    await sleep(1500); // the stream's first event already refreshed the table once
    await page.focus('#alerts td[data-label="Alert"] >> nth=2 >> a');
    console.log("focus before refresh:", await active(page));
    const swapped = page.evaluate(() => new Promise((r) =>
      document.body.addEventListener("htmx:afterSettle", () => r(true), { once: true })));
    const target = (await alerts())[0].finding_id;
    await api("PATCH", "/api/alerts/" + target, { actor: "review", assignee: "Fiona" });
    await swapped;
    console.log("focus after refresh:", await active(page));
    await api("PATCH", "/api/alerts/" + target, { actor: "review", assignee: "" });
    await page.close();
  },

  // H: no sideways scrolling at 375 px, both modes, queue and alert pages.
  async width_375(browser) {
    for (const mode of ["analyst", "home"]) {
      const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
      await ctx.addCookies([{ name: "mg_mode", value: mode, url: BASE }]);
      const page = await ctx.newPage();
      const paths = ["/", "/upload"].concat((await alerts()).map((a) => "/alerts/" + a.finding_id));
      for (const path of paths) {
        await page.goto(BASE + path);
        const m = await page.evaluate(() => {
          const wide = [...document.querySelectorAll("body *")]
            .filter((e) => e.getBoundingClientRect().right > document.documentElement.clientWidth + 0.5)
            .map((e) => `${e.tagName}.${e.className} "${(e.textContent || "").trim().slice(0, 40)}" right=${Math.round(e.getBoundingClientRect().right)}`);
          return { scrollWidth: document.documentElement.scrollWidth,
                   clientWidth: document.documentElement.clientWidth, wide: wide.slice(0, 3) };
        });
        console.log(`${mode} ${path}: scrollWidth=${m.scrollWidth} clientWidth=${m.clientWidth}` +
                    (m.wide.length ? " overflowing: " + m.wide.join(" | ") : ""));
      }
      await ctx.close();
    }
  },

  // I: two filter changes, then the browser Back button.
  async history_back(browser) {
    const ids = await alerts();
    await api("PATCH", "/api/alerts/" + ids[0].finding_id, { actor: "review", status: "investigating" });
    const page = await browser.newPage();
    await page.goto(BASE + "/");
    await page.selectOption("#status", "new");
    await page.waitForURL(/status=new/);
    await page.selectOption("#status", "investigating");
    await page.waitForURL(/status=investigating/);
    await page.goBack();
    await page.waitForURL(/status=new/);
    await sleep(500);
    const s = await page.evaluate(() => ({
      url: location.pathname + location.search,
      status_select: document.getElementById("status").value,
      rows: [...document.querySelectorAll('#alerts td[data-label="Status"]')].map((t) => t.textContent),
    }));
    console.log("after Back:", JSON.stringify(s));
    await page.selectOption("#severity", "high");
    await page.waitForURL(/severity=high/);
    console.log("then severity=High ->", await page.evaluate(() => location.search),
      JSON.stringify(await page.evaluate(() => [...document.querySelectorAll('#alerts td[data-label="Status"]')].map((t) => t.textContent))));
    await api("PATCH", "/api/alerts/" + ids[0].finding_id, { actor: "review", status: "new" });
    await page.close();
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
