"""timeline_end, utc_time and text_field on odd inputs. Run: python s9_types.py <build>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from maxguard.web.routes import LAST_TIME, text_field, timeline_end, utc_time

cases = [1791300000.7, 0, -0.5, -5, 1e12, float("inf"), float("-inf"), float("nan"), 1e308,
         "1791300000", "abc", None, True, LAST_TIME, LAST_TIME - 1, LAST_TIME + 1, 2**70, b"12"]
for ts in cases:
    try:
        te = timeline_end(ts)
    except Exception as err:  # noqa: BLE001
        te = f"RAISED {type(err).__name__}: {err}"
    try:
        ut = utc_time(ts)
    except Exception as err:  # noqa: BLE001
        ut = f"RAISED {type(err).__name__}: {err}"
    print(f"{ts!r:>22}: timeline_end={te!r:<40} utc_time={ut!r}")
print()
for v in ["Ali\r\nB", " Ali ", "Ali B", "Ali\x0bB", 12, None, ["a", "b"], b"bytes"]:
    print(f"text_field({v!r}) = {text_field(v)!r}")
