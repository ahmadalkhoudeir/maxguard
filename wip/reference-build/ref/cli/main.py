"""MaxGuard command line (Fiona).

    maxguard analyze INPUT [-o report.json] [--no-ai] [--offline]
                           [--frameworks 'PCI DSS,NIST SP 800-53'] [--format json|csv|html]

INPUT is a .pcap/.pcapng capture, or a folder/.zip/.tar.gz of Zeek logs.
Run it as `maxguard ...` (console script) or `python -m cli.main ...`.

Exit codes, so scripts and CI can react without reading the text:
    0  the report was written
    2  bad input: missing file, not a capture or Zeek log folder, unknown framework
       (argparse also uses 2 for a wrong option)
    3  Zeek failed on the capture
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from maxguard.mapping.loader import ATTACK, load_all
from maxguard.pipeline import UnsupportedInput, analyze, mappings_dir
from maxguard.zeek.runner import ZeekError

EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_ZEEK_ERROR = 3

FORMATS = ("json", "csv", "html")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maxguard", description="Find security weaknesses in network traffic, offline.")
    commands = parser.add_subparsers(dest="command", required=True)

    cmd = commands.add_parser(
        "analyze", help="analyze a capture file or a folder/archive of Zeek logs")
    cmd.add_argument("input", type=Path,
                     help=".pcap/.pcapng file, or a folder, .zip or .tar.gz of Zeek logs")
    cmd.add_argument("-o", "--output", type=Path,
                     help="write the report to this file (default: print it)")
    cmd.add_argument("--no-ai", action="store_true",
                     help="skip the AI explanations (no Ollama needed)")
    cmd.add_argument("--offline", action="store_true",
                     help="block all network access except this machine and the local Ollama")
    cmd.add_argument("--frameworks",
                     help="comma-separated list, e.g. 'PCI DSS,NIST SP 800-53' (default: all)")
    cmd.add_argument("--format", choices=FORMATS, default="json",
                     help="report format (default: json)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)  # a wrong option: argparse prints usage, exits with 2
    if args.command == "analyze":
        return run_analyze(args)
    parser.error(f"unknown command {args.command!r}")  # exits with 2


def run_analyze(args: argparse.Namespace) -> int:
    """The `analyze` command: check the input, run the pipeline, write the report."""
    if not args.input.exists():
        return fail(f"{args.input}: no such file or folder", EXIT_BAD_INPUT)

    frameworks = parse_frameworks(args.frameworks)
    unknown = unknown_frameworks(frameworks)
    if unknown:
        # Without this check a typo ("PCI-DSS") would silently give a report with no controls.
        return fail(f"unknown framework(s): {', '.join(unknown)}. "
                    f"Known: {', '.join(known_frameworks())}", EXIT_BAD_INPUT)

    if args.offline:
        enable_offline_guard()  # first, so no Python code in the analysis can go online

    try:
        # Zeek's logs go to a temporary folder that is deleted afterwards, so no
        # copy of the user's traffic is left behind on disk.
        with tempfile.TemporaryDirectory(prefix="maxguard-") as workdir:
            report = analyze(args.input, workdir, frameworks=frameworks,
                             explain=not args.no_ai)
    except UnsupportedInput as error:
        return fail(str(error), EXIT_BAD_INPUT)
    except ZeekError as error:
        return fail(f"Zeek failed: {error}", EXIT_ZEEK_ERROR)

    write_report(render(report, args.format), args.output)
    if args.output:
        # Status goes to stderr, so stdout stays clean when the report is printed.
        print(f"maxguard: {len(report['findings'])} finding(s), report written to "
              f"{args.output}", file=sys.stderr)
    return EXIT_OK


def parse_frameworks(text: str | None) -> list[str] | None:
    """'PCI DSS, NIST SP 800-53' -> ['PCI DSS', 'NIST SP 800-53']. None means "all"."""
    if not text:
        return None
    names = [name.strip() for name in text.split(",")]
    return [name for name in names if name] or None


def known_frameworks() -> list[str]:
    """Compliance framework names from mappings/*.yaml, e.g. ['CISA CPG', 'CJIS', ...].

    MITRE ATT&CK is left out: its techniques are always added, so it is not
    something to select (and selecting only it would hide every control).
    """
    return sorted({fw["framework"] for fw in load_all(mappings_dir())} - {ATTACK})


def unknown_frameworks(selected: list[str] | None) -> list[str]:
    if not selected:
        return []
    known = set(known_frameworks())
    return [name for name in selected if name not in known]


def enable_offline_guard() -> None:
    # Imported here, not at the top: only --offline needs these modules.
    from maxguard import offline
    from maxguard.ai.ollama_client import ollama_url

    offline.enable(ollama_url())


def render(report: dict, fmt: str) -> str:
    """The report as JSON, CSV or HTML text."""
    # Imported here, not at the top: the analysis itself does not need the
    # export code, so `analyze` keeps working even while report.py changes.
    from maxguard import report as export

    writers = {"json": export.to_json, "csv": export.to_csv, "html": export.to_html}
    return writers[fmt](report)


def write_report(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
    else:
        output.write_text(text, encoding="utf-8")


def fail(message: str, exit_code: int) -> int:
    print(f"maxguard: error: {message}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
