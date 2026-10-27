#!/bin/bash
R=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/r3-browser
cd $R/scripts
echo "### c4"; timeout 400 node c4_filter_race.js fixed-03 orig-03 fixed-02 fixed-06
echo "### c5"; timeout 400 node c5_history.js fixed-03 orig-03 fixed-02 fixed-06
echo "### c6 (bfcache off)"; timeout 400 node c6_status.js fixed-03 orig-03 fixed-06
echo "### c6 (bfcache on)"; timeout 400 node c6_status.js bfcache fixed-03 orig-03
echo "### c9"; timeout 400 node c9_upload_focus.js fixed-02 orig-02 fixed-03 fixed-06
echo "### done $(date)"
