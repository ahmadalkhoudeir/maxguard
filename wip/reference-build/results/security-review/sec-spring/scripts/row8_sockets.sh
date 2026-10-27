#!/usr/bin/env bash
# AHM-04 row 8: which sockets do Zeek 9.0.0 and Suricata 8.0.7 open on the sensor?
# Same private namespace and container commands as row8_sensor.sh, no traffic.
# Usage: row8_sockets.sh REPO NEW_OUT_DIR   (NEW_OUT_DIR must not exist yet)
set -eu
REPO=$(realpath "$1")
OUT=$2
mkdir "$OUT"
OUT=$(realpath "$OUT")
mkdir -p "$OUT/data/spool/zeek" "$OUT/data/spool/suricata" "$OUT/data/zeek"
NS=secspring-sensorns
docker container rm --force $NS secspring-zeek secspring-suricata >/dev/null 2>&1 || true
docker run -d --name $NS --network none --cap-add NET_ADMIN --cap-add NET_RAW \
  nicolaka/netshoot:v0.15 sleep 600 >/dev/null
docker exec $NS ip link add cap0 type veth peer name tap0
docker exec $NS ip link set cap0 promisc on
docker exec $NS ip link set cap0 up
docker exec $NS ip link set tap0 up
docker exec $NS ip link add mgmt0 type veth peer name mtap0
docker exec $NS ip addr add 198.51.100.20/24 dev mgmt0
docker exec $NS ip link set mgmt0 up
docker exec $NS ip link set mtap0 up
docker run -d --name secspring-zeek --network container:$NS --cap-drop ALL --cap-add NET_RAW \
  --cap-add NET_ADMIN --security-opt no-new-privileges:true -e TZ=UTC -w /data/spool/zeek \
  -v "$OUT/data:/data" -v "$REPO/maxguard:/opt/maxguard/maxguard:ro" zeek/zeek:9.0.0 \
  zeek -i cap0 -C LogAscii::use_json=T Log::default_rotation_interval=1min \
  /opt/maxguard/maxguard/zeek/site.zeek policy/protocols/conn/community-id-logging \
  /opt/maxguard/maxguard/zeek/scripts/cleartext.zeek /opt/maxguard/maxguard/zeek/scripts/inventory.zeek \
  /opt/maxguard/maxguard/zeek/scripts/live/rotate.zeek >/dev/null
docker run -d --name secspring-suricata --network container:$NS --cap-drop ALL \
  --cap-add NET_ADMIN --cap-add NET_RAW --cap-add SYS_NICE --cap-add CHOWN --cap-add DAC_OVERRIDE \
  --cap-add SETUID --cap-add SETGID --cap-add SETPCAP --security-opt no-new-privileges:true -e TZ=UTC \
  -v "$OUT/data/spool/suricata:/var/log/suricata" -v "$REPO/maxguard:/opt/maxguard/maxguard:ro" \
  jasonish/suricata:8.0.7 -c /opt/maxguard/maxguard/suricata/maxguard-suricata-live.yaml \
  --af-packet=cap0 -S /opt/maxguard/maxguard/suricata/rules/maxguard.rules >/dev/null
sleep 15
echo "--- TCP/UDP sockets in the sensor namespace (ss -tulpn), Zeek and Suricata running:"
docker exec $NS ss -tulpn
echo "--- packet (capture) sockets (ss -0 -p):"
docker exec $NS ss -0 -p | head -12
echo "--- processes still running: $(docker ps --filter name=secspring- --format '{{.Names}}' | tr '\n' ' ')"
docker container rm --force $NS secspring-zeek secspring-suricata >/dev/null
echo "containers removed"
