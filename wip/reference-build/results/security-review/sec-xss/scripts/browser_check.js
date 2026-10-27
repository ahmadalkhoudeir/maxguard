// Load every dashboard page (and the HTML exports) in Chromium after uploading
// hostile Zeek logs; record dialogs, injected DOM, CSP headers/meta, outside requests.
// node browser_check.js <base url> <zip> <out.json> [report.html ...]
// Env: SPRING=1 also visits /timeline links and /assets. BANNER_ONLY=1: only alert pages.
"use strict";
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const [base, zip, outFile, ...reports] = process.argv.slice(2);
const SPRING = process.env.SPRING === "1";
const EXPECTED_CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; " +
  "connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'";

const out = { base, dialogs: [], outside: [], consoleCsp: [], pageErrors: [], pages: [],
              responses: [], statusForm: {}, controls: {}, reports: [] };

function isLocal(url) {
  return url.startsWith(base) || url.startsWith("file:") || url.startsWith("data:") ||
         url.startsWith("about:");
}

async function domFacts(page) {
  return page.evaluate(() => {
    const all = [...document.querySelectorAll("*")];
    const onAttrs = [];
    const jsUrls = [];
    for (const el of all) {
      for (const a of el.attributes) {
        if (a.name.toLowerCase().startsWith("on")) onAttrs.push(el.tagName + " " + a.name + "=" + a.value);
        const v = a.value.trim().toLowerCase().replace(/[\s\u0000-\u001f]/g, "");
        if (["href", "src", "action", "formaction", "hx-get", "hx-post", "hx-patch",
             "hx-put", "hx-delete", "data", "xlink:href"].includes(a.name.toLowerCase()) &&
            v.startsWith("javascript:")) jsUrls.push(el.tagName + " " + a.name + "=" + a.value);
      }
    }
    const meta = document.querySelector('meta[http-equiv="Content-Security-Policy" i]');
    const text = document.body ? document.body.innerText : "";
    return {
      title: document.title,
      scripts: [...document.scripts].map(s => s.getAttribute("src") || ("INLINE:" + s.textContent.slice(0, 60))),
      onAttrs, jsUrls,
      imgs: document.querySelectorAll("img").length,
      svgs: document.querySelectorAll("svg").length,
      iframes: document.querySelectorAll("iframe,object,embed,frame").length,
      bases: document.querySelectorAll("base").length,
      metaRefresh: document.querySelectorAll('meta[http-equiv="refresh" i]').length,
      metaCsp: meta ? meta.getAttribute("content") : null,
      hxAttrsWithPayload: [...document.querySelectorAll("[hx-get],[hx-post],[hx-patch]")]
        .map(e => e.getAttribute("hx-get") || e.getAttribute("hx-post") || e.getAttribute("hx-patch"))
        .filter(v => /alert|<|>/.test(v)),
      shows: {
        scriptText: text.includes("<script>alert(1)</script>"),
        imgText: text.includes("<img src=x onerror=alert("),
        svgText: text.includes("<svg onload=alert("),
        jsText: text.includes("javascript:alert("),
        template: text.includes("{{7*7}}"),
        aiK2: text.includes("K2 <script>alert(51)</script>"),
      },
      textLength: text.length,
    };
  });
}

