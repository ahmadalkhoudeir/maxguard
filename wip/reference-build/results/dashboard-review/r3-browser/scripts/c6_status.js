// Check 6: the status form. (a) two analysts; (b) Chrome form restore after Back;
// (c) a name of only spaces is refused by the browser; (d) server stopped -> "No answer";
// (e) an assignee with a line break (JSON API) is not "changed" by a status-only save.
// Usage: node c6_status.js [bfcache] <build>...
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const bf = process.argv.includes("bfcache");
const builds = process.argv.slice(2).filter((a) => a !== "bfcache");

const formState = (page) => page.evaluate(() => {
  const f = document.getElementById("status-form");
  const m = f && f.querySelector(".message");
  return { select: f.querySelector("#alert-status").value, assignee: f.querySelector("#assignee").value,
    shown_status: f.elements.shown_status ? f.elements.shown_status.value : "(no field)",
    shown_assignee: f.elements.shown_assignee ? f.elements.shown_assignee.value : "(no field)",
    autocomplete: f.getAttribute("autocomplete"), message: m ? m.textContent : null };
});
const stored = async (port, id) => { const a = (await L.api(port, "GET", "/api/alerts/" + id)).body; return `${a.status}/${JSON.stringify(a.assignee)}`; };
const audit = async (port, n = 1) => (await L.api(port, "GET", "/api/audit?limit=" + n)).body.map((r) => [r.actor, r.details]);

async function run(buildName, browser) {
  const out = { build: buildName, bfcache: bf };
  const server = await L.startServer(buildName);
  const { port } = server;
  try {
    await L.upload(port, "telnet");
    const id = await L.telnetId(port);
    const ctx = await L.newContext(browser);
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    await ctx.addInitScript(() => { addEventListener("pageshow", (e) => { window.__persisted = e.persisted; }); });
    const page = await ctx.newPage();

    // (a) Fiona sets Investigating while Ahmad's page still shows New; Ahmad saves only an assignee
    await L.patchAlert(port, id, { actor: "setup", status: "new", assignee: "" });
    await page.goto(server.origin + "/alerts/" + id);
    const shownBefore = await formState(page);
    await L.patchAlert(port, id, { actor: "Fiona", status: "investigating" });
    await page.fill("#assignee", "Ahmad");
    await page.click("#status-save, #status-form button[type=submit]");
    await page.waitForSelector("#status-form .message", { timeout: 8000 });
    await L.sleep(300);
    out.a = { ahmadSawStatus: shownBefore.select, afterSave: await formState(page), stored: await stored(port, id), audit: await audit(port, 1) };
    out.a.pass = out.a.stored === 'investigating/"Ahmad"' && JSON.stringify(out.a.audit[0][1]) === JSON.stringify({ assignee: { from: "", to: "Ahmad" } });

    // (b) Chrome form restore after Back cannot undo Fiona's change
    await L.patchAlert(port, id, { actor: "setup", status: "new", assignee: "" });
    await page.goto(server.origin + "/alerts/" + id);
    await page.selectOption("#alert-status", "investigating");      // chosen but not saved
    await page.goto(server.origin + "/upload");                      // he looks at something else
    await L.patchAlert(port, id, { actor: "Fiona", status: "resolved" });
    await page.goBack({ waitUntil: "commit" });   // "load" never fires for a bfcache restore
    await page.waitForSelector("#status-form");
    await L.sleep(1000);
    const afterBack = await formState(page);
    afterBack.persisted = await page.evaluate(() => window.__persisted);
    await page.fill("#assignee", "Ahmad");                           // he only takes the alert
    await page.click("#status-save, #status-form button[type=submit]");
    await page.waitForSelector("#status-form .message", { timeout: 8000 });
    await L.sleep(300);
    out.b = { afterBack, stored: await stored(port, id), audit: await audit(port, 1) };
    out.b.pass = out.b.stored === 'resolved/"Ahmad"';

    // (c) a name of only spaces is refused by the browser before any request
    const ctx2 = await L.newContext(browser);
    const p2 = await ctx2.newPage();
    const sent = [];
    p2.on("request", (r) => { if (r.method() === "PATCH") sent.push(r.url()); });
    await p2.goto(server.origin + "/alerts/" + id);
    await p2.fill("#actor", "   ");
    await p2.selectOption("#alert-status", "new");
    await p2.click("#status-save, #status-form button[type=submit]");
    await L.sleep(1000);
    out.c = { patchRequestsSent: sent.length, nameValid: await p2.evaluate(() => document.getElementById("actor").checkValidity()),
      validationMessage: await p2.evaluate(() => document.getElementById("actor").validationMessage),
      message: await p2.evaluate(() => (document.querySelector("#status-form .message") || {}).textContent || null),
      stored: await stored(port, id) };
    out.c.pass = sent.length === 0 && out.c.nameValid === false;
    await ctx2.close();

    // (e) an assignee with a line break set through the JSON API
    await L.patchAlert(port, id, { actor: "api-client", status: "new", assignee: "Ali\nBaba" });
    await page.goto(server.origin + "/alerts/" + id);
    const e0 = await formState(page);
    await page.selectOption("#alert-status", "investigating");      // only the status
    await page.click("#status-save, #status-form button[type=submit]");
    await page.waitForSelector("#status-form .message", { timeout: 8000 });
    await L.sleep(300);
    out.e = { formShowed: { assignee: e0.assignee, shown_assignee: e0.shown_assignee }, stored: await stored(port, id), audit: await audit(port, 1) };
    out.e.pass = out.e.stored === 'investigating/"Ali\\nBaba"' && JSON.stringify(out.e.audit[0][1]) === JSON.stringify({ status: { from: "new", to: "investigating" } });

    // (d) the server is stopped when Save is pressed
    await page.goto(server.origin + "/alerts/" + id);
    await server.stop();
    await page.selectOption("#alert-status", "resolved");
    await page.click("#status-save, #status-form button[type=submit]");
    await L.sleep(1500);
    out.d = { message: await page.evaluate(() => (document.querySelector("#status-form .message") || {}).textContent || null),
      formStillThere: await page.evaluate(() => !!document.getElementById("status-form")) };
    out.d.pass = out.d.message === "No answer from the MaxGuard server: the change may not be saved. Reload the page to check.";
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const opts = bf ? { channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] } : {};
  const browser = await chromium.launch(opts);
  console.log("Chromium", browser.version(), bf ? "bfcache on" : "Playwright default (bfcache off)");
  try {
    for (const b of builds) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
