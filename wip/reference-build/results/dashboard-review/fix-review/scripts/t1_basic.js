// T1: basic multi-tab behaviour, handover on close, and the 6-connection claim.
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    const up = await L.upload(server.port, "telnet");
    out.upload1 = up.status;
    const context = await browser.newContext();
    const streams = [];
    context.on("request", (r) => {
      if (r.url().includes("/api/stream")) streams.push({ page: r.frame().page()._label, t: Date.now() });
    });
    const A = await context.newPage(); A._label = "A";
    const B = await context.newPage(); B._label = "B";
    await A.goto(server.origin + "/");
    await B.goto(server.origin + "/");
    await L.sleep(1500);
    out.streamsAfterTwoTabs = streams.map((s) => s.page).join(",");
    out.locks = await A.evaluate(async () => {
      if (!navigator.locks) return "no navigator.locks";
      const q = await navigator.locks.query();
      return { held: q.held.map((l) => l.name), pending: q.pending.map((l) => l.name) };
    });
    // a change: both tabs must refresh
    await L.upload(server.port, "ftp");
    const a = await L.waitFor(async () => (await L.rowCount(A)) === 2, 5000);
    const b = await L.waitFor(async () => (await L.rowCount(B)) === 2, 5000);
    out.afterUpload2 = { A: [a.ok, a.ms], B: [b.ok, b.ms] };
    // close the first tab: the other one must take over the stream
    const before = streams.length;
    await A.close();
    await L.sleep(1500);
    out.newStreamsAfterClosingA = streams.slice(before).map((s) => s.page).join(",") || "none";
    await L.upload(server.port, "imap");
    const b2 = await L.waitFor(async () => (await L.rowCount(B)) === 3, 5000);
    out.afterUpload3 = { B: [b2.ok, b2.ms] };
    await context.close();

    // seven queue tabs in one profile: does the 7th page (and a page load from tab 1) still load?
    const ctx2 = await browser.newContext();
    const pages = [];
    for (let i = 0; i < 6; i++) {
      const p = await ctx2.newPage();
      await p.goto(server.origin + "/");
      pages.push(p);
    }
    await L.sleep(1000);
    const p7 = await ctx2.newPage();
    const t0 = Date.now();
    let seventh;
    try {
      await p7.goto(server.origin + "/upload", { timeout: 8000 });
      seventh = `loaded in ${Date.now() - t0} ms`;
    } catch (e) {
      seventh = `NOT loaded after ${Date.now() - t0} ms (${e.message.split("\n")[0]})`;
    }
    out.seventhTabUploadPage = seventh;
    await ctx2.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  console.log("chromium", browser.version());
  try {
    const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
