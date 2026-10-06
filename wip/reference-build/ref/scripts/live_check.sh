#!/usr/bin/env bash
# Live-sensor end-to-end check (Karthik, KAR-06).
#
# Run it on the MaxGuard console: its API answers only on 127.0.0.1 (sensors reach
# a separate ingest-only port). It makes one plain-HTTP request (port 80) and one
# Telnet connection (port 23) to a test service on another lab machine, then
# asks the console for its alerts every minute, for up to 30 minutes,
# until a cleartext.http and a cleartext.telnet alert show traffic seen after the
# start. It prints how long each alert took.
#
# Usage:    bash scripts/live_check.sh <console URL> <lab service IPv4 address>
# Example:  bash scripts/live_check.sh http://127.0.0.1:8000 192.168.50.30
#
# The sensor sees only traffic that crosses the mirrored switch port (the cable to
# the router, docs/HARDWARE.md section 1). Plug the test service's machine into a
# LAN port of the router itself for this test, so the probes cross that cable.
#
# Settings (environment variables), mainly so a test can finish in seconds:
#   LIVE_CHECK_POLL_SECONDS     seconds between two looks at the console (default 60)
#   LIVE_CHECK_TIMEOUT_SECONDS  give up after this many seconds (default 1800 = 30 minutes)
#
# Exit codes: 0 both alerts appeared; 1 a probe or the console failed, or an
# alert did not appear in time; 2 wrong arguments or an address outside the lab.
#
# Needs: bash, python3, and curl with Telnet support ("curl --version" lists
# telnet under Protocols).
set -euo pipefail

POLL_SECONDS="${LIVE_CHECK_POLL_SECONDS:-60}"
TIMEOUT_SECONDS="${LIVE_CHECK_TIMEOUT_SECONDS:-1800}"

usage() {
  echo "usage: bash scripts/live_check.sh <console URL> <lab service IPv4 address>" >&2
  echo "example: bash scripts/live_check.sh http://127.0.0.1:8000 192.168.50.30" >&2
  exit 2
}

# Only lab machines may be probed (CLAUDE.md rule 4: never touch hosts you do not
# own). Allowed: the private ranges of RFC 1918, which home and office networks
# use (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), and the documentation ranges
# of RFC 5737 (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24), which are never
# routed on the internet and are the example addresses in MaxGuard's docs. Any
# other address could be someone else's computer. Host names are refused because
# a name can point anywhere; leading zeros are refused because some programs
# read "010" as octal (8).
is_lab_address() {
  local octet='(0|[1-9][0-9]{0,2})'
  [[ "$1" =~ ^$octet\.$octet\.$octet\.$octet$ ]] || return 1
  local a="${BASH_REMATCH[1]}" b="${BASH_REMATCH[2]}" c="${BASH_REMATCH[3]}" d="${BASH_REMATCH[4]}"
  (( a <= 255 && b <= 255 && c <= 255 && d <= 255 )) || return 1
  (( a == 10 )) && return 0
  (( a == 172 && b >= 16 && b <= 31 )) && return 0
  (( a == 192 && b == 168 )) && return 0
  (( a == 192 && b == 0 && c == 2 )) && return 0
  (( a == 198 && b == 51 && c == 100 )) && return 0
  (( a == 203 && b == 0 && c == 113 )) && return 0
  return 1
}

# Every curl call uses --noproxy '*': with a web proxy set (http_proxy), curl
# would send the request to the proxy, so the sensor would see traffic to the
# proxy instead of the lab service, and the console might not be reachable.
fetch_alerts() {
  curl --silent --show-error --fail --max-time 30 --noproxy '*' "$1/api/alerts?limit=1000"
}

# Succeeds when the alert list (JSON on stdin) has an alert for rule $1 whose
# last_seen is at or after $2. Both are Unix seconds; last_seen is when the sensor
# saw the traffic, so the sensor's and this machine's clocks must agree (NTP).
alert_seen_since() {
  python3 -c '
import json, sys
rule, start = sys.argv[1], float(sys.argv[2])
alerts = json.load(sys.stdin)
sys.exit(0 if any(a["rule_id"] == rule and a["last_seen"] >= start for a in alerts) else 1)
' "$1" "$2"
}

