"""Tests for maxguard.response.generate (Ahmad, AHM-07)."""

import pytest

from maxguard.response.generate import NFT_SETUP, parse_ip, rules_for

HOSTILE = [
    "1.2.3.4; rm -rf /",
    "1.2.3.4 && reboot",
    "$(reboot)",
    " 203.0.113.7",          # leading space
    "203.0.113.7\n",         # trailing newline
    "203.0.113.0/24",        # a network, not one address
    "203.0.113",
    "",
    "2001:db8::1%$(id)",     # ipaddress accepts this scope: it must still be refused
    "2001:db8::1%eth0",
]

REFUSED = [
    "127.0.0.1", "127.0.0.2", "::1",            # loopback
    "224.0.0.1", "ff02::1",                     # multicast
    "0.0.0.0", "::",                            # unspecified
    "169.254.10.1", "fe80::1", "fe80::1%eth0",  # link-local
    "255.255.255.255",                          # broadcast
    "::ffff:203.0.113.7",                       # IPv4 written as IPv6
]


def all_text(rules: dict) -> str:
    """Every command and step in one string, to search for leaked input."""
    parts = []
    for method in ("nftables", "iptables", "opnsense", "home_router"):
        for key in ("block", "undo"):
            parts.extend(rules[method][key])
    return "\n".join(parts)


@pytest.mark.parametrize("text", HOSTILE)
def test_hostile_input_never_reaches_a_command(text):
    with pytest.raises(ValueError):
        rules_for(text, "both")


@pytest.mark.parametrize("text", REFUSED)
def test_special_addresses_are_refused(text):
    with pytest.raises(ValueError):
        rules_for(text, "inbound")


def test_a_number_is_not_an_address():
    with pytest.raises(ValueError):
        parse_ip(16909060)  # ipaddress alone would read this as 1.2.3.4


def test_unknown_direction_is_refused():
    with pytest.raises(ValueError, match="direction"):
        rules_for("203.0.113.7", "sideways")


def test_inbound_ipv4_rules_and_undo():
    rules = rules_for("203.0.113.7", "inbound")
    assert rules["ip"] == "203.0.113.7" and rules["version"] == 4
    assert rules["nftables"]["block"] == [
        "sudo nft 'add element inet maxguard maxguard_block_in_v4 { 203.0.113.7 }'"]
    assert rules["nftables"]["undo"] == [
        "sudo nft 'delete element inet maxguard maxguard_block_in_v4 { 203.0.113.7 }'"]
    assert rules["iptables"]["block"] == [
        "sudo iptables -I INPUT -m conntrack --ctorigsrc 203.0.113.7 "
        "-m comment --comment maxguard -j DROP",
        "sudo iptables -I FORWARD -m conntrack --ctorigsrc 203.0.113.7 "
        "-m comment --comment maxguard -j DROP",
    ]


def test_every_block_command_has_an_undo():
    rules = rules_for("198.51.100.20", "both")
    for method in ("nftables", "opnsense"):
        assert len(rules[method]["block"]) == len(rules[method]["undo"]) == 2  # in + out
    assert len(rules["iptables"]["block"]) == len(rules["iptables"]["undo"]) == 4
    assert all(" -D " in c for c in rules["iptables"]["undo"])  # -D deletes, -I inserts
    undo = [c.replace(" -D ", " -I ") for c in rules["iptables"]["undo"]]
    assert undo == rules["iptables"]["block"]  # the same rule, deleted instead of inserted
    assert all("'delete element " in c for c in rules["nftables"]["undo"])


def test_ipv6_uses_the_v6_sets_and_ip6tables():
    rules = rules_for("2001:DB8:0:0:0:0:0:7", "outbound")
    assert rules["ip"] == "2001:db8::7"  # one spelling, the same as Zeek writes
    assert "maxguard_block_out_v6 { 2001:db8::7 }" in rules["nftables"]["block"][0]
    assert all(c.startswith("sudo ip6tables -I ") for c in rules["iptables"]["block"])
    assert all("--ctorigdst 2001:db8::7" in c for c in rules["iptables"]["block"])


def test_private_addresses_can_be_blocked():
    # A compromised device on the user's own network is a valid thing to block.
    assert rules_for("192.168.1.50", "both")["ip"] == "192.168.1.50"


def test_only_the_parsed_address_appears():
    rules = rules_for("203.0.113.7", "both")
    text = all_text(rules)
    assert ";" not in text.replace("Save, then", "")  # no shell separators
    assert "$(" not in text and "`" not in text


def test_setup_declares_every_set_the_commands_use():
    for ip in ("203.0.113.7", "2001:db8::7"):
        for command in rules_for(ip, "both")["nftables"]["block"]:
            set_name = command.split()[6]  # sudo nft 'add element inet maxguard <set> ...
            assert f"add set inet maxguard {set_name} " in NFT_SETUP


def test_same_input_same_output():
    assert rules_for("203.0.113.7", "both") == rules_for("203.0.113.7", "both")


def test_opnsense_setup_puts_the_block_rules_first():
    # OPNsense rules are "quick": the first match wins, so a Block rule below the
    # default allow rule would never match.
    setup = rules_for("203.0.113.7", "both")["opnsense"]["setup"]
    assert any("above every Pass rule" in step for step in setup)
