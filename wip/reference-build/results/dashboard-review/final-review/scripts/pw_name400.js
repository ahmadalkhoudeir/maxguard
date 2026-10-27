// A name of spaces: does the person's status choice survive until they fix the name?
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const browser = await chromium.launch();
  const id = (await (await fetch(BASE + "/api/alerts")).json())[0].finding_id;
  const page = await browser.newPage();
  const sent = [];
  page.on("request", (r) => { if (r.method() === "PATCH") sent.push(r.url()); });
  await page.goto(BASE + "/alerts/" + id);
  await page.fill("#actor", "   ");
  await page.selectOption("#alert-status", "resolved");
  await page.fill("#assignee", "Ali");
  await page.click("#status-save");
  await sleep(800);
  const s = await page.evaluate(() => ({ select: document.getElementById("alert-status").value,
    assignee: document.getElementById("assignee").value,
    message: (document.querySelector("#status-form .message") || {}).textContent || null,
    nameInvalid: !document.getElementById("actor").checkValidity() }));
  console.log("PATCH requests sent:", sent.length, "| form now:", JSON.stringify(s));
  await browser.close();
})();