check_console() {
  local alerts
  if ! alerts="$(fetch_alerts "$1")"; then
    echo "error: cannot read $1/api/alerts: is the console running?" >&2
    exit 1
  fi
  if ! python3 -c 'import json, sys; assert isinstance(json.load(sys.stdin), list)' \
      <<< "$alerts" 2> /dev/null; then
    echo "error: $1/api/alerts did not return a JSON list: is this a MaxGuard console?" >&2
    exit 1
  fi
}

probe_http() {
  # Any HTTP answer is fine (even 404): what matters is the unencrypted request.
  if ! curl --silent --show-error --max-time 10 --noproxy '*' --output /dev/null "http://$1/"; then
    echo "error: no HTTP answer from $1 port 80: is the test service running?" >&2
    exit 1
  fi
  echo "sent: plain HTTP request to $1 port 80"
}

probe_telnet() {
  # curl speaks Telnet too: type the lab user name, then "exit" so the service hangs up.
  local reply status=0
  reply="$(printf 'labuser\r\nexit\r\n' \
    | curl --silent --max-time 10 --noproxy '*' "telnet://$1:23")" || status=$?
  # A service that keeps asking for a password stops only at curl's time limit
  # (exit code 28); that is fine. What counts is that the service answered:
  # MaxGuard only reports a Telnet session in which the server sent something.
  if [[ -z "$reply" ]]; then
    echo "error: no Telnet answer from $1 port 23 (curl exit code $status):" \
      "is the test service running?" >&2
    exit 1
  fi
  echo "sent: Telnet session to $1 port 23"
}

minutes_and_seconds() {
  echo "$(( $1 / 60 )) min $(( $1 % 60 )) s"
}

main() {
  [[ $# -eq 2 ]] || usage
  local console="${1%/}" service="$2"
  [[ "$console" =~ ^https?:// ]] || usage
  if ! [[ "$POLL_SECONDS" =~ ^[1-9][0-9]*$ && "$TIMEOUT_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
    echo "error: LIVE_CHECK_POLL_SECONDS and LIVE_CHECK_TIMEOUT_SECONDS must be" \
      "whole numbers above 0" >&2
    exit 2
  fi
  if ! is_lab_address "$service"; then
    echo "refused: $service is not a lab address (allowed: 10.0.0.0/8, 172.16.0.0/12," \
      "192.168.0.0/16 and the documentation ranges 192.0.2.0/24, 198.51.100.0/24," \
      "203.0.113.0/24; IPv4 numbers only)" >&2
    exit 2
  fi

  check_console "$console"  # fail now, not after 30 minutes of waiting
  local start
  start="$(date +%s)"
  probe_http "$service"
  probe_telnet "$service"
  echo "waiting for the alerts (checking every ${POLL_SECONDS} s, for up to" \
    "$(minutes_and_seconds "$TIMEOUT_SECONDS"))"

  local http_took="" telnet_took="" alerts now
  while true; do
    now="$(date +%s)"
    # A console that is busy or restarting is not a failure: try again next time.
    if alerts="$(fetch_alerts "$console")"; then
      if [[ -z "$http_took" ]] && alert_seen_since cleartext.http "$start" <<< "$alerts"; then
        http_took=$(( now - start ))
        echo "cleartext.http alert after $(minutes_and_seconds "$http_took")"
      fi
      if [[ -z "$telnet_took" ]] && alert_seen_since cleartext.telnet "$start" <<< "$alerts"; then
        telnet_took=$(( now - start ))
        echo "cleartext.telnet alert after $(minutes_and_seconds "$telnet_took")"
      fi
    else
      echo "warning: could not read the alerts this time; trying again" >&2
    fi
    if [[ -n "$http_took" && -n "$telnet_took" ]]; then
      echo "PASS: both alerts appeared"
      exit 0
    fi
    if (( now - start >= TIMEOUT_SECONDS )); then
      [[ -n "$http_took" ]] || echo "FAIL: no cleartext.http alert" >&2
      [[ -n "$telnet_took" ]] || echo "FAIL: no cleartext.telnet alert" >&2
      echo "after $(minutes_and_seconds "$TIMEOUT_SECONDS")" >&2
      exit 1
    fi
    sleep "$POLL_SECONDS"
  done
}

main "$@"
