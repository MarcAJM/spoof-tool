#!/usr/bin/env python3

import aiohttp
import json
from aiohttp import web
import os
import sys


# Prints a json info message that java can pick up and display to the logger.
def log_info(msg):
    print(json.dumps({"type": "info", "info": msg}), flush=True)


# Prints a json error message that java can pick up and display to the logger.
def log_error(msg):
    print(json.dumps({"type": "error", "error": msg}), flush=True)

# Constants
PORT = 80  # Must be 80 for HTTP
LOCK_ICON_PATH = os.path.join(os.path.dirname(__file__), '..', 'lock.ico')

# Helper function to clean headers
def clean_headers(headers):
    headers_to_remove = ['accept-encoding', 'if-modified-since', 'cache-control']
    return {k: v for k, v in headers.items() if k.lower() not in headers_to_remove}

# Helper function to get path to lock icon
def get_path_to_lock_icon():
    if os.path.exists(LOCK_ICON_PATH):
        return LOCK_ICON_PATH

    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    script_path = os.path.join(script_path, "../lock.ico")

    if os.path.exists(script_path):
        return script_path

    log_error("Error: Could not find lock.ico")
    return LOCK_ICON_PATH

# Handler for incoming HTTP requests
async def handle_request(request):
    host = request.headers.get('Host')
    if not host:
        return web.Response(status=400, text="No Host header provided.")

    path = request.rel_url.path_qs or "/"
    url = f"https://{host}{path}"
    headers = clean_headers(request.headers)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=request.method,
                url=url,
                headers=headers,
                data=await request.read(),
                allow_redirects=False,
                ssl=False  # Disable SSL verification
            ) as resp:
                # Read and modify HTTPS response
                body = await resp.read()
                body = body.replace(b"https://", b"http://")
                headers = dict(resp.headers)
                headers = {k: v for k, v in headers.items() if k.lower() != 'strict-transport-security'}
                headers['Connection'] = 'close'

                log_info(f"Proxied request to {url} with status {resp.status}")
                return web.Response(
                    status=resp.status,
                    headers=headers,
                    body=body
                )
    except Exception as e:
        log_error(f"Proxy error: {e}")
        return web.Response(status=502, text=f"Proxy error: {e}")

async def handle_favicon():
    try:
        with open(get_path_to_lock_icon(), 'rb') as f:
            icon_data = f.read()
        log_info("Served favicon.ico")
        return web.Response(body=icon_data, content_type='image/x-icon')
    except Exception as e:
        log_error(f"Error serving favicon: {e}")
        return web.Response(status=404, text="Favicon not found.")

def main():
    app = web.Application()
    app.router.add_route('*', '/favicon.ico', handle_favicon)
    app.router.add_route('*', '/{tail:.*}', handle_request)

    log_info(f"Starting proxy server on port {PORT}")
    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    main()
