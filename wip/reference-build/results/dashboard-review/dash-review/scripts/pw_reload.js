// uvicorn --reload (docker/compose.dev.yaml) with a queue tab open: does a code change reload?
// Usage: node pw_reload.js <uvicorn> <repo> <data> <port> <tab: queue|none>
"use strict";
const { spawn } = require("child_process");
const fs = require("fs");
const { chromium } = require("playwright");
const [UV, REPO, DATA, PORT, TAB] = process.argv.slice(2);
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  let log = "";
  const server = spawn(UV, ["maxguard.api.app:create_app", "--factory", "--host", "127.0.0.1", "--port", PORT,
    "--reload", "--reload-dir", REPO + "/maxguard"].concat(process.env.EXTRA ? process.env.EXTRA.split(" ") : []), { cwd: REPO, env: { ...process.env, MAXGUARD_DATA_DIR: DATA } });
  server.stderr.on("data", (d) => { log += d; });
  for (let i = 0; i < 80; i++) { try { if ((await fetch(BASE + "/upload")).ok) break; } catch (e) { /* not up */ } await sleep(250); }
  const browser = await chromium.launch();
  if (TAB === "queue") { const page = await browser.newPage(); await page.goto(BASE + "/"); }
  await sleep(2000);
  const marker = REPO + "/maxguard/web/__init__.py";
  fs.appendFileSync(marker, "\n");  // a code edit (in this throwaway copy)
  const t0 = Date.now();
  let back = false;
  for (let i = 0; i < 40; i++) {
    await sleep(500);
    if ((log.match(/Started server process/g) || []).length >= 2) { back = true; break; }
  }
  console.log(`queue tab open: ${TAB === "queue"} -> ${back ? `reloaded in ${Date.now() - t0} ms` : "no reload within 20 s"}`);
  console.log("uvicorn said:", JSON.stringify(log.split("\n").filter((l) => /WatchFiles|StatReload|Reloading|Shutting down|Waiting for connections|Started server process/.test(l)).map((l) => l.replace(/\[\d+\]/, "[pid]"))));
  fs.writeFileSync(marker, fs.readFileSync(marker, "utf8").replace(/\n+$/, "\n"));
  server.kill("SIGINT"); await sleep(500); server.kill("SIGKILL");
  try { process.kill(-server.pid); } catch (e) { /* gone */ }
  await Promise.race([browser.close(), sleep(5000)]);
  process.exit(0);
})();
