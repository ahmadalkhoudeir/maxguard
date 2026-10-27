// T14: Page Lifecycle "frozen" tabs, forced through CDP (Page.setWebLifecycleState),
// which is what Chrome does to some background tabs.
//  (a) the holder is frozen: do the other tabs still get live refresh?
//  (b) a non-holder is frozen, then the holder closes: who gets the lock?
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    let rows = 1;
    const ctx = await browser.newContext();
    const streams = [];
    ctx.on("request", (r) => {
      if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label);
    });
    const open = async (label) => {
      const p = await ctx.newPage(); p._label = label;
      await p.goto(server.origin + "/");
      await L.sleep(400);
      return p;
    };
    // (a)
    const H = await open("H");
    const N = await open("N");
    const cdpH = await ctx.newCDPSession(H);
    await cdpH.send("Page.setWebLifecycleState", { state: "frozen" });
    await L.upload(server.port, "ftp"); rows++;
    const a = await L.waitFor(async () => (await L.rowCount(N)) === rows, 5000);
    out.a_otherTabWhileHolderFrozen = a.ok ? `yes ${a.ms} ms` : "NO within 5 s";
    await cdpH.send("Page.setWebLifecycleState", { state: "active" });
    const a2 = await L.waitFor(async () => (await L.rowCount(N)) === rows, 5000);
    out.a_otherTabAfterUnfreeze = a2.ok ? `yes ${a2.ms} ms` : "NO";
    // (b)
    const cdpN = await ctx.newCDPSession(N);
    await cdpN.send("Page.setWebLifecycleState", { state: "frozen" });
    const before = streams.length;
    await H.close();
    await L.sleep(1000);
    const X = await open("X");
    await L.sleep(1000);
    out.b_streamsAfterHolderClosed = streams.slice(before).join(",") || "none";
    out.b_locks = await X.evaluate(async () => {
      if (!navigator.locks) return "-";
      const q = await navigator.locks.query();
      return `held=${q.held.length} pending=${q.pending.length}`;
    });
    await L.upload(server.port, "imap"); rows++;
    const b = await L.waitFor(async () => (await L.rowCount(X)) === rows, 5000);
    out.b_newTabLiveRefresh = b.ok ? `yes ${b.ms} ms` : "NO within 5 s";
    await cdpN.send("Page.setWebLifecycleState", { state: "active" });
    await L.sleep(1500);
    out.b_streamsAfterUnfreeze = streams.slice(before).join(",") || "none";
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
