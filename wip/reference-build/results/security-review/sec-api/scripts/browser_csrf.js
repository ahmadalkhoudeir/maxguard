// Real-browser CSRF and DNS-rebinding check against the alpha console on 127.0.0.1:18731.
// Attacker pages are served by a local http.server on 127.0.0.1:18750. Host names are
// mapped to 127.0.0.1 inside Chromium; every other name fails to resolve and no proxy
// is used, so nothing leaves this machine.
const { chromium } = require('playwright');
const TARGET = 'http://127.0.0.1:18731';

(async () => {
  const browser = await chromium.launch({ args: [
    '--no-proxy-server',
    '--host-resolver-rules=MAP attacker.example 127.0.0.1, MAP evil.example 127.0.0.1, MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
  ] });
  const context = await browser.newContext();
  const log = [];
  const rows = new Map();
  context.on('request', (req) => {
    if (!req.url().includes(':18731')) return;
    const row = { method: req.method(), url: req.url().replace(TARGET, '') };
    rows.set(req, row);
    log.push(row);
  });
  const fill = async (req, status) => {
    const row = rows.get(req);
    if (!row) return;
    const h = await req.allHeaders().catch(() => ({}));
    Object.assign(row, { origin: h['origin'], site: h['sec-fetch-site'], mode: h['sec-fetch-mode'], status });
  };
  context.on('requestfinished', async (req) => { const res = await req.response(); await fill(req, res ? res.status() : 'none'); });
  context.on('requestfailed', (req) => fill(req, 'failed: ' + req.failure().errorText));

  const page = await context.newPage();
  const visit = async (url) => {
    const before = log.length;
    try { await page.goto(url, { waitUntil: 'load', timeout: 8000 }); } catch (e) { /* form navigations */ }
    await page.waitForTimeout(1500);
    console.log(`\n## ${url}  (title: ${JSON.stringify(await page.title().catch(() => ''))})`);
    for (const r of log.slice(before)) console.log(`   ${r.method} ${r.url} Origin=${r.origin} Sec-Fetch-Site=${r.site} Mode=${r.mode} -> ${r.status}`);
  };
  for (const site of ['http://attacker.example:18750', 'http://localhost:18750', 'http://127.0.0.1:18750']) {
    for (const p of ['form-mode.html', 'form-upload.html', 'fetch-upload.html', 'fetch-patch.html', 'sandbox-form.html']) {
      await visit(`${site}/${p}`);
    }
  }
  console.log('\nmg_mode cookie set for 127.0.0.1 after the attacks:',
              (await context.cookies(TARGET)).filter(c => c.name === 'mg_mode').length > 0);

  // DNS rebinding: the attacker's own name now resolves to 127.0.0.1.
  const rebind = 'http://evil.example:18731';
  const resp = await page.goto(rebind + '/', { waitUntil: 'load' });
  console.log(`\n## rebinding: GET ${rebind}/ -> ${resp.status()} body=${JSON.stringify((await resp.text()).slice(0, 40))}`);
  const same = await page.evaluate(async () => {
    const out = [];
    let r = await fetch('/api/alerts'); out.push(`GET /api/alerts -> ${r.status} ${JSON.stringify((await r.text()).slice(0, 30))}`);
    r = await fetch('/api/analyses', { method: 'POST', body: new FormData() }); out.push(`POST /api/analyses -> ${r.status}`);
    return out;
  });
  for (const line of same) console.log('   same-origin fetch from the rebound page: ' + line);

  // Control: the real dashboard, same origin, switching mode with its own form.
  const dash = await page.goto(TARGET + '/', { waitUntil: 'load' });
  console.log(`\n## control: GET ${TARGET}/ -> ${dash.status()}, CSP: ${dash.headers()['content-security-policy'] ? 'yes' : 'no'}`);
  const before = log.length;
  const form = await page.$('form[action="/mode"]');
  if (form) {
    await page.evaluate(() => {
      const f = document.querySelector('form[action="/mode"]');
      const m = f.querySelector('[name=mode]');
      if (m && m.tagName === 'INPUT' && m.type !== 'radio') m.value = 'home';
      else { const radio = f.querySelector('[name=mode][value=home]'); if (radio) radio.checked = true; }
      f.submit();
    });
    await page.waitForTimeout(1500);
  }
  for (const r of log.slice(before)) console.log(`   ${r.method} ${r.url} Origin=${r.origin} Sec-Fetch-Site=${r.site} -> ${r.status}`);
  console.log('   mg_mode cookie after the same-origin switch:',
              JSON.stringify((await context.cookies(TARGET)).filter(c => c.name === 'mg_mode').map(c => c.value)));
  await browser.close();
})();
