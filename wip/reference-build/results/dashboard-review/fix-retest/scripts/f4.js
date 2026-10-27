// F4: eight queue tabs in one browser context share ONE /api/stream; pages still load,
// filters answer, a PATCH reaches every tab; the stream moves when its tab closes;
// without navigator.locks each tab opens its own stream and live refresh still works.
"use strict";
const fs = require("fs");
const { execFileSync } = require("child_process");
const L = require("./lib.js");
const { chromium } = require("playwright");

const LOAD_TIMEOUT = 10000;
const UPDATE_LIMIT = 3000;   // pass threshold
const UPDATE_WAIT = 8000;    // how long we keep watching after the limit, to report the real time

function serverSockets(s) {
  try {
    const out = execFileSync("lsof", ["-nP", "-a", "-p", String(s.proc.pid), "-iTCP", "-sTCP:ESTABLISHED"], { encoding: "utf8" });
    return out.split("\n").filter((l) => l.includes(`:${s.port}->`)).length;
  } catch (e) { return 0; }  // lsof exits 1 when nothing matches
}
const streamLogLines = (s) => fs.readFileSync(s.logFile, "utf8").split("\n").filter((l) => l.includes('"GET /api/stream')).length;

function trackStreams(page, tab, streams) {
  page.on("request", (q) => {
    if (!q.url().includes("/api/stream")) return;
    const st = { tab, t: Date.now(), responded: false, ended: false, q };
    streams.push(st);
    q.response().then((r) => { if (r) { st.responded = true; st.tResp = Date.now(); } }).catch(() => {});
  });
  page.on("requestfinished", (q) => { for (const st of streams) if (st.q === q) st.ended = true; });
  page.on("requestfailed", (q) => { for (const st of streams) if (st.q === q) { st.ended = true; st.failed = (q.failure() || {}).errorText; } });
}
// page.evaluate waits for a pending navigation forever: bound it.
const evalT = (page, fn, arg, ms = 1500) => Promise.race([
  page.evaluate(fn, arg).catch(() => null),
  new Promise((r) => setTimeout(() => r("__timeout__"), ms)),
]);
const openStreams = (streams) => streams.filter((st) => st.responded && !st.ended);
const pendingStreams = (streams) => streams.filter((st) => !st.responded && !st.ended);

async function timedGoto(page, url) {
  const t0 = Date.now();
  try {
    const r = await page.goto(url, { waitUntil: "load", timeout: LOAD_TIMEOUT });
    return { ms: Date.now() - t0, status: r.status() };
  } catch (e) {
    return { ms: Date.now() - t0, error: String(e).split("\n")[0].slice(0, 80) };
  }
}

async function waitAssignee(tabs, id, name) {
  const t0 = Date.now();
  const res = await Promise.all(tabs.map(async (t) => {
    try {
      await t.page.waitForFunction(([i, n]) => {
        const a = document.querySelector(`a[href="/alerts/${i}"]`);
        return !!a && a.closest("tr").textContent.includes(n);
      }, [id, name], { timeout: UPDATE_LIMIT + UPDATE_WAIT, polling: 50 });
      return { tab: t.n, ms: Date.now() - t0 };
    } catch (e) {
      return { tab: t.n, ms: null };
    }
  }));
  const reloaded = [];
  for (const t of tabs) {
    if (!t.marked) continue;  // never loaded, so there was nothing to reload
    const marker = await evalT(t.page, () => window.__f4marker);
    if (marker !== "f4") reloaded.push(t.n);
  }
  return { perTab: res.map((r) => `${r.tab}:${r.ms === null ? "never" : r.ms}`).join(" "),
    within3s: res.filter((r) => r.ms !== null && r.ms <= UPDATE_LIMIT).length, of: tabs.length, reloaded };
}

