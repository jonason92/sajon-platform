# Local developer setup (quick start)

1. Create venv and install dev deps:
   python3.12 -m venv .venv
   .venv/bin/pip install --upgrade pip
   .venv/bin/pip install -r requirements-dev.txt
   .venv/bin/pip install -r book/requirements.txt || true

2. Build the site:
   .venv/bin/python _restructure_book.py
   .venv/bin/python _build_html.py
   .venv/bin/python _build_all.py

3. Serve locally (with Basic Auth):
   export ADMIN_USER=deepseek
   export ADMIN_PASS=yourpassword
   .venv/bin/python serve_auth.py
   # Open http://127.0.0.1:3080 and authenticate with the credentials above.

Security note: serve_auth.py uses HTTP Basic Auth only and is intended for local development. Do not expose it on public networks without TLS and a proper reverse proxy.
