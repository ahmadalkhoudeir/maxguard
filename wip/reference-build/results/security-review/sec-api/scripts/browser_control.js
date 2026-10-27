// Control: a person using the real dashboard (same origin) is not refused.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--no-proxy-server'] });
  const page = await browser.newPage();
  page.on('request', async (req) => {
    if (req.method() !== 'POST') return;
    const h = await req.allHeaders();
    console.log(`POST ${req.url()} Origin=${h['origin']} Sec-Fetch-Site=${h['sec-fetch-site']}`);
  });
  page.on('response', (res) => { if (res.request().method() === 'POST') console.log(`  -> ${res.status()}`); });
  await page.goto('http://127.0.0.1:18731/', { waitUntil: 'load' });
  await page.click('form.mode-switch button[value=home]');
  await page.waitForLoadState('load');
  const cookies = await page.context().cookies('http://127.0.0.1:18731');
  console.log('mg_mode cookie:', JSON.stringify(cookies.filter(c => c.name === 'mg_mode').map(c => c.value)));
  await browser.close();
})();
