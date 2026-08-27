# DEV_SETUP — Entwicklung / Betrieb

## Repo klonen

```powershell
git clone https://github.com/jonason92/sajon-platform.git
cd sajon-platform
```

## Lokal bauen (Jupyter-Book)

Python 3.12 wird empfohlen (Python 3.14 ist für Jupyter-Book/Sphinx teils zu neu):

```powershell
pip install jupyter-book==1.0.4.post1
python _build_all.py          # baut Archiv + alle works/* + transkripte/* nach _site/
```

Ergebnis: `_site/index.html` (Portal) im Browser öffnen.

## Generatoren

| Skript | Zweck |
|---|---|
| `_restructure_book.py` | Quelle → strukturierte Bücher; `OVERRIDES` für Themen; liest `facebook_posts.md` |
| `_build_html.py` | interaktive Einzelseite `das-lebendige-archiv-buch.html` |
| `_build_jb.py` | Jupyter-Book-Seiten aus der Buch-Markdown |
| `_convert_all.py` | alle `.docx`-Studienarbeiten → `works/<slug>/` |
| `_docx_to_book.py` | einzelne `.docx` → Jupyter-Book |
| `_ingest_posts.py` | FB-Export-JSONs → `facebook_posts.md` (ohne Links) |
| `_transcribe.py` | Faster-Whisper → `transkripte/<slug>/` |

## Veröffentlichen (GitHub Pages)

Der Workflow `deploy-book.yml` baut bei **Push auf `main`** und deployt per GitHub Actions auf Pages. Einmalig: **Settings → Pages → Source: „GitHub Actions"**.

## Transkription (Faster-Whisper)

Lokal & privat: `pip install faster-whisper`. Videos **nicht** von der C:-kDrive öffnen (Speicher!). Arbeitsordner: `D:\Projects\kimi-helfer\` (`Video-Transkription\` = Intake, `Transkripte-Aufbereitet\` = fertiges Markdown).

## Konventionen

- **Autor-Kürzel:** `JH`
- **Transkript-Format:** keine Zeitstempel; Sprecher `[S1]/[S2]`; `[unsicher: …]`.
- **Logos:** `assets/logo.png` (hell), `assets/logo-dark.png` (dunkel).
- **Keine privaten/schweren Dateien im Repo** (gitignored).
