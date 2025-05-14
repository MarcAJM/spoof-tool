from scapy.all import ARP, Ether, srp, conf
import subprocess
import platform
import re
import sys


def get_mac_from_arp_cache(ip):
    """Check the OS ARP cache first."""
    system = platform.system()
    if system == "Windows":
        output = subprocess.getoutput("arp -a")
        # Windows ARP table line: Internet Address  Physical Address     Type
        match = re.search(rf"{ip}\s+([-\w]+)", output)
    else:
        output = subprocess.getoutput("arp -n")
        # Unix ARP line: IP address HWtype HWaddress Flags Mask Iface
        match = re.search(rf"{ip}\s+\S+\s+([0-9a-f:]+)", output)

    if match:
        return match.group(1)
    return None


def get_mac_via_arp_request(ip):
    """Send ARP request on local network to get MAC address."""
    conf.verb = 0  # suppress scapy output
    arp = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]

    for sent, received in result:
        return received.hwsrc
    return None


def get_mac(ip):
    result = get_mac_from_arp_cache(ip)
    if result:
        return result

    result = get_mac_via_arp_request(ip)
    if result:
        return result

    return None


if __name__ == "__main__":
    arg = sys.argv[1]
    mac = get_mac(arg)
    print(mac)
