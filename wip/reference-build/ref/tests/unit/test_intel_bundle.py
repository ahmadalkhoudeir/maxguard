"""Tests for signed offline intel bundles (Jaiden, JAI-11).

Every bad bundle must be refused before anything is written to the install folder.
Some bad bundles below are signed with the RIGHT key: the path and member checks
must hold even if the machine that builds bundles is compromised.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from maxguard.custody.signing import generate_keypair, sign
from maxguard.intel import bundle

RULES = b'alert tcp any any -> any 23 (msg:"MaxGuard test"; sid:9000001; rev:1;)\n'
WATCHLIST = b"[]\n"
MAPPING = b"framework: NIST SP 800-53\n"


@pytest.fixture
def keys(tmp_path) -> tuple[Path, Path]:
    return generate_keypair(tmp_path / "keys")


@pytest.fixture
def src(tmp_path) -> Path:
    """A folder laid out like a bundle: rules/, intel/, mappings/."""
    folder = tmp_path / "src"
    for relative, data in (("rules/maxguard-extra.rules", RULES),
                           ("intel/ja4_watchlist.yaml", WATCHLIST),
                           ("mappings/nist_800_53_r5.yaml", MAPPING)):
        (folder / relative).parent.mkdir(parents=True, exist_ok=True)
        (folder / relative).write_bytes(data)
    return folder


@pytest.fixture
def good(tmp_path, src, keys) -> Path:
    path = tmp_path / "intel-2027.03.01.tar.gz"
    bundle.build_bundle(src, path, keys[0], version="2027.03.01")
    return path


def craft(path: Path, members: list[tuple[str, bytes]], private_key: Path | None,
          manifest_files: list[tuple[str, bytes]] | None = None, version="2027.03.01",
          extra: list[tarfile.TarInfo] = ()) -> Path:
    """Write a bundle by hand, the way an attacker could, signed with private_key."""
    listed = members if manifest_files is None else manifest_files
    manifest = {"version": version, "created_by": "test", "files": [
        {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        for name, data in listed]}
    manifest_bytes = json.dumps(manifest).encode()
    signature = sign(manifest_bytes, private_key) if private_key else b"\0" * 64
    with tarfile.open(path, "w:gz") as tar:
        for name, data in [("manifest.json", manifest_bytes), ("manifest.sig", signature),
                           *members]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        for info in extra:
            tar.addfile(info)
    return path


def rewrite_member(source: Path, target: Path, name: str, new_data: bytes) -> Path:
    """Copy a bundle, replacing one member's content (the header size follows)."""
    with tarfile.open(source, "r:gz") as old, tarfile.open(target, "w:gz") as new:
        for member in old:
            data = old.extractfile(member).read()
            if member.name == name:
                data = new_data
                member.size = len(data)
            new.addfile(member, io.BytesIO(data))
    return target


def assert_refused(path: Path, keys, dest: Path, match: str) -> None:
    with pytest.raises(bundle.BundleError, match=match):
        bundle.install_bundle(path, keys[1], dest)
    assert not dest.exists() or list(dest.iterdir()) == []  # nothing was written


# ---------- good bundles ----------

def test_a_good_bundle_verifies(good, keys):
    manifest = bundle.verify_bundle(good, keys[1])
    assert manifest["version"] == "2027.03.01"
    assert [entry["path"] for entry in manifest["files"]] == [
        "intel/ja4_watchlist.yaml", "mappings/nist_800_53_r5.yaml",
        "rules/maxguard-extra.rules"]


def test_a_good_bundle_installs(good, keys, tmp_path):
    dest = tmp_path / "intel"
    bundle.install_bundle(good, keys[1], dest)
    current = dest / "current"
    assert current.is_symlink()
    assert (current / "rules" / "maxguard-extra.rules").read_bytes() == RULES
    assert (current / "intel" / "ja4_watchlist.yaml").read_bytes() == WATCHLIST
    assert json.loads((current / "manifest.json").read_text())["version"] == "2027.03.01"
    assert bundle.installed_version(dest) == "2027.03.01"


def test_the_same_files_give_the_same_bundle_bytes(src, keys, tmp_path):
    a = tmp_path / "a.tar.gz"
    b = tmp_path / "b.tar.gz"
    bundle.build_bundle(src, a, keys[0], version="2027.03.01")
    bundle.build_bundle(src, b, keys[0], version="2027.03.01")
    assert a.read_bytes() == b.read_bytes()


def test_a_newer_version_keeps_the_previous_one_for_rollback(good, src, keys, tmp_path):
    dest = tmp_path / "intel"
    bundle.install_bundle(good, keys[1], dest)
    (src / "rules" / "maxguard-extra.rules").write_bytes(RULES + b"# v2\n")
    newer = tmp_path / "intel-2027.04.01.tar.gz"
    bundle.build_bundle(src, newer, keys[0], version="2027.04.01")
    bundle.install_bundle(newer, keys[1], dest)
    assert bundle.installed_version(dest) == "2027.04.01"
    assert bundle.installed_version(dest, "previous") == "2027.03.01"

    assert bundle.rollback(dest) == "2027.03.01"
    assert (dest / "current" / "rules" / "maxguard-extra.rules").read_bytes() == RULES


