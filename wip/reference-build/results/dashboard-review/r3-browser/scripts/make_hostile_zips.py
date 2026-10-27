"""Zip the Telnet fixture logs with one hostile ts in maxguard_cleartext.log.
Usage: python make_hostile_zips.py <fixture dir> <out dir>   -> telnet-ts-1e12.zip, telnet-ts-1e400.zip"""
import json
import sys
import zipfile
from pathlib import Path

fixture, out = Path(sys.argv[1]), Path(sys.argv[2])
for literal in ("1e12", "1e400"):
    target = out / f"telnet-ts-{literal}.zip"
    with zipfile.ZipFile(target, "w") as z:
        for f in sorted(fixture.iterdir()):
            text = f.read_text()
            if f.name == "maxguard_cleartext.log":
                rec = json.loads(text.splitlines()[0])
                rec["ts"] = "@@TS@@"
                text = json.dumps(rec).replace('"@@TS@@"', literal) + "\n"
            z.writestr(f"telnet/{f.name}", text)
    print(target.name, target.stat().st_size, "bytes; ts literal", literal)
