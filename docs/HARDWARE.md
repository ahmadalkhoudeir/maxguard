# MaxGuard lab build guide

This guide builds the **reference lab**: a Raspberry Pi 5 sensor that listens
to a switch mirror port and sees every device on a small network. Follow it in
order. It ends with five tests that prove the mirror really works.

Owner: Jakub (@SXafir-byte): task **JAK-06** builds this lab (due Friday,
December 4, 2026, or the first spring week if the parts arrive later) and task
**JAK-07** turns it into the live sensor (spring 2027). The locked hardware
decisions are in `docs/PROJECT_DECISIONS.md` section 4.

> **Read this first.** There was no Raspberry Pi, switch, router, or mesh Wi-Fi in
> the planning environment, so **every hardware step here is marked
> "not run — verify on hardware"**. Commands that *could* be checked were run in
> a Docker simulation (marked **[SIM]**), and menu names were checked against
> the vendors' manuals and help pages (links in [References](#references)).
> Vendor websites were blocked during planning, so menu names come from search
> excerpts of those pages: when a menu is not where this guide says, trust your
> screen and fix this file in your pull request.

> **Public repository.** Every address below is an *example* from the private
> range 192.168.50.0/24 (RFC 1918) or the documentation range 203.0.113.0/24
> (RFC 5737). Never commit your real addresses, MAC addresses, passwords, Wi-Fi
> names, SSH keys, or captures from your home network.

## Contents

