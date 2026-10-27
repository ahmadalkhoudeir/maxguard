// Check 9: after an upload, focus is on Analyze; if the person moved to another link
// during the upload, focus stays there.  Usage: node c9_upload_focus.js <build>...
"use strict";
const { chromium } = require("playwright");
const path = require("path");
const L = require("./lib");

const active = (page) => page.evaluate(() => {
  const a = document.activeElement;
  return a === document.body ? "<body> (focus lost)" : `${a.tagName} "${a.textContent.trim()}" focus-visible=${a.matches(":focus-visible")}`;
});

async function once(server, browser, move) {
  const ctx = await L.newContext(browser);
  const page = await ctx.newPage();
  const r = {};
  await page.goto(server.origin + "/upload");
  await page.setInputFiles("#file", path.join(L.ZIPS, move ? "ftp.zip" : "telnet.zip"));
  await page.route("**/api/analyses", async (route) => { await L.sleep(2000); await route.continue(); });
  await page.focus("#upload-form button");
  await page.keyboard.press("Enter");
  await L.sleep(400);
  r.duringUpload = await active(page);
  r.buttonDisabled = await page.evaluate(() => document.querySelector("#upload-form button").disabled);
  if (move) {
    await page.focus("text=Go to the alert queue");                // the person moves on meanwhile
    r.movedTo = await active(page);
  }
  await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "", null, { timeout: 30000 });
  await L.sleep(300);
  r.afterUpload = await active(page);
  r.result = (await page.textContent("#upload-result")).trim().slice(0, 80);
  await ctx.close();
  return r;
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    out.nobodyMoved = await once(server, browser, false);
    out.nobodyMoved.pass = out.nobodyMoved.afterUpload.startsWith('BUTTON "Analyze"');
    out.movedToLink = await once(server, browser, true);
    out.movedToLink.pass = out.movedToLink.afterUpload.startsWith('A "Go to the alert queue"');
    out.pass = out.nobodyMoved.pass && out.movedToLink.pass;
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
