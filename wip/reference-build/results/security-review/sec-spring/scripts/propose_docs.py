"""Write proposed doc changes into out/docs-proposed/b (copies; the repository is never touched)."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out" / "docs-proposed"
FENCE = "`" * 3


def sub(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


hw = (OUT / "a" / "HARDWARE.md").read_text()
hw = sub(hw, "**Now plug `eth0` into switch port 5.**\n", f"""No address is not enough on its own: Linux can still answer an ARP request for
the management address (`eth1`) on `eth0`, and answer packets for that address
that arrive on `eth0` through `eth1`. It does both when `rp_filter` is 0 (the
kernel's own default); the AHM-04 review saw both in a test network namespace.
Pin both settings for `eth0` (**not run — verify on hardware**):

{FENCE}bash
printf '%s\\n' 'net.ipv4.conf.eth0.arp_ignore = 8' 'net.ipv4.conf.eth0.rp_filter = 1' \\
  | sudo tee /etc/sysctl.d/90-maxguard-capture.conf
sudo sysctl -p /etc/sysctl.d/90-maxguard-capture.conf
{FENCE}

`arp_ignore = 8` means "never answer ARP on this port"; `rp_filter = 1` drops
packets for this computer that arrive on a port without an address.

**Now plug `eth0` into switch port 5.**
""")
hw = sub(hw, "sudo ethtool -k eth0 | grep -E '^(generic|large)-receive-offload:'\n",
         "sudo ethtool -k eth0 | grep -E '^(generic|large)-receive-offload:'\n"
         "sysctl net.ipv4.conf.eth0.arp_ignore net.ipv4.conf.eth0.rp_filter\n")
hw = sub(hw, "both offload lines `off` (maybe `off [fixed]`). Reboot and check again: settings\n",
         "both offload lines `off` (maybe `off [fixed]`); `arp_ignore = 8` and\n"
         "`rp_filter = 1`. Reboot and check again: settings\n")
(OUT / "b" / "HARDWARE.md").write_text(hw)
print("wrote", OUT / "b" / "HARDWARE.md")
