# Konkrete MCP-Server-Details

Ergänzung zur MCP-Panel-Box in `infografik.html` — hier mit konkreten Paketen, Quellen und Rechten.

## Übersicht

| MCP-Server | Paket / Quelle | Zweck | Rechte | Einsatz im Projekt |
| --- | --- | --- | --- | --- |
| Filesystem | `@modelcontextprotocol/server-filesystem` (offiziell) | lokale Dateien lesen/schreiben | **read-only** auf `/originals/` | Originale unantastbar (Mona-Lisa-Protokoll) |
| Fetch | `@modelcontextprotocol/server-fetch` (offiziell) | Web-Inhalte/URLs abrufen | read-only | Quellen & Links nachrecherchieren |
| GitHub | `@modelcontextprotocol/server-github` (offiziell) | Repo, Issues, PRs, Dateien | read+write (Working-Branch) | Versionierung, Deploy auf GitHub Pages |
| Notion | `@notionhq/notion-mcp-server` (offiziell) | Datenbanken & Seiten | read+write | Notizen in die Pipeline ziehen |
| Zotero | community `zotero-mcp` | Bibliografie (CSL-JSON) | read-only | Single Source of Truth für Metadaten |
| Calibre | community `calibre-mcp` / `mcp-server-calibre` | Bibliothek & Konvertierung | read+write (nur Working-Copies) | EPUB/MOBI erzeugen |
| Sequential Thinking | `@modelcontextprotocol/server-sequential-thinking` (offiziell) | schrittweises Denken | n/a | DeepSeek-Reasoning strukturieren |
| Memory (Knowledge Graph) | `@modelcontextprotocol/server-memory` (offiziell) | persistenter Wissensgraph | read+write | Querverweise der „Spiritual Science Bridge" |

## Routing-Empfehlung (Kimi vs. DeepSeek)

- **Kimi** (Langkontext) → Filesystem + Zotero + Calibre + Notion — liest ganze Bücher, hält den Kontext.
- **DeepSeek-Harness** (Reasoning/Orchestrierung) → Sequential Thinking + GitHub + Fetch — plant und schreibt Glue-Code.
- **GitHub Copilot** → GitHub — Code-Assist in VS Code.

## Sicherheitsregeln

- `Filesystem` nur **read-only** auf Originale (`/originals/`); Schreiben ausschließlich auf `/working/`.
- MCP-Schreibzugriffe immer nur über Working-Copies — nie auf Originale.
- **Kill-Schalter-Test:** ein Schreibversuch auf `/originals/` MUSS fehlschlagen (das ist der gewünschte Erfolgsfall).
