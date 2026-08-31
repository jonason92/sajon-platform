# Info: Notion-Export & Kimi-Agent-Webflow

## 1) Punkt [1] — Notion-taugliche Export-Variante der Übersicht

Ziel: die Übersicht (Startseite `index.html`) so bereitstellen, dass sie sich direkt in Notion nutzen lässt.

**Was bereits vorbereitet ist:**
- `index.html` — die Startseite/Anleitung des Ordners, verlinkt alle Bausteine.
- `export/` — fertige **PNG-Bilder** (`infografik.png`, `mindmap.png`, `index.png`, `lebendiges-archiv.png`).
- `README.md` — dieselbe Übersicht als Markdown.
- Export-Modus der Infografik: `infografik.html?clean=1` blendet Kopfleiste und Seitenpanel aus → sauberes Diagramm für Neu-Exporte.

**Drei Wege nach Notion:**
1. **Bild einfügen** — PNGs aus `export/` per Drag & Drop in eine Notion-Seite ziehen.
2. **Markdown-Import** — `README.md` über „Importieren → Markdown" als strukturierte Übersicht übernehmen.
3. **Neu-Export** — Diagramm bei Bedarf mit `?clean=1` neu rendern (Headless-Browser, z. B. Edge `--screenshot`).

## 2) Ideale Integration mit dem „Kimi-Agent-Webflow"

Vision für die kommende, detaillierte Umsetzung des Web-Interface — für **Plattform-Nutzer:innen** und **Kundenaufträge** (Bezahlung/Download).

### Leitidee
Ein **Kimi-Agent** (Langkontext, „liest ganze Bücher") orchestriert den Web-Workflow über **MCP-Server** — statt dass jede Seite mühsam von Hand gebaut wird. Kimi kennt den Inhalt (Bücher, Transkripte, Notizen) und erzeugt daraus Struktur und Text; DeepSeek-Harness liefert die Glue-Logik, Copilot den Feinschliff.

### Der Webflow in Schritten
1. **Inhalt verstehen:** Kimi liest via `Filesystem`/Zotero die Originale und Transkripte (Langkontext).
2. **Struktur ableiten:** Kimi erzeugt aus der Infografik/Mindmap die Sitemap und Seitenstruktur.
3. **Seiten erzeugen:** Kimi schreibt HTML/Komponenten (bzw. MyST/Markdown), speichert via `GitHub-MCP` in den Working-Branch.
4. **Publizieren:** Build läuft, Deploy auf GitHub Pages (`jonason92.github.io/sajon-platform`).
5. **Kundenaufträge:** Stripe-Checkout → nach Zahlung generiert `Calibre-MCP` on-the-fly ein wasserzeichen-PDF/EPUB → Download über signierte URL.
6. **Rückfluss:** Käufer-Feedback/Notizen fließen via `Notion-MCP` zurück, Kimi schlägt die nächste Überarbeitung vor.

### Rollentrennung
| Rolle | Werkzeug | Aufgabe |
| --- | --- | --- |
| Konzeption | **Du (Autor)** | Inhalte, Kuratierung, Ästhetik — bleibt die letzte Instanz. |
| Kontext & Inhalt | **Kimi** | ganze Werke lesen, zusammenfassen, strukturieren. |
| Orchestrierung/Code | **DeepSeek-Harness** | Pipelines, Glue, Build-Skripte. |
| Code-Assist | **GitHub Copilot** | Editieren im Editor. |
| Infrastruktur | MCP-Server | Filesystem, GitHub, Notion, Zotero, Calibre, Fetch. |

### Sicherheits-Leitplanken
- Originale bleiben **read-only** (Mona-Lisa-Protokoll); KI arbeitet nur auf Working-Copies.
- Bibliografie bleibt **Zotero = Autorität**; Kimi darf Metadaten nicht erfinden, nur abfragen.
- Alle Schreibzugriffe über MCP laufen in den Working-Branch, nie direkt auf `main`.

### Offene Fragen für die Detailumsetzung
- Statisch (GitHub Pages + MyST) vs. dynamisch (FastAPI/Backend) für Stripe?
- Wo läuft der Kimi-Agent (lokal `Kimi.exe`, API, oder über Harness)?
- Wie wird der Bestell-Workflow (Stripe → Calibre → Download) konkret verdrahtet?
