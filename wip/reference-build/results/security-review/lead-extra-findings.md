# Extra AHM-04 findings from the lead's own checks (October 27, 2026)

## L1. Row 1: no limit on the number of files in an archive (Partial)

- Where: `maxguard/adapters/zeeklogs.py` `_check_size()` / `_extract()` (FIO-01 guide, Fiona).
- What: the 4 GiB check sums member sizes only. An archive of many empty files passes it.
- How checked (alpha build `stages/AHM-04`, Python 3.11.15): a `.tar.gz` with 200,000 empty
  members is 0.9 MB; `_extract()` unpacked all 200,000 files in 32.3 s. Scaled, 10 million
  members is about 47 MB compressed, far under the 1,024 MB upload limit
  (`DEFAULT_MAX_UPLOAD_MB = 1024` in `maxguard/api/app.py`), and would create 10 million files:
  inode exhaustion on a small disk (Raspberry Pi SD card) and a long CPU stall.
  The same holds for zip (`z.infolist()` is not counted).
- Source: Python's tarfile documentation, "Hints for further verification": even with
  `filter='data'`, tarfile "is not suited for extracting untrusted files without prior
  inspection"; the filters "do not prevent denial-of-service attacks"; limit "the number of
  extracted files, total size of extracted data, filename length (including symlink length),
  and size of individual files"; "Disallow symbolic links if you do not need the
  functionality." (CPython 3.11 `Doc/library/tarfile.rst`.)
- Fix (FIO-01 guide; ask before changing, it changes test counts in later guides):
  `MAX_MEMBERS = 10_000` (a week of hourly logs is about 3,400 files) checked with the size
  before extracting, for zip and tar; refuse symlinks and hard links in log archives
  (Zeek logs never need them); refuse names longer than 255 characters.

## L2. Row 1 wording: the `data` filter does not refuse absolute paths or all links

- Source code `/usr/lib/python3.11/tarfile.py` `_get_filtered_attrs()` and the CPython docs:
  leading `/` is stripped (the file lands inside the destination); `..` that leaves the
  destination raises `OutsideDestinationError`; links to an absolute path or outside the
  destination raise `AbsoluteLinkError` / `LinkOutsideDestinationError`; links inside the
  destination are allowed; device files and pipes raise `SpecialFileError`.
- Wrong today: `docs/ARCHITECTURE.md` section 14 row 1 ("refuses absolute paths, `..`, links,
  and device files") and the comment in `zeeklogs.py` (`"data" blocks links, devices, "..",
  absolute`).
- Fix: correct ARCHITECTURE.md in the AHM-04 pull request; correct the comment in the FIO-01
  guide together with L1.

## L3. Hostile timestamps break pages and exports (Fail, fixed in the dashboard)

- How checked: a Zeek log record with `ts = 1e12` (year 33658) uploaded as a zip
  (`agentwork/dash-review/scripts/far_future_upload.py`, original AHM-03 build):
  upload 200, then `GET /` 500 and `GET /alerts/<id>` 500
  (`ValueError: year 33658 is out of range` in `web/routes.py` `utc_time`).
- Fixed in Ahmad's AHM-02/AHM-03 code (`utc_time()` never raises; tested).
- Still open elsewhere, same call with no range check (checked on the alpha build):
  `maxguard/report.py:109` `iso_utc()` makes `to_csv()` raise `ValueError: year 33658 is out
  of range` (AMO-03; `to_json()` and `to_html()` work), and `maxguard/storage/events.py:41`
  `hour_key()` makes `EventStore.write()` raise for an event with `ts = 1e12` (JAI-06), so an
  upload whose `conn.log` holds such a record fails at the storage step.
- Root fix (JAI-03, Jaiden; contract-adjacent, needs his review): the normalizer refuses or
  quarantines records whose `ts` is not finite or outside a sane range.
