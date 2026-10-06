"""Signed offline intel bundles (Jaiden, JAI-11).

Rule and intel updates (Suricata rules, the JA4 watchlist, mapping files) reach
an offline MaxGuard on a USB stick, as one .tar.gz "bundle":

    manifest.json                 version, created_by, and every file with its SHA-256 and size
    manifest.sig                  Ed25519 signature (64 bytes) over manifest.json's exact bytes
    rules/<name>.rules            Suricata rules
    intel/ja4_watchlist.yaml      the JA4 watchlist
    mappings/<name>.yaml          mapping files

An update channel is a favorite attack path: whoever can change the rules can
blind the sensor. So a bundle is checked in this order, and nothing is written
to disk until every check has passed:
1. the archive's member list: only regular files, no duplicates, sane sizes;
2. the signature over manifest.json, with the public key the user installed;
3. the member list against the manifest: same files, only allowed paths
   (this also refuses absolute paths, "..", links and devices);
4. every file's size and SHA-256 against the manifest.
Installing then extracts into a new folder, checks the hashes again on disk,
and switches the "current" link to it in one step (os.replace), keeping the
previous version for rollback. An older version is refused, so a stolen old
bundle cannot roll the rules back (a "rollback attack").

Command line:
    python -m maxguard.intel.bundle build SRC_DIR OUT.tar.gz PRIVATE_KEY --version 2027.03.01
    python -m maxguard.intel.bundle verify BUNDLE PUBLIC_KEY
    python -m maxguard.intel.bundle install BUNDLE PUBLIC_KEY DEST_DIR
    python -m maxguard.intel.bundle rollback DEST_DIR
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

from maxguard import __version__
from maxguard.custody.signing import sign, verify

MANIFEST = "manifest.json"
SIGNATURE = "manifest.sig"
SIGNATURE_BYTES = 64          # an Ed25519 signature is always 64 bytes
MAX_MANIFEST_BYTES = 1 << 20  # 1 MiB
MAX_MEMBERS = 1000
MAX_TOTAL_BYTES = 1 << 30     # 1 GiB unpacked: refuse "archive bombs"

NAME = r"[A-Za-z0-9][A-Za-z0-9._-]*"
ALLOWED_PATHS = (
    re.compile(rf"rules/{NAME}\.rules"),
    re.compile(r"intel/ja4_watchlist\.yaml"),
    re.compile(rf"mappings/{NAME}\.yaml"),
)
VERSION_PATTERN = re.compile(r"\d{1,6}(\.\d{1,6}){0,3}")  # 2027.03.01 or 2027.03.01.2
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")

VERSIONS_DIR = "versions"
CURRENT = "current"
PREVIOUS = "previous"


class BundleError(ValueError):
    """The bundle is not safe to install. Nothing was written."""


# ---------- building (on the maintainer's machine, which has the private key) ----------

def build_bundle(src_dir: Path, out_path: Path, private_key_path: Path, *, version: str) -> dict:
    """Write a signed bundle of every file under src_dir and return its manifest.

    The same files and version always give the same bundle bytes (fixed times and
    owners, sorted names), so anyone can rebuild it and compare."""
    check_version(version)
    files = collect_files(Path(src_dir))
    manifest = {
        "version": version,
        "created_by": f"maxguard {__version__}",
        "files": [{"path": path, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
                  for path, data in files],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    signature = sign(manifest_bytes, private_key_path)
    members = [(MANIFEST, manifest_bytes), (SIGNATURE, signature), *files]
    write_tar_gz(Path(out_path), members)
    return manifest


def collect_files(src_dir: Path) -> list[tuple[str, bytes]]:
    """(path inside the bundle, content) for every file, sorted; refuses anything not allowed."""
    files = []
    for path in sorted(src_dir.rglob("*")):
        relative = path.relative_to(src_dir).as_posix()
        if path.is_symlink():
            raise BundleError(f"{relative}: links are not allowed in a bundle")
        if path.is_dir():
            continue
        if not is_allowed(relative):
            raise BundleError(f"{relative}: not an allowed bundle file "
                              "(rules/*.rules, intel/ja4_watchlist.yaml, mappings/*.yaml)")
        files.append((relative, path.read_bytes()))
    if not files:
        raise BundleError(f"{src_dir}: no files to bundle")
    return files


def write_tar_gz(out_path: Path, members: list[tuple[str, bytes]]) -> None:
    """A .tar.gz with fixed times and owners, so the same input gives the same bytes."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as raw, \
            gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as packed, \
            tarfile.open(fileobj=packed, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for name, data in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))


