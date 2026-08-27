# sajon-platform

Repository (ehemals Setup für ein „prototype-fund / open-data“-Vorhaben) — aktueller Inhalt: **„Das Lebendige Archiv“**.

---

# Das Lebendige Archiv

Gedanken zur Verfassung eines **ausführbaren, interaktiven Online-Buches** — Grundlage und Arbeitsstand für ein Buch, das über reines Lesen hinausgeht (Autor:in-Ebene, Lexikon, Referenzen, Notizen).

## Dateien

| Datei | Beschreibung |
|---|---|
| `the_book_2.73.md` | **Quelle**: der unstrukturierte, zusammenhanglose Originaltext (Stream of Consciousness). |
| `the_book_2.73_strukturiert.md` | **Thematisch strukturierte Ausgabe**: bereinigt, dedupliziert, mit Inhaltsverzeichnis und Kapiteln. |
| `the_book_2.73_buch.md` | **Interaktiv-Buch-Ausgabe**: Gliederung anlehnt an die Abschnitte/Eintauch-Modi der Konzeptseite (Autor:in, Der Text, Lexikon, Referenzen & Quellen, Notizen). |
| `jonason-lebendiges-archiv.html` | **Konzeptseite** „Die Bibliothek der Zukunft“ — Design-Vorschlag für das interaktive Buch. |
| `das-lebendige-archiv-buch.html` | **Ausführbares interaktives Buch** — aus `the_book_2.73_buch.md` erzeugte, eigenständige HTML-Seite (Navigation, Scrollspy, Lexikon-Suche, Vorlesen, Dunkelmodus). |
| `_restructure_book.py` | **Generator-Skript**: erzeugt beide Markdown-Ausgaben aus der Quelle. Kuratierte Kapitelzuordnung, wieder zusammengesetzte Zitate, Leseliste. |
| `_build_html.py` | **Generator-Skript**: erzeugt `das-lebendige-archiv-buch.html` aus der Buch-Markdown. |
| `book/` | **Jupyter-Book-Projekt** (Executable Books): MyST-Seiten + `_config.yml` + `_toc.yml`, wird per GitHub Actions auf GitHub Pages veröffentlicht. |
| `.github/workflows/deploy-book.yml` | **CI-Workflow**: baut das Jupyter Book und deployt es auf GitHub Pages. |
| `assets/` | **Design-Ordner**: `logo.svg` (Standard) + optional `theme.css` (übersteuert das Layout). Hier lädst du eigene Logo-/Layout-Elemente hoch. |
| `works/` | **Studienarbeiten**: jede Arbeit als eigener Unterordner = eigenes Jupyter-Book (`works/<name>/`). Vorlage: `works/beispielarbeit/`. |
| `transkripte/` | **Videotranskriptionen**: jeweils ein kleines eigenes Jupyter-Book (`transkripte/<name>/`). Vorlage: `transkripte/beispiel/`. |
| `_build_all.py` | **Portal-Build**: baut Archiv + alle `works/*` + alle `transkripte/*` in `_site/` und erzeugt die Startseite (Portal). |
| `README.md` | Diese Übersicht. |

## Inhaltliche Ausrichtung

Esoterisch-spirituelle Reflexionen (Anthroposophie/Steiner, Christus-Impuls, Karma, Non-Dualität, Personologie/Astrologie), durchzogen von Themen zu KI & digitaler Welt, Gesellschaft & Macht, Natur & Tieren sowie Kunst & Kultur. Tonal: bewusst anti-strukturell, aphoristisch, im Originalton belassen.

## Skript nutzen

```powershell
python _restructure_book.py   # erzeugt die beiden Markdown-Ausgaben
python _build_html.py         # erzeugt das interaktive Buch (HTML)
```

`_restructure_book.py` erzeugt `the_book_2.73_strukturiert.md` und `the_book_2.73_buch.md` (Anpassungen an der Kapitelzuordnung über die `OVERRIDES`-Liste). `_build_html.py` erzeugt daraus `das-lebendige-archiv-buch.html` — einfach im Browser öffnen. `_build_jb.py` erzeugt das Jupyter-Book-Projekt in `book/` für die Online-Veröffentlichung.

## Online veröffentlichen (Jupyter Book → GitHub Pages)

Das Buch liegt als **Jupyter Book** in `book/`. Der Workflow `.github/workflows/deploy-book.yml` baut es bei jedem Push und veröffentlicht es auf GitHub Pages:

1. Auf GitHub: **Settings → Pages → Source: „GitHub Actions“** wählen (einmalig).
2. Danach baut und deployt der Workflow automatisch bei jedem Push.

Die Seite ist dann unter `https://<user>.github.io/<repo>/` erreichbar. **Startseite (Portal)** listet das Archiv, die Videotranskriptionen und alle Studienarbeiten; jede Arbeit ist ein eigenes Jupyter-Book. Deploy setzt `_site/` (erzeugt von `_build_all.py`). Lokal bauen: `pip install jupyter-book && python _build_all.py`.

## Hinweis

Die Kapitelzuordnung ist **kuratiert, aber nicht endgültig** — bei diesem stark verwobenen Text gibt es Passagen, die mehrere Themen berühren. Jedes einzigartige Textstück bleibt unverändert erhalten.
