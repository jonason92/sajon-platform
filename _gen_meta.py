# -*- coding: utf-8 -*-
"""Best-effort metadata (place + year) per study work, written to works/_meta.json.
Used by the portal card header. 'JH' is applied as the author code in the portal.
"""
import glob, os, re, json

PLACE_RE = re.compile(r"(Universität\s+[A-Za-zÄÖÜäöü\- ]+|University|ETH\s+Zürich|"
                      r"Fachhochschule|Hochschule|PH\s+Bern|Institut\s+[A-Za-z]|"
                      r"Universität\s+Luzern|Universität\s+Basel)", re.I)
YEAR_RE = re.compile(r"(?:19|20)\d{2}")

meta = {}
for d in sorted(glob.glob("works/*")):
    slug = os.path.basename(d)
    intro = os.path.join(d, "intro.md")
    if not os.path.exists(intro):
        continue
    txt = open(intro, encoding="utf-8").read()
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    place = ""
    for ln in lines:
        if ln.startswith("title:") or ln.startswith("#") or ":" in ln[:12]:
            continue
        if PLACE_RE.search(ln) and len(ln) < 70:
            place = ln
            break
    years = YEAR_RE.findall(txt)
    year = years[0] if years else ""
    meta[slug] = {"place": place, "year": year}

with open("works/_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("wrote works/_meta.json with", len(meta), "entries")
for slug, m in list(meta.items())[:6]:
    print(" ", slug, "->", m)
