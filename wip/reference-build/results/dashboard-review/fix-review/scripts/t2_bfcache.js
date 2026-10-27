// T2: back/forward cache. Playwright turns bfcache off by default
// (--disable-back-forward-cache); this run turns it back on, like a normal Chrome.
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
    const reasons = nav && nav.notRestoredReasons;
    const flat = [];
    const walk = (r) => {
      if (!r) return;
      for (const x of r.reasons || []) flat.push(x.reason);
      for (const c of r.children || []) walk(c);
    };
    walk(reasons);
    return { shows: window.__shows, type: nav && nav.type, notRestored: flat };
  });
}

async function locks(page) {
  return page.evaluate(async () => {
    if (!navigator.locks) return null;
    const q = await navigator.locks.query();
    return { held: q.held.length, pending: q.pending.length };
  });
}

async function run(buildName, browser) {
  const out = { build: buildName };
  const server = await L.startServer(buildName);
  try {
    await L.upload(server.port, "telnet");
    const context = await browser.newContext();
    await context.addInitScript(INIT);
    const streams = [];
    context.on("request", (r) => {
      if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label);
    });

    // (a) one tab: queue -> alert -> back
    const A = await context.newPage(); A._label = "A";
    await A.goto(server.origin + "/");
    await L.sleep(800);
    await A.click("#alerts tbody a");
    await A.waitForURL(/\/alerts\//);
    await L.sleep(800);
    await A.goBack();
    await L.sleep(1500);
    out.a_backToQueue = await navInfo(A);
    out.a_locks = await locks(A);
    out.a_streams = streams.join(",");
    await L.upload(server.port, "ftp");
    const r1 = await L.waitFor(async () => (await L.rowCount(A)) === 2, 6000);
    out.a_refreshAfterBack = r1.ok ? `yes, ${r1.ms} ms` : `NO (rows=${await L.rowCount(A)} after ${r1.ms} ms)`;

    // (b) two tabs: holder goes to /upload and back
    const ctx2 = await browser.newContext();
    await ctx2.addInitScript(INIT);
    const s2 = [];
    ctx2.on("request", (r) => {
      if (r.url().includes("/api/stream")) s2.push(r.frame().page()._label);
    });
    const H = await ctx2.newPage(); H._label = "H";
    await H.goto(server.origin + "/");
    await L.sleep(500);
    const O = await ctx2.newPage(); O._label = "O";
    await O.goto(server.origin + "/");
    await L.sleep(800);
    out.b_streamsBefore = s2.join(",");
    await H.click("nav a[href='/upload']");
    await H.waitForURL(/\/upload/);
    await L.sleep(1500);
    out.b_streamsAfterHolderLeft = s2.join(",");
    out.b_locksSeenFromO = await locks(O);
    await L.upload(server.port, "imap");
    const r2 = await L.waitFor(async () => (await L.rowCount(O)) === 3, 6000);
    out.b_otherTabRefreshWhileHolderOnUpload = r2.ok ? `yes, ${r2.ms} ms` : `NO after ${r2.ms} ms`;
    await H.goBack();
    await L.sleep(1500);
    out.b_holderBack = await navInfo(H);
    out.b_streamsAfterBack = s2.join(",");
    out.b_locksSeenFromH = await locks(H);
    await L.upload(server.port, "pop3");
    const r3h = await L.waitFor(async () => (await L.rowCount(H)) === 4, 6000);
    const r3o = await L.waitFor(async () => (await L.rowCount(O)) === 4, 6000);
    out.b_afterBackRefresh = { H: r3h.ok ? `yes ${r3h.ms} ms` : `NO ${r3h.ms} ms`, O: r3o.ok ? `yes ${r3o.ms} ms` : `NO ${r3o.ms} ms` };
    await ctx2.close();
    await context.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ ignoreDefaultArgs: ["--disable-back-forward-cache"] });
  console.log("chromium", browser.version(), "(bfcache on)");
  try {
    for (const b of ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
