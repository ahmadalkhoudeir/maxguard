// Check 3 (c): a stub answers 502 on the stream port while the server restarts. After
// the server returns, live refresh works again within about 10 s (old tab and new tab).
// Usage: node c3c_stream502.js <build>...
"use strict";
const { chromium } = require("playwright");
const http = require("http");
const L = require("./lib");

function stub502(port) {
  const hits = [];
  const srv = http.createServer((req, res) => {
    hits.push(req.url);
    res.writeHead(502, { "content-type": "text/html" });
    res.end("<h1>502 Bad Gateway</h1>");
  });
  return new Promise((resolve) => srv.listen(port, "127.0.0.1", () => resolve({ srv, hits })));
}

async function run(buildName, browser) {
  const out = { build: buildName };
  let server = await L.startServer(buildName);
  const { port, dataDir } = server;
  try {
    await L.upload(port, "telnet");
    const ctx = await L.newContext(browser);
    const streams = [];
    ctx.on("request", (r) => { if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label); });
    const H = await ctx.newPage(); H._label = "H";
    await H.goto(server.origin + "/");
    await L.sleep(1000);
    await server.stop();                       // the server goes down ...
    const stub = await stub502(port);          // ... and the proxy answers 502
    await L.sleep(8000);
    out.streamRequestsTo502 = stub.hits.filter((u) => u.startsWith("/api/stream")).length;
    out.otherRequestsTo502 = stub.hits.filter((u) => !u.startsWith("/api/stream")).length;
    await new Promise((r) => stub.srv.close(r));
    server = await L.startServer(buildName, { port, dataDir });   // back up
    const tBack = Date.now();
    await L.sleep(1000);
    await L.upload(port, "ftp");               // a change 1 s after the server is back
    const h = await L.waitFor(async () => (await L.rowCount(H)) === 2, 35000, 100);
    const elapsed = Date.now() - tBack;
    out.oldTabLiveRefresh = h.ok ? `yes, ${elapsed} ms after the server returned` : "NO within 36 s";
    out.streamsSoFar = streams.join(",");
    const X = await ctx.newPage(); X._label = "X";
    await X.goto(server.origin + "/");          // a new queue tab after the outage
    await L.sleep(1500);
    await L.upload(port, "imap");
    const x = await L.waitFor(async () => (await L.rowCount(X)) === 3, 10000, 100);
    const h2 = await L.waitFor(async () => (await L.rowCount(H)) === 3, 10000, 100);
    out.afterNewTab = { newTabX: x.ok ? `yes ${x.ms} ms` : "NO within 10 s", oldTabH: h2.ok ? `yes ${h2.ms} ms` : "NO within 10 s" };
    out.streamsEnd = streams.join(",");
    out.pass = h.ok && elapsed <= 12000 && x.ok && h2.ok;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  console.log("Chromium", browser.version());
  try {
    for (const b of process.argv.slice(2)) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
