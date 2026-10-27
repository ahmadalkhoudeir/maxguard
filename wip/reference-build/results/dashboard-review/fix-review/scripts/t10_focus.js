// T10: keyboard focus across htmx swaps.
// (a) queue: an alert link has focus (keyboard), the table refreshes because of a
//     change that also re-orders the rows; is focus still on the same alert's link,
//     with a visible focus ring?
// (b) alert page: Save pressed with the keyboard; is focus on the new Save button?
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "ftp");
    await L.upload(server.port, "imap");
    const ctx = await browser.newContext();
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    const page = await ctx.newPage();
    await page.goto(server.origin + "/");
    await L.sleep(800);
    const links = await page.evaluate(() => [...document.querySelectorAll("#alerts tbody a")].map((a) => a.textContent.trim()));
    out.rowsBefore = links;
    const target = links[links.length - 1];
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press("Tab");
      const t = await page.evaluate(() => document.activeElement && document.activeElement.textContent.trim());
      if (t === target) break;
    }
    out.focusedBefore = await page.evaluate(() => document.activeElement.textContent.trim());
    await L.upload(server.port, "telnet");         // high severity: goes to the top of the table
    await L.waitFor(async () => (await L.rowCount(page)) === links.length + 1, 5000);
    await L.sleep(300);
    out.rowsAfter = await page.evaluate(() => [...document.querySelectorAll("#alerts tbody a")].map((a) => a.textContent.trim()));
    out.focusedAfterRefresh = await page.evaluate(() => {
      const a = document.activeElement;
      return a === document.body ? "<body> (focus lost)" : `${a.textContent.trim()} focus-visible=${a.matches(":focus-visible")}`;
    });

    // (b) the status form
    const alertHref = await page.evaluate(() => document.querySelector("#alerts tbody a").getAttribute("href"));
    await page.goto(server.origin + alertHref);
    await page.focus("#alert-status");
    await page.keyboard.press("ArrowDown");          // pick the next status
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press("Tab");
      const tag = await page.evaluate(() => document.activeElement.tagName + "#" + document.activeElement.id);
      if (tag.startsWith("BUTTON")) break;
    }
    out.saveFocused = await page.evaluate(() => document.activeElement.outerHTML);
    await page.keyboard.press("Enter");
    await page.waitForSelector("#status-form .message");
    await L.sleep(300);
    out.message = (await page.textContent("#status-form .message")).trim();
    out.focusedAfterSave = await page.evaluate(() => {
      const a = document.activeElement;
      return a === document.body ? "<body> (focus lost)" : `${a.tagName}#${a.id} focus-visible=${a.matches(":focus-visible")}`;
    });
    out.statusSaveIds = await page.evaluate(() => document.querySelectorAll("#status-save").length);
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
