"""Make the two upload files from a build's Telnet fixture logs.
telnet_logs.zip        : tests/fixtures/zeek/telnet as a .zip (the guide's upload)
telnet_far_future.zip  : the same, but the maxguard_cleartext.log record has ts=1e12
Usage: python make_zips.py <build> <out_dir>"""
import json
import sys
import zipfile
from pathlib import Path

build, out = Path(sys.argv[1]), Path(sys.argv[2])
fixture = build / "tests/fixtures/zeek/telnet"
for name, future in (("telnet_logs.zip", False), ("telnet_far_future.zip", True)):
    with zipfile.ZipFile(out / name, "w") as z:
        for f in sorted(fixture.iterdir()):
            text = f.read_text()
            if future and f.name == "maxguard_cleartext.log":
                rec = json.loads(text.splitlines()[0])
                rec["ts"] = 1e12
                text = json.dumps(rec) + "\n"
            z.writestr(f"telnet/{f.name}", text)
    print(out / name, (out / name).stat().st_size, "bytes")
