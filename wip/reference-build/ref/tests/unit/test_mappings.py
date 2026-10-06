"""Checks for mappings/*.yaml (Contract 2 and CLAUDE.md rule 8).

These tests guard the compliance rows that end up in every report: each file
must load, use the locked framework version, name only real rule IDs, and
say where every row was verified.
"""

import re
from pathlib import Path

import pytest
import yaml

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.mapping.loader import ATTACK, REQUIRED_TOP, validate
from maxguard.rules.base import RULES

MAPPINGS_DIR = Path(__file__).resolve().parents[2] / "mappings"
MAPPING_FILES = sorted(MAPPINGS_DIR.glob("*.yaml"))

# docs/PROJECT_DECISIONS.md section 8. Change this table only when that one changes.
LOCKED_VERSIONS = {
    "PCI DSS": "4.0.1",
    "NIST SP 800-53": "Rev. 5 (Release 5.2.0)",
    "CISA CPG": "2.0",
    "CJIS": "6.1",
}
# ATT&CK is locked to major version 19; the file records the exact point release.
ATTACK_VERSION = re.compile(r"^v19\.\d+$")

COMPLIANCE_FILES = {
    "pci_dss_4_0_1.yaml": "PCI DSS",
    "nist_800_53_r5.yaml": "NIST SP 800-53",
    "cisa_cpg_2_0.yaml": "CISA CPG",
    "cjis_6_1.yaml": "CJIS",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def rows_of(fw: dict):
    """Yield (rule_id, row) for every row in one mapping file."""
    for rule_id, rows in fw["mappings"].items():
        for row in rows:
            yield rule_id, row


def by_name(paths):
    return [pytest.param(p, id=p.name) for p in paths]


def test_every_compliance_framework_has_its_file():
    for file_name, framework in COMPLIANCE_FILES.items():
        path = MAPPINGS_DIR / file_name
        assert path.exists(), f"missing {file_name}"
        assert load(path)["framework"] == framework


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_file_loads_with_required_keys(path):
    fw = load(path)
    assert isinstance(fw, dict)
    for key in REQUIRED_TOP:
        assert key in fw, f"{path.name}: missing {key!r}"
    # "mappings:" left blank loads as None and would crash the loader.
    assert isinstance(fw["mappings"], dict), "write 'mappings: {}' when there are no rows"


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_version_is_the_locked_one(path):
    fw = load(path)
    # Unquoted 2.0 or 6.1 would load as a number, so check the type first.
    assert isinstance(fw["version"], str), "put the version in quotes"
    if fw["framework"] == ATTACK:
        assert ATTACK_VERSION.match(fw["version"])
    else:
        assert fw["version"] == LOCKED_VERSIONS[fw["framework"]]


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_source_is_a_web_link(path):
    assert load(path)["source"].startswith("https://")


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_every_rule_id_is_registered(path):
    unknown = set(load(path)["mappings"]) - set(RULES)
    assert not unknown, f"not in the rule registry: {sorted(unknown)}"


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_loader_finds_no_problems(path):
    assert validate(load(path), set(RULES)) == []


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_every_compliance_row_says_where_it_was_verified(path):
    fw = load(path)
    if fw["framework"] == ATTACK:
        pytest.skip("this check is for the four compliance files, not ATT&CK")
    for rule_id, row in rows_of(fw):
        assert str(row.get("verified", "")).strip(), f"{rule_id} {row['control_id']}: no 'verified'"


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_no_control_listed_twice_for_one_rule(path):
    for rule_id, rows in load(path)["mappings"].items():
        ids = [row["control_id"] for row in rows]
        assert len(ids) == len(set(ids)), f"{rule_id}: repeated control_id"


def test_demo_finding_is_mapped_in_nist():
    # cleartext.telnet is the demo finding; it must show controls in reports.
    nist = load(MAPPINGS_DIR / "nist_800_53_r5.yaml")
    assert "SC-8" in [row["control_id"] for row in nist["mappings"]["cleartext.telnet"]]
