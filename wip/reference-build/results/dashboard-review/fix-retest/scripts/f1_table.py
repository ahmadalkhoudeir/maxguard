import json, sys, collections
raw = json.load(open(sys.argv[1]))
g = collections.OrderedDict()
for r in raw:
    g.setdefault((r["build"], r["page"], r["status"], r["mode"]), []).append(r)
def short(f):
    f = f.strip('"')
    return {"DejaVu Sans": "DejaVu", "Liberation Sans": "Liberation", "Roboto": "Roboto", "Noto Sans": "Noto"}.get(f, "def")
print("build | page | mode | sideways/25 | max scrollWidth (width/font) | failing width/font=scrollWidth")
for (b, p, st, m), rows in g.items():
    bad = [r for r in rows if r["scrollWidth"] > r["clientWidth"] or r["scrollX"] > 0 or r["over"] or r["textOver"]]
    worst = max(rows, key=lambda r: r["scrollWidth"] - r["clientWidth"])
    fails = " ".join(f'{r["width"]}/{short(r["font"])}={r["scrollWidth"]}' for r in bad)
    print(f'{b} | {p} ({st}) | {m} | {len(bad)}/{len(rows)} | {worst["scrollWidth"]} ({worst["width"]}/{short(worst["font"])}) | {fails or "-"}')
