// T15 (AHM-02 stage): two queue tabs. In the second one, go to Upload, upload a
// capture with the page's own form, then press Back. Is the new alert in the queue?
"use strict";
const { chromium } = require("playwright");
const path = require("path");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const ctx = await browser.newContext();
    let H = await ctx.newPage();
    await H.goto(server.origin + "/");
    await L.sleep(500);
    let N = await ctx.newPage();
    await N.goto(server.origin + "/");
    await L.sleep(500);
    if (process.env.UPLOADER === "holder") {
      // the first tab (the stream holder) does the upload; the second one just stays open
      const tmp = H; H = N; N = tmp;   // eslint-disable-line no-const-assign
    }
    out.uploaderIsHolder = process.env.UPLOADER === "holder";
    await N.click("nav a[href='/upload']");
    await N.waitForURL(/\/upload/);
    await N.setInputFiles("#file", path.join(L.W, "zips", "ftp.zip"));
    await N.click("#upload-form button[type=submit]");
    await N.waitForFunction(() => document.getElementById("upload-result").textContent.length > 0);
    out.uploadResult = await N.textContent("#upload-result");
    await L.sleep(800);
    out.holderRows = await L.rowCount(H);
    const t0 = Date.now();
    await N.goBack({ waitUntil: "commit" });
    await N.waitForSelector("#alerts");
    const r = await L.waitFor(async () => (await L.rowCount(N)) === 2, 8000, 100);
    out.queueAfterBack = r.ok ? `2 rows after ${Date.now() - t0} ms` : `still ${await L.rowCount(N)} row(s) ${Date.now() - t0} ms after Back (server has 2)`;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of builds.length ? builds : ["orig-02", "fixed-02"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
