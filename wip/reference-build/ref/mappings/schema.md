# Mapping files: what every field means

MaxGuard finds problems on a network (for example "someone used Telnet").
A **mapping file** says which rules of a compliance framework each problem
breaks (for example "NIST SP 800-53 control SC-8"). MaxGuard copies these rows
into every report, so an auditor can see *which rule* a finding touches and
*why*.

There is one file per framework in this folder:

| File | Framework | Version (exact text) |
|---|---|---|
| `pci_dss_4_0_1.yaml` | PCI DSS | `4.0.1` |
| `nist_800_53_r5.yaml` | NIST SP 800-53 | `Rev. 5 (Release 5.2.0)` |
| `cisa_cpg_2_0.yaml` | CISA CPG | `2.0` |
| `cjis_6_1.yaml` | CJIS | `6.1` |
| `attack.yaml` (Fiona) | MITRE ATT&CK | `v19.x` point release |

The versions are locked in `docs/PROJECT_DECISIONS.md` section 8. Do not
change a version unless that table changes first.

## The file, line by line

```yaml
framework: NIST SP 800-53            # the framework's short name
version: "Rev. 5 (Release 5.2.0)"    # exact version text, ALWAYS in quotes
source: https://csrc.nist.gov/...    # where anyone can read the framework

mappings:                            # one entry per MaxGuard rule
  cleartext.telnet:                  # the rule's ID (see "Rule IDs" below)
    - control_id: SC-8               # the framework's own number for the rule
      title: Transmission Confidentiality and Integrity
      rationale: Telnet sends every keystroke in readable form, so ...
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
```

### Top of the file (once per file)

| Field | Required | What to write |
|---|---|---|
| `framework` | yes | The framework's short name, spelled exactly as in the table above. Reports group findings by this name. |
| `version` | yes | The exact version text from the table above. **Put it in quotes.** Without quotes, a version like `2.0` is read as the number 2 and the test fails. |
| `source` | yes | A link to the publisher's own page for this version (not a blog or a vendor summary). |
| `mappings` | yes | The list of rules, described below. If you have no checked rows yet, write `mappings: {}` (an empty list), never leave it blank. |

### One row (one framework control for one MaxGuard rule)

| Field | Required | What to write |
|---|---|---|
| `control_id` | yes | The control or requirement number exactly as the framework prints it, for example `SC-8(1)` or `4.2.1`. |
| `title` | yes | The control's title, copied word for word. For a NIST control enhancement write `<base title> \| <enhancement title>`, the way SP 800-53 prints it, for example `Transmission Confidentiality and Integrity \| Cryptographic Protection`. |
| `rationale` | yes | One plain sentence: why this finding breaks this control. Write it for a manager, not an engineer. |
| `verified` | yes for these four files | Where you checked the ID and title, precise enough that someone else can find it again in a minute: document + page or section, for example `PCI DSS v4.0.1 PDF, p. 112`. |
| `tactic` | ATT&CK only | The ATT&CK tactic, for example `credential-access`. Only `attack.yaml` uses it. |

The loader reads `control_id`, `title` and `rationale`; `verified` is for
people (reviewers and auditors) and is checked by the tests.

## Rule IDs

The keys under `mappings:` must be MaxGuard rule IDs that already exist, for
example `cleartext.telnet`, `cleartext.ftp`, `tls.weak_version`,
`cert.expired`. The full list is the rule ID table in
`docs/ARCHITECTURE.md` section 5; in code it is `maxguard.rules.base.RULES`. A rule may
be left out of a framework when no control in that framework fits it.
New rule IDs need Security Lead approval before they get mapping rows.

## The one rule that matters most: never guess

CLAUDE.md rule 8: every row must cite an exact control ID **you read in the
publisher's document** for the locked version. If you cannot check a row,
do not add it. A wrong control ID in a compliance report is worse than a
missing one, because people trust it.

That is why three files are shipped with `mappings: {}`: during planning the
PCI, CISA and FBI websites could not be opened, so Amory fills them in during
tasks AMO-02 (PCI DSS) and AMO-04 (CISA CPG and CJIS).

## How to check your work

From the repository root:

```
pytest tests/unit/test_mappings.py -q
```

The test fails if a file does not load, a required field is missing or
empty, a rule ID does not exist, a version is not the locked one, or a row
has no `verified` note.