# ---------- checking (on the user's machine, which has only the public key) ----------

def verify_bundle(path: Path, public_key_path: Path) -> dict:
    """Run every check without writing anything; return the verified manifest."""
    with tarfile.open(path, mode="r:gz") as tar:
        members = list_members(tar)
        manifest_bytes = read_member(tar, members, MANIFEST, MAX_MANIFEST_BYTES)
        signature = read_member(tar, members, SIGNATURE, SIGNATURE_BYTES)
        if not verify(manifest_bytes, signature, public_key_path):
            raise BundleError("bad signature: the manifest was changed, or this is the wrong key")
        manifest = parse_manifest(manifest_bytes)
        check_member_list(members, manifest)
        for entry in manifest["files"]:
            check_content(tar.extractfile(members[entry["path"]]), entry)
    return manifest


def list_members(tar: tarfile.TarFile) -> dict[str, tarfile.TarInfo]:
    """Name -> member. Reads only the headers, and stops early on an archive bomb."""
    members: dict[str, tarfile.TarInfo] = {}
    total = 0
    for member in tar:
        if member.name in members:
            raise BundleError(f"{member.name}: appears twice in the archive")
        if not member.isreg():
            raise BundleError(f"{member.name}: only regular files are allowed "
                              "(no folders, links or devices)")
        total += member.size
        if len(members) >= MAX_MEMBERS or total > MAX_TOTAL_BYTES:
            raise BundleError("archive too large")
        members[member.name] = member
    return members


def read_member(tar: tarfile.TarFile, members: dict, name: str, max_bytes: int) -> bytes:
    member = members.get(name)
    if member is None:
        raise BundleError(f"{name} is missing")
    if member.size > max_bytes:
        raise BundleError(f"{name} is too large")
    return tar.extractfile(member).read()  # into memory: nothing touches the disk


def parse_manifest(data: bytes) -> dict:
    try:
        manifest = json.loads(data)
        version, files = manifest["version"], manifest["files"]
        well_formed = all(isinstance(entry["path"], str) and isinstance(entry["size"], int)
                          and isinstance(entry["sha256"], str)
                          and SHA256_PATTERN.fullmatch(entry["sha256"]) for entry in files)
    except (ValueError, KeyError, TypeError) as err:
        raise BundleError(f"manifest.json is malformed: {err!r}") from None
    if not well_formed:
        raise BundleError("manifest.json: every file needs a path, a size and a sha256")
    check_version(version)
    paths = [entry["path"] for entry in files]
    if len(set(paths)) != len(paths):
        raise BundleError("manifest.json lists a file twice")
    return manifest


def check_member_list(members: dict[str, tarfile.TarInfo], manifest: dict) -> None:
    listed = {entry["path"] for entry in manifest["files"]}
    present = set(members) - {MANIFEST, SIGNATURE}
    for name in sorted(present | listed):
        if not is_allowed(name):
            raise BundleError(f"{name}: not an allowed bundle path")
    if present - listed:
        raise BundleError(f"files not in the manifest: {sorted(present - listed)}")
    if listed - present:
        raise BundleError(f"files missing from the archive: {sorted(listed - present)}")


def check_content(stream, entry: dict) -> None:
    """Size and SHA-256 of one file's content against its manifest entry."""
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1 << 20), b""):
        digest.update(block)
        size += len(block)
    if size != entry["size"] or digest.hexdigest() != entry["sha256"]:
        raise BundleError(f"{entry['path']}: content does not match the manifest")


def is_allowed(path: str) -> bool:
    return any(pattern.fullmatch(path) for pattern in ALLOWED_PATHS)


def check_version(version) -> None:
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise BundleError(f"version must look like 2027.03.01, got {version!r}")


def version_key(version: str) -> tuple[int, ...]:
    """'2027.03.01' -> (2027, 3, 1), so versions compare as numbers, not text."""
    return tuple(int(part) for part in version.split("."))


# ---------- installing ----------