def test_an_older_or_equal_version_is_refused(good, src, keys, tmp_path):
    dest = tmp_path / "intel"
    bundle.install_bundle(good, keys[1], dest)
    with pytest.raises(bundle.BundleError, match="not newer"):
        bundle.install_bundle(good, keys[1], dest)
    older = tmp_path / "old.tar.gz"
    bundle.build_bundle(src, older, keys[0], version="2027.02.28")
    with pytest.raises(bundle.BundleError, match="not newer"):
        bundle.install_bundle(older, keys[1], dest)
    assert bundle.installed_version(dest) == "2027.03.01"


def test_versions_compare_as_numbers():
    assert bundle.version_key("2027.10.01") > bundle.version_key("2027.9.30")


# ---------- refused bundles ----------

def test_a_changed_file_is_refused(good, keys, tmp_path):
    changed = rewrite_member(good, tmp_path / "changed.tar.gz", "rules/maxguard-extra.rules",
                             RULES.replace(b"23", b"24"))
    assert_refused(changed, keys, tmp_path / "intel", "does not match the manifest")


def test_a_changed_manifest_is_refused(good, keys, tmp_path):
    with tarfile.open(good, "r:gz") as tar:
        manifest = json.loads(tar.extractfile("manifest.json").read())
    manifest["version"] = "2099.01.01"
    changed = rewrite_member(good, tmp_path / "changed.tar.gz", "manifest.json",
                             json.dumps(manifest).encode())
    assert_refused(changed, keys, tmp_path / "intel", "bad signature")


def test_the_wrong_key_is_refused(good, tmp_path):
    other = generate_keypair(tmp_path / "other-keys")
    assert_refused(good, other, tmp_path / "intel", "bad signature")


@pytest.mark.parametrize("name", ["../evil.rules", "/etc/evil.rules", "rules/../../evil.rules",
                                  "scripts/run.sh", "rules/sub/deeper.rules"])
def test_a_bad_path_is_refused_even_when_signed(name, keys, tmp_path):
    path = craft(tmp_path / "bad.tar.gz", [(name, RULES)], keys[0])
    assert_refused(path, keys, tmp_path / "intel", "not an allowed bundle path")


def test_an_extra_file_is_refused(keys, tmp_path):
    path = craft(tmp_path / "extra.tar.gz",
                 [("rules/a.rules", RULES), ("rules/b.rules", RULES)], keys[0],
                 manifest_files=[("rules/a.rules", RULES)])
    assert_refused(path, keys, tmp_path / "intel", "not in the manifest")


def test_a_link_is_refused(keys, tmp_path):
    link = tarfile.TarInfo("rules/link.rules")
    link.type = tarfile.SYMTYPE
    link.linkname = "/etc/passwd"
    path = craft(tmp_path / "link.tar.gz", [("rules/a.rules", RULES)], keys[0], extra=[link])
    assert_refused(path, keys, tmp_path / "intel", "only regular files")


def test_a_duplicate_member_is_refused(keys, tmp_path):
    path = craft(tmp_path / "dup.tar.gz", [("rules/a.rules", RULES), ("rules/a.rules", b"x")],
                 keys[0], manifest_files=[("rules/a.rules", RULES)])
    assert_refused(path, keys, tmp_path / "intel", "appears twice")


def test_an_unsigned_bundle_is_refused(keys, tmp_path):
    path = craft(tmp_path / "unsigned.tar.gz", [("rules/a.rules", RULES)], private_key=None)
    assert_refused(path, keys, tmp_path / "intel", "bad signature")


def test_a_bad_version_is_refused(keys, tmp_path):
    path = craft(tmp_path / "v.tar.gz", [("rules/a.rules", RULES)], keys[0], version="../x")
    assert_refused(path, keys, tmp_path / "intel", "version must look like")


def test_build_refuses_files_that_are_not_allowed(src, keys, tmp_path):
    (src / "notes.txt").write_text("not intel")
    with pytest.raises(bundle.BundleError, match="not an allowed bundle file"):
        bundle.build_bundle(src, tmp_path / "x.tar.gz", keys[0], version="2027.03.01")


def test_not_a_gzip_file_is_refused(keys, tmp_path):
    path = tmp_path / "junk.tar.gz"
    path.write_bytes(gzip.compress(b"not a tar archive"))
    with pytest.raises(tarfile.TarError):
        bundle.verify_bundle(path, keys[1])


# ---------- command line ----------

def test_command_line(src, keys, tmp_path, capsys):
    out = tmp_path / "cli.tar.gz"
    dest = tmp_path / "intel"
    assert bundle.main(["build", str(src), str(out), str(keys[0]),
                        "--version", "2027.03.01"]) == 0
    assert bundle.main(["verify", str(out), str(keys[1])]) == 0
    assert bundle.main(["install", str(out), str(keys[1]), str(dest)]) == 0
    assert bundle.main(["install", str(out), str(keys[1]), str(dest)]) == 1
    printed = capsys.readouterr()
    assert "ok: version 2027.03.01, 3 files" in printed.out
    assert "installed version 2027.03.01" in printed.out
    assert "refused: version 2027.03.01 is not newer" in printed.err