async function visit(page, url, label) {
  const resp = await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(400);  // let htmx run and any error/load event fire
  const facts = await domFacts(page);
  const entry = { label, url, status: resp ? resp.status() : null,
                  csp: resp ? (resp.headers()["content-security-policy"] || null) : null, ...facts };
  out.pages.push(entry);
  return entry;
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  await context.route("**/*", route => {
    const url = route.request().url();
    if (isLocal(url)) return route.continue();
    out.outside.push(url);
    return route.abort();
  });
  const page = await context.newPage();
  page.on("dialog", async d => { out.dialogs.push({ message: d.message(), url: page.url() }); await d.dismiss(); });
  page.on("console", m => { if (/Content Security Policy|Content-Security-Policy/i.test(m.text())) out.consoleCsp.push(m.text().slice(0, 220)); });
  page.on("pageerror", e => out.pageErrors.push(String(e).slice(0, 200)));
  page.on("response", r => {
    const ct = r.headers()["content-type"] || "";
    if (ct.startsWith("text/html") && r.url().startsWith(base)) {
      out.responses.push({ url: r.url(), status: r.status(), method: r.request().method(),
                           csp: r.headers()["content-security-policy"] || null,
                           nosniff: r.headers()["x-content-type-options"] || null });
    }
  });

  if (zip) {
    // 1) upload through the real upload form (htmx posts multipart to /api/analyses)
    await page.goto(base + "/upload", { waitUntil: "load" });
    await page.setInputFiles("#file", zip);
    await page.click("#upload-form button[type=submit]");
    await page.waitForFunction(() => /Done|failed/.test(document.getElementById("upload-result").textContent), null, { timeout: 180000 });
    out.upload = await page.textContent("#upload-result");
  }

  // 2) every page, both modes
  await page.goto(base + "/", { waitUntil: "load" });
  const alertLinks = [...new Set(await page.$$eval('a[href^="/alerts/"]', as => as.map(a => a.getAttribute("href"))))];
  out.alertLinks = alertLinks;
  const errorPages = [
    "/?status=" + encodeURIComponent("<script>alert(31)</script>"),
    "/?severity=" + encodeURIComponent('"><img src=x onerror=alert(32)>'),
    "/alerts/" + encodeURIComponent('"><img src=x onerror=alert(33)>'),
    "/?x=" + encodeURIComponent('"><script>alert(34)</script>'),
    "/upload?next=" + encodeURIComponent("javascript:alert(35)"),
  ];
  for (const mode of ["analyst", "home"]) {
    await page.goto(base + "/", { waitUntil: "load" });
    await page.click(`form.mode-switch button[value=${mode}]`);
    await page.waitForLoadState("load");
    const pages = process.env.BANNER_ONLY === "1" ? alertLinks : ["/", "/upload", ...alertLinks, ...errorPages];
    for (const p of pages) await visit(page, base + p, mode);
    if (SPRING) {
      const timelineLinks = new Set();
      for (const a of alertLinks) {
        await page.goto(base + a, { waitUntil: "load" });
        for (const h of await page.$$eval('a[href^="/timeline"]', as => as.map(x => x.getAttribute("href")))) timelineLinks.add(h);
      }
      out.timelineLinks = [...timelineLinks];
      for (const t of ["/timeline", "/assets", ...timelineLinks]) await visit(page, base + t, mode);
      await page.goto(base + "/assets", { waitUntil: "load" });
      for (const h of await page.$$eval('a[href^="/timeline"]', as => as.map(x => x.getAttribute("href")))) await visit(page, base + h, mode + "-assetlink");
    }
  }

  if (process.env.BANNER_ONLY !== "1") {
    // 3) the status form: hostile name and assignee typed by a person (stored, shown to others)
    await page.goto(base + "/", { waitUntil: "load" });
    await page.click("form.mode-switch button[value=analyst]");
    await page.waitForLoadState("load");
    const first = base + alertLinks[0];
    await page.goto(first, { waitUntil: "load" });
    await page.fill("#actor", "<script>alert(41)</script>");
    await page.fill("#assignee", '"><img src=x onerror=alert(42)>');
    await page.selectOption("#alert-status", "investigating");
    const [patch] = await Promise.all([
      page.waitForResponse(r => r.url().endsWith("/status") && r.request().method() === "PATCH"),
      page.click("#status-form button[type=submit]"),
    ]);
    await page.waitForTimeout(400);
    out.statusForm.save = { status: patch.status(), csp: patch.headers()["content-security-policy"] || null,
                            message: await page.textContent("#status-form .message").catch(() => null) };
    out.statusForm.afterSave = await domFacts(page);
    out.statusForm.afterSave.actorShown = await page.textContent("#status-form strong").catch(() => null);
    const reload = await visit(page, first, "after-status-save");
    out.statusForm.queue = await visit(page, base + "/", "queue-after-status-save");
    out.statusForm.queueAssignee = await page.$$eval('td[data-label="Assignee"]', tds => tds.map(t => t.textContent)).catch(() => null);
    // an invalid status value, sent by htmx; the 400 fragment echoes it and htmx swaps it in
    await page.goto(first, { waitUntil: "load" });
    await page.evaluate(() => { const o = document.querySelector("#alert-status option"); o.value = "<img src=x onerror=alert(43)>"; o.selected = true; });
    const [bad] = await Promise.all([
      page.waitForResponse(r => r.url().endsWith("/status") && r.request().method() === "PATCH"),
      page.click("#status-form button[type=submit]"),
    ]);
    await page.waitForTimeout(400);
    out.statusForm.badStatus = { status: bad.status(), csp: bad.headers()["content-security-policy"] || null,
                                 message: await page.textContent("#status-form .message").catch(() => null),
                                 dom: await domFacts(page) };

    // 4) controls: does the CSP header really stop an injected inline script? And does
    //    this harness notice a dialog when there is no CSP (proves the detector works)?
    for (const keepCsp of [true, false]) {
      const p2 = await context.newPage();
      const dialogs = [];
      const csp = [];
      p2.on("dialog", async d => { dialogs.push(d.message()); await d.dismiss(); });
      p2.on("console", m => { if (/Content Security Policy/i.test(m.text())) csp.push(m.text().slice(0, 160)); });
      await p2.route(base + "/upload", async route => {
        const resp = await route.fetch();
        const headers = { ...resp.headers() };
        if (!keepCsp) delete headers["content-security-policy"];
        const body = (await resp.text()).replace("<main", "<script>alert(99)</script><img src=x onerror=alert(100)><main");
        await route.fulfill({ status: resp.status(), headers, body });
      });
      await p2.goto(base + "/upload", { waitUntil: "load" });
      await p2.waitForTimeout(600);
      out.controls[keepCsp ? "dashboard_injected_with_csp" : "dashboard_injected_without_csp"] = { dialogs, csp };
      await p2.close();
    }
  }

  // 5) the HTML exports, opened from disk
  for (const r of reports) {
    const url = "file://" + path.resolve(r);
    const before = out.dialogs.length;
    const facts = await visit(page, url, "report");
    facts.dialogsHere = out.dialogs.length - before;
    if (/many_report/.test(r)) {
      facts.mediumMentions = await page.evaluate(() => (document.body.innerText.match(/medium/gi) || []).length);
      facts.aiHeadings = await page.$$eval("h3", hs => hs.map(h => h.innerText));
    }
    out.reports.push(facts);
    // tampered copy: what if a later edit forgot to escape? The meta CSP must still block it.
    for (const keepMeta of [true, false]) {
      let html = fs.readFileSync(r, "utf8").replace("<main>", "<main><script>alert(97)</script><img src=x onerror=alert(98)>");
      if (!keepMeta) html = html.replace(/<meta http-equiv="Content-Security-Policy"[^>]*>/, "");
      const tampered = path.join(path.dirname(outFile), path.basename(r, ".html") + (keepMeta ? "-tampered.html" : "-tampered-nocsp.html"));
      fs.writeFileSync(tampered, html);
      const p3 = await context.newPage();
      const dialogs = [];
      const csp = [];
      p3.on("dialog", async d => { dialogs.push(d.message()); await d.dismiss(); });
      p3.on("console", m => { if (/Content Security Policy/i.test(m.text())) csp.push(m.text().slice(0, 160)); });
      await p3.goto("file://" + tampered, { waitUntil: "load" });
      await p3.waitForTimeout(600);
      out.controls[path.basename(tampered)] = { dialogs, csp };
      await p3.close();
    }
  }

  out.expectedCsp = EXPECTED_CSP;
  out.summary = {
    dialogs: out.dialogs.length,
    outsideRequests: out.outside.length,
    pages: out.pages.length,
    htmlResponses: out.responses.length,
    htmlResponsesWithoutExpectedCsp: out.responses.filter(r => r.csp !== EXPECTED_CSP).map(r => r.method + " " + r.url + " " + r.status),
    pagesWithInjectedDom: out.pages.filter(p => p.onAttrs.length || p.jsUrls.length || p.imgs || p.svgs || p.iframes || p.bases || p.metaRefresh ||
      p.scripts.some(s => !["/static/htmx-2.0.11.min.js", "/static/app.js"].includes(s))).map(p => p.label + " " + p.url),
    dashboardPagesWithoutCspHeader: out.pages.filter(p => !p.url.startsWith("file:") && p.csp !== EXPECTED_CSP).map(p => p.url),
  };
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out.summary, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
