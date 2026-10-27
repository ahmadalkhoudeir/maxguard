// Small Playwright helpers for the manual dashboard review (dash-manual).
"use strict";

// Record every request any page in the context makes, plus console messages
// and page errors (a CSP violation shows up as a console error).
function recordContext(context, log) {
  context.on("request", (req) => {
    log.requests.push({
      url: req.url(), method: req.method(), type: req.resourceType(),
      hx: req.headers()["hx-request"] || null,
      page: req.frame() && req.frame().page() ? req.frame().page().__name || "?" : "?",
    });
  });
  context.on("page", (page) => watchPage(page, log));
}

function watchPage(page, log) {
  page.on("console", (msg) => log.console.push({ page: page.__name || "?", type: msg.type(), text: msg.text() }));
  page.on("pageerror", (err) => log.pageErrors.push({ page: page.__name || "?", text: String(err) }));
}

// A short, readable description of the focused element.
const DESCRIBE = `(el) => {
  if (!el || el === document.body) return "BODY";
  const tag = el.tagName.toLowerCase();
  let s = tag;
  if (el.id) s += "#" + el.id;
  if (el.getAttribute("name")) s += "[name=" + el.getAttribute("name") + "]";
  if (el.getAttribute("type") && tag === "input") s += "[type=" + el.getAttribute("type") + "]";
  if (el.getAttribute("value") && tag === "button") s += "[value=" + el.getAttribute("value") + "]";
  if (el.getAttribute("href")) s += "[href=" + el.getAttribute("href") + "]";
  const text = (el.innerText || el.value || "").trim().replace(/\\s+/g, " ").slice(0, 40);
  if (text && tag !== "select") s += ' "' + text + '"';
  return s;
}`;

// Every element a keyboard user should be able to reach with Tab.
async function focusables(page) {
  return page.evaluate(`(() => {
    const describe = ${DESCRIBE};
    const all = [...document.querySelectorAll("a[href], button, select, input, textarea, [tabindex]")];
    return all.filter((el) => {
      if (el.disabled) return false;
      if (el.tagName === "INPUT" && el.type === "hidden") return false;
      const ti = el.getAttribute("tabindex");
      if (ti !== null && Number(ti) < 0) return false;
      return true;
    }).map(describe);
  })()`);
}

// Press Tab (or Shift+Tab) up to max times; record each stop with its focus style.
async function tabWalk(page, { max = 40, shift = false } = {}) {
  const stops = [];
  for (let i = 0; i < max; i++) {
    await page.keyboard.press(shift ? "Shift+Tab" : "Tab");
    const info = await page.evaluate(`(() => {
      const describe = ${DESCRIBE};
      const el = document.activeElement;
      const cs = el ? getComputedStyle(el) : null;
      const r = el ? el.getBoundingClientRect() : null;
      return {
        el: describe(el),
        focusVisible: el && el !== document.body ? el.matches(":focus-visible") : false,
        outline: cs ? cs.outlineStyle + " " + cs.outlineWidth + " " + cs.outlineColor : null,
        inViewport: r ? (r.width > 0 && r.height > 0 && r.left >= -1 && r.top >= -1 &&
                         r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1) : false,
      };
    })()`);
    if (stops.length && info.el === stops[0].el) break;  // wrapped around to the first stop
    stops.push(info);
  }
  return stops;
}

// No sideways scrolling: scrollWidth must fit the viewport. Also list what sticks out.
async function overflow(page) {
  return page.evaluate(`(() => {
    const vw = document.documentElement.clientWidth;
    const wide = [];
    for (const el of document.querySelectorAll("body *")) {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.right > vw + 0.5) {
        wide.push(el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") +
                  (el.className && typeof el.className === "string" ? "." + el.className.split(" ").join(".") : "") +
                  " right=" + Math.round(r.right));
      }
    }
    return { innerWidth, clientWidth: vw, scrollWidth: document.documentElement.scrollWidth,
             bodyScrollWidth: document.body.scrollWidth, wide: wide.slice(0, 10) };
  })()`);
}

module.exports = { recordContext, watchPage, focusables, tabWalk, overflow, DESCRIBE };
