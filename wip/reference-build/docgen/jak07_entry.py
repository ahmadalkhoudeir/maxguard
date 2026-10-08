    {
        "id": "JAK-07", "owner": "jakub", "milestone": "S4",
        "title": "Live sensor: capture, rotation, and shipping to the console",
        "labels": ["area:sensor", "critical-path"], "hardware": True,
        "depends": ["JAK-06", "JAI-07", "JAK-08"],
        "goal": (
            "Turn the lab into MaxGuard's live sensor (`docs/ARCHITECTURE.md` section 4): Zeek and "
            "Suricata run all the time on the capture port and write their logs into one folder "
            "per 15-minute interval on the SSD, and a small shipper sends each completed folder "
            "to the console's `POST /api/ingest`. The console analyzes it like an upload, with "
            "`sensor_id` set to the sensor's name."
        ),
        "prereq": ("JAK-06 (the lab works), JAI-07 (the API with `/api/ingest`) and JAK-08 "
                   "(which creates `maxguard/sensor/`) are merged."),
        "steps": [
            start_step("jakub/live-sensor"),
            "**Zeek rotation.** Zeek 9 rotates its own logs, without `zeekctl`, when "
            "`Log::default_rotation_interval` is set. `Log::rotation_format_func` decides where "
            "each closed file goes. Create `maxguard/zeek/scripts/live/rotate.zeek`:\n\n"
            "@@FILE maxguard/zeek/scripts/live/rotate.zeek@@\n\n"
            "The folder is named after the interval's **start** in UTC, and the files keep their "
            "plain names, so a finished folder is an ordinary Zeek log folder. The script sits in "
            "`scripts/live/` on purpose: `maxguard/zeek/runner.py` loads only `scripts/*.zeek`, so "
            "analyzing a capture file never rotates anything.",
            "**Suricata live settings.** Create `maxguard/suricata/maxguard-suricata-live.yaml`, "
            "a copy of `maxguard-suricata.yaml` with three changes (Community ID and JA4 are "
            "unchanged):\n\n@@FILE maxguard/suricata/maxguard-suricata-live.yaml@@\n\n"
            "Why a file per **minute** and not per 15 minutes: Suricata 8.0's `rotate-interval` "
            "accepts `minute`, `hour` and `day`, which start at the next whole minute, hour or "
            "day, or a relative value such as `15m`, which counts from the moment Suricata "
            "started (user guide, \"Rotate log file\"; source: `src/util-logopenfile.c`). A "
            "relative 15 minutes would not line up with Zeek's folders, so Suricata writes "
            "minute files and the adapter merges each interval's minutes into that interval's "
            "folder. Never add `copy-mode` to the `af-packet` section: it turns Suricata into an "
            "inline device that sends packets (CLAUDE.md rule 5).",
            "**Compose file.** Create `docker/sensor-compose.yaml`:\n\n"
            "@@FILE docker/sensor-compose.yaml@@\n\n"
            "Zeek runs **without `-D`**: random seeds protect a live sensor's tables against "
            "deliberate slow-down attacks. Every service drops all capabilities and adds back "
            "only what it needs. Suricata needs five more than `NET_ADMIN`, `NET_RAW` and "
            "`SYS_NICE` only while it starts: the image's start script hands its folders (such as `/var/log/suricata`) "
            "to the `suricata` user, and Suricata then switches to that user. The shipper uses "
            "the `zeek/zeek` image only for its Python 3: it needs nothing outside the standard "
            "library. Check the file:\n\n@@RUN compose@@",
            "**Adapter.** Create `maxguard/adapters/live.py` with `LiveSensorAdapter` "
            "(Contract 3, unchanged):\n\n@@FILE maxguard/adapters/live.py@@\n\n"
            "A folder is *complete* two minutes after its interval ends: by then Zeek has moved "
            "every log into it and Suricata has closed the last minute file that belongs to it. "
            "`merge_eve()` writes `eve.json` under a hidden name first and renames it, so a crash "
            "halfway never leaves a half-merged file. The adapter reads "
            "`MAXGUARD_INTERVAL_MINUTES` only when it analyzes a folder, because "
            "`pipeline.py` creates it when it is imported, and a wrong setting must not stop "
            "MaxGuard from analyzing uploads.",
            "Add it to `ADAPTERS` in `maxguard/pipeline.py` (two lines change):\n\n"
            "@@FILE maxguard/pipeline.py@@",
            "Add one line to the docstring of `maxguard/sensor/__init__.py`:\n\n"
            "@@FILE maxguard/sensor/__init__.py@@",
            "**Shipper.** Create `maxguard/sensor/shipper.py`:\n\n"
            "@@FILE maxguard/sensor/shipper.py@@\n\n"
            "Three choices to notice. It marks a folder shipped only after a `2xx` answer and "
            "stops at the first failure, so a console that is down only delays folders. It packs "
            "the same folder into the same bytes every time, so if the sensor crashes between "
            "sending and marking, the console sees the same SHA-256 and does not count the "
            "alerts twice. And it never uses a proxy: the token and the logs go straight to the "
            "console the user configured.",
            "**Tests.** Create `tests/unit/test_live_adapter.py`:\n\n"
            "@@FILE tests/unit/test_live_adapter.py@@\n\n"
            "and `tests/unit/test_shipper.py` (a fake console: `http.server` in a thread on "
            "`127.0.0.1`):\n\n@@FILE tests/unit/test_shipper.py@@\n\nRun them:\n\n@@RUN tests@@",
            "Before the sensor ships anything, put the console's address and token in "
            "`/data/shipper.toml` on the sensor (never in the repository) and make it readable "
            "only by root:\n\n"
            "```toml\n"
            "console_url = \"http://192.168.50.20:8000\"   # the console's LAN address\n"
            "token = \"<the console's MAXGUARD_INGEST_TOKEN>\"\n"
            "sensor_id = \"sensor-01\"\n"
            "```\n\n"
            "```bash\nsudo chmod 600 /data/shipper.toml\n```\n\n"
            "On the console, ingest stays off until `MAXGUARD_INGEST_TOKEN` is set "
            "(`docs/ARCHITECTURE.md` section 10).",
            "Try the whole path on the Pi with 1-minute folders first:\n\n@@RUN lab@@",
            "Then start it for real (15-minute folders), run the sensor on the lab for one day, "
            "and check that alerts appear on the console within about 20 minutes of the "
            "traffic: `docker compose -f docker/sensor-compose.yaml up -d`.",
            pr_step("feat: live sensor with rotation and shipping (JAK-07)", "flau0306"),
        ],
        "files": ["maxguard/zeek/scripts/live/rotate.zeek",
                  "maxguard/suricata/maxguard-suricata-live.yaml", "docker/sensor-compose.yaml",
                  "maxguard/adapters/live.py", ("maxguard/pipeline.py", "snip:pipeline_v3.py"),
                  "maxguard/sensor/__init__.py", "maxguard/sensor/shipper.py",
                  "tests/unit/test_live_adapter.py", "tests/unit/test_shipper.py"],
        "commands": [
            {"id": "compose", "show": ("docker compose -f docker/sensor-compose.yaml config --quiet "
                                       "&& echo \"compose file OK\"")},
            {"id": "tests",
             "show": "pytest tests/unit/test_live_adapter.py tests/unit/test_shipper.py -q"},
            {"id": "lab", "env": "none", "show": '# On the sensor: 1-minute folders for this test only\nexport MAXGUARD_INTERVAL_MINUTES=1\ndocker compose -f docker/sensor-compose.yaml up -d\n# use the lab service\'s HTTP (port 8080) and Telnet from a lab machine, wait 4 minutes\nls /data/zeek\nls -A /data/zeek/2026-10-06-2103\ndocker compose -f docker/sensor-compose.yaml ps --format \'{{.Service}} {{.State}}\'\ndocker compose -f docker/sensor-compose.yaml logs --no-log-prefix shipper\n# On the console:\ncurl -s http://127.0.0.1:8000/api/alerts | python3 -c "import json, sys; [print(a[\'rule_id\'], a[\'severity\'], a[\'count\']) for a in json.load(sys.stdin)]"\ncurl -s \'http://127.0.0.1:8000/api/events?limit=1\' | python3 -c "import json, sys; e = json.load(sys.stdin)[0]; print(e[\'sensor_id\'], e[\'source\'], e[\'log\'])"\n# Back on the sensor: stop the test\ndocker compose -f docker/sensor-compose.yaml down && unset MAXGUARD_INTERVAL_MINUTES', "output": '2026-10-06-2102\n2026-10-06-2103\n2026-10-06-2104\n2026-10-06-2105\n.shipped\ncapture_loss.log\nconn.log\neve.json\nfiles.log\nhttp.log\nknown_hosts.log\nknown_services.log\nmaxguard_cleartext.log\nsoftware.log\nshipper running\nsuricata running\nzeek running\n2026-10-06 21:02:35,859 INFO shipping complete 1-minute folders from /data/zeek\n2026-10-06 21:05:36,159 INFO 2026-10-06-2102: shipped (5066 bytes, HTTP 200)\n2026-10-06 21:06:36,274 INFO 2026-10-06-2103: shipped (2612 bytes, HTTP 200)\n2026-10-06 21:07:36,351 INFO 2026-10-06-2104: shipped (2218 bytes, HTTP 200)\ncleartext.telnet high 5\ncleartext.http_alt medium 6\nlab-sensor-01 zeek conn.log',
             "note": 'Not run on a Raspberry Pi: verify on hardware. This output is from planning, where Zeek and Suricata listened inside a lab-server container\'s network namespace instead of on `eth0` (a two-line Compose override), the console ran on the same machine, and `shipper.toml` named `sensor_id = "lab-sensor-01"`. The first Telnet session was at 21:03:09 and its alert reached the console at 21:06:36: the 21:03 folder is complete at 21:06:00 (end of the interval plus two minutes), and the shipper checks once a minute. With 15-minute folders, expect up to about 18 minutes plus the analysis time. Your folder names are your own times.'},
        ],
        "test": (
            "Both test files pass on your laptop. On the lab, `ls /data/zeek` shows a new folder "
            "every 15 minutes, `docker compose -f docker/sensor-compose.yaml ps` shows all three "
            "containers running after a reboot, and the console's alert queue shows the lab "
            "phone's traffic with the sensor's `sensor_id`. The capture port still has no IP "
            "address (`ip -br addr show eth0`)."
        ),
        "why": (
            "Shipping completed folders instead of streaming keeps the design simple: the console "
            "already knows how to analyze a folder of logs, and a network hiccup only delays a "
            "folder instead of losing events. A 15-minute interval is the trade-off between how "
            "quickly an alert appears and how many small Parquet files the console has to manage "
            "(each one costs about 3 KB). The sensor never transmits on the capture port; the "
            "shipper uses only the management port (CLAUDE.md rule 5)."
        ),
        "checklist": checklist(extra=[
            "Zeek runs without `-D`",
            "The token and console address are read from `/data`, not from the repository",
            "One full day of live data reached the console",
        ]),
    },
