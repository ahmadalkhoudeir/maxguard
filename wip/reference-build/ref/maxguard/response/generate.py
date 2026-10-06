"""Firewall commands for blocking one IP address, with their undo (Ahmad, AHM-07).

CLAUDE.md rule 4: blocking is defensive only, needs a person's approval, and must
be reversible. This module only *writes text*: it never runs a command and never
sends anything toward the address. A person (or an approved Enforcer) uses it.

Safety: the address is parsed with Python's ipaddress module and only the parsed
address is ever put into a command. Anything that is not a plain IP address, such
as "1.2.3.4; rm -rf /", raises ValueError before a command is built.

What "direction" means (the same in the preview, so the numbers match):
- inbound:  connections the address starts toward us (it is the originator),
- outbound: connections we start toward the address,
- both:     either of them.
The rules match the connection's *original* direction (conntrack), so an
inbound-only block still lets our own connections to that address work.

nftables keeps blocked addresses in named sets, so blocking and undoing are one
command each. A set holds one address family, so there is one set per direction
and family: maxguard_block_in_v4, maxguard_block_in_v6, maxguard_block_out_v4,
maxguard_block_out_v6. NFT_SETUP creates them once (safe to run again: it keeps
the addresses already in the sets).
"""

from __future__ import annotations

import ipaddress

DIRECTIONS = ("inbound", "outbound", "both")
NFT_TABLE = "inet maxguard"
LIMITED_BROADCAST = ipaddress.ip_address("255.255.255.255")

# Run once on the Linux firewall with:  sudo nft -f maxguard-setup.nft
# "add" does nothing when the table, set or chain exists already; "flush chain"
# then removes the old rules so running the file twice never doubles them.
NFT_SETUP = """\
add table inet maxguard
add set inet maxguard maxguard_block_in_v4 { type ipv4_addr; }
add set inet maxguard maxguard_block_in_v6 { type ipv6_addr; }
add set inet maxguard maxguard_block_out_v4 { type ipv4_addr; }
add set inet maxguard maxguard_block_out_v6 { type ipv6_addr; }
add chain inet maxguard input { type filter hook input priority filter; policy accept; }
add chain inet maxguard forward { type filter hook forward priority filter; policy accept; }
add chain inet maxguard output { type filter hook output priority filter; policy accept; }
flush chain inet maxguard input
flush chain inet maxguard forward
flush chain inet maxguard output
add rule inet maxguard input ct original ip saddr @maxguard_block_in_v4 drop
add rule inet maxguard input ct original ip6 saddr @maxguard_block_in_v6 drop
add rule inet maxguard forward ct original ip saddr @maxguard_block_in_v4 drop
add rule inet maxguard forward ct original ip6 saddr @maxguard_block_in_v6 drop
add rule inet maxguard forward ct original ip daddr @maxguard_block_out_v4 drop
add rule inet maxguard forward ct original ip6 daddr @maxguard_block_out_v6 drop
add rule inet maxguard output ct original ip daddr @maxguard_block_out_v4 drop
add rule inet maxguard output ct original ip6 daddr @maxguard_block_out_v6 drop
"""

# OPNsense: one firewall alias per direction (an alias holds IPv4 and IPv6).
OPNSENSE_ALIASES = {"inbound": "maxguard_block_in", "outbound": "maxguard_block_out"}


