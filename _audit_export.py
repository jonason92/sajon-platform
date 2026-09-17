# -*- coding: utf-8 -*-
"""Audit: Voll-Export (fb_export/*.json) gegen facebook_posts.md abgleichen.

Lokal ausfuehren (neben dem Repo, grosser Export in fb_export/):
    python _audit_export.py

Erzeugt fb_export/AUDIT.md mit:
  - Posts pro Quelldatei (mit Zeitstempel-Statistik)
  - wie viele davon in facebook_posts.md gelandet sind
  - Diff-Liste der weggefallenen Posts inkl. Abbruchgrund
  - KEINE Rohdaten ausserhalb des Rechtsrahmens: Ausgabe ist kuratiert-klein.
"""
import os, re, json, glob, hashlib, datetime, html as _html

SRC = "fb_export"
CUR = "facebook_posts.md"
OUT = os.path.join(SRC, "AUDIT.md")

boiler = re.compile(r"(hat .*(geteilt|hochgeladen|aktualisiert|hinzugef|veröffentlicht)|"
                    r"shared a|added a|uploaded a|updated their|posted (a|an)|created an event|"
                    r"changed .*profile|became friends)", re.I)

def fix_mojibake(t):
    try: return t.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError): return t

def clean_text(t):
    t = fix_mojibake(t); t = _html.unescape(t)
    t = re.sub(r"https?://\S+", "", t); t = re.sub(r"www\.\S+", "", t)
    t = re.sub(r"\[[^\]]*\]\(https?://[^)]*\)", "", t)
    t = re.sub(r"[ \t]{2,}", " ", t); t = re.sub(r"\s*\n\s*", " ", t).strip()
    return t

def h(t): return hashlib.md5(t.lower().encode()).hexdigest()

def iter_posts(path):
    with open(path, encoding="utf-8") as fh: parsed = json.load(fh)
    items = parsed if isinstance(parsed, list) else (parsed.get("data") or [])
    for p in items:
        if not isinstance(p, dict): continue
        raw = ""
        for a in p.get("data", []):
            if isinstance(a, dict) and isinstance(a.get("post"), str) and len(a["post"].strip()) > 3:
                raw = a["post"]; break
        if not raw:
            t = p.get("title", "")
            if isinstance(t, str): raw = t
        ts = p.get("timestamp") or 0
        yield raw, ts

def main():
    cur = set()
    if os.path.exists(CUR):
        for p in re.split(r"\n\s*\n+", open(CUR, encoding="utf-8").read()):
            p = p.strip()
            if p: cur.add(h(p))

    files = sorted(glob.glob(os.path.join(SRC, "**", "*.json"), recursive=True))
    lines = ["# AUDIT: Export vs. facebook_posts.md", "",
             f"Quellen: {len(files)} JSON-Dateien | Kuratierter Korpus: {len(cur)} Einträge", ""]
    total = kept = 0
    dropped = {"link_only": 0, "boilerplate": 0, "zu_kurz": 0, "leer": 0}
    samples = {k: [] for k in dropped}
    years = {}

    for f in files:
        n_file = 0
        for raw, ts in iter_posts(f):
            n_file += 1
            if ts:
                y = datetime.datetime.utcfromtimestamp(ts).year
                years[y] = years.get(y, 0) + 1
            if not raw or not raw.strip(): dropped["leer"] += 1; continue
            if boiler.search(raw) and len(raw) < 200: dropped["boilerplate"] += 1; continue
            cleaned = clean_text(raw)
            if len(cleaned) <= 3:
                reason = "link_only" if re.search(r"https?://|www\.", raw) else "zu_kurz"
                dropped[reason] += 1
                if len(samples[reason]) < 10: samples[reason].append(raw[:120])
                continue
            total += 1
            if h(cleaned) in cur: kept += 1
        lines.append(f"- `{os.path.basename(f)}`: {n_file} Einträge")

    lines += ["", "## Ergebnis", "",
              f"- Text-Posts im Export (nach Filterlogik verwertbar): **{total}**",
              f"- Davon im kuratierten Korpus enthalten: **{kept}**",
              f"- **Differenz: {total - kept}** (im Export, aber nicht im Korpus — oder umgekehrt verändert)",
              "", "## Weggefallene Posts nach Grund", ""]
    for k, v in dropped.items():
        lines.append(f"- {k}: **{v}**")
    lines += ["", "### Beispiele (gekürzt)", ""]
    for k, ss in samples.items():
        for s in ss:
            lines.append(f"- [{k}] {s!r}")
    if years:
        lines += ["", "## Zeitstempel-Verteilung (Jahr: Anzahl Posts)", ""]
        for y in sorted(years): lines.append(f"- {y}: {years[y]}")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print("geschrieben:", OUT, "| verwertbar:", total, "| im Korpus:", kept, "| Diff:", total-kept)

if __name__ == "__main__":
    main()
