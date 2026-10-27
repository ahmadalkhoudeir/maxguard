#!/usr/bin/env bash
# AHM-04 row 8: does anything send packets on the sensor's capture interface?
#
# A private network namespace (container secspring-sensorns, --network none)
# plays the sensor host: cap0 is the capture port (up, promiscuous, no IPv4,
# IPv6 disabled, as HARDWARE.md section 8.3 sets it), tap0 is the "switch" end
# of the same cable, and mgmt0 (198.51.100.20/24, RFC 5737) is the management
# port. Zeek 9.0.0 and Suricata 8.0.7 run with the exact commands, capabilities
# and config files of docker/sensor-compose.yaml, joined to that namespace.
# The repository's synthetic test captures are replayed into tap0. tcpdump
# records every frame cap0 TRANSMITS (-Q out). Nothing leaves this machine.
#
# Usage: row8_sensor.sh REPO OUT VARIANT
#   VARIANT: sensor     (rp_filter=2, IPv6 off: Zeek + Suricata + replay + ARP/ICMP probes)
#            rpf0       (rp_filter=0, IPv6 off: kernel only, ARP/ICMP probes)
#            ipv6on     (rp_filter=2, IPv6 left on as with ipv6.method ignore: kernel only)
#            reject     (as "sensor", plus one Suricata rule with the "reject" action)
set -euo pipefail
REPO=$(realpath "$1"); OUT=$(realpath -m "$2"); VARIANT=$3
NS=secspring-sensorns
rm -rf "$OUT"; mkdir -p "$OUT/cap" "$OUT/data/spool/zeek" "$OUT/data/spool/suricata" "$OUT/data/zeek" "$OUT/rules"
cleanup() { docker rm -f $NS secspring-zeek secspring-suricata >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup

RPF=2; ARPIGN=0
[ "$VARIANT" = rpf0 ] && RPF=0
[ "$VARIANT" = rpf0-fix ] && RPF=0 && ARPIGN=8
[ "$VARIANT" = rpf0-egressdrop ] && RPF=0
RPF_DEFAULT=$RPF
# The proposed HARDWARE.md fix: all=0 (kernel default) but the port itself gets 1 and 8.
[ "$VARIANT" = rpf0-sysctlfix ] && RPF=0 && RPF_DEFAULT=1 && ARPIGN=8
docker run -d --name $NS --network none --cap-add NET_ADMIN --cap-add NET_RAW \
  --sysctl net.ipv4.conf.all.rp_filter=$RPF --sysctl net.ipv4.conf.default.rp_filter=$RPF_DEFAULT \
  --sysctl net.ipv4.conf.default.arp_ignore=$ARPIGN \
  -v "$REPO/tests/pcaps:/pcaps:ro" -v "$OUT/cap:/cap" -v "$(cd "$(dirname "$0")" && pwd):/scripts:ro" \
  nicolaka/netshoot:v0.15 sleep 3600 >/dev/null
docker exec $NS sh -c '
  set -e
  ip link add cap0 type veth peer name tap0
  ip link add mgmt0 type veth peer name mtap0
  ip link set cap0 promisc on
  ip link set cap0 up; ip link set tap0 up
  ip addr add 198.51.100.20/24 dev mgmt0
  ip link set mgmt0 up; ip link set mtap0 up
  ip route add default via 198.51.100.1 dev mgmt0
  ip neigh replace 198.51.100.1 lladdr 02:00:00:00:00:fe dev mgmt0 nud permanent
'
echo "--- sensor namespace ($VARIANT)"
docker exec $NS sh -c 'ip -br addr show cap0; ip -br addr show mgmt0; ip -d link show cap0 | grep -o "promiscuity [0-9]*";
  for k in net.ipv4.conf.cap0.rp_filter net.ipv4.conf.all.rp_filter net.ipv4.conf.cap0.arp_ignore; do echo "$k = $(sysctl -n $k)"; done; echo "IPv6 in this kernel: $(test -d /proc/sys/net/ipv6 && echo on || echo off \(booted with ipv6.disable=1\))"'
CAP0_MAC=$(docker exec $NS cat /sys/class/net/cap0/address)
if [ "${VARIANT%egressdrop}" != "$VARIANT" ]; then
  docker exec $NS sh -c 'nft add table netdev maxguard_capture && nft add chain netdev maxguard_capture egress "{ type filter hook egress device cap0 priority 0; policy drop; }" && nft add rule netdev maxguard_capture egress counter drop && echo "nft: egress drop-all chain on cap0"'
fi
echo "cap0 MAC: $CAP0_MAC"

docker exec -d $NS sh -c 'tcpdump -i cap0 -Q out -nn -U -w /cap/cap0-out.pcap 2>/cap/cap0-out.err'
docker exec -d $NS sh -c 'tcpdump -i cap0 -Q in -nn -U -w /cap/cap0-in.pcap 2>/cap/cap0-in.err'
docker exec -d $NS sh -c 'tcpdump -i mgmt0 -Q out -nn -U -w /cap/mgmt0-out.pcap 2>/cap/mgmt0-out.err'
sleep 2

if [ "$VARIANT" = sensor ] || [ "${VARIANT#reject}" != "$VARIANT" ]; then
  RULES=/opt/maxguard/maxguard/suricata/rules/maxguard.rules
  if [ "${VARIANT#reject}" != "$VARIANT" ]; then
    printf '%s\n' 'reject tcp any any -> any 23 (msg:"AHM-04 review: reject action in IDS mode"; flow:to_server; sid:9900001; rev:1;)' > "$OUT/rules/review.rules"
    RULES=/review-rules/review.rules
  fi
  # docker/sensor-compose.yaml, service "zeek" (interface and 1-minute rotation for a quick test)
  docker run -d --name secspring-zeek --network container:$NS --cap-drop ALL --cap-add NET_RAW \
    --cap-add NET_ADMIN --security-opt no-new-privileges:true -e TZ=UTC -w /data/spool/zeek \
    -v "$OUT/data:/data" -v "$REPO/maxguard:/opt/maxguard/maxguard:ro" zeek/zeek:9.0.0 \
    zeek -i cap0 -C LogAscii::use_json=T Log::default_rotation_interval=1min \
    /opt/maxguard/maxguard/zeek/site.zeek policy/protocols/conn/community-id-logging \
    /opt/maxguard/maxguard/zeek/scripts/cleartext.zeek /opt/maxguard/maxguard/zeek/scripts/inventory.zeek \
    /opt/maxguard/maxguard/zeek/scripts/live/rotate.zeek >/dev/null
  # docker/sensor-compose.yaml, service "suricata"
  docker run -d --name secspring-suricata --network container:$NS --cap-drop ALL \
    --cap-add NET_ADMIN --cap-add NET_RAW --cap-add SYS_NICE --cap-add CHOWN --cap-add DAC_OVERRIDE \
    --cap-add SETUID --cap-add SETGID --cap-add SETPCAP --security-opt no-new-privileges:true -e TZ=UTC \
    -v "$OUT/data/spool/suricata:/var/log/suricata" -v "$REPO/maxguard:/opt/maxguard/maxguard:ro" \
    -v "$OUT/rules:/review-rules:ro" jasonish/suricata:8.0.7 \
    -c /opt/maxguard/maxguard/suricata/maxguard-suricata-live.yaml --af-packet=cap0 -S "$RULES" >/dev/null
  for i in $(seq 1 60); do
    if docker logs secspring-suricata 2>&1 | grep -q -i "engine started\|threads created"; then break; fi
    sleep 1
  done
  sleep 3
  echo "--- suricata start-up lines"; docker logs secspring-suricata 2>&1 | grep -i -E "af-packet|engine|rules|error|warn" | head -8
  echo "--- zeek start-up lines"; docker logs secspring-zeek 2>&1 | head -5
fi

echo "--- inject into tap0 (arrives at cap0)"
docker exec $NS python3 /scripts/row8_inject.py "$CAP0_MAC"
sleep 5
if [ "$VARIANT" = sensor ] || [ "${VARIANT#reject}" != "$VARIANT" ]; then
  echo "--- wait for Zeek's 1-minute rotation and Suricata's minute file"
  sleep 70
  echo "zeek interval folders: $(ls "$OUT/data/zeek" | tr '\n' ' ')"
  for f in "$OUT"/data/zeek/*/conn.log; do [ -f "$f" ] && echo "  $(basename "$(dirname "$f")")/conn.log lines: $(wc -l < "$f")"; done
  ls "$OUT"/data/zeek/*/ 2>/dev/null | grep -E "\.log$" | sort | uniq -c | head -20
  echo "suricata eve files: $(ls "$OUT/data/spool/suricata" | grep eve | tr '\n' ' ')"
  cat "$OUT"/data/spool/suricata/eve-*.json 2>/dev/null | python3 -c "
import collections, json, sys
c = collections.Counter(); alerts = []
for line in sys.stdin:
    e = json.loads(line); c[e['event_type']] += 1
    if e['event_type'] == 'alert': alerts.append((e['alert']['signature'], e['alert'].get('action')))
print('  eve event types:', dict(c)); print('  alerts:', alerts[:3])"
  docker stop -t 10 secspring-zeek secspring-suricata >/dev/null
  echo "--- suricata stats lines"; docker logs secspring-suricata 2>&1 | grep -i -E "packets|reject|libnet|drop" | tail -6
fi
docker exec $NS sh -c 'pkill tcpdump; sleep 1'
echo "--- what cap0 TRANSMITTED (tcpdump -Q out on cap0)"
docker exec $NS sh -c 'cat /cap/cap0-out.err | tail -2; tcpdump -nn -e -r /cap/cap0-out.pcap 2>/dev/null | head -12; echo "frames sent on cap0: $(tcpdump -r /cap/cap0-out.pcap 2>/dev/null | wc -l)"'
echo "--- what cap0 RECEIVED"
docker exec $NS sh -c 'echo "frames received on cap0: $(tcpdump -r /cap/cap0-in.pcap 2>/dev/null | wc -l)"'
if [ "${VARIANT%egressdrop}" != "$VARIANT" ]; then
  echo "--- nft egress counter on cap0"; docker exec $NS nft list table netdev maxguard_capture | grep counter
fi
echo "--- what the management port mgmt0 TRANSMITTED"
docker exec $NS sh -c 'tcpdump -nn -e -r /cap/mgmt0-out.pcap 2>/dev/null | head -8; echo "frames sent on mgmt0: $(tcpdump -r /cap/mgmt0-out.pcap 2>/dev/null | wc -l)"'
