"""ZeekLogAdapter: a folder, .zip, or .tar.gz of existing Zeek logs (JSON or TSV).

Fall 2026 roadmap adapter with v2.0 fixes found while testing with Zeek 9.0.0:
- TSV values are converted with the log's own `#types` header, so numbers become
  numbers and sets/vectors become lists. Before, a set like cert_chain_fps stayed
  one comma-separated string and every certificate rule silently found nothing.
- Suricata's eve.json is kept (it used to be dropped, so JA4 and Suricata
  events were lost for imported folders).
- Zeek's rotated, gzipped archives (conn.00:00:00-01:00:00.log.gz) are read, and
  logs of the same type are appended in sorted order instead of overwriting each
  other, so the result does not depend on folder order.
- Archives are checked before extracting, so a tiny "zip bomb" cannot fill the disk.
"""

from __future__ import annotations

import gzip
import json
import shutil
import tarfile
import zipfile
from pathlib import Path

MAX_EXTRACTED_BYTES = 4 * 1024**3  # 4 GiB: refuse archives that unpack to more


class ArchiveTooLarge(ValueError):
    pass


def _convert(value: str, zeek_type: str, set_sep: str, empty: str, unset: str):
    """Turn one TSV text value into the same JSON value Zeek would have written."""
    if value == unset:
        return None
    if zeek_type.startswith(("set[", "vector[")):
        if value == empty:
            return []
        inner = zeek_type[zeek_type.index("[") + 1 : -1]
        return [_convert(v, inner, set_sep, empty, unset) for v in value.split(set_sep)]
    if value == empty:
        return ""
    if zeek_type in ("count", "int", "port"):
        return int(value)
    if zeek_type in ("double", "time", "interval"):
        return float(value)
    if zeek_type == "bool":
        return value == "T"
    return value


def _tsv_to_json(fin, fout) -> None:
    """Convert one TSV log (an open text file) to JSON lines written to fout."""
    sep, set_sep, empty, unset = "\t", ",", "(empty)", "-"
    fields: list[str] = []
    types: list[str] = []
    for line in fin:
        line = line.rstrip("\n")
        if line.startswith("#set_separator"):
            set_sep = line.split(sep, 1)[1]
        elif line.startswith("#empty_field"):
            empty = line.split(sep, 1)[1]
        elif line.startswith("#unset_field"):
            unset = line.split(sep, 1)[1]
        elif line.startswith("#fields"):
            fields = line.split(sep)[1:]
        elif line.startswith("#types"):
            types = line.split(sep)[1:]
        elif line.startswith("#") or not line:
            continue
        elif fields:
            values = line.split(sep)
            kinds = types or ["string"] * len(fields)
            rec = {f: _convert(v, t, set_sep, empty, unset)
                   # strict=False: a line cut short (e.g. by a crash) keeps the fields it has
                   for f, v, t in zip(fields, values, kinds, strict=False)}
            fout.write(json.dumps(rec) + "\n")


def _open_text(path: Path):
    if path.name.endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open()


def _log_name(path: Path) -> str:
    """'conn.00:00:00-01:00:00.log.gz' -> 'conn.log'; 'eve.json' stays 'eve.json'."""
    base = path.name.split(".")[0]
    return "eve.json" if base == "eve" else f"{base}.log"


def _check_size(sizes: list[int]) -> None:
    if sum(sizes) > MAX_EXTRACTED_BYTES:
        raise ArchiveTooLarge("archive unpacks to more than 4 GiB; split it into smaller parts")


def _extract(path: Path, dest: Path) -> None:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            _check_size([i.file_size for i in z.infolist()])
            z.extractall(dest)  # zipfile drops absolute paths and ".." parts
    else:
        with tarfile.open(path) as t:
            _check_size([m.size for m in t.getmembers()])
            t.extractall(dest, filter="data")  # "data" blocks links, devices, "..", absolute


class ZeekLogAdapter:
    name = "zeek-logs"

    def accepts(self, path: Path) -> bool:
        return (path.is_dir() and (path / "conn.log").exists()) or \
               path.suffix == ".zip" or path.name.endswith(".tar.gz")

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        src = workdir / "imported"
        if path.is_dir():
            shutil.copytree(path, src, dirs_exist_ok=True)
        else:
            _extract(path, src)
        out = workdir / "zeek_logs"
        out.mkdir(parents=True, exist_ok=True)
        found = [p for p in src.rglob("*") if p.is_file() and (
            p.name.endswith((".log", ".log.gz")) or p.name.startswith("eve.json"))]
        for log in sorted(found):  # sorted: same result whatever order the disk lists files
            with _open_text(log) as fin, (out / _log_name(log)).open("a") as fout:
                first = fin.readline()
                if first.startswith("{"):  # JSON lines (Zeek JSON or Suricata eve.json)
                    fout.write(first if first.endswith("\n") else first + "\n")
                    shutil.copyfileobj(fin, fout)
                else:  # Zeek's default tab-separated format
                    _tsv_to_json([first, *fin], fout)
        return out
