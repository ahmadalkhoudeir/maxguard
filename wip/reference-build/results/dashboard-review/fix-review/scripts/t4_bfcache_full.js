// T4: bfcache with full Chromium (new headless), bfcache on like a normal Chrome.
// What happens to live refresh after Back, for the holder and for a non-holder tab?
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");

const INIT = () => {
  window.__shows = window.__shows || [];
  addEventListener("pageshow", (e) => window.__shows.push(e.persisted ? "persisted" : "fresh"));
};

async function navInfo(page) {
  return page.evaluate(() => {
    const nav = performance.getEntriesByType("navigation")[0];
    const flat = [];
    const walk = (r) => {
      if (!r) return;
      for (const x of r.reasons || []) flat.push(x.reason);
      for (const c of r.children || []) walk(c);
    };
    walk(nav && nav.notRestoredReasons);
    return { shows: window.__shows.join(","), notRestored: flat.join(",") || "-" };
  });
}

async function locks(page) {
  return page.evaluate(async () => {
    if (!navigator.locks) return null;
    const q = await navigator.locks.query();
    return `held=${q.held.length} pending=${q.pending.length}`;
  });
}

const refreshed = async (page, rows) => {
  const r = await L.waitFor(async () => (await L.rowCount(page)) === rows, 4000);
  return r.ok ? `yes ${r.ms} ms` : `NO (rows=${await L.rowCount(page)} after ${r.ms} ms)`;
};

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    let rows = 1;
    const ctx = await browser.newContext();
    await ctx.addInitScript(INIT);
    const streams = [];
    ctx.on("request", (r) => {
      if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label);
    });

    // 1) single tab: queue -> alert -> Back, then a change
    const A = await ctx.newPage(); A._label = "A";
    await A.goto(server.origin + "/");
    await L.sleep(700);
    await A.click("#alerts tbody a");
    await A.waitForURL(/\/alerts\//);
    await L.sleep(700);
    await A.goBack({ waitUntil: "commit" });
    await L.sleep(1200);
    out.s1_back = await navInfo(A);
    out.s1_streams = streams.join(",");
    await L.upload(server.port, "ftp"); rows++;
    out.s1_liveRefreshAfterBack = await refreshed(A, rows);

    // 2) a non-holder tab N goes to /upload; a change happens; N comes Back
    const N = await ctx.newPage(); N._label = "N";
    await N.goto(server.origin + "/");
    await L.sleep(700);
    out.s2_locksFromN = await locks(N);
    await N.click("nav a[href='/upload']");
    await N.waitForURL(/\/upload/);
    await L.sleep(500);
    await L.upload(server.port, "imap"); rows++;
    await L.sleep(1500);
    await N.goBack({ waitUntil: "commit" });
    await L.sleep(1200);
    out.s2_back = await navInfo(N);
    out.s2_rowsInNAfterBack = `${await L.rowCount(N)} (server has ${rows})`;

    // 3) N again, but no change while it is away: restored from bfcache?
    await N.click("nav a[href='/upload']");
    await N.waitForURL(/\/upload/);
    await L.sleep(800);
    await N.goBack({ waitUntil: "commit" });
    await L.sleep(1200);
    out.s3_back = await navInfo(N);
    out.s3_locksFromN = await locks(N);
    // now the holder A closes: does N take over the stream?
    const before = streams.length;
    await A.close();
    await L.sleep(1500);
    out.s3_newStreamsAfterHolderClosed = streams.slice(before).join(",") || "none";
    await L.upload(server.port, "pop3"); rows++;
    out.s3_liveRefreshInN = await refreshed(N, rows);
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ channel: "chromium", ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("chromium", browser.version(), "(full Chromium, new headless, bfcache on)");
  try {
    const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
