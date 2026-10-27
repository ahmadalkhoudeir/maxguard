// Sideways overflow at several widths, with long names and the long Home badges.
// Usage: node pw_css.js <base-url>
"use strict";
const { chromium } = require("playwright");
const BASE = process.argv[2];
async function api(method, path, body) {
  const res = await fetch(BASE + path, { method, headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined });
  return [res.status, await res.json()];
}
const VARIANT = process.argv[3] || "realistic";
const LONG = { realistic: "Ahmad Alkhoudeir", email: "firstname.lastname@smallbusiness.example", max: "A".repeat(100) }[VARIANT];
(async () => {
  const browser = await chromium.launch();
  const alerts = (await api("GET", "/api/alerts"))[1];
  const info = alerts.find((a) => a.severity === "info");
  const crit = alerts.find((a) => a.severity === "critical");
  await api("PATCH", "/api/alerts/" + crit.finding_id, { actor: "setup", assignee: LONG });
  const pages = ["/", "/upload", "/alerts/" + info.finding_id, "/alerts/" + crit.finding_id];
  for (const font of ["default", "DejaVu Sans", "Noto Sans"]) {
    for (const mode of ["analyst", "home"]) {
      for (const width of (process.env.WIDTHS || "320,375,768,1280").split(",").map(Number)) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 }, bypassCSP: font !== "default" });
        await ctx.addCookies([{ name: "mg_mode", value: mode, url: BASE }, { name: "mg_actor", value: encodeURIComponent(LONG), url: BASE }]);
        const page = await ctx.newPage();
        const out = [];
        for (const path of pages) {
          await page.goto(BASE + path);
          if (font !== "default") {
            await page.addStyleTag({ content: `html, body, input, button, select, label { font-family: "${font}" !important }` });
          }
          const r = await page.evaluate(() => {
            const vw = document.documentElement.clientWidth;
            const sticking = [...document.querySelectorAll("body *")].filter((e) => {
              const b = e.getBoundingClientRect(); return b.width && b.right > vw + 0.5;
            }).map((e) => `${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""}${e.className && typeof e.className === "string" ? "." + e.className.split(" ")[0] : ""}`);
            const form = document.getElementById("status-form");
            const save = document.getElementById("status-save");
            return { sw: document.documentElement.scrollWidth, vw, sticking: [...new Set(sticking)].slice(0, 6),
              form: form ? Math.round(form.getBoundingClientRect().width) : null,
              save: save ? Math.round(save.getBoundingClientRect().right) : null };
          });
          const label = path.startsWith("/alerts/") ? (path.includes(info.finding_id) ? "/alerts/<info>" : "/alerts/<critical, long assignee>") : path;
          out.push(`${label}: scrollWidth ${r.sw}${r.sw > r.vw ? " OVERFLOW " + JSON.stringify(r.sticking) : ""}${r.form ? ` (form ${r.form}px, Save right edge ${r.save})` : ""}`);
        }
        console.log(`[${font}] ${mode} ${width}px\n  ` + out.join("\n  "));
        await ctx.close();
      }
    }
  }
  await api("PATCH", "/api/alerts/" + crit.finding_id, { actor: "setup", assignee: "" });
  await browser.close();
})();
