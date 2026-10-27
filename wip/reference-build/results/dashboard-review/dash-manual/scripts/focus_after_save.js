// Where is keyboard focus after saving the status form? (A) Enter on the Save button,
// (B) Enter inside the Assignee field. Keyboard only.
"use strict";
const { chromium } = require("playwright");
const { DESCRIBE } = require("./lib.js");
const [BASE, FINDING] = process.argv.slice(2);
async function active(page) { return page.evaluate(`(${DESCRIBE})(document.activeElement)`); }
async function tabTo(page, wanted) {
  for (let i = 0; i < 40; i++) { await page.keyboard.press("Tab"); if ((await active(page)).includes(wanted)) return; }
  throw new Error("no " + wanted);
}
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  const out = {};
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  if (await page.$("#actor")) { await tabTo(page, "input#actor"); await page.keyboard.type("Focus Tester"); }
  // (A) Enter on Save
  await tabTo(page, "select#alert-status");
  await page.keyboard.press("ArrowDown");
  await tabTo(page, 'button');
  const before = await active(page);
  await Promise.all([page.waitForResponse((r) => r.request().method() === "PATCH"), page.keyboard.press("Enter")]);
  await page.waitForTimeout(300);
  out.A_enterOnSave = { focusBefore: before, focusAfter: await active(page),
                        message: await page.locator("#status-form .message").innerText() };
  await page.keyboard.press("Tab");
  out.A_enterOnSave.nextTab = await active(page);
  // (B) Enter inside the Assignee field
  await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  await tabTo(page, "input#assignee");
  await page.keyboard.type("x");
  await Promise.all([page.waitForResponse((r) => r.request().method() === "PATCH"), page.keyboard.press("Enter")]);
  await page.waitForTimeout(300);
  out.B_enterInAssignee = { focusAfter: await active(page) };
  await browser.close();
  console.log(JSON.stringify(out, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
