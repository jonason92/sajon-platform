# Abgleich-Bericht: facebook_posts.md vs. Facebook-Export
**v1.0 · 2026-09-18 · Basis: nur Repo-Inhalte (Voll-Export >2 GB liegt lokal beim Autor)**

---

## 1. Was verifiziert wurde

| Prüfpunkt | Ergebnis |
|---|---|
| Notizen in `facebook_posts.md` | **315** |
| Exakte Duplikate | **0** ✅ |
| Übrig gebliebene URLs/Link-Reste | **0** ✅ (Filter hat sauber gearbeitet) |
| Längenverteilung | 149 kurz (<70 Z.) · 115 mittel · 51 lang (≥500 Z.) · Median 78 · Max 3706 |
| Interne FB-Markup-Artefakte | **2** (`@[1462514113:2048:Simon Balz]`, `@[100001256809816:2048:Projeçt Riot]`) ⚠️ |

## 2. Kritischer Befund: Der Export im Repo ist unvollständig

- `fb_export/facebook-sajon92-27.08.2026-rAfEWPMw.zip` enthält **nur 13 Sticker-PNGs** — keine Post-Daten.
- Die eigentliche Quelle (`facebook-sajon92-27.08.2026-BuQQGj1c.zip`, >2 GB) und die daraus extrahierten 6 JSON-Dateien sind **nicht im Repo**.
- **Konsequenz:** Die 315 Notizen können repo-intern nicht gegen die Quelle verifiziert werden. Der Korpus beruht auf einem lokalen Lauf von `_extract_fb.py` + `_ingest_posts.py`.

## 3. Was die Pipeline bewusst wegwirft (Filter-Audit `_ingest_posts.py`)

1. **Alle URLs werden aus dem Text gelöscht** — Posts, die nur aus Link + Kommentar bestanden, verlieren ihren Kontext; reine Link-Posts fallen ganz weg. *(Die frühen Hip-Hop-Tipps waren genau solche Posts — vermutlich sind hier Verluste entstanden.)*
2. **Posts mit ≤3 Zeichen** Text werden verworfen.
3. **System-Boilerplate** ("hat geteilt/hochgeladen/aktualisiert", "became friends"…) wird verworfen — gut so, aber Events ("created an event") gehen dabei möglicherweise verloren.
4. **Zeitstempel werden nicht übernommen.** Für ein Werk über 18 Jahre (2008→2026) ist das der grösste inhaltliche Verlust: Der Korpus ist aktuell un-datierbar.
5. **Weitere Quellen ungenutzt:** `posts_on_other_pages_and_profiles`, `edits_you_made_to_posts`, `content_sharing_links`, App-Posts — diese JSONs wurden extrahiert, aber `_ingest_posts.py` verarbeitet nur den Haupt-Posts-Strom.
6. **2 FB-Markup-Artefakte** (`@[ID:2048:Name]`) sind durchgesickert und sollten bereinigt werden (Namen stehen drin, IDs entfernen).

## 4. Empfohlene Vorgehensweise für den Voll-Abgleich (2-GB-Export)

Da der Export zu gross für den Upload ist, läuft der Abgleich **lokal beim Autor**, ich liefere die Werkzeuge:

1. `_extract_fb.py` lokal auf das grosse Zip anwenden (liegt im Repo).
2. Neu: `_audit_export.py` (von mir, folgt) — zählt Posts pro JSON, vergleicht gegen `facebook_posts.md`, erzeugt eine Diff-Liste: welche Posts fielen weg und aus welchem Grund (Link-only, Boilerplate, zu kurz).
3. Nur die **Audit-Ausgabe** (kleine .md/.json, keine Rohdaten) committen.
4. Optional grosser Gewinn: **Re-Ingest mit Zeitstempeln** — Format `JJJJ-MM-TT · Text`, damit Kapitel die 18-Jahre-Achse nutzen können. Die bisherige Reihenfolge der Datei bleibt als `altversionen/facebook_posts_v1-ohne-daten.md` erhalten.

## 5. Fazit

- Der bestehende Korpus ist **sauber kuratiert** (keine Doppelgänger, keine Link-Reste) und als *Arbeitsbasis* tauglich.
- Er ist aber **nachweislich eine Teilmenge** mit bekannten blinden Flecken: Link-Posts, Kurz-Posts, Sekundär-Quellen, Zeitstempel.
- Für die Buch-Expansion empfohlene Reihenfolge: erst Audit-Lauf (Schritt 4), dann Kapitel-Exposés auf dem verifizierten Korpus.

*Nächster Schritt meinerseits: `_audit_export.py` schreiben und ins Repo legen.*
