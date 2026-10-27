#!/bin/bash
R=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/r3-browser
cd $R/scripts
echo "### c7"; timeout 400 node c7_times.js fixed-06 orig-06 fixed-03 orig-03
echo "### c8"; timeout 400 node c8_limit.js fixed-02 orig-02 fixed-03 fixed-06
echo "### c11 tab order"; timeout 600 node c11_tab_order.js fixed-06 fixed-02 fixed-03
echo "### c10 axe"; timeout 900 node c10_axe.js fixed-06 orig-06
echo "### done $(date)"
