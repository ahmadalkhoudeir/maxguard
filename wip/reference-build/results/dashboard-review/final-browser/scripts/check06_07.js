// Check 6: the ts=1e12 zip uploaded through the real server; / and /alerts/<id> in Chromium.
// Check 7: 201 alerts -> 200 rows and the "more match" caption; 3 alerts -> "3 alerts, most severe first".
// Usage: node check06_07.js <buildKey...>
"use strict";
const { chromium } = require("playwright");
const L = require("./lib.js");

async function check6(browser, srv) {
  const up = await L.upload(srv.base, L.FAR_ZIP);
  const list = await L.alerts(srv.base);
  const id = list[0].finding_id;
  const paths = ["/"].concat(srv.key.endsWith("3") ? ["/alerts/" + id] : []);
  const page = await browser.newPage();
  const out = { upload: `${up.status} ${up.text}`, apiLastSeen: list[0].last_seen, pages: {} };
  for (const p of paths) {
    const resp = await page.goto(srv.base + p);
    const body = await page.textContent("body");
    const m = body.match(/[0-9.e+]+ \(not a valid time\)/g);
    out.pages[p.replace(id, "<id>")] = { http: resp.status(), notValid: m ? m.length : 0, sample: m ? m[0] : body.trim().slice(0, 60) };
  }
  await page.close();
  out.pass = Object.values(out.pages).every((x) => x.http === 200 && x.notValid > 0);
  return out;
}

async function check7(browser, srv, n) {
  const sevs = [];
  const five = ["critical", "high", "medium", "low", "info"];
  for (let i = 0; i < n; i++) sevs.push(five[i % 5]);
  L.addAlerts(srv.build, srv.data, sevs, 70);
  const stored = (await L.alerts(srv.base)).length;
  const page = await browser.newPage();
  await page.goto(srv.base + "/");
  await L.sleep(800);  // the stream's first event refreshes the table once
  const r = await page.evaluate(() => {
    const rows = [...document.querySelectorAll("#alerts tbody tr")];
    const sev = (tr) => tr.querySelector('td[data-label="Severity"]').textContent.trim();
    return { rows: rows.length, caption: document.querySelector("#alerts caption").textContent.trim(),
             first: rows.length ? sev(rows[0]) : null, last: rows.length ? sev(rows[rows.length - 1]) : null };
  });
  let filtered = null;
  if (n > 200) {  // "use the filters to see them": the Info filter
    await page.selectOption("#severity", "info");
    await page.waitForURL(/severity=info/);
    await L.sleep(500);
    filtered = await page.evaluate(() => ({ url: location.search, rows: document.querySelectorAll("#alerts tbody tr").length,
      caption: document.querySelector("#alerts caption").textContent.trim() }));
  }
  await page.close();
  return { storedAlerts: stored, ...r, infoFilter: filtered };
}

(async () => {
  const browser = await chromium.launch();
  for (const key of process.argv.slice(2)) {
    const r6 = await L.withServer(key, "c06", (srv) => check6(browser, srv), { upload: false });
    console.log(`== ${key} check 6 (ts=1e12 through the real server): ${JSON.stringify(r6)}`);
    const r7a = await L.withServer(key, "c07a", (srv) => check7(browser, srv, 201), { upload: false });
    const r7b = await L.withServer(key, "c07b", (srv) => check7(browser, srv, 3), { upload: false });
    const pass = r7a.rows === 200 && r7a.caption === "The 200 most severe alerts. More alerts match: use the filters to see them." &&
                 r7b.caption === "3 alerts, most severe first";
    console.log(`== ${key} check 7 (queue limit): ${JSON.stringify({ with201: r7a, with3: r7b, pass })}`);
  }
  await browser.close();
})();
