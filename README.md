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

Die Seite ist dann unter `https://<user>.github.io/<repo>/` erreichbar. **Startseite** ist `das-lebendige-archiv-buch.html` (die interaktive Ausgabe); von dort führt ein Button ins ausführbare Jupyter-Book. Lokal bauen: `pip install -r book/requirements.txt && jupyter-book build book`.

## Hinweis

Die Kapitelzuordnung ist **kuratiert, aber nicht endgültig** — bei diesem stark verwobenen Text gibt es Passagen, die mehrere Themen berühren. Jedes einzigartige Textstück bleibt unverändert erhalten.
