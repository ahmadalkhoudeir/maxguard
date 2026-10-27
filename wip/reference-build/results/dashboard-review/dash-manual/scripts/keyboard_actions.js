// AHM-02 step 8 part 3: every control is USABLE with the keyboard only
// (Tab, Shift+Tab, Enter, Space, arrow keys). No mouse, no page.click, no fill.
// usage: node keyboard_actions.js <base url> <finding id> <out dir> <label>
"use strict";
const { chromium } = require("playwright");
const { recordContext, DESCRIBE } = require("./lib.js");
const [BASE, FINDING, OUT, LABEL] = process.argv.slice(2);

const steps = [];
function step(name, observed, pass) { steps.push({ name, observed, pass }); }

async function active(page) {
  return page.evaluate(`(${DESCRIBE})(document.activeElement)`);
}
async function tabTo(page, wanted, { shift = false, max = 20 } = {}) {
  for (let i = 0; i < max; i++) {
    await page.keyboard.press(shift ? "Shift+Tab" : "Tab");
    const now = await active(page);
    if (now.includes(wanted)) return now;
  }
  throw new Error("could not Tab to " + wanted);
}
async function pressAndWaitTable(page, key) {
  const [resp] = await Promise.all([
    page.waitForResponse((r) => r.url().startsWith(BASE + "/?") && r.request().headers()["hx-request"] === "true"),
    page.keyboard.press(key),
  ]);
  await page.waitForTimeout(150); // let htmx finish the swap and push the URL
  return { url: page.url(), requested: resp.url(), table: (await page.locator("#alerts").innerText()).split("\n")[0] };
}

