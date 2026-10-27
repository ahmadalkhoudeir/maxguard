// Upload one file through the Upload page with the keyboard (Tab, Space, Tab, Enter).
// usage: node upload.js <base url> <file>
"use strict";
const { chromium } = require("playwright");
const [BASE, FILE] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(BASE + "/upload", { waitUntil: "load" });
  for (let i = 0; i < 15 && (await page.evaluate(() => document.activeElement.id)) !== "file"; i++) {
    await page.keyboard.press("Tab");
  }
  const [chooser] = await Promise.all([page.waitForEvent("filechooser"), page.keyboard.press("Space")]);
  await chooser.setFiles(FILE);
  await page.keyboard.press("Tab");
  const [resp] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/api/analyses"), { timeout: 120000 }),
    page.keyboard.press("Enter")]);
  await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "");
  console.log(JSON.stringify({ http: resp.status(), body: await resp.json(),
                               shown: await page.locator("#upload-result").innerText() }));
  await browser.close();
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
