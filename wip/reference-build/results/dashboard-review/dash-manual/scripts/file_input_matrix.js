"use strict";
const { chromium } = require("playwright");
const [BASE] = process.argv.slice(2);
const FIX = ".status-form, #upload-form { grid-template-columns: minmax(0, 1fr); }";
(async () => {
  const browser = await chromium.launch();
  const rows = [];
  for (const width of [320, 360, 375, 390]) {
    for (const family of [null, "Liberation Sans"]) {
      for (const fix of [false, true]) {
        const context = await browser.newContext({ viewport: { width, height: 700 }, bypassCSP: true });
        const page = await context.newPage();
        await page.goto(BASE + "/upload", { waitUntil: "load" });
        if (family) await page.addStyleTag({ content: `#file { font-family: "${family}" !important; }` });
        if (fix) await page.addStyleTag({ content: FIX });
        const m = await page.evaluate(() => {
          const card = document.getElementById("upload-form").getBoundingClientRect();
          const input = document.getElementById("file").getBoundingClientRect();
          return { scrollWidth: document.documentElement.scrollWidth, inputRight: Math.round(input.right),
                   cardInnerRight: Math.round(card.right - 17) };  // 1px border + 16px padding
        });
        rows.push(`${width}px  font=${(family || "default (DejaVu Sans)").padEnd(21)} fix=${fix ? "yes" : "no "}  scrollWidth=${m.scrollWidth}  ` +
                  `${m.scrollWidth > width ? "SIDEWAYS SCROLL" : "fits          "}  input right=${m.inputRight} card content right=${m.cardInnerRight}` +
                  `${m.inputRight > m.cardInnerRight ? "  (input sticks out of the card)" : ""}`);
        await context.close();
      }
    }
  }
  await browser.close();
  console.log(rows.join("\n"));
})();