const step = (m) => { if (process.env.F_DEBUG) console.error(`[${new Date().toISOString()}] ${m}`); };
async function mainTest(browser, s, id, records, res) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const streams = [];
  const tabs = [];
  for (let n = 1; n <= 8; n++) {
    const page = await ctx.newPage();
    L.instrument(page, `${s.buildName} f4 tab${n}`, records);
    trackStreams(page, n, streams);
    tabs.push({ n, page, load: await timedGoto(page, s.base + "/") });
    step(`tab ${n} loaded: ${JSON.stringify(tabs[n - 1].load)}`);
  }
  res.tabLoads = tabs.map((t) => `${t.n}:${t.load.error ? "TIMEOUT>" + LOAD_TIMEOUT : t.load.ms}`).join(" ");
  await L.sleep(2500);
  res.streams8 = { requested: streams.length, open: openStreams(streams).length, pending: pendingStreams(streams).length,
    openTabs: openStreams(streams).map((st) => st.tab).join(","), serverLogLines: streamLogLines(s), serverSockets: serverSockets(s) };

  // 9th tab: the upload page
  const p9 = await ctx.newPage();
  L.instrument(p9, `${s.buildName} f4 tab9`, records);
  const g9 = await timedGoto(p9, s.base + "/upload");
  res.tab9upload = g9.error ? `TIMEOUT>${LOAD_TIMEOUT} ms` : `${g9.ms} ms (status ${g9.status})`;

  step(`tab9 ${res.tab9upload}`);
  // filter change in tab 5
  const t5 = tabs[4].page;
  const t0 = Date.now();
  const answered = t5.waitForResponse((r) => r.url().includes("status=new"), { timeout: LOAD_TIMEOUT }).then(() => Date.now() - t0).catch(() => null);
  await t5.selectOption("#status", "new").catch(() => {});
  const ms5 = await answered;
  res.tab5filter = ms5 === null ? `no answer in ${LOAD_TIMEOUT} ms` : `${ms5} ms`;
  if (ms5 !== null) {
    await L.sleep(300);
    res.tab5after = await evalT(t5, () => `${location.search} | select=${document.getElementById("status").value} | caption="${(document.querySelector("#alerts caption") || {}).textContent}"`);
  }

  step(`tab5 filter ${res.tab5filter}; server alive: ${s.proc.exitCode === null}`);
  // PATCH 1 from another client; every queue tab must show it within 3 s, no reload
  for (const t of tabs) t.marked = (await evalT(t.page, () => { window.__f4marker = "f4"; return true; })) === true;
  res.tabsLoadedBeforePatch = tabs.filter((t) => t.marked).map((t) => t.n).join(",");
  res.patch1 = (await L.patchAlert(s, id, { actor: "x", assignee: "Someone" })).status;
  res.patch1Update = await waitAssignee(tabs, id, "Someone");

  // close the tab that holds the stream
  const holder = openStreams(streams)[0];
  res.holderTab = holder ? holder.tab : null;
  if (holder) {
    const before = streams.length;
    const tc = Date.now();
    await Promise.race([tabs[holder.tab - 1].page.close({ runBeforeUnload: false }).catch(() => {}), L.sleep(5000)]);
    for (const st of streams) if (st.tab === holder.tab) st.ended = true;
    let took = null;
    for (let i = 0; i < 100; i++) {
      const fresh = streams.slice(before).find((st) => st.responded);
      if (fresh) { took = { tab: fresh.tab, ms: fresh.tResp - tc }; break; }
      await L.sleep(100);
    }
    res.newStreamAfterClose = took ? `tab ${took.tab} after ${took.ms} ms` : "none within 10 s";
    await L.sleep(1000);
    const remaining = tabs.filter((t) => t.n !== holder.tab);
    res.streamsAfterClose = { open: openStreams(streams).length, pending: pendingStreams(streams).length,
      serverLogLines: streamLogLines(s), serverSockets: serverSockets(s) };
    res.patch2 = (await L.patchAlert(s, id, { actor: "x", assignee: "Second" })).status;
    res.patch2Update = await waitAssignee(remaining, id, "Second");
  }
  await Promise.race([ctx.close().catch(() => {}), L.sleep(10000)]);
}

async function fallbackTest(browser, s, id, records, res) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  await ctx.addInitScript(() => { Object.defineProperty(navigator, "locks", { value: undefined }); });
  const streams = [];
  const tabs = [];
  const open = async (n) => {
    const page = await ctx.newPage();
    L.instrument(page, `${s.buildName} f4 fallback tab${n}`, records);
    trackStreams(page, n, streams);
    const g = await timedGoto(page, s.base + "/");
    const marked = (await evalT(page, () => { window.__f4marker = "f4"; return true; })) === true;
    tabs.push({ n, page, load: g, marked });
  };
  await open(1);
  await L.sleep(1500);
  res.fb_locksInPage = await evalT(tabs[0].page, () => String(navigator.locks));
  res.fb_streams1 = openStreams(streams).length;
  res.fb_patch3 = (await L.patchAlert(s, id, { actor: "x", assignee: "Third" })).status;
  res.fb_singleTabUpdate = await waitAssignee(tabs, id, "Third");
  await open(2);
  await open(3);
  await L.sleep(1500);
  res.fb_streams3 = { open: openStreams(streams).length, perTab: openStreams(streams).map((st) => st.tab).join(",") };
  res.fb_patch4 = (await L.patchAlert(s, id, { actor: "x", assignee: "Fourth" })).status;
  res.fb_threeTabUpdate = await waitAssignee(tabs, id, "Fourth");
  await ctx.close();
}

async function runBuild(browser, buildName, records) {
  const s = await L.startServer(buildName, "f4");
  const res = { build: buildName };
  try {
    await L.upload(s, "telnet");
    const id = await L.telnetId(s);
    await mainTest(browser, s, id, records, res);
    await fallbackTest(browser, s, id, records, res);
  } finally {
    await L.stopServer(s);
  }
  return res;
}

for (const sig of ["SIGTERM", "SIGHUP", "SIGINT"]) {
  process.on(sig, async () => {
    console.error(`[${new Date().toISOString()}] node got ${sig}`);
    await L.stopAll();
    process.exit(128 + ({ SIGTERM: 15, SIGHUP: 1, SIGINT: 2 })[sig]);
  });
}
(async () => {
  const builds = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(L.BUILDS);
  const browser = await chromium.launch();
  const records = [];
  const results = [];
  try {
    for (const b of builds) results.push(await runBuild(browser, b, records));
  } finally {
    await browser.close();
    await L.stopAll();
  }
  for (const r of results) console.log(JSON.stringify(r, null, 1));
  const sum = L.summarizeRecords(records);
  console.log("console errors:", sum.consoleErrors.length, sum.consoleErrors.slice(0, 12), "outside:", sum.outside, "requests:", sum.requests);
  L.writeJSON(`f4-${builds.join("+")}.json`, { results, console: sum });
})();
