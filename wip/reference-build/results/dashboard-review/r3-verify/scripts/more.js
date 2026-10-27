// Extra helpers: established connections to a port (from /proc/net/tcp, no ss here),
// Web Locks state and bfcache restore info from a page.
"use strict";
const fs = require("fs");

function established(port) {
  let n = 0;
  for (const file of ["/proc/net/tcp", "/proc/net/tcp6"]) {
    let text = "";
    try { text = fs.readFileSync(file, "utf8"); } catch (e) { continue; }
    for (const line of text.split("\n").slice(1)) {
      const cols = line.trim().split(/\s+/);
      if (cols.length < 4) continue;
      const localPort = parseInt(cols[1].split(":").pop(), 16);
      if (localPort === port && cols[3] === "01") n++;   // 01 = ESTABLISHED, server side
    }
  }
  return n;
}

async function locks(page) {
  return page.evaluate(async () => {
    if (!navigator.locks) return "no Web Locks";
    const q = await navigator.locks.query();
    return `held=${q.held.length} pending=${q.pending.length}`;
  });
}

async function navInfo(page) {
  return page.evaluate(() => {
    const nav = performance.getEntriesByType("navigation")[0];
    const flat = [];
    const walk = (r) => { if (!r) return; for (const x of r.reasons || []) flat.push(x.reason); for (const c of r.children || []) walk(c); };
    walk(nav && nav.notRestoredReasons);
    return flat.length ? "not restored: " + flat.join(",") : (nav && nav.notRestoredReasons === null ? "restored from bfcache" : "unknown");
  });
}

const INIT = () => {
  window.__shows = [];
  addEventListener("pageshow", (e) => window.__shows.push(e.persisted ? "persisted" : "fresh"));
  window.__errors = [];
  addEventListener("error", (e) => window.__errors.push(String(e.message)));
  addEventListener("unhandledrejection", (e) => window.__errors.push("unhandled: " + String(e.reason)));
};

module.exports = { established, locks, navInfo, INIT };
