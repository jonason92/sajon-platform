# Developer makefile for local development
PY = python3.12
VENV = .venv
PIP = $(VENV)/bin/pip
PYV = $(VENV)/bin/python

.PHONY: venv install build serve clean

venv:
	$(PY) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -r book/requirements.txt || true

build:
	$(PYV) _restructure_book.py
	$(PYV) _build_html.py
	$(PYV) _build_all.py

serve:
	# set ADMIN_USER and ADMIN_PASS in your env before running (placeholders below)
	# Example: ADMIN_USER=deepseek ADMIN_PASS=changeme make serve
	ADMIN_USER?=admin
	ADMIN_PASS?=adminpass
	ADMIN_USER=$(ADMIN_USER) ADMIN_PASS=$(ADMIN_PASS) $(PYV) serve_auth.py

clean:
	rm -rf $(VENV) _site
