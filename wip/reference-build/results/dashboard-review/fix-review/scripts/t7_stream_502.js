// T7: the holder's stream reconnects while a reverse proxy answers 502 (the server is
// restarting behind it). EventSource gives up for good on a non-200 answer. After the
// server is back, does a NEW queue tab get live refresh?
"use strict";
const { chromium } = require("playwright");
const http = require("http");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

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
    const ctx = await browser.newContext();
    const streams = [];
    ctx.on("request", (r) => {
      if (r.url().includes("/api/stream")) streams.push(r.frame().page()._label);
    });
    const H = await ctx.newPage(); H._label = "H";
    await H.goto(server.origin + "/");
    await L.sleep(1000);
    await server.stop();                       // the server goes down ...
    const stub = await stub502(port);          // ... and the proxy answers 502
    await L.sleep(8000);
    out.streamRequestsTo502 = stub.hits.filter((u) => u.startsWith("/api/stream")).length;
    await new Promise((r) => stub.srv.close(r));
    server = await L.startServer(buildName, { port, dataDir });   // back up
    await L.sleep(4000);
    out.streamsSoFar = streams.join(",");
    const X = await ctx.newPage(); X._label = "X";
    await X.goto(server.origin + "/");          // a new queue tab after the outage
    await L.sleep(1500);
    out.streamsAfterNewTab = streams.join(",");
    await L.upload(port, "ftp");
    const x = await L.waitFor(async () => (await L.rowCount(X)) === 2, 5000);
    const h = await L.waitFor(async () => (await L.rowCount(H)) === 2, 1000);
    out.liveRefresh = { newTabX: x.ok ? `yes ${x.ms} ms` : "NO within 5 s", oldTabH: h.ok ? "yes" : "NO" };
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  console.log("chromium", browser.version());
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(JSON.stringify(await run(b, browser)));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
