// AHM-03 step 6: change an alert's status and assignee with the keyboard only,
// then read the audit trail. Also: saving without a name is blocked in the browser.
// usage: node status_keyboard.js <base url> <finding id> <out dir>
"use strict";
const { chromium } = require("playwright");
const { DESCRIBE } = require("./lib.js");
const [BASE, FINDING, OUT] = process.argv.slice(2);
const NAME = "José Núñez";

async function active(page) { return page.evaluate(`(${DESCRIBE})(document.activeElement)`); }
async function tabTo(page, wanted, { shift = false, max = 40 } = {}) {
  const seen = [];
  for (let i = 0; i < max; i++) {
    await page.keyboard.press(shift ? "Shift+Tab" : "Tab");
    const now = await active(page);
    seen.push(now);
    if (now.includes(wanted)) return now;
  }
  throw new Error("could not Tab to " + wanted + "; saw " + JSON.stringify(seen));
}
async function formState(page) {
  return page.evaluate(() => {
    const f = document.getElementById("status-form");
    return { actorInput: !!document.getElementById("actor"), recordedAs: (f.querySelector("p.muted") || {}).innerText || null,
             status: document.getElementById("alert-status").value, assignee: document.getElementById("assignee").value,
             message: (f.querySelector(".message") || {}).innerText || null };
  });
}

(async () => {
  const out = { steps: [] };
  const errors = [], patches = [];
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  context.on("page", (p) => p.on("pageerror", (e) => errors.push(String(e))));

  // tab A: the queue, to see it refresh by itself after each change
  const queue = await context.newPage();
  await queue.goto(BASE + "/", { waitUntil: "load" });
  await queue.waitForTimeout(1000);
  await queue.evaluate(() => { window.__marker = "never reloaded"; });

  // tab B: the alert
  const page = await context.newPage();
  page.on("request", (r) => { if (r.method() === "PATCH") patches.push({ url: r.url(), body: r.postData() }); });
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });

  // --- 0. Save with no name: the browser's required-field check stops it (no PATCH sent)
  await tabTo(page, 'button "Save"');
  await page.keyboard.press("Enter");
  await page.waitForTimeout(800);
  const validation = await page.evaluate(() => ({ actorValid: document.getElementById("actor").validity.valid,
    message: document.getElementById("actor").validationMessage }));
  out.steps.push({ name: "Enter on Save with no name: blocked by the browser, nothing sent",
                   observed: { ...validation, patchesSent: patches.length, focusNow: await active(page) },
                   pass: patches.length === 0 && validation.actorValid === false });

  // --- 1. first change: name, status (arrow key), assignee, Enter on Save
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  const before = await formState(page);
  await tabTo(page, "input#actor");
  await page.keyboard.type(NAME);
  await page.keyboard.press("Tab");                  // -> Status select
  const onSelect = await active(page);
  await page.keyboard.press("ArrowDown");            // New -> Investigating
  await page.keyboard.press("Tab");                  // -> Assignee
  const onAssignee = await active(page);
  await page.keyboard.type("Fiona");
  await page.keyboard.press("Tab");                  // -> Save
  const onSave = await active(page);
  const [resp1] = await Promise.all([
    page.waitForResponse((r) => r.request().method() === "PATCH"),
    page.keyboard.press("Enter"),
  ]);
  await page.waitForTimeout(300);
  const after1 = await formState(page);
  const focusAfterSave = await active(page);
  await page.keyboard.press("Tab");
  const focusAfterNextTab = await active(page);
  const cookies1 = (await context.cookies(BASE)).filter((c) => c.name === "mg_actor");
  out.steps.push({ name: "Keyboard-only change 1 (Enter on Save)", observed: { before, onSelect, onAssignee, onSave,
    http: resp1.status(), after1, focusAfterSave, focusAfterNextTab, mg_actor_cookie: cookies1.map((c) => c.value) },
    pass: resp1.status() === 200 && after1.message === "Saved." && after1.status === "investigating" && after1.assignee === "Fiona" });
  await page.screenshot({ path: `${OUT}/alert-analyst-status-saved.png`, fullPage: true });

  // queue in tab A refreshed by itself?
  await queue.waitForFunction(() => document.querySelector("#alerts").innerText.includes("Investigating"), null, { timeout: 10000 })
    .catch(() => null);
  const q1 = await queue.evaluate(() => ({ marker: window.__marker, row: document.querySelector("#alerts tbody tr").innerText }));
  out.steps.push({ name: "Queue tab shows the new status and assignee without reload", observed: q1,
                   pass: q1.marker === "never reloaded" && q1.row.includes("Investigating") && q1.row.includes("Fiona") });

  // --- 2. second change: the name now comes from the cookie; Space on Save; clear the assignee
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  const reload2 = await formState(page);
  await tabTo(page, "select#alert-status");
  await page.keyboard.press("ArrowDown");            // Investigating -> Resolved
  await page.keyboard.press("Tab");
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Backspace");            // clear the assignee (unassign)
  await page.keyboard.press("Tab");
  const onSave2 = await active(page);
  const [resp2] = await Promise.all([
    page.waitForResponse((r) => r.request().method() === "PATCH"),
    page.keyboard.press("Space"),
  ]);
  await page.waitForTimeout(300);
  const after2 = await formState(page);
  out.steps.push({ name: "Keyboard-only change 2 (name from cookie, Space on Save, assignee cleared)",
    observed: { reload2, onSave2, http: resp2.status(), after2 },
    pass: resp2.status() === 200 && !reload2.actorInput && after2.status === "resolved" && after2.assignee === "" });

  // --- 3. the audit trail, as the API serves it (GET /api/audit)
  const audit = await page.evaluate(async () => (await fetch("/api/audit")).json());
  out.audit = audit;
  out.patches = patches;
  out.errors = errors;
  await browser.close();
  console.log(JSON.stringify(out, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
