"use strict";
const L = require("./lib");
(async () => {
  const s = await L.startServer("fixed-06");
  let t = Date.now();
  const up = await L.upload(s.port, "telnet");
  console.log("upload", up.status, "in", Date.now() - t, "ms:", JSON.stringify(up.body).slice(0, 300));
  const id = await L.telnetId(s.port);
  console.log("telnet id", id);
  const p = await L.patchAlert(s.port, id, { actor: "smoke", assignee: "firstname.lastname@example-company.com" });
  console.log("patch", p.status, p.body && p.body.assignee);
  const page = await fetch(s.origin + "/alerts/" + id, { headers: { cookie: "mg_actor=Abcdefghijklmnopqrstuvwxyzabcdefghijklmn" } });
  const html = await page.text();
  const m = html.match(/<div class="banner"[\s\S]*?<\/div>/);
  console.log("banner:", m ? m[0].replace(/\s+/g, " ") : "none");
  console.log("actor note:", (html.match(/Changes are recorded[^<]*<strong>[^<]*<\/strong>/) || ["none"])[0]);
  await s.stop();
  console.log("log:", s.log().slice(0, 500));
})();
