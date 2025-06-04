#!/usr/bin/env python3
"""
random_server.py – minimal one-file HTTP server that returns the same
random text on every request.  Stops cleanly when you quit the script.
"""

import http.server
import socketserver
import random
import string

PORT = 80  # change if you want a different port


class RandomTextHandler(http.server.BaseHTTPRequestHandler):
    # One random string per server run
    _payload = "You have been DNS spoofed!"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(self._payload.encode("utf-8"))

    # Silence the default noisy logging
    def log_message(self, format, *args):
        return


def main():
    with socketserver.TCPServer(("", PORT), RandomTextHandler) as httpd:
        print(f"Serving random text at http://localhost:{PORT}/")
        print("Hit Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down…")


if __name__ == "__main__":
    main()