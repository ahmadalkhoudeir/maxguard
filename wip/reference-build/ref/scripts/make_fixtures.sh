#!/usr/bin/env bash
# Rebuild the unit-test fixtures from the lab captures (Karthik, KAR-02).
#
# For every tests/pcaps/<name>.pcap this writes tests/fixtures/zeek/<name>/:
# the Zeek JSON logs and Suricata's eve.json, made exactly the way MaxGuard
# makes them (Zeek 9.0.0 with -D and Community ID, MaxGuard's Zeek scripts,
# Suricata 7.0.10 with MaxGuard's config). Unit tests read these folders, so
# they run in seconds without Docker.
#
# Usage (from the repository root):  bash scripts/make_fixtures.sh
# Optional: FIXTURES_DIR=/tmp/x bash scripts/make_fixtures.sh   (write elsewhere)
set -euo pipefail

ZEEK_IMAGE="zeek/zeek:9.0.0"
SURICATA_IMAGE="jasonish/suricata:7.0.10"   # same base version as Debian 13's package
FIXTURES_DIR="${FIXTURES_DIR:-tests/fixtures/zeek}"
USER_IDS="$(id -u):$(id -g)"   # files belong to you, not to root

cd "$(dirname "$0")/.."
mkdir -p "$FIXTURES_DIR"
FIXTURES_DIR="$(cd "$FIXTURES_DIR" && pwd)"

for pcap in tests/pcaps/*.pcap; do
  name="$(basename "$pcap" .pcap)"
  out="$FIXTURES_DIR/$name"
  rm -rf "$out"
  mkdir -p "$out"

  # Zeek: -D makes the output identical on every run; --network none proves it is offline.
  docker run --rm --network none --user "$USER_IDS" \
    -v "$PWD/tests/pcaps:/pcaps:ro" -v "$PWD/maxguard/zeek:/mgzeek:ro" \
    -v "$out:/logs" -w /logs "$ZEEK_IMAGE" \
    zeek -D -C -r "/pcaps/$name.pcap" /mgzeek/site.zeek LogAscii::use_json=T \
      policy/protocols/conn/community-id-logging /mgzeek/scripts/cleartext.zeek \
      /mgzeek/scripts/inventory.zeek
  # These logs describe the Zeek run itself, not the traffic, and change every run.
  rm -f "$out"/loaded_scripts.log "$out"/packet_filter.log "$out"/stats.log \
        "$out"/capture_loss.log "$out"/reporter.log

  # Suricata: writes eve.json (plus files we do not keep) into a scratch folder.
  scratch="$(mktemp -d)"
  docker run --rm --network none --user "$USER_IDS" --entrypoint suricata \
    -v "$PWD/tests/pcaps:/pcaps:ro" -v "$PWD/maxguard/suricata:/cfg:ro" -v "$scratch:/out" \
    "$SURICATA_IMAGE" -c /cfg/maxguard-suricata.yaml -r "/pcaps/$name.pcap" -l /out \
      -k none --runmode single -S /cfg/rules/maxguard.rules > /dev/null
  cp "$scratch/eve.json" "$out/eve.json"
  rm -rf "$scratch"

  echo "$name: $(cd "$out" && ls | tr '\n' ' ')"
done
