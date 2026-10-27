"use strict";
const { chromium } = require("playwright");
const [BASE, FILE] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(BASE + "/upload");
  await page.setInputFiles("#file", FILE);
  const [resp] = await Promise.all([page.waitForResponse((r) => r.url().endsWith("/api/analyses")), page.keyboard.press("Tab").then(() => page.focus("#upload-form button")).then(() => page.keyboard.press("Enter"))]);
  await page.waitForFunction(() => document.getElementById("upload-result").textContent !== "");
  console.log(JSON.stringify({ http: resp.status(), body: await resp.text(),
    shown: await page.locator("#upload-result").innerText(),
    resultChildElements: await page.evaluate(() => document.getElementById("upload-result").children.length),
    buttonEnabledAgain: await page.evaluate(() => !document.querySelector("#upload-form button").disabled) }, null, 1));
  await browser.close();
})();
