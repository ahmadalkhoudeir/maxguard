#!/bin/bash
# Check 15a: the AHM-02 guide's step-7 header check, run in a build folder.
# Usage: check15_headers.sh <build_dir> <label>
W=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/final-browser
VENV=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin
GUIDE=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/fix2/docgen/outputs/AHM-02/headers.txt
cd $1
PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')
export PATH=$VENV:$PATH MAXGUARD_DATA_DIR=$W/data/c15h-$2 PYTHONDONTWRITEBYTECODE=1
(uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port $PORT > $W/logs/c15h-$2.log 2>&1 & echo $! > $W/tmp/c15h-$2.pid)
for i in $(seq 1 50); do curl -s -o /dev/null http://127.0.0.1:$PORT/docs && break; sleep 0.2; done
curl -s -D - -o /dev/null http://127.0.0.1:$PORT/ | grep -i -E '^(content-security-policy|referrer-policy|x-content-type-options):' | tr -d '\r' > $W/results/c15h-$2.txt
kill $(cat $W/tmp/c15h-$2.pid)
cat $W/results/c15h-$2.txt
if diff $GUIDE $W/results/c15h-$2.txt > /dev/null; then echo "MATCH: byte-for-byte the 3 lines of the guide's headers.txt (same order)"; else echo "DIFFERENT from the guide:"; diff $GUIDE $W/results/c15h-$2.txt; fi
