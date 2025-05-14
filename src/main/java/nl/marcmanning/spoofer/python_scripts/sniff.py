import socket
import json
import threading
from scapy.all import sniff, IP

tracked_pairs = set()
tracked_pairs_lock = threading.Lock()
should_run = threading.Event()
should_run.set()
conn = None


def packet_callback(pkt):
    if IP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst

        with tracked_pairs_lock:
            if (src, dst) in tracked_pairs or (dst, src) in tracked_pairs:
                message = json.dumps({
                    'src': src,
                    'dst': dst,
                    'summary': pkt.summary()
                }) + '\n'
                try:
                    conn.sendall(message.encode())
                except Exception as e:
                    print("Send failed:", e)
                    should_run.clear()


def socket_listener():
    global conn
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen(1)
    conn, _ = server.accept()

    while should_run.is_set():
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            for line in data.strip().split('\n'):
                msg = json.loads(line)
                action = msg.get('action')
                if action == 'add_pair':
                    ip1 = msg.get('ip1')
                    ip2 = msg.get('ip2')
                    if ip1 and ip2:
                        with tracked_pairs_lock:
                            tracked_pairs.add((ip1, ip2))
                        print("Added tracked pair:", ip1, ip2)
                elif action == 'shutdown':
                    print("Shutdown received.")
                    should_run.clear()
        except Exception as e:
            print("Exception in socket listener:", e)
            should_run.clear()


sniffer_thread = threading.Thread(target=lambda: sniff(prn=packet_callback, store=0, stop_filter=lambda _: not should_run.is_set()))
listener_thread = threading.Thread(target=socket_listener)

listener_thread.start()
sniffer_thread.start()

listener_thread.join()
sniffer_thread.join()
print("Python sniffer exited cleanly.")