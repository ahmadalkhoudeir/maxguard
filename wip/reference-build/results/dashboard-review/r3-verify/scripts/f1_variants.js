// F1 (bfcache status form) variants, bfcache ON, to tell scope apart:
//  b1: the finding's flow (choose Investigating, leave, Fiona resolves, Back from bfcache, type assignee, Save)
//  b2: the same but the person never touches the Status list before leaving (a true assignee-only save)
//  b3: no navigation at all: choose Investigating, Fiona resolves meanwhile, type assignee, Save
//  b4: the finding's flow, but the page is reloaded (F5) after Back before saving
// Usage: node f1_variants.js <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const formState = (page) => page.evaluate(() => {
  const f = document.getElementById("status-form");
  return { select: f.querySelector("#alert-status").value, assignee: f.querySelector("#assignee").value,
    shown_status: f.elements.shown_status ? f.elements.shown_status.value : "(no field)" };
});
const stored = async (port, id) => { const a = (await L.api(port, "GET", "/api/alerts/" + id)).body; return `${a.status}/${JSON.stringify(a.assignee)}`; };
const audit = async (port) => (await L.api(port, "GET", "/api/audit?limit=1")).body.map((r) => [r.actor, r.details]);

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  const { port } = server;
  try {
    await L.upload(port, "telnet");
    const id = await L.telnetId(port);
    const ctx = await L.newContext(browser);
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    await ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
    const page = await ctx.newPage();
    const save = async () => {
      await page.fill("#assignee", "Ahmad");
      await page.click("#status-save, #status-form button[type=submit]");
      await page.waitForSelector("#status-form .message", { timeout: 8000 });
      await L.sleep(300);
    };
    const back = async () => {
      await page.goBack({ waitUntil: "commit" });
      await page.waitForSelector("#status-form");
      await L.sleep(1000);
      const s = await formState(page);
      s.persisted = await page.evaluate(() => window.__persisted);
      return s;
    };

    // b1: the finding's flow
    await L.patchAlert(port, id, { actor: "setup", status: "new", assignee: "" });
    await page.goto(server.origin + "/alerts/" + id);
    await page.selectOption("#alert-status", "investigating");
    await page.goto(server.origin + "/upload");
    await L.patchAlert(port, id, { actor: "Fiona", status: "resolved" });
    const b1 = await back();
    await save();
    out.b1_choose_leave_back_save = { afterBack: b1, stored: await stored(port, id), audit: await audit(port) };

    // b2: the person never touched the Status list before leaving
    await L.patchAlert(port, id, { actor: "setup", status: "new", assignee: "" });
    await page.goto(server.origin + "/alerts/" + id);
    await page.goto(server.origin + "/upload");
    await L.patchAlert(port, id, { actor: "Fiona", status: "resolved" });
    const b2 = await back();
    await save();
    out.b2_untouched_leave_back_save = { afterBack: b2, stored: await stored(port, id), audit: await audit(port) };

    // b3: no navigation: the page simply stays open while Fiona resolves the alert
    await L.patchAlert(port, id, { actor: "setup", status: "new", assignee: "" });
    await page.goto(server.origin + "/alerts/" + id);
    await page.selectOption("#alert-status", "investigating");
    await L.patchAlert(port, id, { actor: "Fiona", status: "resolved" });
    const b3 = await formState(page);
    await save();
    out.b3_choose_stay_save = { before: b3, stored: await stored(port, id), audit: await audit(port) };

    // b4: the finding's flow, then Reload before saving
    await L.patchAlert(port, id, { actor: "setup", status: "new", assignee: "" });
    await page.goto(server.origin + "/alerts/" + id);
    await page.selectOption("#alert-status", "investigating");
    await page.goto(server.origin + "/upload");
    await L.patchAlert(port, id, { actor: "Fiona", status: "resolved" });
    const b4 = await back();
    await page.reload();
    await page.waitForSelector("#status-form");
    const b4r = await formState(page);
    await save();
    out.b4_choose_leave_back_reload_save = { afterBack: b4, afterReload: b4r, stored: await stored(port, id), audit: await audit(port) };
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("Chromium", browser.version(), "bfcache on");
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
