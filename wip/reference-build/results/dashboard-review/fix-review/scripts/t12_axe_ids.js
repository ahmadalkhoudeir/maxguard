// T12: duplicate ids and axe-core results on the changed pages, original vs fixed.
"use strict";
const { chromium } = require("playwright");
const { AxeBuilder } = require("/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/tools/node/node_modules/@axe-core/playwright");
const L = require("./lib");

const builds = process.argv.filter((a) => /^(orig|fixed|patched[0-9]*)-/.test(a));

async function run(buildName, browser) {
  const out = {};
  const server = await L.startServer(buildName);
  try {
    for (const z of ["telnet", "ftp", "imap", "pop3", "plain_http", "plain_http_alt", "tls_weak_version", "cert_self_signed"]) {
      await L.upload(server.port, z);
    }
    const list = await L.alerts(server.port);
    const ctx = await browser.newContext();
    await ctx.addCookies([{ name: "mg_actor", value: "Ahmad", url: server.origin }]);
    const page = await ctx.newPage();
    for (const mode of ["analyst", "home"]) {
      await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin }]);
      for (const url of ["/", "/upload", `/alerts/${list[0].finding_id}`]) {
        await page.goto(server.origin + url);
        await L.sleep(400);
        const dup = await page.evaluate(() => {
          const ids = [...document.querySelectorAll("[id]")].map((e) => e.id);
          const seen = new Set(), d = new Set();
          for (const id of ids) (seen.has(id) ? d : seen).add(id);
          return { ids: ids.length, duplicates: [...d], alertLinkIds: ids.filter((i) => i.startsWith("alert-") && i !== "alert-status").length };
        });
        const axe = await new AxeBuilder({ page }).analyze();
        out[`${mode} ${url.startsWith("/alerts/") ? "/alerts/<id>" : url}`] = {
          ...dup,
          title: await page.title(),
          axe: axe.violations.map((v) => `${v.id}(${v.nodes.length})`).join(",") || "none",
        };
      }
    }
    out.alertsInStore = list.length;
    await ctx.close();
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of builds.length ? builds : ["orig-03", "fixed-03"]) console.log(b, JSON.stringify(await run(b, browser), null, 1));
  } finally {
    await browser.close();
    await L.stopAll();
  }
})();
