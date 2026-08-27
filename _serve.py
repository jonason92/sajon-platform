# -*- coding: utf-8 -*-
"""Authentifizierter statischer Server für das Lebendige Archiv.

Servt `_site/` unter http://127.0.0.1:3080 mit HTTP-Basic-Login.

Konfiguration über Umgebungsvariablen:
  DSH_SITE_USER       (Default: admin)
  DSH_SITE_PASSWORD   (Default: admin)  -> bitte für eine geteilte Instanz ändern
  DSH_SITE_PORT       (Default: 3080)
  DSH_SITE_DIR        (Default: ./_site)

Aufruf:  python _serve.py   (oder `make serve`)
"""
import os
import base64
import http.server
import socketserver

ROOT = os.environ.get("DSH_SITE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_site"))
USER = os.environ.get("DSH_SITE_USER", "admin")
PASS = os.environ.get("DSH_SITE_PASSWORD", "admin")
HOST = os.environ.get("DSH_SITE_HOST", "127.0.0.1")
PORT = int(os.environ.get("DSH_SITE_PORT", "3080"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _authorized(self):
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                user, pwd = base64.b64decode(header[6:]).decode("utf-8").split(":", 1)
                return user == USER and pwd == PASS
            except Exception:
                return False
        return False

    def do_GET(self):
        if not self._authorized():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Das Lebendige Archiv"')
            self.end_headers()
            self.wfile.write(b"401 - Login erforderlich\n")
            return
        super().do_GET()

    def log_message(self, fmt, *args):  # kurze Logs
        print(f"[{self.client_address[0]}] {fmt % args}")


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    print(f"Serving {ROOT}")
    print(f"  URL:   http://{HOST}:{PORT}/")
    print(f"  Login: {USER} / {'*' * len(PASS)}  (via DSH_SITE_USER / DSH_SITE_PASSWORD)")
    try:
        Server((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStop.")
