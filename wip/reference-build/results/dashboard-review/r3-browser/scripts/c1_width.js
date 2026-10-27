// Check 1: no sideways scroll on any page, both modes, six widths, four injected fonts,
// with alerts of all five severities, a long assignee, a 40-character actor name and
// the AI-unavailable banner (Ollama absent).  Usage: node c1_width.js <build>...
"use strict";
const { chromium } = require("playwright");
const path = require("path");
const L = require("./lib");

const WIDTHS = [320, 375, 414, 701, 768, 1280];
const FONTS = ["default", "DejaVu Sans", "Liberation Sans", "Roboto", "Noto Sans"];
const ACTOR = "Abcdefghijklmnopqrstuvwxyzabcdefghijklmn"; // 40 characters, no spaces
const ASSIGNEE = "firstname.lastname@example-company.com";

async function measure(page) {
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  return page.evaluate(() => {
    const vw = window.innerWidth;
    const sw = document.documentElement.scrollWidth;
    let offenders = [];
    if (sw > vw) {
      for (const el of document.querySelectorAll("body *")) {
        const r = el.getBoundingClientRect();
        if (r.right > vw + 0.5 && r.width > 0) offenders.push([Math.round(r.right), el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (el.className && typeof el.className === "string" ? "." + el.className.split(" ").join(".") : "")]);
      }
      offenders.sort((a, b) => b[0] - a[0]);
      offenders = offenders.slice(0, 3);
    }
    return { vw, sw, cw: document.documentElement.clientWidth, font: getComputedStyle(document.body).fontFamily, offenders };
  });
}

async function run(buildName, browser) {
  const stage = buildName.slice(-2);
  const dataDir = L.newDataDir(buildName + "-c1");
  const added = L.addAlerts(buildName, dataDir, ["critical", "high", "medium", "low", "info"]);
  const server = await L.startServer(buildName, { dataDir });
  const out = { build: buildName, added, checks: 0, fails: [], fonts: {} };
  try {
    const up = await L.upload(server.port, "telnet");          // explain=True, Ollama absent -> banner
    const id = await L.telnetId(server.port);
    await L.patchAlert(server.port, id, { actor: ACTOR, assignee: ASSIGNEE });
    const alert = (await L.api(server.port, "GET", "/api/alerts/" + id)).body;
    out.upload = up.status; out.telnet = id; out.assignee = alert.assignee;
    const paths = ["/", "/upload"];
    if (stage !== "02") paths.push("/alerts/" + id, "/alerts/0000000000000000", "/?status=bogus");
    if (stage === "06") paths.push("/timeline?ip=172.18.0.3", `/timeline?ip=172.18.0.3&end=${Math.floor(alert.last_seen) + 1}`, "/assets");
    out.paths = paths;
    for (const mode of ["analyst", "home"]) {
      const ctx = await L.newContext(browser, { viewport: { width: 1280, height: 900 } });
      await ctx.addCookies([{ name: "mg_mode", value: mode, url: server.origin },
        { name: "mg_actor", value: ACTOR, url: server.origin }]);
      const page = await ctx.newPage();
      for (const p of paths) {
        for (const width of WIDTHS) {
          await page.setViewportSize({ width, height: 900 });
          const resp = await page.goto(server.origin + p);
          const status = resp.status();
          if (p.includes("/alerts/" + id) && mode === "analyst") {
            out.banner = await page.evaluate(() => { const b = document.querySelector(".banner"); return b ? b.textContent.replace(/\s+/g, " ").trim().slice(0, 90) + "..." : null; });
            out.actorNote = await page.evaluate(() => { const s = document.querySelector(".status-form strong"); return s ? s.textContent : null; });
          }
          if (p === "/") out.severities = await page.evaluate(() => [...new Set([...document.querySelectorAll("#alerts .sev")].map((e) => e.className.replace("sev ", "")))].sort().join(","));
          for (const font of FONTS) {
            const fam = await L.setFont(page, font);
            if (font !== "default" && !fam.includes(font)) out.fails.push({ p, mode, width, font, error: "font not applied: " + fam });
            out.fonts[font] = fam;
            const m = await measure(page);
            out.checks++;
            if (m.sw !== width || m.vw !== width) out.fails.push({ p, mode, width, font, status, sw: m.sw, vw: m.vw, offenders: m.offenders });
            // screenshots asked for in the task (fixed and original, for comparison)
            const shot = (name) => page.screenshot({ path: path.join(L.R, "shots", `${buildName}-${name}.png`), fullPage: true });
            if (font === "default" && mode === "home" && p === "/" && width === 375) await shot("home-queue-375");
            if (font === "default" && mode === "analyst" && p === "/upload" && width === 320) await shot("upload-320");
            if (font === "default" && mode === "analyst" && p === "/alerts/" + id && width === 320) await shot("alert-ai-banner-320");
          }
        }
      }
      await ctx.close();
    }
  } finally {
    await server.stop();
  }
  return out;
}

(async () => {
  const builds = process.argv.slice(2);
  const browser = await chromium.launch();
  console.log("Chromium", browser.version());
  try {
    for (const b of builds) {
      const r = await run(b, browser);
      const { fails, ...rest } = r;
      console.log(JSON.stringify(rest));
      console.log(`${b}: ${r.checks} measurements, ${fails.length} with sideways scroll`);
      const byKey = {};
      for (const f of fails) { const k = `${f.p} [${f.mode}]`; (byKey[k] = byKey[k] || []).push(`${f.width}px/${f.font}->${f.sw}${f.offenders ? " " + JSON.stringify(f.offenders[0]) : ""}${f.error ? " " + f.error : ""}`); }
      for (const [k, v] of Object.entries(byKey)) console.log(`  FAIL ${k}: ${v.length}x: ${v.join("; ")}`);
      const byWidth = {};
      for (const f of fails) byWidth[f.width] = (byWidth[f.width] || 0) + 1;
      console.log(`  fails by width: ${JSON.stringify(byWidth)}`);
    }
  } finally {
    await browser.close();
    await L.stopAll();
    console.log("hosts:", JSON.stringify(L.hostsSeen()));
  }
})();
