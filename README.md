# Das Lebendige Archiv

Gedanken zur Verfassung eines **ausführbaren, interaktiven Online-Buches** — Grundlage und Arbeitsstand für ein Buch, das über reines Lesen hinausgeht (Autor:in-Ebene, Lexikon, Referenzen, Notizen).

## Dateien

| Datei | Beschreibung |
|---|---|
| `the_book_2.73.md` | **Quelle**: der unstrukturierte, zusammenhanglose Originaltext (Stream of Consciousness). |
| `the_book_2.73_strukturiert.md` | **Thematisch strukturierte Ausgabe**: bereinigt, dedupliziert, mit Inhaltsverzeichnis und Kapiteln. |
| `the_book_2.73_buch.md` | **Interaktiv-Buch-Ausgabe**: Gliederung anlehnt an die Abschnitte/Eintauch-Modi der Konzeptseite (Autor:in, Der Text, Lexikon, Referenzen & Quellen, Notizen). |
| `jonason-lebendiges-archiv.html` | **Konzeptseite** „Die Bibliothek der Zukunft" — Design-Vorschlag für das interaktive Buch. |
| `_restructure_book.py` | **Generator-Skript**: erzeugt beide Markdown-Ausgaben aus der Quelle. Kuratierte Kapitelzuordnung, wieder zusammengesetzte Zitate, Leseliste. |
| `README.md` | Diese Übersicht. |

## Inhaltliche Ausrichtung

Esoterisch-spirituelle Reflexionen (Anthroposophie/Steiner, Christus-Impuls, Karma, Non-Dualität, Personologie/Astrologie), durchzogen von Themen zu KI & digitaler Welt, Gesellschaft & Macht, Natur & Tieren sowie Kunst & Kultur. Tonal: bewusst anti-strukturell, aphoristisch, im Originalton belassen.

## Skript nutzen

```powershell
python _restructure_book.py
```

Erzeugt `the_book_2.73_strukturiert.md` und `the_book_2.73_buch.md`. Anpassungen an der Kapitelzuordnung erfolgen über die `OVERRIDES`-Liste im Skript.

## Hinweis

Die Kapitelzuordnung ist **kuratiert, aber nicht endgültig** — bei diesem stark verwobenen Text gibt es Passagen, die mehrere Themen berühren. Jedes einzigartige Textstück bleibt unverändert erhalten.
