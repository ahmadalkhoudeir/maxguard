"""Runs inside the private sensor namespace (netshoot image, scapy). Sends frames into
tap0, so they arrive at cap0, the capture port. Synthetic data only:
the repository's test captures and probes with RFC 5737 / RFC 3849 addresses."""
import glob
import sys

from scapy.all import ARP, ICMP, IP, Ether, TCP, UDP, BOOTP, DHCP, IPv6, ICMPv6EchoRequest, rdpcap, sendp
from scapy.layers.inet6 import ICMPv6ND_NS, ICMPv6ND_RA

cap0_mac = sys.argv[1]
peer = "02:00:00:00:00:01"
total = 0
for path in sorted(glob.glob("/pcaps/*.pcap")):
    frames = []
    for p in rdpcap(path):
        if not p.haslayer(Ether):
            continue
        # The test captures come from a Docker bridge (checksum offload): recompute the
        # checksums so Suricata inspects them like real mirrored traffic.
        for layer in (IP, TCP, UDP):
            if p.haslayer(layer) and hasattr(p[layer], "chksum"):
                del p[layer].chksum
        frames.append(Ether(bytes(p)))
    sendp(frames, iface="tap0", verbose=False)
    total += len(frames)
print(f"replayed {total} frames from {len(glob.glob('/pcaps/*.pcap'))} test captures")

probes = [
    ("ARP who-has 198.51.100.20 (the management address), broadcast",
     Ether(src=peer, dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, hwsrc=peer, psrc="198.51.100.1",
                                                    pdst="198.51.100.20")),
    ("ICMP echo to 198.51.100.20, sent to cap0's MAC",
     Ether(src=peer, dst=cap0_mac) / IP(src="198.51.100.1", dst="198.51.100.20") / ICMP()),
    ("TCP SYN to 198.51.100.20:22, sent to cap0's MAC",
     Ether(src=peer, dst=cap0_mac) / IP(src="198.51.100.1", dst="198.51.100.20") / TCP(dport=22, flags="S")),
    ("DHCP offer broadcast",
     Ether(src=peer, dst="ff:ff:ff:ff:ff:ff") / IP(src="198.51.100.1", dst="255.255.255.255")
     / UDP(sport=67, dport=68) / BOOTP(op=2, yiaddr="198.51.100.77", chaddr=bytes.fromhex(cap0_mac.replace(":", "")))
     / DHCP(options=[("message-type", "offer"), "end"])),
    ("IPv6 echo to ff02::1 (all nodes)",
     Ether(src=peer, dst="33:33:00:00:00:01") / IPv6(src="fe80::1", dst="ff02::1") / ICMPv6EchoRequest()),
    ("IPv6 router advertisement",
     Ether(src=peer, dst="33:33:00:00:00:01") / IPv6(src="fe80::1", dst="ff02::1") / ICMPv6ND_RA()),
    ("IPv6 neighbor solicitation for 2001:db8::20",
     Ether(src=peer, dst="33:33:ff:00:00:20") / IPv6(src="fe80::1", dst="ff02::1:ff00:20")
     / ICMPv6ND_NS(tgt="2001:db8::20")),
]
for label, frame in probes:
    sendp(frame, iface="tap0", count=3, inter=0.2, verbose=False)
    print(f"sent 3x {label}")
