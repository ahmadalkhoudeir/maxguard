"""Milestones, people, and labels shared by every part of the task plan."""

MILESTONES = {
    # key: (GitHub milestone title, due date, short description)
    "W0": ("W0 Onboarding and contracts", "2026-10-09",
           "Everyone has a merged pull request; repo restructured; CI runs; contracts merged."),
    "W1": ("W1 Building blocks", "2026-10-16",
           "Adapters, rules, lab captures and fixtures, normalizer, inventory, citation check."),
    "W2": ("W2 First end-to-end demo", "2026-10-23",
           "maxguard analyze turns telnet.pcap into a mapped, explained finding."),
    "W3": ("W3 API and alert queue", "2026-10-30",
           "Upload in the browser; alerts stored and listed; CI runs integration tests."),
    "W4": ("W4 Full offline report", "2026-11-06",
           "Alert detail with Analyst and Home modes; Suricata in the pipeline; works unplugged."),
    "W5": ("W5 Alpha feature freeze", "2026-11-13",
           "All alpha features merged; CPG 2.0 and CJIS v6.1 mappings; bug fixes only after this."),
    "W6": ("W6 Release candidate", "2026-11-20",
           "v2.0-alpha-rc1 tagged and handed to an outside tester."),
    "W8": ("W8 v2.0-alpha", "2026-12-04",
           "v2.0-alpha released; acceptance test passes; presentation delivered."),
    "S4": ("S1-S4 Live sensor", "2027-02-12",
           "Pi sensor on the mirror port; logs reach the console every 15 minutes; timeline and device pages."),
    "S8": ("S5-S8 Respond", "2027-03-12",
           "Generated rules, preview before you block, approvals, OPNsense; signed intel bundles; JA4."),
    "S11": ("S9-S11 Detect more", "2027-04-16",
            "Decoys, per-device baselines, NetFlow/IPFIX input."),
    "S12": ("S12 v2.0 feature freeze", "2027-04-23", "Host agent; all v2.0 features merged."),
    "S13": ("S13 v2.0 release candidate", "2027-04-30", "v2.0-rc1 tagged; outside tester."),
    "S14": ("S14 v2.0", "2027-05-07", "v2.0 released; acceptance test passes."),
}

WEEK_TEXT = {
    "W0": "Week 0 (due Fri Oct 9, 2026)", "W1": "Week 1 (due Fri Oct 16)",
    "W2": "Week 2 (due Fri Oct 23)", "W3": "Week 3 (due Fri Oct 30)",
    "W4": "Week 4 (due Fri Nov 6)", "W5": "Week 5 (due Fri Nov 13)",
    "W6": "Week 6 (due Fri Nov 20)", "W8": "Week 8 (due Fri Dec 4)",
    "S4": "Spring S1-S4 (due Fri Feb 12, 2027)", "S8": "Spring S5-S8 (due Fri Mar 12, 2027)",
    "S11": "Spring S9-S11 (due Fri Apr 16, 2027)", "S12": "Spring S12 (due Fri Apr 23, 2027)",
    "S13": "Spring S13 (due Fri Apr 30, 2027)", "S14": "Spring S14 (due Fri May 7, 2027)",
}

OWNERS = {
    "ahmad": dict(name="Ahmad Al Khoudeir", first="Ahmad", handle="ahmadalkhoudeir",
                  role="Security Lead", module="Dashboard, response module",
                  reviewer="JWinborne1", reviewer_first="Jaiden", help="Jaiden"),
    "jaiden": dict(name="Jaiden Winborne", first="Jaiden", handle="JWinborne1",
                   role="Co-lead; Architecture and Release Lead",
                   module="Architecture, API, storage, releases",
                   reviewer="ahmadalkhoudeir", reviewer_first="Ahmad", help="Ahmad"),
    "fiona": dict(name="Fiona Lau", first="Fiona", handle="flau0306",
                  role="Detection Engine Lead", module="Engine",
                  reviewer="JWinborne1", reviewer_first="Jaiden", help="Jaiden"),
    "jakub": dict(name="Jakub Kania", first="Jakub", handle="SXafir-byte",
                  role="Protocol Coverage Engineer", module="Sensor",
                  reviewer="flau0306", reviewer_first="Fiona", help="Fiona"),
    "jonattan": dict(name="Jonattan Escalante", first="Jonattan", handle="MeliorExi",
                     role="Offline AI Engineer", module="AI",
                     reviewer="JWinborne1", reviewer_first="Jaiden", help="Jaiden"),
    "ali": dict(name="Ali Al-Kheder", first="Ali", handle="al-kheder",
                role="AI Model Evaluation Engineer", module="AI evaluation",
                reviewer="MeliorExi", reviewer_first="Jonattan", help="Jonattan"),
    "amory": dict(name="Amory B.", first="Amory", handle="gettalife",
                  role="Compliance Mapping Analyst", module="Mapping and reports",
                  reviewer="ahmadalkhoudeir", reviewer_first="Ahmad", help="Ahmad"),
    "karthik": dict(name="Karthik Nair", first="Karthik", handle="Karthiknair91",
                    role="Test and CI Engineer", module="Testing",
                    reviewer="JWinborne1", reviewer_first="Jaiden", help="Jaiden"),
}

LABELS = {
    # name: (color, description) -- descriptions must stay under 100 characters
    "type:task": ("1D76DB", "A roadmap task"),
    "type:bug": ("D73A4A", "Something is broken"),
    "type:question": ("D876E3", "A question (prefer GitHub Discussions)"),
    "type:docs": ("0075CA", "Documentation only"),
    "phase:alpha": ("0E8A16", "Ships in v2.0-alpha (Fall 2026)"),
    "phase:spring": ("5319E7", "Ships in v2.0 (Spring 2027)"),
    "area:engine": ("FBCA04", "Adapters, Zeek, Suricata, rules, pipeline"),
    "area:ai": ("C5DEF5", "Local AI, citations, offline guard, evaluation"),
    "area:mapping": ("BFD4F2", "Compliance and ATT&CK mapping files, reports"),
    "area:ui": ("F9D0C4", "Dashboard pages"),
    "area:api": ("D4C5F9", "FastAPI backend"),
    "area:storage": ("C2E0C6", "SQLite state, Parquet events"),
    "area:sensor": ("FEF2C0", "Live sensor, NetFlow, host agent, hardware"),
    "area:response": ("E99695", "Blocking, preview, approvals, enforcers"),
    "area:testing": ("BFDADC", "Lab, captures, fixtures, integration tests, CI"),
    "area:release": ("006B75", "Packaging, Docker, releases, signing"),
    "area:program": ("EDEDED", "Planning, meetings, reviews, onboarding"),
    "critical-path": ("B60205", "A delay here delays the next demo"),
    "contract-change": ("B60205", "Changes a contract: Jaiden reviews, Security Lead approves"),
    "blocked": ("000000", "Waiting on another task (say which in a comment)"),
    "needs-hardware": ("FEF2C0", "Has steps marked: not run, verify on hardware"),
}
for _key in OWNERS:
    LABELS[f"owner:{_key}"] = ("EDEDED", f"Assigned to {OWNERS[_key]['first']}")

PROJECT_TITLE = "MaxGuard v2.0 Roadmap"
REPO = "ahmadalkhoudeir/maxguard"