(async () => {
  const log = { requests: [], console: [], pageErrors: [] };
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  recordContext(context, log);
  const page = await context.newPage();
  page.__name = "kb";
  await page.goto(BASE + "/", { waitUntil: "load" });
  await page.waitForTimeout(800);

  // 1. skip link: first Tab stop, visible when focused, Enter moves focus to <main>
  await page.keyboard.press("Tab");
  const skip = await page.evaluate(() => {
    const el = document.activeElement, r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    return { text: el.textContent, left: r.left, top: r.top, outline: cs.outlineStyle + " " + cs.outlineWidth + " " + cs.outlineColor };
  });
  step("Tab 1 = skip link, visible on screen with focus outline", skip, skip.text === "Skip to content" && skip.left >= 0 && skip.outline.startsWith("solid 3px"));
  await page.keyboard.press("Enter");
  const afterSkip = await page.evaluate(() => ({ active: document.activeElement.id, hash: location.hash }));
  step("Enter on skip link focuses <main id=main>", afterSkip, afterSkip.active === "main");

  // 2. status filter with arrow keys (htmx swaps only the table and pushes the URL)
  const onStatus = await tabTo(page, "select#status");
  const s1 = await pressAndWaitTable(page, "ArrowDown");
  const s2 = await pressAndWaitTable(page, "ArrowDown");
  step("ArrowDown on Status: 'New' then 'Investigating' filter the table, URL updated", { onStatus, s1, s2 },
       s1.url.endsWith("/?status=new&severity=") && s1.table.startsWith("1 alert") &&
       s2.url.endsWith("/?status=investigating&severity=") && s2.table.startsWith("No alerts match these filters"));
  const s3 = await pressAndWaitTable(page, "ArrowUp");
  const s4 = await pressAndWaitTable(page, "ArrowUp");
  const focusAfterSwap = await active(page);
  step("ArrowUp twice returns to 'All'; focus stays on the select after the swap", { s3, s4, focusAfterSwap },
       s4.url.endsWith("/?status=&severity=") && s4.table.startsWith("1 alert") && focusAfterSwap.includes("select#status"));

  // 3. severity filter
  await page.keyboard.press("Tab");
  const v1 = await pressAndWaitTable(page, "ArrowDown"); // critical
  const v2 = await pressAndWaitTable(page, "ArrowDown"); // high
  step("ArrowDown on Severity: 'Critical' (no match) then 'High' (Telnet alert)", { v1, v2 },
       v1.table.startsWith("No alerts match") && v2.url.endsWith("/?status=&severity=high") && v2.table.startsWith("1 alert"));
  await pressAndWaitTable(page, "ArrowUp");
  await pressAndWaitTable(page, "ArrowUp");

  // 4. Apply button: set Status=New with the keyboard, then Space on Apply submits the form (full GET)
  await tabTo(page, "select#status", { shift: true });
  await pressAndWaitTable(page, "ArrowDown");
  const applyEl = await tabTo(page, 'button "Apply"');
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Space")]);
  const applied = { url: page.url(), statusValue: await page.locator("#status").inputValue() };
  step("Space on Apply submits the filter form", { applyEl, applied },
       applied.url.endsWith("/?status=new&severity=") && applied.statusValue === "new");

  // 5. mode switch: Enter on Home, Space on Analyst (a plain POST form; stays on the same URL)
  const homeBtn = await tabTo(page, "button[name=mode][value=home]", { shift: true, max: 10 });
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Enter")]);
  const home = await page.evaluate(() => ({
    url: location.href, pressed: document.querySelector('button[value=home]').getAttribute("aria-pressed"),
    badge: document.querySelector("#alerts .sev") ? document.querySelector("#alerts .sev").textContent : null }));
  await page.screenshot({ path: `${OUT}/queue-home${LABEL}.png`, fullPage: true });
  step("Enter on 'Home' switches to Home mode and keeps the URL", { homeBtn, home },
       home.pressed === "true" && home.url.endsWith("/?status=new&severity=") && home.badge === "High: fix this week");
  const analystBtn = await tabTo(page, "button[name=mode][value=analyst]", { max: 10 });
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Space")]);
  const analyst = await page.evaluate(() => document.querySelector('button[value=analyst]').getAttribute("aria-pressed"));
  step("Space on 'Analyst' switches back", { analystBtn, analystPressed: analyst }, analyst === "true");

  // 6. the alert link in the table
  const link = await tabTo(page, `a[href=/alerts/${FINDING}]`);
  const [nav] = await Promise.all([page.waitForNavigation(), page.keyboard.press("Enter")]);
  const alertPage = { url: page.url(), http: nav ? nav.status() : null, type: nav ? nav.headers()["content-type"] : null,
                      start: (await page.locator("body").innerText()).slice(0, 80) };
  step("Enter on the alert link opens /alerts/<id>", { link, alertPage }, alertPage.url.endsWith(`/alerts/${FINDING}`));

  // 7. nav link Upload, then 'Go to the alert queue'
  await page.goto(BASE + "/", { waitUntil: "load" });
  await tabTo(page, "a[href=/upload]");
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Enter")]);
  const onUpload = page.url();
  await tabTo(page, 'a[href=/] "Go to the alert queue"');
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Enter")]);
  step("Enter on 'Upload' nav link, then on 'Go to the alert queue'", { onUpload, back: page.url() },
       onUpload.endsWith("/upload") && page.url() === BASE + "/");

  // 8. the 400 error page's link back
  await page.goto(BASE + "/?status=bogus", { waitUntil: "load" });
  const errText = await page.locator("main").innerText();
  await tabTo(page, 'a[href=/] "Back to the alert queue"');
  await Promise.all([page.waitForNavigation(), page.keyboard.press("Enter")]);
  step("400 page: message shown, Enter on 'Back to the alert queue' works", { errText, back: page.url() },
       page.url() === BASE + "/");

  await browser.close();
  console.log(JSON.stringify({ steps, allPass: steps.every((s) => s.pass), pageErrors: log.pageErrors,
    consoleErrors: log.console.filter((c) => c.type === "error"),
    origins: [...new Set(log.requests.map((r) => new URL(r.url).origin))] }, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
