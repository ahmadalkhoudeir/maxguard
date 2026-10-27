#!/bin/bash
# Final browser run: original AHM-03 build vs. the fixed copy, fresh data each.
W=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/dash-review
PY=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin/python
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 UPLOAD_ZIP=$W/telnet_logs.zip
cd $W/scripts
for pair in "original:repo:28741:data5" "fixed:fixed:28743:data6"; do
  IFS=: read label copy port data <<< "$pair"
  rm -rf $W/$data
  $PY $W/scripts/serve.py $W/$copy $W/$data $port basic > $W/server-$label.log 2>&1 &
  pid=$!
  for i in $(seq 1 60); do curl -s -o /dev/null http://127.0.0.1:$port/ && break; sleep 0.5; done
  $PY $W/scripts/add_alerts.py $W/$copy $W/$data info,critical,low > /dev/null
  echo "################ $label ($copy, port $port)"
  timeout 300 node pw_a11y.js http://127.0.0.1:$port mode_switch_keeps_filter status_form_focus queue_refresh_focus width_375 history_back
  timeout 300 node pw_live.js http://127.0.0.1:$port refresh_during_refresh refresh_vs_filter two_analysts upload_focus seven_tabs
  timeout 300 node pw_extra.js http://127.0.0.1:$port catch_up server_ok upload_focus_during
  timeout 120 node pw_tabs_refresh.js http://127.0.0.1:$port
  timeout 120 node pw_labels.js http://127.0.0.1:$port
  kill $pid; wait $pid 2>/dev/null
  rm -rf $W/$data-down
  echo "--- server_down ($label)"
  timeout 120 node pw_server_down.js $PY $W/scripts/serve.py $W/$copy $W/$data-down $((port + 1))
done