def install_bundle(path: Path, public_key_path: Path, dest_dir: Path) -> dict:
    """Verify, then install as dest_dir/versions/<version> and point dest_dir/current at it.

    dest_dir/previous keeps the version before, for rollback(). Returns the manifest."""
    manifest = verify_bundle(path, public_key_path)
    dest_dir = Path(dest_dir)
    current = installed_version(dest_dir)
    if current is not None and version_key(manifest["version"]) <= version_key(current):
        raise BundleError(f"version {manifest['version']} is not newer than the installed "
                          f"{current}; use rollback to go back")
    versions = dest_dir / VERSIONS_DIR
    versions.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".incoming-", dir=versions))
    try:
        extract_checked(path, manifest, staging)
        target = versions / manifest["version"]
        if target.exists():  # left from before a rollback: replace it with the checked copy
            shutil.rmtree(target)
        os.replace(staging, target)  # one step: the folder appears complete or not at all
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    if current is not None:
        point_link(dest_dir / PREVIOUS, Path(VERSIONS_DIR) / current)
    point_link(dest_dir / CURRENT, Path(VERSIONS_DIR) / manifest["version"])
    remove_unused_versions(dest_dir)
    return manifest


def extract_checked(path: Path, manifest: dict, staging: Path) -> None:
    """Extract the listed files, then check their hashes again on disk: the bundle
    file could have been swapped between verify_bundle() and this read."""
    names = {entry["path"] for entry in manifest["files"]} | {MANIFEST}
    with tarfile.open(path, mode="r:gz") as tar:
        members = [member for member in tar.getmembers() if member.name in names]
        # "data" refuses absolute paths, "..", links and devices a second time.
        tar.extractall(staging, members=members, filter="data")
    for entry in manifest["files"]:
        with (staging / entry["path"]).open("rb") as f:
            check_content(f, entry)
    on_disk = parse_manifest((staging / MANIFEST).read_bytes())
    if on_disk != manifest:
        raise BundleError("manifest.json changed while installing")


def point_link(link: Path, target: Path) -> None:
    """Make link point at target (relative), replacing any old link in one step."""
    temporary = link.with_name(f".{link.name}.new")
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)  # atomic on POSIX: readers see the old or the new link


def installed_version(dest_dir: Path, link: str = CURRENT) -> str | None:
    path = Path(dest_dir) / link
    return os.readlink(path).rsplit("/", 1)[-1] if path.is_symlink() else None


def remove_unused_versions(dest_dir: Path) -> None:
    keep = {installed_version(dest_dir, CURRENT), installed_version(dest_dir, PREVIOUS)}
    for folder in (Path(dest_dir) / VERSIONS_DIR).iterdir():
        if folder.name not in keep and not folder.name.startswith(".incoming-"):
            shutil.rmtree(folder)


def rollback(dest_dir: Path) -> str:
    """Switch current and previous. Returns the version that is now current."""
    current = installed_version(dest_dir, CURRENT)
    previous = installed_version(dest_dir, PREVIOUS)
    if current is None or previous is None:
        raise BundleError("nothing to roll back to")
    point_link(Path(dest_dir) / CURRENT, Path(VERSIONS_DIR) / previous)
    point_link(Path(dest_dir) / PREVIOUS, Path(VERSIONS_DIR) / current)
    return previous


# ---------- command line ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m maxguard.intel.bundle",
                                     description="Build, check and install signed intel bundles.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="sign a folder into a bundle")
    build.add_argument("src_dir", type=Path)
    build.add_argument("out", type=Path)
    build.add_argument("private_key", type=Path)
    build.add_argument("--version", required=True)
    check = commands.add_parser("verify", help="check a bundle without installing it")
    check.add_argument("bundle", type=Path)
    check.add_argument("public_key", type=Path)
    install = commands.add_parser("install", help="check and install a bundle")
    install.add_argument("bundle", type=Path)
    install.add_argument("public_key", type=Path)
    install.add_argument("dest_dir", type=Path)
    back = commands.add_parser("rollback", help="go back to the previous version")
    back.add_argument("dest_dir", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            manifest = build_bundle(args.src_dir, args.out, args.private_key, version=args.version)
            print(f"built {args.out}: version {manifest['version']}, "
                  f"{len(manifest['files'])} files")
        elif args.command == "verify":
            manifest = verify_bundle(args.bundle, args.public_key)
            print(f"ok: version {manifest['version']}, {len(manifest['files'])} files")
        elif args.command == "install":
            manifest = install_bundle(args.bundle, args.public_key, args.dest_dir)
            print(f"installed version {manifest['version']}")
        else:
            print(f"current version is now {rollback(args.dest_dir)}")
    except (BundleError, tarfile.TarError, OSError) as err:
        print(f"refused: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
