// Compare the axe results of the original and the fixed build (results/check14-<key>.json).
// Usage: node axe_compare.js <originalKey> <fixedKey>
"use strict";
const fs = require("fs");
const L = require("./lib.js");
const [O, F] = process.argv.slice(2);
const load = (k) => JSON.parse(fs.readFileSync(`${L.W}/results/check14-${k}.json`, "utf8"));
const flat = (rows) => rows.flatMap((r) => r.violations.map((v) => ({ key: `${r.mode} ${r.width} ${r.page}`, ...v })));
const o = flat(load(O)), f = flat(load(F));
const states = load(F).length;
const fmt = (v) => `${v.key}: ${v.id} [${v.impact}] ${v.nodes} node(s) ${v.targets.join(" ; ")}`;
console.log(`${O}: ${o.length} violation entries over ${load(O).length} page states`);
for (const v of o) console.log("   " + fmt(v));
console.log(`${F}: ${f.length} violation entries over ${states} page states`);
for (const v of f) console.log("   " + fmt(v));
const isNew = f.filter((v) => !o.some((w) => w.key === v.key && w.id === v.id && w.nodes >= v.nodes));
const gone = o.filter((v) => !f.some((w) => w.key === v.key && w.id === v.id));
const serious = f.filter((v) => v.impact === "serious" || v.impact === "critical");
console.log(`new or larger in ${F}: ${isNew.length}${isNew.length ? "\n   " + isNew.map(fmt).join("\n   ") : ""}`);
console.log(`gone in ${F}: ${gone.length}${gone.length ? "\n   " + gone.map(fmt).join("\n   ") : ""}`);
console.log(`serious or critical in ${F}: ${serious.length}${serious.length ? "\n   " + serious.map(fmt).join("\n   ") : ""}`);
const ids = (xs) => [...new Set(xs.map((v) => `${v.id}(${v.impact})`))].join(", ") || "none";
console.log(`rule ids: ${O}: ${ids(o)} | ${F}: ${ids(f)}`);
