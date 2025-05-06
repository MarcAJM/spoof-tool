import click
import utils
from scapy.arch import get_if_addr, get_if_hwaddr
from scapy.layers.l2 import ARP, Ether
from scapy.config import conf
from scapy.sendrecv import srp

class SpoofSession:

    def __init__(self, victim_ip_address):
        self.is_running = True
        interface = conf.iface

        self.user_ip_address = get_if_addr(interface)
        self.user_mac_address = get_if_hwaddr(interface)
        self.victim_ip_address = victim_ip_address
        self.victim_mac_address = find_mac_address(victim_ip_address)

        if self.victim_mac_address is None:
            utils.print_error_message("Unable to find MAC address of " + victim_ip_address)
        else:
            self.start()


    def start(self):
        while self.is_running:
            try:
                user_input = input("$ ").strip()
                if user_input in ["exit", "quit", "q"]:
                    self.is_running = False
                    utils.print_info_message("Stopped spoofing")
                    break
            except KeyboardInterrupt:
                click.echo()
                utils.print_error_message("Session interrupted")
                break

def find_mac_address(ip_address):
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=ip_address)
    packet = ether / arp

    utils.print_info_message("Requesting MAC address of " + ip_address)
    for i in range(3):
        ans, _ = srp(packet, timeout=2, verbose=False)
        if ans:
            utils.print_info_message("MAC address of " + ip_address + " acquired")
            return ans[0][1].hwsrc
        else:
            utils.print_error_message("No response arrived for attempt " + str(i+1))

    return None