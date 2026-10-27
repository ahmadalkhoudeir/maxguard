#!/usr/bin/env bash
# AHM-04 row 9, short repro: refused response steps leave no audit row.
# Usage: row9_curl.sh REPO OUT PORT   (starts the console on 127.0.0.1:PORT, stops it after)
set -u
REPO=$(realpath "$1"); OUT=$(realpath -m "$2"); PORT=$3
PY=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin/python
rm -rf "$OUT"; mkdir -p "$OUT/data"
cd "$REPO" || exit 1
env -u HTTPS_PROXY -u https_proxy PYTHONDONTWRITEBYTECODE=1 MAXGUARD_DATA_DIR="$OUT/data" \
  "$PY" -m uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port "$PORT" \
  --log-level warning > "$OUT/server.log" 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null; wait $SERVER 2>/dev/null' EXIT
for _ in $(seq 50); do curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/api/audit" && break; sleep 0.2; done
B="http://127.0.0.1:$PORT/api/response/proposals"
post() { curl -s --noproxy '*' -w ' -> HTTP %{http_code}\n' -X POST "$1" -H 'Content-Type: application/json' -d "$2"; }
echo "1 propose 203.0.113.7:        $(post "$B" '{"actor":"a","ip":"203.0.113.7"}' | tail -c 14)"
echo "2 approve without preview:    $(post "$B/1/approve" '{"actor":"a","confirm_ip":"203.0.113.7"}')"
echo "3 propose 127.0.0.1:          $(post "$B" '{"actor":"a","ip":"127.0.0.1"}')"
echo "4 propose 203.0.113.7 again:  $(post "$B" '{"actor":"a","ip":"203.0.113.7"}')"
echo "5 apply before approval:      $(post "$B/1/apply" '{"actor":"a"}')"
echo "6 audit table (action, target):"
curl -s --noproxy '*' "http://127.0.0.1:$PORT/api/audit" \
  | "$PY" -c "import json, sys; print('  ', [(r['action'], r['target']) for r in json.load(sys.stdin)])"
