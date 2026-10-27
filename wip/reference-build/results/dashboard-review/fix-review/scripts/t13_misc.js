// T13: odds and ends of the lock design.
//  (a) http://localhost and http://127.0.0.1 at once (two origins)
//  (b) refresh requests per tab per change (duplicates?), console errors (CSP)
//  (c) the holder's renderer crashes (like a discarded tab): does another tab take over?
//  (d) plain server restart (no proxy): does the stream come back and do all tabs refresh?
//  (e) a non-loopback http:// address (not a secure context): which path runs?
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));
const LAN = "172.17.0.1";

async function run(buildName, browser) {
  const out = { build: buildName };
  let server = await L.startServer(buildName, {
    host: "0.0.0.0", env: { MAXGUARD_ALLOWED_HOSTS: `localhost,127.0.0.1,[::1],${LAN}` },
  });
  const { port, dataDir } = server;
  try {
    await L.upload(port, "telnet");
    let rows = 1;
    const ctx = await browser.newContext();
    const consoleErrors = [];
    const streams = [];
    const gets = {};
    ctx.on("request", (r) => {
      const label = r.frame().page()._label;
      if (r.url().includes("/api/stream")) streams.push(label);
      if (r.url().includes("/?status=")) gets[label] = (gets[label] || 0) + 1;
    });
    const open = async (label, origin) => {
      const p = await ctx.newPage(); p._label = label;
      p.on("console", (m) => { if (m.type() === "error") consoleErrors.push(`${label}: ${m.text()}`); });
      p.on("pageerror", (e) => consoleErrors.push(`${label}: ${e.message}`));
      await p.goto(origin + "/");
      return p;
    };
    // (a) + (b)
    const A = await open("A-127", `http://127.0.0.1:${port}`);
    const B = await open("B-127", `http://127.0.0.1:${port}`);
    const C = await open("C-localhost", `http://localhost:${port}`);
    const D = await open("D-localhost", `http://localhost:${port}`);
    await L.sleep(1500);
    console.error("step a done");
    out.a_streams = streams.join(",");
    out.a_secureContext = await C.evaluate(() => `${isSecureContext} locks=${!!navigator.locks}`);
    for (const k of Object.keys(gets)) gets[k] = 0;
    await L.upload(port, "ftp"); rows++;
    const ok = [];
    for (const p of [A, B, C, D]) ok.push((await L.waitFor(async () => (await L.rowCount(p)) === rows, 5000)).ok);
    await L.sleep(1500);
    out.b_allTabsRefreshed = ok.join(",");
    out.b_refreshRequestsPerTabForOneChange = JSON.stringify(gets);

    console.error("step b done");
    // (c) the 127.0.0.1 holder's renderer crashes
    const holder127 = streams.find((s) => s.endsWith("127"));
    const victim = holder127 === "A-127" ? A : B;
    const other = victim === A ? B : A;
    const before = streams.length;
    const cdp = await ctx.newCDPSession(victim);
    cdp.send("Page.crash").catch(() => {});  // never answers: the page is gone
    await L.sleep(2000);
    out.c_crashed = victim._label;
    out.c_newStreams = streams.slice(before).join(",") || "none";
    await L.upload(port, "imap"); rows++;
    const c = await L.waitFor(async () => (await L.rowCount(other)) === rows, 5000);
    out.c_otherTabLiveRefresh = c.ok ? `yes ${c.ms} ms` : "NO";

    console.error("step c done");
    // (d) plain restart, no proxy: connection refused while down
    await server.stop();
    await L.sleep(4000);
    server = await L.startServer(buildName, {
      port, dataDir, host: "0.0.0.0", env: { MAXGUARD_ALLOWED_HOSTS: `localhost,127.0.0.1,[::1],${LAN}` },
    });
    await L.sleep(5000);
    await L.upload(port, "pop3"); rows++;
    const d1 = await L.waitFor(async () => (await L.rowCount(other)) === rows, 6000);
    const d2 = await L.waitFor(async () => (await L.rowCount(C)) === rows, 2000);
    const d3 = await L.waitFor(async () => (await L.rowCount(D)) === rows, 2000);
    out.d_afterRestart = { [other._label]: d1.ok, C: d2.ok, D: d3.ok };

    console.error("step d done");
    // (e) not a secure context
    const E = await open("E-lan", `http://${LAN}:${port}`);
    await L.sleep(800);
    out.e_lan = await E.evaluate(() => `isSecureContext=${isSecureContext} navigator.locks=${!!navigator.locks} BroadcastChannel=${!!window.BroadcastChannel}`);
    out.e_streamsFromLanTab = streams.filter((s) => s === "E-lan").length;
    out.consoleErrors = consoleErrors.filter((e) => !e.includes("ERR_CONNECTION_REFUSED") && !e.includes("Failed to load resource")).slice(0, 5);
    out.consoleErrorsAll = consoleErrors.length;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
