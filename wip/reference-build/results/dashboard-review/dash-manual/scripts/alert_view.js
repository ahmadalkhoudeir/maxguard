// Open one alert in Analyst or Home mode and report what the page shows.
// usage: node alert_view.js <base url> <finding id> <mode> <screenshot path>
"use strict";
const { chromium } = require("playwright");
const [BASE, FINDING, MODE, SHOT] = process.argv.slice(2);

const JARGON = ["cleartext.telnet", "NIST", "PCI", "CISA", "CJIS", "T1040", "ATT&CK", "credential-access",
                "SC-8", "maxguard_cleartext.log", "CJKFoj4bpHEhTeaRoj", "Rule", "Evidence", "record",
                "False positive", "Investigating", "src_ip", "dst_port", "tactic"];

(async () => {
  const errors = [], requests = [];
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addCookies([{ name: "mg_mode", value: MODE, url: BASE }]);
  const page = await context.newPage();
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
  page.on("request", (r) => requests.push(r.method() + " " + r.url()));
  const resp = await page.goto(`${BASE}/alerts/${FINDING}`, { waitUntil: "load" });
  const info = await page.evaluate((jargon) => {
    const main = document.querySelector("main");
    const text = main.innerText;
    const q = (s) => [...document.querySelectorAll(s)];
    const ai = document.querySelector('section[aria-labelledby="ai-heading"]');
    return {
      title: document.title,
      h1: q("main h1").map((e) => e.innerText),
      h2: q("main h2").map((e) => e.innerText),
      severityBadge: q("main .sev").map((e) => e.innerText),
      homeAction: q(".home-action").map((e) => e.innerText),
      aiSection: ai ? ai.innerText : null,
      banner: q(".banner").map((e) => ({ role: e.getAttribute("role"), text: e.innerText })),
      sentences: q(".ai-sentences li").map((li) => ({
        text: li.childNodes[0].textContent.trim(),
        chips: [...li.querySelectorAll("a.chip")].map((a) => ({ text: a.innerText, href: a.getAttribute("href"),
          targetRowExists: !!document.getElementById(a.getAttribute("href").slice(1)) })),
      })),
      evidenceRows: q('tr[id^="ev-"]').map((tr) => tr.id),
      statusForm: !!document.getElementById("status-form"),
      jargonFound: jargon.filter((j) => text.includes(j)),
      mainText: text,
    };
  }, JARGON);
  await page.screenshot({ path: SHOT, fullPage: true });
  await browser.close();
  console.log(JSON.stringify({ http: resp.status(), mode: MODE, ...info, errors,
    origins: [...new Set(requests.map((r) => new URL(r.split(" ")[1]).origin))] }, null, 1));
})().catch((e) => { console.error("SCRIPT ERROR", e); process.exit(1); });
