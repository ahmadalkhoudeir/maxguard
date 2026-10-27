// Check 9: two PATCHes 200 ms apart to different alerts; both changes must appear in an open
// queue within 3 s without a reload.
// The server's stream looks for changes every 0.5 s, so two PATCHes 200 ms apart give two
// "alerts-changed" events only when a look falls between them. "aligned" trials learn the
// look times from the page (EventSource wrapped by an init script) and send PATCH 1 0.1 s
// before a look; "random" trials do not. "slow" holds every table-refresh answer 1.5 s
// (a busy Pi); "plain" does not.
// Usage: node check09_quick.js <buildKey> [trials]
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");
const KEY = process.argv[2];
const N = +(process.argv[3] || 5);
const PERIOD = 500;

(async () => {
  const browser = await chromium.launch();
  const result = await L.withServer(KEY, "c09", async (srv) => {
    L.addAlerts(srv.build, srv.data, ["critical", "medium", "low"], 90);
    const list = await L.alerts(srv.base);
    const [a, b, c] = [list[0].finding_id, list[1].finding_id, list[2].finding_id];
    const out = {};
    for (const variant of ["aligned-plain", "aligned-slow", "random-plain", "random-slow"]) {
      const page = await browser.newPage();
      await page.addInitScript(() => {
        const Orig = window.EventSource;
        window.__events = [];
        window.EventSource = function (url, opts) {
          const es = new Orig(url, opts);
          es.addEventListener("alerts-changed", () => window.__events.push(Date.now()));
          return es;
        };
        window.EventSource.prototype = Orig.prototype;
      });
      let refreshes = 0;
      page.on("request", (r) => { const u = new URL(r.url()); if (u.pathname === "/" && u.search.startsWith("?status=")) refreshes += 1; });
      if (variant.endsWith("slow")) {
        await page.route((u) => u.pathname === "/" && u.search.startsWith("?status="), async (route) => {
          let response;
          try { response = await route.fetch(); } catch (e) { return; }
          await L.sleep(1500);
          try { await route.fulfill({ response }); } catch (e) { /* the page aborted it */ }
        });
      }
      await page.goto(srv.base + "/");
      await L.sleep(2500);  // the first stream event and its (maybe slow) refresh
      const trials = [];
      for (let i = 1; i <= N; i++) {
        const tag = `${variant[0]}${variant.endsWith("slow") ? "s" : "p"}${i}`;
        if (variant.startsWith("aligned")) {
          // Probe: one change to a third alert; its event time gives the stream's look times.
          const nBefore = await page.evaluate(() => window.__events.length);
          await L.api(srv.base, "PATCH", "/api/alerts/" + c, { actor: "x", assignee: "probe" + tag });
          await page.waitForFunction((n) => window.__events.length > n, nBefore, { timeout: 5000 });
          const te = await page.evaluate(() => window.__events[window.__events.length - 1]);
          await L.sleep(2200);  // let the probe's refresh finish (slow: 1.5 s)
          let target = te + PERIOD;
          while (target - 100 < Date.now() + 50) target += PERIOD;
          await L.sleep(target - 100 - Date.now());  // PATCH 1 at 0.1 s before a look
        } else {
          await L.sleep(Math.random() * PERIOD);
        }
        const eventsBefore = await page.evaluate(() => window.__events.length);
        const refreshesBefore = refreshes;
        const t0 = Date.now();
        await L.api(srv.base, "PATCH", "/api/alerts/" + a, { actor: "x", assignee: tag + "a" });
        await L.sleep(200 - (Date.now() - t0));
        const t1 = Date.now();
        await L.api(srv.base, "PATCH", "/api/alerts/" + b, { actor: "x", assignee: tag + "b" });
        let both = null, first = null;
        while (Date.now() - t0 < 3000) {
          const s = await page.evaluate(([x, y]) => {
            const cells = [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].map((t) => t.textContent);
            return [cells.includes(x), cells.includes(y)];
          }, [tag + "a", tag + "b"]);
          if (s[0] && first === null) first = Date.now() - t0;
          if (s[0] && s[1]) { both = Date.now() - t0; break; }
          await L.sleep(50);
        }
        const events = (await page.evaluate(() => window.__events.length)) - eventsBefore;
        let lateMs = null;
        if (both === null) {  // how long until it shows after all (the 30-second poll)?
          const tLate = Date.now();
          try {
            await page.waitForFunction((y) => [...document.querySelectorAll('#alerts td[data-label="Assignee"]')].some((t) => t.textContent === y),
              tag + "b", { timeout: 40000, polling: 200 });
            lateMs = Date.now() - t0;
          } catch (e) { lateMs = `not within ${Math.round((Date.now() - t0) / 1000)} s`; }
          void tLate;
        }
        trials.push({ trial: i, patchGapMs: t1 - t0, streamEvents: events, refreshRequests: refreshes - refreshesBefore,
                      firstShownMs: first, bothShownMs: both, secondShownAtMs: lateMs, pass: both !== null });
        await L.sleep(2500);
      }
      await page.close();
      out[variant] = { passed: `${trials.filter((t) => t.pass).length}/${trials.length}`, trials };
    }
    return out;
  });
  console.log(`== ${KEY} check 9 (two quick changes):`);
  for (const [v, r] of Object.entries(result)) {
    console.log(`   ${v}: ${r.passed} trials showed both changes within 3 s`);
    for (const t of r.trials) console.log(`      ${JSON.stringify(t)}`);
  }
  await browser.close();
})();
