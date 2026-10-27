"use strict";
const L = require("./lib.js");
(async () => {
  const s = await L.startServer("fixed-AHM-03", "sev");
  try {
    for (const f of ["plain_http", "dns_lookup", "cert_self_signed", "tls_weak_version", "pop3", "telnet"]) {
      try { console.log(f, JSON.stringify(await L.upload(s, f))); } catch (e) { console.log(f, "ERR", String(e).slice(0, 200)); }
    }
    for (const a of await L.alerts(s)) console.log(a.severity, a.rule_id, "|", a.title, "|", a.last_seen);
  } finally { await L.stopAll(); }
})();
