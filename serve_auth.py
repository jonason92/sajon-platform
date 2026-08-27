# Simple local server with Basic Auth for serving the _site directory (development use only).
# Usage:
#   export ADMIN_USER=deepseek
#   export ADMIN_PASS=somepassword
#   python serve_auth.py
import os
import base64
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "3080"))
USER = os.environ.get("ADMIN_USER", "admin")
PASS = os.environ.get("ADMIN_PASS", "adminpass")
HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(HERE, "_site")

class AuthHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=SITE_DIR, **kwargs)

    def send_auth_request(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Local Admin"')
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Authentication required')

    def is_authenticated(self):
        auth = self.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return False
        try:
            encoded = auth.split(' ', 1)[1].strip()
            decoded = base64.b64decode(encoded).decode('utf-8')
            u, p = decoded.split(':', 1)
            return u == USER and p == PASS
        except Exception:
            return False

    def do_HEAD(self):
        if not self.is_authenticated():
            return self.send_auth_request()
        return super().do_HEAD()

    def do_GET(self):
        if not self.is_authenticated():
            return self.send_auth_request()
        return super().do_GET()

if __name__ == "__main__":
    if not os.path.isdir(SITE_DIR):
        print(f"Error: site directory not found: {SITE_DIR}")
        print("Run the build targets first (Makefile build) to create _site/")
        raise SystemExit(1)
    addr = ("127.0.0.1", PORT)
    with ThreadingHTTPServer(addr, AuthHandler) as httpd:
        print(f"Serving {SITE_DIR} at http://{addr[0]}:{addr[1]} (user={USER})")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down")
            httpd.server_close()
