// Where does the alert page's horizontal scroll at 375 px come from (both builds)?
"use strict";
const { chromium } = require("playwright");
const L = require("./lib");
(async () => {
  const browser = await chromium.launch();
  try {
    for (const b of ["orig-03", "fixed-03"]) {
      const server = await L.startServer(b);
      try {
        await L.upload(server.port, "telnet");
        const [alert] = await L.alerts(server.port);
        await L.patchAlert(server.port, alert.finding_id, { actor: "t", assignee: "Wolfeschlegelsteinhausenbergerdorffwelchevoralternwarengewissenhaftschaferswessenschafewarenwohlgepflegeundsorgf" });
        const page = await (await browser.newContext({ viewport: { width: 375, height: 800 } })).newPage();
        await page.goto(server.origin + "/alerts/" + alert.finding_id);
        const r = await page.evaluate(() => {
          const vw = document.documentElement.clientWidth;
          const over = [...document.querySelectorAll("body *")].filter((e) => e.getBoundingClientRect().right > vw + 1);
          const texts = [];
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const n = walker.currentNode;
            if (!n.textContent.trim()) continue;
            const range = document.createRange(); range.selectNodeContents(n);
            for (const rect of range.getClientRects()) {
              if (rect.right > vw + 1) { texts.push(`${n.parentElement.tagName.toLowerCase()}${n.parentElement.className ? "." + n.parentElement.className : ""}: "${n.textContent.trim().slice(0, 50)}" right=${Math.round(rect.right)}`); break; }
            }
          }
          return { hscroll: document.scrollingElement.scrollWidth - vw, texts,
                   widest: over.map((e) => `${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""}${e.className ? "." + e.className : ""} right=${Math.round(e.getBoundingClientRect().right)}`).slice(-4) };
        });
        console.log(b, JSON.stringify(r));
        await L.patchAlert(server.port, alert.finding_id, { actor: "t", assignee: "" });
        await page.reload();
        console.log(b, "assignee empty: hscroll", await page.evaluate(() => document.scrollingElement.scrollWidth - document.documentElement.clientWidth));
      } finally { await server.stop(); }
    }
  } finally { await browser.close(); await L.stopAll(); }
})();
