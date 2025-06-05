#!/usr/bin/env python3

import aiohttp
import json
from aiohttp import web
import os
from urllib.parse import parse_qs

# Constants
PORT = 80  # Must be 80 for HTTP
LOCK_ICON_PATH = os.path.join(os.path.dirname(__file__), '..', 'lock.ico')

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


def get_path_to_lock_icon():
    paths = [
        os.path.join(os.path.dirname(__file__), 'lock.ico'),
        os.path.join(os.getcwd(), 'lock.ico'),
        os.path.join(os.path.dirname(__file__), '..', 'lock.ico'),
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    log_error("Error: Could not find lock.ico")
    return None

async def handle_request(request):
    try:
        query_params = parse_qs(request.rel_url.query)
        original_host = query_params.get('original_host', [None])[0]

        if not original_host:
            return web.Response(status=400, text="Missing original_host")

        path = request.rel_url.path or "/"
        url = f"https://{original_host}{path}"
        headers = clean_headers(request.headers)
        headers['Host'] = original_host
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
    try:
        path = get_path_to_lock_icon()
        if not path:
            return web.Response(status=404, text="Favicon not found.")

        with open(path, 'rb') as f:
            icon_data = f.read()
        log_info("Served favicon.ico")
        return web.Response(body=icon_data, content_type='image/x-icon')
    except Exception as e:
        log_error(f"Favicon error: {e}")
        return web.Response(status=500, text="Favicon error.")

def main():
    app = web.Application()
    app.router.add_route('*', '/favicon.ico', handle_favicon)
    app.router.add_route('*', '/{tail:.*}', handle_request)
    log_info(f"Starting proxy on port {PORT}")
    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    main()
