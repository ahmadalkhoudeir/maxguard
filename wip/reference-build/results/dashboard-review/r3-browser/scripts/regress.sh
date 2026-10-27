#!/bin/bash
# ruff + pytest (not integration) in each fixed build; last lines quoted in the report
W=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad
R=$W/agentwork/r3-browser
V=$W/ref/.venv/bin
export PYTHONDONTWRITEBYTECODE=1 TMPDIR=$R/tmp
for s in AHM-02 AHM-03 AHM-06; do
  cd $R/fixed-$s || exit 1
  echo "=== fixed-$s: ruff check ."
  $V/ruff check . 2>&1 | tail -3
  echo "=== fixed-$s: pytest -m 'not integration' -q"
  $V/pytest -m "not integration" -q -p no:cacheprovider 2>&1 | tail -5
done
echo "=== done $(date)"
