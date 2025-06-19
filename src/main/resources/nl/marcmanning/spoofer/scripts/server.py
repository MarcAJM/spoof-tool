#!/usr/bin/env python3
"""
random_server.py – minimal one-file HTTP server that returns the same
random text on every request.  Stops cleanly when you quit the script.
"""

import http.server
import socketserver
import random
import string
import json
import aiohttp
from aiohttp import web

# Constants
PORT = 80  # Must be 80 for HTTP

# Logging helpers
def log_info(msg):
    print(json.dumps({"type": "info", "info": msg}), flush=True)

def log_error(msg):
    print(json.dumps({"type": "error", "error": msg}), flush=True)

# Header cleaning
def clean_headers(headers):
    headers_to_remove = [
        'accept-encoding', 'if-modified-since', 'cache-control',
        'strict-transport-security', 'content-security-policy',
        'upgrade-insecure-requests'
    ]
    return {k: v for k, v in headers.items() if k.lower() not in headers_to_remove}


async def handle_request(request):
    try:
        requested_domain = request.host

        if not requested_domain:
            return web.Response(status=400, text="Missing Host")

        path = request.rel_url.path or "/"
        url = f"https://{requested_domain}{path}"
        headers = clean_headers(request.headers)
        headers['Host'] = requested_domain
        headers['X-Forwarded-For'] = request.remote or '0.0.0.0'

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=request.method,
                url=url,
                headers=headers,
                data=await request.read(),
                allow_redirects=True,
                ssl=True
            ) as resp:

                body = await resp.read()
                content_type = resp.headers.get('Content-Type', '')

                if any(ct in content_type for ct in ['text/html', 'application/javascript']):
                    body = body.replace(b"https://", b"http://")
                if body and any(ct in content_type.lower() for ct in ['text/html', 'text/css', 'application/javascript', 'application/json']):
                    try:
                        # Convert bytes to string, process, then back to bytes
                        text_content = body.decode('utf-8', errors='ignore')
                        text_content = text_content.replace("https://", "http://")
                        body = text_content.encode('utf-8')
                        log_info("HTTPS links stripped from response")
                    except Exception as e:
                        log_error(f"Error processing response content: {e}")

                clean_resp_headers = clean_headers(resp.headers)
                clean_resp_headers['Connection'] = 'close'

                log_info(f"Proxied {url} with status {resp.status}")
                return web.Response(
                    status=resp.status,
                    headers=clean_resp_headers,
                    body=body
                )

    except Exception as e:
        log_error(f"Proxy error: {e}")
        return web.Response(status=502, text=f"Proxy error: {e}")

# favicon handler
async def handle_favicon(request):
    # simple ICO file
    favicon_data = (
        b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00'
        b'h\x05\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00'
        b' \x00\x00\x00\x01\x00\x08\x00\x00\x00\x00\x00@\x05\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00'
    )
    
    return web.Response(body=favicon_data, content_type='image/x-icon')

def main():
    app = web.Application()
    app.router.add_route('', '/favicon.ico', handle_favicon)
    app.router.add_route('', '/{tail:.*}', handle_request)
    log_info(f"Starting proxy server on port {PORT}")
    web.run_app(app, host='0.0.0.0', port=PORT)


if __name__ == "__main__":
    main()