def parse_ip(text: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """Parse one address the user typed, or raise ValueError saying why not."""
    if not isinstance(text, str):
        # ip_address(16909060) would quietly mean 1.2.3.4
        raise ValueError("the IP address must be text")
    ip = ipaddress.ip_address(text)  # "1.2.3.4; rm -rf /" raises ValueError here
    if getattr(ip, "scope_id", None):
        # "2001:db8::1%$(id)" is a valid address with a scope: refuse the scope.
        raise ValueError(f"{text!r}: an address with a %scope cannot be blocked")
    if getattr(ip, "ipv4_mapped", None):
        raise ValueError(f"{text!r}: write the IPv4 address {ip.ipv4_mapped} instead")
    refuse_special(ip)
    return ip


def refuse_special(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    """Blocking these would cut off this machine or the whole network segment."""
    if ip.is_loopback:
        raise ValueError(f"{ip} is a loopback address (this machine)")
    if ip.is_multicast:
        raise ValueError(f"{ip} is a multicast address")
    if ip.is_unspecified:
        raise ValueError(f"{ip} is the unspecified address")
    if ip.is_link_local:
        raise ValueError(f"{ip} is a link-local address")
    if ip == LIMITED_BROADCAST:
        raise ValueError(f"{ip} is the broadcast address")


def check_direction(direction: str) -> str:
    if direction not in DIRECTIONS:
        raise ValueError(f"direction must be one of {', '.join(DIRECTIONS)}")
    return direction


def sides(direction: str) -> list[str]:
    """'both' -> ['inbound', 'outbound']; the others stay as they are."""
    return ["inbound", "outbound"] if direction == "both" else [direction]


def rules_for(ip: str, direction: str) -> dict:
    """All the ways to block ip (and undo it): nftables, iptables, OPNsense, home router."""
    address = parse_ip(ip)
    check_direction(direction)
    return {
        "ip": str(address),
        "version": address.version,
        "direction": direction,
        "nftables": nftables_rules(address, direction),
        "iptables": iptables_rules(address, direction),
        "opnsense": opnsense_steps(address, direction),
        "home_router": home_router_steps(address, direction),
    }


def nft_set_name(side: str, version: int) -> str:
    short = "in" if side == "inbound" else "out"
    return f"maxguard_block_{short}_v{version}"


def nftables_rules(ip, direction: str) -> dict:
    block, undo = [], []
    for side in sides(direction):
        target = f"{NFT_TABLE} {nft_set_name(side, ip.version)} {{ {ip} }}"
        # One quoted argument, so the shell never interprets the braces.
        block.append(f"sudo nft 'add element {target}'")
        undo.append(f"sudo nft 'delete element {target}'")
    return {"setup": NFT_SETUP, "block": block, "undo": undo}


def iptables_rules(ip, direction: str) -> dict:
    program = "iptables" if ip.version == 4 else "ip6tables"
    matches = []
    for side in sides(direction):
        if side == "inbound":   # connections the address starts
            matches += [("INPUT", f"--ctorigsrc {ip}"), ("FORWARD", f"--ctorigsrc {ip}")]
        else:                   # connections we start toward the address
            matches += [("OUTPUT", f"--ctorigdst {ip}"), ("FORWARD", f"--ctorigdst {ip}")]
    rule = "-m conntrack {match} -m comment --comment maxguard -j DROP"
    block = [f"sudo {program} -I {chain} {rule.format(match=m)}" for chain, m in matches]
    undo = [f"sudo {program} -D {chain} {rule.format(match=m)}" for chain, m in matches]
    return {"block": block, "undo": undo}


def opnsense_steps(ip, direction: str) -> dict:
    block, undo = [], []
    for side in sides(direction):
        alias = OPNSENSE_ALIASES[side]
        block.append(f"Firewall > Aliases: add {ip} to the content of the alias {alias}, "
                     "click Save, then Apply.")
        undo.append(f"Firewall > Aliases: remove {ip} from the alias {alias}, "
                    "click Save, then Apply.")
    setup = [
        "Once: Firewall > Aliases: create the aliases maxguard_block_in and "
        "maxguard_block_out, type Host(s), empty.",
        "Once: Firewall > Rules > WAN: a Block rule with source maxguard_block_in "
        "(stops connections an address on the internet starts).",
        "Once: Firewall > Rules > LAN: a Block rule with source maxguard_block_in "
        "(stops connections a device on your network starts through the firewall), and "
        "a Block rule with destination maxguard_block_out (stops connections your devices "
        "start toward that address).",
    ]
    return {"setup": setup, "block": block, "undo": undo}


def home_router_steps(ip, direction: str) -> dict:
    wording = {
        "inbound": f"incoming connections from {ip}",
        "outbound": f"connections from your devices to {ip}",
        "both": f"all connections to and from {ip}",
    }[direction]
    block = [
        "Open your router's admin page (often printed on a sticker on the router).",
        "Find the firewall, 'access control', or 'IP filter' settings "
        "(the name differs between brands).",
        f"Add a rule that blocks {wording}, and save it.",
        "Write down where you added it, so you can find it again to undo it.",
    ]
    undo = [f"Open the same settings page, delete the rule for {ip}, and save."]
    return {"block": block, "undo": undo}
