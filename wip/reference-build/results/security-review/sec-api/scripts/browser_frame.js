// Clickjacking check: can another site put the console in a frame?
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--no-proxy-server',
    '--host-resolver-rules=MAP attacker.example 127.0.0.1, MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1'] });
  const page = await browser.newPage();
  const statuses = {};
  page.on('response', (r) => { if (r.url().includes(':18731')) statuses[r.url()] = r.status(); });
  page.on('console', (m) => { if (/frame-ancestors|Refused to frame/i.test(m.text())) console.log('console:', m.text().slice(0, 160)); });
  await page.goto('http://attacker.example:18750/frame.html', { waitUntil: 'load' });
  await page.waitForTimeout(2000);
  for (const f of page.frames()) {
    if (f === page.mainFrame()) continue;
    let text = '';
    try { text = (await f.evaluate(() => document.body ? document.body.innerText : '')).slice(0, 60); } catch (e) { text = 'evaluate failed: ' + e.message.slice(0, 60); }
    console.log(`frame url=${f.url()} text=${JSON.stringify(text)}`);
  }
  console.log('HTTP status of framed URLs:', JSON.stringify(statuses));
  await browser.close();
})();
