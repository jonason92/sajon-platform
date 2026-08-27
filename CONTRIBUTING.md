# Beitragen

Danke fürs Mitwirken am **Lebendigen Archiv** (`sajon-platform`). Dieses Projekt ist ein wachsendes Archiv persönlicher Aphorismen, Schriften, Videotranskriptionen und Studienarbeiten — jede Sammlung und jede Arbeit ist ein eigenes Jupyter-Book, veröffentlicht über GitHub Pages.

## Was du beitragen kannst

### Inhalt
- **Studienarbeiten** → `works/<name>/` (Vorlage: `works/beispielarbeit/`). Konvertierung: `python _docx_to_book.py "<pfad>.docx" works/<slug> "Titel"`.
- **Video-Transkripte** → `transkripte/<name>/` (Vorlage: `transkripte/beispiel/`). Aufbereitetes Markdown: keine Zeitstempel, Sprecherwechsel als `[S1]/[S2]`, Unsicheres als `[unsicher: …]`.
- **Eigene Texte / FB-Posts** → siehe `_ingest_posts.py` bzw. Quellen.
- **Logo/Layout** → `assets/` (`logo.png`, optional `theme.css`).
- **Metadaten** (Ort/Jahr je Arbeit) → `works/_meta.json`.

### Code / Infrastruktur
- Generatoren: `_restructure_book.py`, `_build_html.py`, `_build_jb.py`, `_build_all.py`, `_ingest_posts.py`, `_convert_all.py`, `_docx_to_book.py`, `_transcribe.py`.
- CI: `.github/workflows/` (`ci.yml` (lint) + `deploy-book.yml` (Build & Pages)).

## Arbeitsschritte

1. Branch von `main` erstellen: `git checkout -b feature/xyz`.
2. Änderungen vornehmen (Content oder Code).
3. Format: **Markdown** für Inhalt, **ruff**-Style für Python.
4. Committen mit klarer Message, pushen, **Pull Request** öffnen.

## Qualität

- Python-Skripte: `ruff check`.
- Inhalte: kein automatischer Test — aber klare Struktur (Kapitel/Überschriften).
- **Keine** schweren/privaten Dateien ins Repo (ZIPs, Medien, Transkript-Rohdaten) — die liegen außerhalb (`D:\…`) bzw. sind gitignored.

## Autoren-Kürzel
`[JH]` = Autor. Verwendet in Karten-Köpfen und Buch-Konfigs (`author: JH`).