1. [What you are building](#1-what-you-are-building)
2. [Parts](#2-parts)
3. [Wiring](#3-wiring)
4. [Router: TP-Link Archer AX4400](#4-router-tp-link-archer-ax4400)
5. [Switch: TP-Link TL-SG105E port mirroring](#5-switch-tp-link-tl-sg105e-port-mirroring)
6. [Mesh Wi-Fi in bridge (access point) mode](#6-mesh-wi-fi-in-bridge-access-point-mode)
7. [Raspberry Pi 5: power, cooling, and Raspberry Pi OS 64-bit](#7-raspberry-pi-5-power-cooling-and-raspberry-pi-os-64-bit)
8. [Sensor networking: a management port and a silent capture port](#8-sensor-networking-a-management-port-and-a-silent-capture-port)
9. [USB SSD for the logs](#9-usb-ssd-for-the-logs)
10. [Docker Engine on the Pi](#10-docker-engine-on-the-pi)
11. [Zeek and Suricata on ARM64](#11-zeek-and-suricata-on-arm64)
12. [Prove the mirror works (five tests)](#12-prove-the-mirror-works-five-tests)
13. [Known limits](#13-known-limits)
14. [Troubleshooting](#14-troubleshooting)

## 1. What you are building

```text
Fiber ONT ──► Archer AX4400 router (NAT + DHCP, its Wi-Fi OFF)
                  │  one cable from ONE router LAN port
                  ▼
          TL-SG105E port 1   ◄── mirrored: Ingress + Egress
          TL-SG105E port 2  ──► mesh Wi-Fi primary node (bridge / access point mode)
          TL-SG105E port 3  ──► Pi management port (USB RTL8153 adapter, eth1)
          TL-SG105E port 4      (empty)
          TL-SG105E port 5  ──► Pi capture port (onboard Ethernet, eth0) = mirror destination
```

**Why it works:** every packet between your devices and the internet passes the
cable on switch port 1. The switch copies both directions of port 1 to port 5,
where the Pi listens. Because the router is *above* the switch, the Pi sees each
device's own internal address (not one shared public address) and the DHCP
messages that carry device names.

**Why each rule matters:**

| Rule | What breaks if you ignore it |
|---|---|
| Router Wi-Fi off | Devices on the router's own Wi-Fi never cross port 1: invisible. |
| Mesh in bridge/AP mode | In router mode the mesh hides all its devices behind one address (double NAT). |
| Nothing else on the router's LAN ports | Those devices never cross port 1: invisible. |
| Port 1 mirrored in **both** directions | The Pi sees only half of every conversation; most detections fail. |
| Capture port has no IP address | The Pi would send packets into the network it watches (CLAUDE.md rule 5). |

## 2. Parts

From `docs/PROJECT_DECISIONS.md`, plus what you need to install it.

| Part | Purpose | Notes |
|---|---|---|
| Raspberry Pi 5, 8 GB | Sensor (Zeek + Suricata) | 8 GB leaves room for both tools and the OS. |
| Raspberry Pi **27 W USB-C** power supply (5.1 V, 5 A) | Power | Required: only with a 5 A supply does the Pi 5 give USB devices 1.6 A instead of 600 mA. The SSD and the USB Ethernet adapter need it. (Verified, Raspberry Pi documentation, *Power supply*.) |
| Raspberry Pi **Active Cooler** | Cooling | Zeek and Suricata keep the CPU busy; the Pi throttles from 80 °C, and a throttled sensor drops packets. (Verified, Raspberry Pi documentation, *Frequency management and thermal control*.) Fit it once: it is not meant to be removed. |
| 64 GB A2 microSD card | Operating system | Only the OS lives here. |
| **USB 3 SSD, 128 GB or more** | Logs and events (`/data`) | Recommended in PROJECT_DECISIONS: 7 days of logs would wear out a microSD card. |
| USB 3 gigabit Ethernet adapter, **RTL8153** chipset | Management port (`eth1`) | Linux driver `r8152` is part of the Pi 5 kernel. (Verified, Raspberry Pi kernel config `CONFIG_USB_RTL8152=m`.) |
| TP-Link **TL-SG105E** smart switch | Port mirroring | Hardware version 2 and later have a web interface; version 1 needs a Windows utility. |
| TP-Link **Archer AX4400** router (already owned) | NAT and DHCP | Its Wi-Fi gets turned off. |
| Consumer **mesh Wi-Fi** that supports bridge/AP mode with several units | Wi-Fi | TP-Link Deco and eero do. **Google Nest Wifi / Google Wifi only support bridge mode with a single unit** (Verified, Google Nest Help 6240987), so a multi-point Google mesh would hide devices behind NAT. |
| 4 × Cat 6 patch cables | Wiring | Router→port 1, mesh→port 2, Pi USB adapter→port 3, Pi eth0→port 5. |
| A laptop with an Ethernet port (or adapter) | Setup | You will turn the router's Wi-Fi off, so you need a cable. |

Prices change; check the retailer. PROJECT_DECISIONS estimates the switch at
about $30. The upgrade path for capture, the Dualcomm ETAP-2003 TAP, was listed at
about US $210–$230 in October 2026; it has **one** monitor port, so it has the same
1 Gbps ceiling as the mirror port, but it physically blocks the sensor from
transmitting. (Likely: Dualcomm product page and TAP selection guide, read
through search excerpts.)

## 3. Wiring

**Not run — verify on hardware.** Do the steps in sections 4–11 first; connect
the Pi's capture port to switch port 5 only when section 8 says so.

1. Router: one cable from **one** AX4400 LAN port to **switch port 1**. Nothing
   else in the router's LAN ports.
2. Mesh: the primary mesh node's WAN/internet port to **switch port 2**.
3. Pi management: the RTL8153 USB adapter (in a blue USB 3 port) to **switch port 3**.
4. Port 4 stays empty (test 4 in section 12 borrows it).
5. Pi capture: the Pi's onboard Ethernet to **switch port 5** (section 8.3).

## 4. Router: TP-Link Archer AX4400

Menu names below come from the AX4400 user guide (REV2.6.0) and TP-Link's FAQs.
Your hardware version is on the label under the router (`Ver: ...`); if a menu
differs, open the user guide for that version. **Not run — verify on hardware.**

### 4.1 Log in and update

1. Plug your laptop into an AX4400 LAN port with a cable.
2. Open `http://tplinkwifi.net` (or `http://192.168.0.1` on a factory-default
   router). The first time, it asks you to create a login password. Store it in
   the lab's password manager, never in this repository.
3. Update the firmware (*Advanced → System → Firmware Upgrade*, or download it
   from tp-link.com for your hardware version).

*Expected:* the router's **Network Map** page loads.

### 4.2 Turn the router's Wi-Fi off

1. Go to **Advanced → Wireless → Wireless Settings**.
2. Untick **Enable** for each band (2.4 GHz and 5 GHz). Click **Save**.

*Expected:* the 2.4 GHz and 5 GHz lights go dark, your phone no longer lists the
router's network name, and the wired laptop still has internet. (Verified, TP-Link
FAQ 2519: "Disabling Wi-Fi turns off the wireless signal only.")

*Also check:* the **Guest Network** and any **Wireless Schedule** are off. Holding
a button on the back of the AX4400 for more than 2 seconds turns Wi-Fi back on
(the user guide's timing; whether your unit has a separate Wi-Fi button or one
shared LED/Wi-Fi button was not confirmed), so label it.

### 4.3 Check the DHCP server

1. Go to **Advanced → Network → DHCP Server**. It must be **enabled**: in this lab
   the router is the **only** DHCP server.
2. Write down the **IP Address Pool** (example: `192.168.50.100`–`192.168.50.249`)
   and the **Default Gateway** (example: `192.168.50.1`, the router's own address).

**Why:** a phone joining the mesh broadcasts a DHCP Discover (RFC 2131). That
broadcast crosses port 1 to the router, so the sensor learns the device's MAC
address and name. If the mesh ran its own DHCP server, the sensor would never see it.

### 4.4 Reserve addresses for the switch and the sensor

1. **Advanced → Network → DHCP Server → Address Reservation → Add**.
2. Pick the device (or type its MAC address) and an address. Examples used in
   this guide: switch `192.168.50.2`, sensor management port `192.168.50.10`.
3. **Save**, then reconnect the device so it picks up the reserved address.

Do **not** switch the AX4400 to **Access Point** operation mode: the lab would lose
its only DHCP server and NAT.

### 4.5 Blocking on this router

The AX4400 has **Access Control** (Deny List / Allow List by MAC address),
Parental Controls and IP & MAC Binding, all in the web interface or the Tether
app. **No documented local API was found** (not verified with TP-Link — absence of
evidence only). So on this router MaxGuard *generates* the steps and a person
applies them; automatic blocking is demonstrated against OPNsense
(`docs/PROJECT_DECISIONS.md` section 4). An unofficial Python library exists
(`tplinkrouterc6u`), but it does not list the AX4400, has no blocking functions,
and is GPL-3.0-or-later, so it is not used.

## 5. Switch: TP-Link TL-SG105E port mirroring

**Not run — verify on hardware.** Menu names follow the current Easy Smart
web interface (hardware version 5 / 5.6).

### 5.1 Which hardware version do you have?

Turn the switch over and read the label (`Ver: 5.6`, for example). Version 1 can
only be configured with the Windows **Easy Smart Configuration Utility**;
version 2 and later also have a web interface. Download firmware **only** for
your exact hardware version. (Verified, TP-Link download pages.)

### 5.2 Log in

The switch's fallback address is `192.168.0.1` (mask `255.255.255.0`), user
`admin`, password `admin` (Verified). On current versions it first asks your
router for an address and uses 192.168.0.1 only if no DHCP server answers
(Likely: user-guide excerpts; the default may differ between hardware versions).

**Option A (recommended):** cable the switch into the lab, find it in the
router's DHCP client list (match the MAC address on the switch label), and open
`http://<that address>`.

**Option B (switch alone on your desk):** connect only your laptop (to port 2),
give the laptop the static address `192.168.0.2` / `255.255.255.0`, and open
`http://192.168.0.1`.

*Expected:* the **System Info** page with the hardware and firmware versions.
Write them down.

### 5.3 Change the password, then the address

1. **System → User Account**: set a strong password. Anyone who can reach the
   switch could otherwise turn mirroring off. The web interface uses plain HTTP
   (no HTTPS option was found in TP-Link's documentation), so manage it only from
   the trusted LAN.
2. **System → IP Setting**: keep **DHCP Setting: Enable** and use the reservation
   from section 4.4, or set a static address outside the router's pool (example
   `192.168.50.2`, mask `255.255.255.0`, gateway `192.168.50.1`).

### 5.4 Update the firmware

Back up first (**System → System Tools → Backup and Restore**), then upload the
file from tp-link.com for your hardware version in **System → System Tools →
Firmware Upgrade**. Do not unplug the switch while it upgrades. The newest
firmware seen in October 2026 for V5/V5.6 was `TL-SG105E(UN)_V5.6_1.0.0 Build
20250710`. Firmware from 2023 onwards changed the management protocol "to enhance
security", so if you use the Windows utility, use version 1.3.13.0 or newer.
(Verified, TP-Link download page excerpts. Older firmware had a published
unauthenticated-reboot flaw, CVE-2019-16893, shown on a version 4 unit in
Exploit-DB 47958, which is another reason to update.)

### 5.5 Mirror port 1 (both directions) to port 5

Two words first. The **mirrored** port is the one you watch (port 1, the router
uplink). The **mirroring** port receives the copies (port 5, the Pi). **Ingress**
copies packets the mirrored port *receives* (downloads, replies, DHCP offers);
**Egress** copies packets it *sends* (uploads, requests, DNS queries, DHCP
Discover). You need **both**.

1. Open **Monitoring → Port Mirror**.
2. Set **Port Mirror** to **Enable**, **Mirroring Port** to **Port 5**, click **Apply**.
3. Select **Port 1**, set **Ingress: Enable** and **Egress: Enable**, click **Apply**.
4. Leave ports 2, 3 and 4 with Ingress and Egress **disabled**.
5. Check the summary table: one row, Port 1, Ingress Enable, Egress Enable,
   mirroring port 5.

(Menu and settings: TP-Link FAQ 527 and the Easy Smart user guide. The FAQ lists
other models, so the exact layout on your unit is *likely*, not verified.)

**Two important limits:**

- **Port 5 is still a normal switch port.** Anything the Pi *sends* on port 5
  goes into the LAN. That is why section 8 makes the capture port completely
  silent (no IPv4, no IPv6, no link-local address).
- **Port 5 can send at most 1 Gbps.** Port 1 can carry up to 1 Gbps in *and*
  1 Gbps out. When both directions together exceed 1 Gbps, the switch drops some
  of the *copies* (your real traffic is not affected). With the switch's small
  buffer (about 1–1.5 Mbit, shared), even millisecond bursts above line rate can
  drop copies. Test 4 in section 12 measures this.

## 6. Mesh Wi-Fi in bridge (access point) mode

**Not run — verify on hardware.** A mesh system arrives set up as a *router*:
it runs its own DHCP server and hides every device behind its one address
(double NAT). For the sensor that is fatal: every phone and laptop would look
like the same device. In **bridge / access point** mode the mesh only passes
frames between Wi-Fi and the cable, and the AX4400 does the only NAT and DHCP.

1. Finish section 4 first (the router's DHCP must be on).
2. Plug the primary node's WAN/internet port into **switch port 2**.
3. Set up the mesh with its app as usual (it starts in router mode).
4. Switch the mode:

| Brand | Mode name | Steps (vendor help page) |
|---|---|---|
| TP-Link Deco | Access Point | Update the Decos first (**More → System → Update Deco**). Then Deco app → **More → Advanced → Operation Mode → Access Point → Save**, and tap **Reboot** to confirm; wait about 2 minutes for the solid green light. Satellites keep meshing. (Verified, TP-Link FAQ 1842.) |
| eero | Bridge | eero app → **Settings → Advanced networking → DHCP & NAT → Bridge**. One eero must stay wired. You lose Profiles and per-device blocking in the eero app. (Verified, eero Help.) |
| Google Nest Wifi / Google Wifi | Bridge mode | Google Home app → **Wifi → Settings → Advanced networking → Network mode → (your device) → Bridge mode → Save**. **Only works with a single Wifi device**; a multi-point Google mesh cannot be bridged. (Verified, Google Nest Help 6240987.) |

5. Reconnect your phone to the Wi-Fi.

**Check there is no double NAT:**

- The phone's IP address is in the AX4400's pool (example `192.168.50.x`) and its
  router/gateway is the AX4400 (example `192.168.50.1`). An address from another
  range (for example `192.168.86.x` or `192.168.68.x`) means the mesh is still routing.
- On a laptop on the mesh: `traceroute -n 1.1.1.1` (Windows: `tracert /d 1.1.1.1`).
  The **first** hop must be the AX4400.
- The AX4400's DHCP client list shows the phone and laptop as separate rows.

Phones use private, sometimes rotating Wi-Fi MAC addresses (iPhone: Settings →
Wi-Fi → ⓘ → Private Wi-Fi Address; Android 10+: randomized per network). For a
lab phone you want to recognize reliably, set it to **Fixed** (iPhone) and note
the address the router shows.

## 7. Raspberry Pi 5: power, cooling, and Raspberry Pi OS 64-bit

### 7.1 Hardware

**Not run — verify on hardware.**

1. Fit the Active Cooler on the Pi (it plugs into the 4-pin fan connector).
2. Put the SSD and the RTL8153 adapter in the two **blue USB 3** ports.
3. Use the 27 W supply.

After the first boot (section 7.3), check:

```bash
vcgencmd get_config usb_max_current_enable
vcgencmd get_throttled
```

Expected: a non-zero `usb_max_current_enable` (the 5 A supply was detected) and
`throttled=0x0` (no under-voltage). A non-zero value proves the supply only if
nobody forced the setting, so also run
`grep usb_max_current_enable /boot/firmware/config.txt`: it must print nothing.
If you see `usb_max_current_enable=0`, use the right supply; do not force the
setting in `config.txt`.

### 7.2 Flash the microSD card

The current Raspberry Pi OS is based on **Debian 13 "Trixie"** (Verified,
Raspberry Pi documentation). Use **Raspberry Pi OS Lite (64-bit)**: the sensor is
headless, and Docker no longer supports 32-bit Raspberry Pi OS after version 28.

1. On your laptop, make an SSH key (press Enter for the default file, and set a passphrase):

```bash
ssh-keygen -t ed25519 -C "maxguard sensor admin"
```

2. Install **Raspberry Pi Imager** from raspberrypi.com/software and open it.
3. **Device:** Raspberry Pi 5. **OS:** Raspberry Pi OS Lite (64-bit). **Storage:**
   your microSD card (keep *Exclude system drives* ticked).
4. **Customisation:**
   - Hostname `sensor-01`; user `sensoradmin` with a strong password; your time zone.
   - **Wi-Fi: leave it empty.** Imager pre-fills your laptop's network: delete it.
     The sensor must have exactly one management path. (Do not press *Skip
     customisation*: that skips the user and SSH settings too.)
   - **Remote access:** Enable SSH → *Use public key authentication* → paste the
     contents of `~/.ssh/id_ed25519.pub`.
5. **Write**, confirm, and wait for the verification to finish.

### 7.3 First boot and update

1. Insert the card. Plug the RTL8153 adapter into switch port 3. **Leave the
   onboard Ethernet unplugged for now.** Power on and wait a few minutes.
2. From your laptop:

```bash
ssh sensoradmin@sensor-01.local
cat /etc/os-release | grep VERSION_CODENAME
dpkg --print-architecture
sudo apt update && sudo apt full-upgrade -y && sudo reboot
```

Expected: `VERSION_CODENAME=trixie` and `arm64`. (`full-upgrade` is what Raspberry
Pi recommends; do not run `rpi-update`, which installs test firmware.)

## 8. Sensor networking: a management port and a silent capture port

Raspberry Pi OS uses **NetworkManager** (`nmcli`). **Not run — verify on
hardware;** every property name below was checked in the NetworkManager source.

### 8.1 Find the two ports

```bash
sudo apt install -y ethtool tcpdump jq
ip -br link
sudo ethtool -i eth0
sudo ethtool -i eth1
nmcli connection show
```

Expected: `eth0` is the onboard port (driver `macb`) and `eth1` the USB adapter
(driver `r8152`). If your adapter has another name, use that name below. Write
down the names of any existing Ethernet profiles.

### 8.2 Management port (eth1)

Use the DHCP reservation from section 4.4 (recommended):

```bash
sudo nmcli connection add type ethernet con-name sensor-mgmt ifname eth1 \
  ipv4.method auto connection.autoconnect yes
sudo nmcli connection up sensor-mgmt
```

If an older profile also claims `eth1`, stop it from starting:
`sudo nmcli connection modify "<old profile name>" connection.autoconnect no`.

### 8.3 Capture port (eth0): up, no IP, promiscuous, offloads off

You are logged in over `eth1`, so this is safe:

```bash
sudo nmcli connection add type ethernet con-name sensor-capture ifname eth0 \
  ipv4.method disabled \
  ipv6.method disabled \
  ethernet.accept-all-mac-addresses true \
  ethtool.feature-gro off \
  ethtool.feature-lro off \
  connection.autoconnect yes \
  connection.autoconnect-priority 100
sudo nmcli connection up sensor-capture
```

| Setting | Why |
|---|---|
| `ipv4.method disabled` | No IPv4 address: the Pi sends no DHCP or ARP from this port. |
| `ipv6.method disabled` | Use `disabled`, **not** `ignore`: with `ignore` NetworkManager still adds an IPv6 link-local address and the port could send neighbour-discovery packets into the mirror. |
| `ethernet.accept-all-mac-addresses true` | Promiscuous mode: accept frames addressed to *other* devices, which is all mirrored traffic is. |
| `ethtool.feature-gro off`, `...-lro off` | Stop the kernel from merging packets into "super packets". Suricata's documentation says GRO/LRO "break the dsize keyword as well as TCP state tracking"; Zeek recommends turning offloads off so it sees packets "as they arrive on the wire". |

If `nmcli connection up` fails with an ethtool error, the card may not allow
changing LRO: run `sudo nmcli connection modify sensor-capture ethtool.feature-lro ignore`
and bring it up again.

**Now plug `eth0` into switch port 5.**

### 8.4 Check the capture port (now and after a reboot)

```bash
ip -br addr show eth0
ip -d link show eth0 | grep -o 'PROMISC\|promiscuity [0-9]*'
sudo ethtool -k eth0 | grep -E '^(generic|large)-receive-offload:'
```

Expected: `eth0 UP` with **no** address after it; `PROMISC` and `promiscuity 1`;
both offload lines `off` (maybe `off [fixed]`). Reboot and check again: settings
that do not survive a reboot are the most common sensor bug.

**[SIM]** On a container interface with the same settings applied,
`ethtool -k` printed `generic-receive-offload: off` and
`large-receive-offload: off [fixed]`, and `ip -d link` showed `PROMISC` and
`promiscuity 1`.

## 9. USB SSD for the logs

**Not run — verify on hardware.** Zeek and Suricata write all the time and we
keep 7 days; the microSD card only holds the OS.

1. Find the SSD (usually `sda`; check the SIZE and MODEL — the next step erases it):

```bash
sudo lsblk -o UUID,NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,MODEL
```

2. Partition and format it:

```bash
sudo apt install -y parted
sudo parted --script /dev/sda mklabel gpt mkpart sensordata ext4 0% 100%
sudo mkfs.ext4 -L sensordata /dev/sda1
sudo blkid /dev/sda1
```

3. Copy the `UUID="..."` value, then `sudo mkdir -p /data` and `sudo nano /etc/fstab`,
   and add one line with **your** UUID (this one is made up):

```text
UUID=0b1c2d3e-1111-2222-3333-444455556666  /data  ext4  defaults,noatime,nofail,x-systemd.device-timeout=30  0  2
```

4. Check and mount:

```bash
sudo systemctl daemon-reload
sudo findmnt --verify
sudo mount -a
findmnt /data
```

Expected: `0 parse errors`, and `/data` on `/dev/sda1` (ext4). `nofail` lets the
Pi still boot (about 30 s slower) if the SSD dies, so you can SSH in and fix it;
`noatime` saves writes. Section 10.4 makes Docker refuse to start without the SSD.

**Sizing:** the event store needed about **60 bytes per event** (compressed
Parquet) in the planning measurements, plus about 3 KB per file: 100,000 events a
day is roughly 6 MB a day, 1 million is roughly 60 MB a day. Raw Zeek and Suricata
logs are much larger than the event store; measure your own network in the first
week. (Measured on x86 with synthetic events — not run on a Pi.)

## 10. Docker Engine on the Pi

For 64-bit Raspberry Pi OS, Docker's documentation says to follow the **Debian**
instructions (Verified). **Not run on a Pi;** the repository commands were checked
in an arm64 Debian 13 container.

### 10.1 Add Docker's repository and install

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Check: `cat /etc/apt/sources.list.d/docker.sources` shows `Suites: trixie` and
`Architectures: arm64`. (In planning, Docker's Debian 13 arm64 repository offered
`docker-ce 5:29.8.2-1~debian.13~trixie`.)

### 10.2 Run Docker without sudo

```bash
sudo usermod -aG docker $USER
exit
```

SSH back in, then:

```bash
docker run --rm hello-world
docker info --format '{{.Architecture}}'
```

Expected: `Hello from Docker!` and `aarch64`. Docker warns that the `docker` group
is root-equivalent: only the admin account belongs in it.

### 10.3 Rotate container logs

Docker's default log driver never rotates. Create `/etc/docker/daemon.json`:

```json
{
  "log-driver": "local"
}
```

```bash
sudo dockerd --validate --config-file /etc/docker/daemon.json
sudo systemctl restart docker
```

Expected: `configuration OK`. (This exact file was validated with Docker 29.6.2 in planning.)

### 10.4 Do not start without the SSD

```bash
sudo systemctl edit docker
```

Add, save, and exit:

```ini
[Unit]
RequiresMountsFor=/data
```

**Why:** with `nofail`, a missing SSD leaves `/data` as an empty folder on the
microSD card, and the sensor would quietly fill the card. With this line Docker
does not start without the SSD: a stopped sensor is easy to notice, a full card is not.

## 11. Zeek and Suricata on ARM64

You do not compile anything: the official Zeek image and the Suricata image
maintained by Suricata developer Jason Ish are published for `linux/arm64`, so
the Pi pulls the right version automatically.

| Image | Version | arm64 | Why this version |
|---|---|---|---|
| `zeek/zeek:9.0.0` | Zeek 9.0.0 | yes | Same version the engine uses (`lts` pointed to 9.0.0 on Oct 6, 2026) |
| `jasonish/suricata:8.0.7` | Suricata 8.0.7 | yes | A sensor parses untrusted traffic all day, so it runs a supported branch: OISF ended the 7.0 branch in July 2026 (7.0.17 was its last release). JA4 is built in. |

**[SIM]** Both images were checked on Docker Hub and started under arm64
emulation in planning (`zeek version 9.0.0`; `This is Suricata version 8.0.7
RELEASE` with `AF_PACKET support: yes` and `JA4 support: yes`; `uname -m` →
`aarch64`).

### 11.1 Pull and check the versions

```bash
docker pull zeek/zeek:9.0.0
docker pull jasonish/suricata:8.0.7
docker run --rm zeek/zeek:9.0.0 zeek --version
docker run --rm jasonish/suricata:8.0.7 suricata -V
```

Expected:

```text
zeek version 9.0.0
This is Suricata version 8.0.7 RELEASE
```

(Both lines were printed in planning, the Suricata one by the arm64 image under
emulation; not run on a Pi.)

### 11.2 One-minute Zeek capture on the mirror port

```bash
sudo mkdir -p /data/smoke/zeek && sudo chown $USER /data/smoke/zeek
docker run --rm --network host --cap-add NET_RAW --cap-add NET_ADMIN \
  -v /data/smoke/zeek:/logs -w /logs zeek/zeek:9.0.0 \
  timeout 60 zeek -i eth0 -C LogAscii::use_json=T misc/capture-loss misc/stats
ls /data/smoke/zeek
```

`misc/capture-loss` and `misc/stats` add the two logs that show lost packets.
Do **not** add Zeek's own `local` policy here or anywhere else: it loads scripts
that send DNS queries to the internet, one of them about every file people
download (`docs/ARCHITECTURE.md` section 12). MaxGuard loads its own copy
without them, `maxguard/zeek/site.zeek`.

While it runs, browse a few websites on a phone on the mesh Wi-Fi.

Expected: after 60 seconds Zeek stops and prints a line like
`736 packets received on interface eth0, 0 (0.00%) dropped, 0 (0.00%) not processed`,
and the folder contains `conn.log`, `capture_loss.log`, `stats.log` and, from
the phone's traffic, `dns.log`, `ssl.log` and others. **[SIM]** The line above
is from the planning simulation, where Zeek listened on a web server
container's interface while another container fetched pages (it wrote
`conn.log`, `http.log`, `files.log`, `capture_loss.log`, `stats.log`,
`packet_filter.log` and `reporter.log`).

What the options do: `--network host` lets the container see the Pi's real `eth0`;
`NET_RAW` and `NET_ADMIN` are the two capabilities Zeek needs to capture; `-i eth0`
listens live; `timeout 60` stops it cleanly so it writes its logs. **No `-D` here:**
that option (used for capture *files* so results repeat exactly) also removes
Zeek's protection against deliberate hash-table slow-downs, so a live sensor never uses it.

### 11.3 One-minute Suricata capture on the mirror port

**Not run — verify on hardware.** Suricata's documentation says a container
needs three capabilities to capture: `NET_ADMIN`, `NET_RAW`, and `SYS_NICE`
(Verified, Suricata user guide, *Packet capture*). This smoke test uses the
image's own default settings; MaxGuard's live settings (Community ID, JA4, log
rotation) come with the live sensor in JAK-07.

```bash
sudo mkdir -p /data/smoke/suricata
docker run -d --name suricata-smoke --network host \
  --cap-add NET_ADMIN --cap-add NET_RAW --cap-add SYS_NICE \
  -v /data/smoke/suricata:/var/log/suricata \
  jasonish/suricata:8.0.7 -i eth0
sleep 60
docker stop suricata-smoke
docker logs suricata-smoke 2>&1 | tail -n 5
docker rm suricata-smoke
sudo ls /data/smoke/suricata
sudo jq -r .event_type /data/smoke/suricata/eve.json | sort | uniq -c
```

While it runs, browse a few websites on a phone on the mesh Wi-Fi.

Expected: the last log lines include a capture summary for `eth0` with a packet
count above zero and its drops (something like `packets: 5120, drops: 0
(0.00%)`; the exact wording differs between versions); the folder holds
`eve.json`, `fast.log`, `stats.log` and `suricata.log`; and the last command
counts `flow`, `dns`, `tls` and `http` events. `docker stop` sends Suricata the
signal to shut down cleanly, which is when it prints the capture summary.

**Why an early planning test saw 0 packets (solved).** In the first planning
test, Suricata reported **0 packets** on a container's network interface where
Zeek, in the same setup, captured 449. The cause was the image, not the
capture: `jasonish/suricata:7.0.17`, used then, ships the ET Open rule set
(53,021 rules), loading it took about 50 seconds on a 4-core x86 machine, and
Suricata captures nothing until its rules are loaded. Those tests stopped after
18–20 seconds. With no rules (`-S /dev/null`) the same image started capturing
in under a second (241 packets in 20 seconds). `jasonish/suricata:8.0.7` ships
no rule file, so the command above starts in about a second; in planning it
captured 738 packets in 60 seconds on a container's interface (**[SIM]**). On the
Pi, loading a large rule set takes longer still: wait for `Engine started` in
the log before you test. If the Pi still reports zero packets:

1. Make sure test 1 in section 12 passes with `tcpdump` (so the mirror works).
2. Read `sudo grep -iE "af-packet|error" /data/smoke/suricata/suricata.log`.
3. Try libpcap capture instead of AF_PACKET: replace `-i eth0` with `--pcap=eth0`.
4. Post the commands and output in GitHub Discussions (category *Q&A*), and fix
   this section in your pull request once you know what works.

The full sensor (both tools running all the time, logs shipped to the console
every 15 minutes) is task **JAK-07** in `docs/roadmap/jakub.md` and uses
`docker/sensor-compose.yaml`.

## 12. Prove the mirror works (five tests)

Run these after sections 4–11. Keep the results: test 4's table goes into this
file in your pull request. Example addresses: phone `192.168.50.23`, laptop
`192.168.50.30`, router `192.168.50.1`, sensor management `192.168.50.10`.

> **Avoid a feedback loop:** SSH into the Pi from a device on the **mesh Wi-Fi**.
> Traffic from the mesh (port 2) to the Pi (port 3) is not mirrored. An SSH
> session from a device plugged into the router would be mirrored, printed by
> tcpdump, mirrored again... (or add `and not port 22` to every filter).

### Test 1 — both directions of one phone's traffic

**Not run — verify on hardware.**

1. Find the phone's IP address (router client list, or the phone's Wi-Fi details).
2. On the Pi:

```bash
sudo tcpdump -i eth0 -nn -e -c 50 host 192.168.50.23
```

3. Open and refresh a website on the phone.

Expected: lines in **both** directions — the phone's address on the left of `>`
in some lines and on the right in others, including a `Flags [S]` from the phone
and a `Flags [S.]` back. **[SIM]** (simulated router, not the Pi; trimmed):

```text
66:c0:21:e7:d6:5e > ea:7a:2f:ae:ed:88, ethertype IPv4 (0x0800), length 74: 192.168.50.23.40838 > 203.0.113.10.80: Flags [S], ...
ea:7a:2f:ae:ed:88 > 66:c0:21:e7:d6:5e, ethertype IPv4 (0x0800), length 74: 203.0.113.10.80 > 192.168.50.23.40838: Flags [S.], ...
```

Then use this helper, which counts each direction and ignores broadcast frames
(a switch floods those to every port even with mirroring **off**, so they would
make a broken mirror look half-working). Save it on the Pi as
`~/mirror-direction-check.sh` and run `chmod +x ~/mirror-direction-check.sh`:

```bash
#!/usr/bin/env bash
# mirror-direction-check.sh — does the sensor see BOTH directions of one device's traffic?
# Usage: sudo ./mirror-direction-check.sh IFACE DEVICE_IP [SECONDS]
set -euo pipefail

IFACE="${1:?usage: $0 IFACE DEVICE_IP [SECONDS]}"
DEVICE="${2:?usage: $0 IFACE DEVICE_IP [SECONDS]}"
SECS="${3:-30}"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
PCAP="$WORKDIR/check.pcap"

echo "Capturing ${SECS}s of traffic to/from ${DEVICE} on ${IFACE}."
echo "Now load a website on that device (refresh it a few times)."
# -Z root: some tcpdump builds drop root before writing the file.
# "not ether multicast" also drops broadcasts (ARP, DHCP Discover, mDNS).
timeout "$SECS" tcpdump -i "$IFACE" -nn -Z root -w "$PCAP" \
  "host ${DEVICE} and not ether multicast" 2>/dev/null || true

FROM=$(tcpdump -nn -r "$PCAP" "src host ${DEVICE}" 2>/dev/null | wc -l)
TO=$(tcpdump -nn -r "$PCAP" "dst host ${DEVICE}" 2>/dev/null | wc -l)

echo "Unicast packets FROM ${DEVICE} (switch port 1 Egress copies):  ${FROM}"
echo "Unicast packets TO   ${DEVICE} (switch port 1 Ingress copies): ${TO}"

if [ "$FROM" -gt 0 ] && [ "$TO" -gt 0 ]; then
  echo "PASS: both directions are reaching the sensor."
elif [ "$FROM" -gt 0 ]; then
  echo "FAIL: only traffic FROM the device. Check that Ingress is enabled on port 1."
  exit 1
elif [ "$TO" -gt 0 ]; then
  echo "FAIL: only traffic TO the device. Check that Egress is enabled on port 1."
  exit 1
else
  echo "FAIL: nothing seen. Check the device IP, the cable to port 5, and that Port Mirror is enabled."
  exit 1
fi
```

```bash
sudo ~/mirror-direction-check.sh eth0 192.168.50.23 30
```

**[SIM]** with the mirror "on", then with the sensor on an ordinary port:

```text
Unicast packets FROM 192.168.50.23 (switch port 1 Egress copies):  24
Unicast packets TO   192.168.50.23 (switch port 1 Ingress copies): 21
PASS: both directions are reaching the sensor.

Unicast packets FROM 192.168.50.23 (switch port 1 Egress copies):  0
Unicast packets TO   192.168.50.23 (switch port 1 Ingress copies): 0
FAIL: nothing seen. Check the device IP, the cable to port 5, and that Port Mirror is enabled.
```

A one-way mirror also shows in Zeek's `conn.log` (from section 11.2). MaxGuard
writes Zeek logs as JSON, so read them with `jq` (Zeek's own `zeek-cut` only
reads the tab-separated format and prints blank lines for JSON):

```bash
jq -c '{"id.orig_h", "id.resp_h", "id.resp_p", conn_state, history, orig_pkts, resp_pkts}' /data/smoke/zeek/conn.log | head
```

Healthy (**[SIM]**): `"conn_state":"SF","history":"ShADadfF","orig_pkts":6,"resp_pkts":6`.
One-way mirror: `conn_state` `SH` or `S0`, `resp_pkts` 0, and no lower-case
letters in `history`, on every connection.

### Test 2 — DNS query and answer

**Not run — verify on hardware.** On the Pi:
`sudo tcpdump -i eth0 -nn -l port 53 and host 192.168.50.30`. On the laptop on
the mesh: `dig @192.168.50.1 example.com A` (Windows: `nslookup example.com 192.168.50.1`).

Expected: a query and an answer with the **same ID**. **[SIM]**:

```text
IP 192.168.50.23.51148 > 192.168.50.1.53: 64703+ [1au] A? www.example.com. (56)
IP 192.168.50.1.53 > 192.168.50.23.51148: 64703 1/0/0 A 203.0.113.10 (49)
```

Query only = Ingress is off; answer only = Egress is off. (Phones and browsers
may use encrypted DNS, which the sensor cannot read; asking the router directly
forces plain DNS for this test.)

### Test 3 — DHCP when a device joins

**Not run — verify on hardware.** On the Pi:
`sudo tcpdump -i eth0 -nn -e -v -l 'udp port 67 or udp port 68'` (the filter
was compiled with `tcpdump -d` in planning). On the phone,
*forget* the Wi-Fi network and join it again.

Expected: `Discover`, `Offer`, `Request`, `ACK` (or just `Request` and `ACK`), with
the device's `Hostname` if it sends one. **This test alone does not prove
mirroring:** Discover and Request are broadcasts that reach every port. An
`Offer` or `ACK` sent to the device's own MAC address (not `ff:ff:ff:ff:ff:ff`)
does prove the Ingress copy works.

### Test 4 — throughput and loss (record the Pi's limit)

**Not run — verify on hardware.** This finds the rate where loss starts and
where it happens. Machine A (iperf3 server, example `192.168.50.60`) goes in a
spare **router** LAN port and machine B (client, `192.168.50.61`) in **switch
port 4**, so the test traffic crosses port 1. Use wired gigabit Linux or macOS
machines, not the Pi. Unplug both afterwards.

Zeek normally reports loss every 15 minutes. For this test, save this file as
`~/mirror-test-timing.zeek` so every stage gets its own report:

```zeek
# mirror-test-timing.zeek: for the throughput test only
redef CaptureLoss::watch_interval = 1min;
redef Stats::report_interval = 1min;
```

Then run Zeek for the whole test (about 25 minutes) with that file added.
Start Suricata too, as in section 11.3 but writing to `/data/test4/suricata`,
and stop it after stage 5:

```bash
sudo mkdir -p /data/test4/zeek && sudo chown $USER /data/test4/zeek
docker run --rm --network host --cap-add NET_RAW --cap-add NET_ADMIN \
  -v /data/test4/zeek:/logs -w /logs \
  -v ~/mirror-test-timing.zeek:/extra/mirror-test-timing.zeek:ro \
  zeek/zeek:9.0.0 timeout 1500 zeek -i eth0 -C LogAscii::use_json=T \
    misc/capture-loss misc/stats /extra/mirror-test-timing.zeek
```

(The two `misc/` scripts must come before the file, because the file changes
their settings. It parses with
`zeek -a misc/capture-loss misc/stats /extra/mirror-test-timing.zeek` on Zeek
9.0.0 — run in planning.)

On A: `iperf3 -s`. On B, one stage at a time (3 minutes each, 1 minute apart):

| Stage | Command on B | Each way | Mirror load (estimate) | Expect |
|---|---|---|---|---|
| 1 | `iperf3 -c 192.168.50.60 -t 180 -b 100M --bidir` | 100 Mbit/s | ~212 Mbit/s | no loss |
| 2 | `... -b 250M --bidir` | 250 Mbit/s | ~531 Mbit/s | the Pi may or may not keep up |
| 3 | `... -b 400M --bidir` | 400 Mbit/s | ~850 Mbit/s | near the mirror limit |
| 4 | `... -b 450M --bidir` | 450 Mbit/s | ~956 Mbit/s | at the limit; bursts may drop |
| 5 | `... -b 600M --bidir` | 600 Mbit/s | ~1,275 Mbit/s | **must** show loss (the switch has to drop about a fifth of the copies) |

The mirror load is about `2 × rate × 1.062` (both directions, plus Ethernet
overhead). **Stage 5 proves the sensor notices loss: if it shows zero loss, the
measurement is wrong.**

Record, before and after each stage:

| Where | How | What it tells you |
|---|---|---|
| Switch | **Monitoring → Port Statistics**: port 1 RX+TX, port 5 TX | Port 5 sending fewer packets than port 1 carried = **switch** dropped copies |
| Pi card | `ip -s link show eth0`: RX `dropped`, `missed` | the network card or driver dropped packets |
| Suricata | `capture.kernel_packets`, `capture.kernel_drops` in its `stats.log` (missing line = 0) | Suricata was too slow; loss % = drops ÷ packets × 100 |
| Zeek | `jq -c '{ts, pkts_proc, pkts_dropped, pkts_link}' /data/test4/zeek/stats.log` | Zeek was too slow |
| Zeek | `jq -c '{ts, gaps, acks, percent_lost}' /data/test4/zeek/capture_loss.log` | loss **anywhere** before Zeek, including the switch (TCP only) |

**[SIM]** The `jq` lines print, for example,
`{"ts":1791255745.942278,"pkts_proc":448,"pkts_dropped":0,"pkts_link":448}` and
`{"ts":1791255745.942278,"gaps":0,"acks":111,"percent_lost":0.0}`.

**`percent_lost` is not "percent of packets lost".** It is the share of TCP
acknowledgements whose data was never seen, and one ACK covers many packets.
**[SIM]** Deleting every 50th packet (2.0%) from a capture made Zeek report
`percent_lost` between 26.7 and 60.9, while `conn.log`'s `missed_bytes` showed
2.0% of bytes missing. Treat `percent_lost` as an alarm that must be **0.0** and use
`missed_bytes` to size the loss.

Fill this in and commit it with your pull request:

| Stage | Each way | iperf3 Retr | Port 1 RX+TX | Port 5 TX | `ip -s link` dropped | Suricata drop % | Zeek `pkts_dropped` | Zeek `percent_lost` |
|---|---|---|---|---|---|---|---|---|
| 1 | 100M | | | | | | | |
| 2 | 250M | | | | | | | |
| 3 | 400M | | | | | | | |
| 4 | 450M | | | | | | | |
| 5 | 600M | | | | | | | |

### Test 5 — mirror off: the Pi sees only broadcasts

**Not run — verify on hardware.**

1. On the switch, set **Port Mirror** to **Disable** and **Apply**.
2. On the Pi, while the phone browses:

```bash
sudo timeout 60 tcpdump -i eth0 -nn -e
sudo timeout 60 tcpdump -i eth0 -nn -e 'not ether multicast'
sudo ~/mirror-direction-check.sh eth0 192.168.50.23 30
```

Expected: the first command shows only broadcast/multicast frames (ARP requests,
DHCP, mDNS); the second shows nothing or almost nothing; the script prints FAIL.
**[SIM]**: 7 broadcast frames in 25 seconds, and `0 packets` for unicast.

3. Turn mirroring back on (port 5 mirroring, port 1 Ingress + Egress, **Apply**)
   and run test 1 again: it must PASS.

You should **never** see the Pi's own `eth0` MAC address as a source in any test.
If you do, the capture port is not silent: go back to section 8.

## 13. Known limits

These come from `docs/PROJECT_DECISIONS.md` section 4, plus what planning found.
Tell users about them.

- Copper Ethernet up to 1 Gbps only; faster links run at 1 Gbps through this switch.
- The mirror drops copies when both directions together exceed 1 Gbps, including
  short bursts. A 500/500 Mbps connection fits on average with no headroom.
- **Wi-Fi to Wi-Fi traffic on the same mesh is invisible** (the mesh relays it
  over the air). **Traffic between two devices plugged into the switch** (for
  example port 2 to port 4) does not cross port 1 and is invisible too.
  Optionally mirror port 2 as well: you would see Wi-Fi ↔ wired traffic, but
  internet traffic would then be copied twice and hit the 1 Gbps ceiling sooner
  (not tested).
- Devices using encrypted DNS hide their DNS names from the sensor.
- The sensor sees its **own** management traffic (it leaves through port 1);
  filter out the management address if it gets in the way.
- A Raspberry Pi 5 is a small-network sensor; test 4 records its real limit.
  For a company rack, use the company's mirror ports or a proper TAP and run the
  sensor on a mini PC or server (same software, `linux/amd64` images).
- The Archer AX4400 has no local blocking API; blocks are applied by hand there.

## 14. Troubleshooting

| Symptom | Most likely cause | Fix |
|---|---|---|
| Test 1: FROM > 0, TO = 0 | Port 1 Ingress disabled | Section 5.5 step 3 |
| Test 1: TO > 0, FROM = 0 | Port 1 Egress disabled | Section 5.5 step 3 |
| Only broadcasts | Mirroring off, wrong mirroring port, or Pi in the wrong port | Section 5.5, cabling in section 3 |
| Nothing at all | `eth0` down or wrong interface | `ip -br link`, `nmcli connection up sensor-capture` |
| Every phone shows the same IP | Mesh in router mode (double NAT) | Section 6 |
| A phone's traffic is missing | It uses IPv6, or its private MAC changed | Filter by `ether host <MAC>`; set the phone's private address to Fixed |
| `eth0` has an `inet6 fe80::` address | `ipv6.method ignore` instead of `disabled` | Section 8.3 |
| `throttled=0x50005` or similar | Under-voltage | Use the 27 W supply |
| Docker will not start | `/data` not mounted (by design) | Check the SSD: `findmnt /data`, `dmesg` |
| Zeek writes `percent_lost` > 0 at low rates | Offloads on, or the switch is overloaded | Section 8.4 checks; test 4 |
| Suricata reports `packets: 0` but tcpdump sees traffic | Capture mode or missing capability | Section 11.3, "A problem to watch for" |

## References

Raspberry Pi Ltd. (2026). *Raspberry Pi documentation* [Power supply; Frequency management and thermal control; Raspberry Pi OS; Configuring networking; External storage]. https://www.raspberrypi.com/documentation/

Docker Inc. (2026). *Install Docker Engine on Debian*. https://docs.docker.com/engine/install/debian/

Docker Inc. (2026). *Raspberry Pi OS (32-bit)* [Install Docker Engine]. https://docs.docker.com/engine/install/raspberry-pi-os/

Docker Inc. (2026). *Local file logging driver*. https://docs.docker.com/engine/logging/drivers/local/

Exploit Database. (2020). *TP-Link TP-SG105E 1.0.0 - Unauthenticated remote reboot* (EDB-ID 47958; CVE-2019-16893). https://www.exploit-db.com/exploits/47958

Google. (n.d.). *Bridge mode* (Google Nest Help 6240987). https://support.google.com/googlenest/answer/6240987

eero. (n.d.). *What is bridge mode?* https://eero.com/support/articles/what-is-bridge-mode

NetworkManager project. (2026). *nm-settings-nmcli*. https://networkmanager.dev/docs/api/latest/nm-settings-nmcli.html

Open Information Security Foundation. (2026). *Packet capture* (Suricata user guide). https://docs.suricata.io/en/latest/performance/packet-capture.html

Open Information Security Foundation. (2026). *Statistics* (Suricata user guide). https://docs.suricata.io/en/latest/performance/statistics.html

Open Information Security Foundation. (2026). *ChangeLog* (Suricata 7.0.17). https://github.com/OISF/suricata/blob/suricata-7.0.17/ChangeLog

Microsoft. (2025). *tracert* (Windows commands). https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tracert

The Tcpdump Group. (n.d.). *tcpdump(1) manual page*. https://www.tcpdump.org/manpages/tcpdump.1.html

TP-Link. (n.d.). *How to configure Port Mirror on TP-Link Easy Smart switches* (FAQ 527). https://www.tp-link.com/us/support/faq/527/

TP-Link. (n.d.). *How to set up Deco in Access Point mode* (FAQ 1842). https://www.tp-link.com/us/support/faq/1842/

TP-Link. (2022). *Archer AX4400 user guide* (REV2.6.0). https://www.tp-link.com/us/support/download/archer-ax4400/

TP-Link. (2025). *TL-SG105E download page* (firmware V5.6). https://www.tp-link.com/us/support/download/tl-sg105e/

Zeek Project. (2026). *capture-loss.zeek* (Zeek 9.0.0 script reference). https://docs.zeek.org/en/master/scripts/policy/misc/capture-loss.zeek.html

Zeek Project. (2026). *Cluster configuration* [offloading]. https://docs.zeek.org/en/master/cluster-setup.html
