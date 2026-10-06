"""Amory's tasks: mapping files and their checks, report export, chain of custody."""

from plan_helpers import checklist, pr_step, start_step

TASKS = [
    {
        "id": "AMO-01", "owner": "amory", "milestone": "W1",
        "title": "NIST SP 800-53 mapping file and the mapping checks",
        "labels": ["area:mapping", "critical-path"],
        "depends": ["JAI-02", "FIO-02", "JAK-03"],
        "goal": (
            "Add the compliance mapping files (Contract 2): NIST SP 800-53 Rev. 5 (Release 5.2.0) "
            "with a verified row for every rule, the field guide `mappings/schema.md`, the PCI "
            "DSS, CISA CPG and CJIS files with their headers but no rows yet, and the tests that "
            "enforce CLAUDE.md rule 8 on every file."
        ),
        "prereq": "JAI-02 (the loader) is merged, and FIO-02 and JAK-03 (all 13 rule IDs exist).",
        "steps": [
            start_step("amory/nist-mapping"),
            "Create the field guide `mappings/schema.md` and read it first:\n\n@@FILE mappings/schema.md@@",
            "Create `mappings/nist_800_53_r5.yaml`:\n\n@@FILE mappings/nist_800_53_r5.yaml@@\n\n"
            "Every `control_id` and `title` was read from NIST's machine-readable copy of the "
            "catalog (OSCAL, version 5.2.0); `verified` says which entry. Open two rows yourself in "
            "that file (the link is in the header) and confirm them before you commit.",
            "Create the three framework files whose rows you will fill later (AMO-02 and AMO-04). "
            "`mappings/pci_dss_4_0_1.yaml`:\n\n@@FILE mappings/pci_dss_4_0_1.yaml@@\n\n"
            "`mappings/cisa_cpg_2_0.yaml`:\n\n@@FILE mappings/cisa_cpg_2_0.yaml@@\n\n"
            "`mappings/cjis_6_1.yaml`:\n\n@@FILE mappings/cjis_6_1.yaml@@",
            "Create the tests `tests/unit/test_mappings.py`:\n\n@@FILE tests/unit/test_mappings.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Count the NIST rows per rule:\n\n@@RUN try@@",
            pr_step("feat: NIST SP 800-53 mapping file and mapping checks (AMO-01)", "ahmadalkhoudeir"),
        ],
        "files": ["mappings/schema.md", "mappings/nist_800_53_r5.yaml", "mappings/pci_dss_4_0_1.yaml",
                  "mappings/cisa_cpg_2_0.yaml", "mappings/cjis_6_1.yaml", "tests/unit/test_mappings.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_mappings.py -q"},
            {"id": "try", "show": (
                "python -c \"import yaml; f = yaml.safe_load(open('mappings/nist_800_53_r5.yaml')); "
                "print(f['version']); [print(rule, [r['control_id'] for r in rows]) "
                "for rule, rows in sorted(f['mappings'].items())]\"")},
        ],
        "test": "`pytest` passes, and every one of the 13 rules has at least one NIST control.",
        "why": (
            "A compliance report is only useful if an auditor can look up every control it names. "
            "That is why each row records where it was checked, why the version string must match "
            "`docs/PROJECT_DECISIONS.md` exactly, and why three files ship empty instead of with "
            "guessed IDs: a wrong control ID is worse than a missing one, because people trust it. "
            "The tests make those rules impossible to forget."
        ),
        "checklist": checklist(extra=["You opened at least two NIST rows in the OSCAL catalog yourself",
                                      "Ahmad reviewed the rows (compliance accuracy)"]),
    },
    {
        "id": "AMO-02", "owner": "amory", "milestone": "W3",
        "title": "PCI DSS v4.0.1 rows, checked in the official document",
        "labels": ["area:mapping"], "status": "process",
        "depends": ["AMO-01"],
        "goal": (
            "Fill `mappings/pci_dss_4_0_1.yaml` with requirement numbers you read in the official "
            "PCI DSS v4.0.1 document, starting with `cleartext.telnet` (the demo finding), so the "
            "Week 4 report shows PCI DSS controls."
        ),
        "prereq": "AMO-01 is merged.",
        "steps": [
            start_step("amory/pci-rows"),
            "Download **PCI DSS v4.0.1** from the PCI Security Standards Council document library "
            "(the `source` link in the file; you accept their license agreement to download it). "
            "Do not commit the PDF: its license does not allow redistribution.",
            "For each rule, find the requirements it shows a failure of. Start with Requirement 4 "
            "(protect cardholder data with strong cryptography during transmission over open, "
            "public networks) and Requirement 2 and 8 for insecure services and passwords, but "
            "only write a row when the requirement's own text fits the finding.",
            "Write each row in the Contract 2 format (`mappings/schema.md`): the exact "
            "requirement number and title as the PDF prints them, a one-sentence rationale in "
            "plain words, and `verified: \"PCI DSS v4.0.1 PDF, p. <page>\"`.",
            "Run `pytest tests/unit/test_mappings.py -q`, then "
            "`maxguard analyze tests/fixtures/zeek/telnet --no-ai --frameworks \"PCI DSS\"` and "
            "check the Telnet finding lists your rows.",
            pr_step("feat: PCI DSS v4.0.1 mapping rows (AMO-02)", "ahmadalkhoudeir"),
        ],
        "files": [], "commands": [],
        "test": "The mapping tests pass, and Ahmad can open the PDF at every page you cite and "
                "find the requirement.",
        "why": (
            "PCI DSS is the framework the original MaxGuard was built for, and small retailers "
            "are a target audience. The requirement numbers changed between versions, so only "
            "the v4.0.1 document itself is a valid source (CLAUDE.md rule 8)."
        ),
        "checklist": checklist(extra=["Every row has a page number in `verified`",
                                      "The PDF itself is not committed",
                                      "Ahmad checked the rows against the PDF"]),
    },
    {
        "id": "AMO-03", "owner": "amory", "milestone": "W4",
        "title": "Report export: JSON, CSV, and HTML",
        "labels": ["area:mapping", "critical-path"],
        "depends": ["JAI-05"],
        "goal": (
            "Write `maxguard/report.py`, which turns the report into three formats: JSON (all of "
            "it), CSV (one row per finding and control, for spreadsheets and auditors), and one "
            "self-contained HTML page that opens offline. All three escape text that came from "
            "network traffic."
        ),
        "prereq": "JAI-05 (the pipeline) is merged.",
        "steps": [
            start_step("amory/report-export"),
            "Create `maxguard/report.py`:\n\n@@FILE maxguard/report.py@@\n\n"
            "Two security details: `safe_cell()` puts a `'` in front of any CSV cell that a "
            "spreadsheet would run as a formula (an attacker can put `=HYPERLINK(...)` into a host "
            "name), and every HTML value goes through `esc()`.",
            "Create the tests `tests/unit/test_report.py`:\n\n@@FILE tests/unit/test_report.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Make the three files for the Telnet fixture and look at the CSV:\n\n@@RUN try@@",
            pr_step("feat: JSON, CSV and HTML report export (AMO-03)", "ahmadalkhoudeir"),
        ],
        "files": ["maxguard/report.py", "tests/unit/test_report.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_report.py -q"},
            {"id": "try", "show": (
                "python -c \"import tempfile; from maxguard.pipeline import analyze; "
                "from maxguard import report; r = analyze('tests/fixtures/zeek/telnet', tempfile.mkdtemp(), explain=False); "
                "open('telnet.csv', 'w').write(report.to_csv(r)); open('telnet.html', 'w').write(report.to_html(r))\" "
                "&& head -n 3 telnet.csv | cut -c1-120 && grep -c '<tr>' telnet.html")},
        ],
        "test": "`pytest` passes; open `telnet.html` in a browser with Wi-Fi off and check that it "
                "looks complete (no missing styles or images).",
        "why": (
            "Different people need different formats: an analyst wants JSON, an auditor a "
            "spreadsheet, a small-business owner a page they can read and email. The HTML page "
            "has no external files, scripts, or fonts, so it works offline and is safe to open, "
            "and every export is deterministic, so two exports of the same report can be compared."
        ),
        "checklist": checklist(extra=["You opened the HTML file with the network off"]),
    },
    {
        "id": "AMO-04", "owner": "amory", "milestone": "W5",
        "title": "CISA CPG 2.0 and CJIS v6.1 rows",
        "labels": ["area:mapping"], "status": "process",
        "depends": ["AMO-02"],
        "goal": (
            "Fill `mappings/cisa_cpg_2_0.yaml` and `mappings/cjis_6_1.yaml` with goal and control "
            "IDs read in the official documents, so all four frameworks appear in the alpha's "
            "reports (the Week 5 milestone)."
        ),
        "prereq": "AMO-02 is merged (same method, so its review comments help here).",
        "steps": [
            start_step("amory/cpg-cjis-rows"),
            "CPG 2.0: open the CPG 2.0 report from the `source` page (the direct PDF link is in the "
            "file's header). CPG 2.0 regrouped the goals, so never copy an ID from an older CPG "
            "version. Write rows with `verified: \"CPG 2.0 report, p. <page>\"`.",
            "CJIS: download CJIS Security Policy v6.1 from the FBI's resource center (the `source` "
            "link). Copy control IDs and titles exactly as v6.1 prints them, with "
            "`verified: \"CJIS SP v6.1, section <x>, p. <page>\"`.",
            "Run `pytest tests/unit/test_mappings.py -q` and check the Telnet finding in "
            "`maxguard analyze tests/fixtures/zeek/telnet --no-ai` lists controls from all four "
            "frameworks.",
            pr_step("feat: CISA CPG 2.0 and CJIS v6.1 mapping rows (AMO-04)", "ahmadalkhoudeir"),
        ],
        "files": [], "commands": [],
        "test": "The mapping tests pass and the Telnet finding has controls in all four frameworks.",
        "why": (
            "CPG gives small organizations a short, practical list, and CJIS matters to anyone who "
            "touches criminal-justice data (local police and the companies that serve them). Both "
            "are locked to exact versions in `docs/PROJECT_DECISIONS.md`, and before each release "
            "someone must check they are still the current versions (CLAUDE.md rule 8)."
        ),
        "checklist": checklist(extra=["Every row has a page or section in `verified`",
                                      "Ahmad checked the rows"]),
    },
    {
        "id": "AMO-05", "owner": "amory", "milestone": "S4",
        "title": "Chain-of-custody log",
        "labels": ["area:mapping", "area:release"],
        "depends": ["JAI-08"],
        "goal": (
            "Write `maxguard/custody/log.py`: an append-only, tamper-evident log of what happened "
            "to evidence (capture received, report generated, report exported). Each entry holds "
            "the previous entry's hash and an Ed25519 signature, so editing, deleting, or "
            "reordering any line is detected."
        ),
        "prereq": "JAI-08 (signing) is merged.",
        "steps": [
            start_step("amory/custody-log"),
            "Create `maxguard/custody/log.py`:\n\n@@FILE maxguard/custody/log.py@@\n\n"
            "Three details: `at` comes from the caller, never from the clock (the same rule as "
            "the stores), so the same inputs give a byte-identical log, because Ed25519 "
            "signatures are deterministic; `os.fsync` puts each entry on the disk before "
            "`append()` returns; and a hash chain cannot show that entries were cut off at the "
            "end, so `verify` prints the last entry's hash (the head) for you to record "
            "somewhere else, such as the case notes or the exported report.",
            "Create the tests `tests/unit/test_custody.py`:\n\n@@FILE tests/unit/test_custody.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Try the command line: make a key pair, log one capture, verify the log, change one "
            "word in it, and verify again:\n\n@@RUN demo@@",
            pr_step("feat: tamper-evident chain-of-custody log (AMO-05)", "ahmadalkhoudeir"),
        ],
        "files": ["maxguard/custody/log.py", "tests/unit/test_custody.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_custody.py -q"},
            {"id": "demo", "expect_code": 1, "show": (
                "python -c \"from pathlib import Path; "
                "from maxguard.custody.signing import generate_keypair; "
                "from maxguard.custody.log import append; "
                "private, public = generate_keypair(Path('data/keys')); "
                "append(Path('data/custody.jsonl'), action='capture_received', "
                "artifact_path=Path('tests/pcaps/telnet.pcap'), actor='amory', "
                "at=1791250000.0, private_key_path=private)\"\n"
                "python -m maxguard.custody.log verify data/custody.jsonl "
                "data/keys/custody_ed25519_public.pem\n"
                "sed -i.bak 's/\"actor\": \"amory\"/\"actor\": \"mallory\"/' data/custody.jsonl\n"
                "python -m maxguard.custody.log verify data/custody.jsonl "
                "data/keys/custody_ed25519_public.pem"),
             "note": ("Your head hash is the same as this one: it covers the entry (file hash, "
                      "time, actor), not the signature, and the inputs here are fixed. The last "
                      "command exits with 1.")},
        ],
        "test": "All tamper cases fail verification at the right line, and a clean log verifies.",
        "why": (
            "If MaxGuard's findings are ever used in an incident report, someone will ask how you "
            "know the capture and report were not changed afterwards. A hash chain shows that no "
            "line was edited or removed, and the signature shows that the log was written by this "
            "MaxGuard installation and not rebuilt by someone else."
        ),
        "checklist": checklist(extra=["No key file is committed"]),
    },
]
