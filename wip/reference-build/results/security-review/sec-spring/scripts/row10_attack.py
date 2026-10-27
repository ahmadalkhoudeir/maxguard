"""AHM-04 row 10: tampered intel bundles against maxguard.intel.bundle (private ALL build).

Throwaway Ed25519 keys are made at run time in the output folder. Every crafted
bundle is installed into its own empty folder; after a refusal the script checks
that nothing was written (no "current" link, no version folder).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import resource
import shutil
import subprocess
import sys
import tarfile
import threading
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(REPO))

from maxguard.custody.signing import generate_keypair, sign  # noqa: E402
from maxguard.intel import bundle  # noqa: E402

RULES = b'alert tcp any any -> any 23 (msg:"MaxGuard review"; sid:9000001; rev:1;)\n'
WATCH = b"[]\n"


def tar_member(name, data=b"", kind=tarfile.REGTYPE, linkname=""):
    info = tarfile.TarInfo(name)
    info.type = kind
    info.size = len(data) if kind == tarfile.REGTYPE else 0
    info.linkname = linkname
    return info, (io.BytesIO(data) if kind == tarfile.REGTYPE else None)


def craft(path: Path, *, manifest_files, members, key, version="2027.03.01", sig=None,
          manifest_bytes=None):
    manifest = {"version": version, "created_by": "review", "files": [
        {"path": n, "sha256": hashlib.sha256(d).hexdigest(), "size": len(d)}
        for n, d in manifest_files]}
    mbytes = manifest_bytes if manifest_bytes is not None else json.dumps(manifest).encode()
    signature = sig if sig is not None else sign(mbytes, key)
    with tarfile.open(path, "w:gz") as tar:
        for info, data in [tar_member("manifest.json", mbytes), tar_member("manifest.sig", signature),
                           *members]:
            tar.addfile(info, data)
    return path


def nothing_written(dest: Path) -> str:
    if not dest.exists():
        return "nothing written (folder not created)"
    left = sorted(str(p.relative_to(dest)) for p in dest.rglob("*"))
    return "nothing written" if not left else f"LEFT ON DISK: {left}"


def attempt(label, path: Path, pub: Path, dest: Path):
    try:
        manifest = bundle.install_bundle(path, pub, dest)
        print(f"  [{label}] INSTALLED version {manifest['version']}  <-- not refused")
    except (bundle.BundleError, tarfile.TarError, OSError) as err:
        print(f"  [{label}] refused: {type(err).__name__}: {err}; {nothing_written(dest)}")


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    priv, pub = generate_keypair(WORK / "keys")
    _, other_pub = generate_keypair(WORK / "other-keys")
    other_priv = WORK / "other-keys" / "custody_ed25519_private.pem"
    src = WORK / "src"
    (src / "rules").mkdir(parents=True)
    (src / "intel").mkdir(parents=True)
    (src / "rules" / "maxguard-extra.rules").write_bytes(RULES)
    (src / "intel" / "ja4_watchlist.yaml").write_bytes(WATCH)
    good = WORK / "good-2027.03.01.tar.gz"
    bundle.build_bundle(src, good, priv, version="2027.03.01")
    print("== good bundle")
    print(f"  verify: {bundle.verify_bundle(good, pub)['version']}")

    print("== attacks (each into an empty install folder)")
    n = iter(range(100))
    d = lambda: WORK / f"dest{next(n)}"  # noqa: E731
    with tarfile.open(good, "r:gz") as t:
        good_manifest = t.extractfile("manifest.json").read()
    flipped = bytearray(good_manifest)
    flipped[good_manifest.index(b"2027.03.01") + 3] = ord("9")  # version 2029.03.01
    attempt("bad signature: manifest version byte changed, old signature kept",
            craft(WORK / "a1.tar.gz", manifest_files=[], members=[
                tar_member("rules/maxguard-extra.rules", RULES),
                tar_member("intel/ja4_watchlist.yaml", WATCH)], key=priv,
                manifest_bytes=bytes(flipped), sig=sign(good_manifest, priv)), pub, d())
    attempt("bad signature: signed with another key",
            craft(WORK / "a2.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES)], key=other_priv), pub, d())
    attempt("bad signature: 64 zero bytes",
            craft(WORK / "a3.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES)], key=priv, sig=b"\0" * 64), pub, d())
    attempt("signature file 65 bytes",
            craft(WORK / "a4.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES)], key=priv,
                  sig=sign(json.dumps({}).encode(), priv) + b"x"), pub, d())
    for bad in ("../x", "rules/../../x.rules", "/etc/x.rules", "./rules/a.rules", "rules/.a.rules",
                "rules/sub/a.rules", "RULES/a.rules", "intel/other.yaml", "scripts/run.sh",
                "rules/a.rules\n"):
        attempt(f"valid signature, manifest lists {bad!r}",
                craft(WORK / "b.tar.gz", manifest_files=[(bad, RULES)],
                      members=[tar_member(bad, RULES)], key=priv), pub, d())
    attempt("valid signature, manifest lists ../x but archive holds only an allowed file",
            craft(WORK / "b2.tar.gz", manifest_files=[("../x", RULES)],
                  members=[tar_member("rules/a.rules", RULES)], key=priv), pub, d())
    attempt("duplicate member (same name twice, second copy different)",
            craft(WORK / "c.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES), tar_member("rules/a.rules", b"evil")],
                  key=priv), pub, d())
    attempt("duplicate of manifest.json",
            craft(WORK / "c2.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES),
                           tar_member("manifest.json", b'{"version": "2099.1.1", "files": []}')],
                  key=priv), pub, d())
    attempt("symlink member listed in the manifest (rules/a.rules -> /etc/passwd)",
            craft(WORK / "e.tar.gz", manifest_files=[("rules/a.rules", b"")],
                  members=[tar_member("rules/a.rules", kind=tarfile.SYMTYPE, linkname="/etc/passwd")],
                  key=priv), pub, d())
    attempt("hard link member",
            craft(WORK / "e2.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES),
                           tar_member("rules/b.rules", kind=tarfile.LNKTYPE, linkname="rules/a.rules")],
                  key=priv), pub, d())
    attempt("directory member",
            craft(WORK / "e3.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules", kind=tarfile.DIRTYPE), tar_member("rules/a.rules", RULES)],
                  key=priv), pub, d())
    attempt("character device member",
            craft(WORK / "e4.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES),
                           tar_member("rules/null.rules", kind=tarfile.CHRTYPE)], key=priv), pub, d())
    attempt("extra file not in the manifest",
            craft(WORK / "f.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES), tar_member("rules/b.rules", RULES)],
                  key=priv), pub, d())
    attempt("file listed in the manifest but missing",
            craft(WORK / "f2.tar.gz", manifest_files=[("rules/a.rules", RULES), ("rules/b.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES)], key=priv), pub, d())
    attempt("member whose content (and hash) differs from the manifest",
            craft(WORK / "g.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES.replace(b"23", b"24"))], key=priv), pub, d())
    attempt("member with the same size, one byte changed",
            craft(WORK / "g2.tar.gz", manifest_files=[("rules/a.rules", RULES)],
                  members=[tar_member("rules/a.rules", RULES.replace(b"review", b"reviex"))], key=priv),
            pub, d())
    big = tarfile.TarInfo("rules/big.rules")
    big.size = (1 << 30) + 1
    path = WORK / "h.tar.gz"
    craft(path, manifest_files=[("rules/a.rules", RULES)], members=[tar_member("rules/a.rules", RULES)],
          key=priv)
    raw = io.BytesIO()
    with tarfile.open(path, "r:gz") as old, tarfile.open(fileobj=raw, mode="w") as new:
        for m in old:
            new.addfile(m, old.extractfile(m))
        new.fileobj.write(big.tobuf())  # a header that announces 1 GiB + 1 byte, no data
    import gzip
    path.write_bytes(gzip.compress(raw.getvalue()))
    attempt("header announces a 1 GiB + 1 byte member", path, pub, d())

    print("== version checks (rollback attack)")
    dest = WORK / "intel"
    print(f"  install 2027.03.01: {bundle.install_bundle(good, pub, dest)['version']}")
    attempt("same version again", good, pub, dest)
    old = WORK / "old-2027.02.01.tar.gz"
    bundle.build_bundle(src, old, priv, version="2027.02.01")
    attempt("older signed bundle 2027.02.01", old, pub, dest)
    attempt("older signed bundle written 2027.3.1 (same number)",
            bundle.build_bundle(src, WORK / "same.tar.gz", priv, version="2027.3.1") and WORK / "same.tar.gz",
            pub, dest)
    print(f"  current={bundle.installed_version(dest)} previous={bundle.installed_version(dest, 'previous')}")
    (src / "rules" / "maxguard-extra.rules").write_bytes(RULES + b"# v2\n")
    newer = WORK / "new-2027.04.01.tar.gz"
    bundle.build_bundle(src, newer, priv, version="2027.04.01")
    print(f"  install 2027.04.01: {bundle.install_bundle(newer, pub, dest)['version']}; "
          f"current={bundle.installed_version(dest)} previous={bundle.installed_version(dest, 'previous')}")
    print(f"  current link: {os.readlink(dest / 'current')}; versions on disk: "
          f"{sorted(p.name for p in (dest / 'versions').iterdir())}")
    print(f"  rollback(): now {bundle.rollback(dest)}; current={bundle.installed_version(dest)} "
          f"previous={bundle.installed_version(dest, 'previous')}")
    mid = WORK / "mid-2027.03.15.tar.gz"
    bundle.build_bundle(src, mid, priv, version="2027.03.15")
    attempt("after a rollback to 2027.03.01: an older-than-newest signed 2027.03.15", mid, pub, dest)
    print(f"  current={bundle.installed_version(dest)} previous={bundle.installed_version(dest, 'previous')}")

    print("== swap the bundle file between verify and extract (TOCTOU)")
    dest2 = WORK / "intel-toctou"
    bundle.install_bundle(good, pub, dest2)
    v2 = WORK / "v2.tar.gz"
    bundle.build_bundle(src, v2, priv, version="2027.05.01")
    with tarfile.open(v2, "r:gz") as t:
        m, s_ = t.extractfile("manifest.json").read(), t.extractfile("manifest.sig").read()
    evil = WORK / "v2-evil.tar.gz"
    with tarfile.open(evil, "w:gz") as tar:
        for info, data in [tar_member("manifest.json", m), tar_member("manifest.sig", s_),
                           tar_member("intel/ja4_watchlist.yaml", WATCH),
                           tar_member("rules/maxguard-extra.rules", b"x" * len(RULES + b"# v2\n"))]:
            tar.addfile(info, data)
    real_verify = bundle.verify_bundle
    target = WORK / "incoming.tar.gz"
    shutil.copy(v2, target)

    def verify_then_swap(path, key):
        manifest = real_verify(path, key)
        shutil.copy(evil, path)  # the USB stick's file changes after the check
        return manifest
    bundle.verify_bundle = verify_then_swap
    try:
        attempt("bundle swapped after verify_bundle()", target, pub, dest2)
    finally:
        bundle.verify_bundle = real_verify
    print(f"  current still {bundle.installed_version(dest2)}; leftovers in versions/: "
          f"{sorted(p.name for p in (dest2 / 'versions').iterdir())}")

    print("== atomic switch of the current link: readers during 150 installs")
    dest3 = WORK / "intel-atomic"
    errors, reads, stop = [], [0], threading.Event()

    def reader():
        while not stop.is_set():
            try:
                json.loads((dest3 / "current" / "manifest.json").read_bytes())
                reads[0] += 1
            except FileNotFoundError as err:
                if (dest3 / "current").is_symlink():
                    errors.append(repr(err))
            except json.JSONDecodeError as err:
                errors.append(repr(err))
    bundle.install_bundle(good, pub, dest3)
    th = threading.Thread(target=reader)
    th.start()
    for i in range(150):
        out = WORK / "loop.tar.gz"
        bundle.build_bundle(src, out, priv, version=f"2028.1.1.{i}")
        bundle.install_bundle(out, pub, dest3)
    stop.set()
    th.join()
    print(f"  {reads[0]} successful reads, {len(errors)} failed reads {errors[:2]}; "
          f"current={bundle.installed_version(dest3)}")

    print("== pax header bomb (read before any size limit or signature check)")
    for mib in (0, 256):
        p = WORK / f"pax-{mib}.tar.gz"
        info = tarfile.TarInfo("rules/a.rules")
        info.size = len(RULES)
        if mib:
            info.pax_headers = {"comment": "A" * (mib << 20)}
        with tarfile.open(p, "w:gz", format=tarfile.PAX_FORMAT) as tar:
            tar.addfile(info, io.BytesIO(RULES))
        code = (f"import sys,resource; sys.path.insert(0, {str(REPO)!r});"
                "from maxguard.intel import bundle\n"
                "try:\n"
                f"    bundle.verify_bundle({str(p)!r}, {str(pub)!r})\n"
                "except Exception as e: print('result:', type(e).__name__, str(e)[:60])\n"
                "print('peak RSS MiB:', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024)")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=300)
        print(f"  pax comment of {mib} MiB, bundle file {p.stat().st_size // 1024} KiB on disk: "
              f"{out.stdout.strip()} {out.stderr.strip()[-200:]}")


if __name__ == "__main__":
    main()
