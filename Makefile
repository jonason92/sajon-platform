# Das Lebendige Archiv — lokaler Dev / Serve
# Ziel: mit einem Befehl bauen und als Admin-Site unter http://127.0.0.1:3080 serven.
# Alternative ohne make:  python _build_all.py   dann   python _serve.py

PY ?= python

.PHONY: install build serve dev clean

# Abhängigkeiten (einmalig). Alternativ venv:  python -m venv .venv
install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install jupyter-book==1.0.4.post1
	@echo "Optional (Transkription): $(PY) -m pip install faster-whisper und ffmpeg installieren"

# Quelle -> Bücher -> Portal/_site
build:
	$(PY) _restructure_book.py
	$(PY) _build_html.py
	$(PY) _build_all.py

# _site unter http://127.0.0.1:3080 mit Login ausliefern
serve:
	$(PY) _serve.py

dev: build serve

clean:
	$(PY) -c "import shutil,glob; [shutil.rmtree(x,ignore_errors=True) for x in ['_site']+glob.glob('book/_build')+glob.glob('works/*/_build')]"
