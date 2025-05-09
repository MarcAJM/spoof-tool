import click
from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp


def print_error_message(message):
    click.echo(click.style("✖ ", bold=True, fg="red") + click.style(message, bold=True))


def print_info_message(message):
    click.echo(click.style("ℹ ", bold=True, fg="blue") + click.style(message, bold=False))


# Try to find the mac address corresponding to the
# given IP address, return None if none is found.
def find_mac_address(ip_address):
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=ip_address)
    packet = ether / arp

    print_info_message("Requesting MAC address of " + ip_address)
    for i in range(3):
        ans, _ = srp(packet, timeout=2, verbose=False)
        if ans:
            print_info_message("MAC address of " + ip_address + " acquired")
            return ans[0][1].hwsrc
        else:
            print_info_message("No response arrived for attempt " + str(i+1))

    return None