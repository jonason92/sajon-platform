# -*- coding: utf-8 -*-
"""Build the Living Archive portal.

Builds the archive book plus every work (works/*) and every transcription
(transkripte/*) — each as its own Jupyter Book — into `_site/<path>/`, then
writes a portal `_site/index.html` that links to every collection.

Run the deploy workflow, not manually (requires `jupyter-book`, network).
"""
import os, re, shutil, subprocess, sys, html as _html, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "_site")

# (source dir, site subpath, section label) for the archive collections
ARCHIVE = ("book", "archive", "Aphorismen & Schriften")
COLLECTIONS = [
    ("works", "works", "Studienarbeiten"),
    ("transkripte", "transkripte", "Videotranskriptionen"),
]


def is_book(d):
    return os.path.isfile(os.path.join(d, "_config.yml")) and os.path.isfile(os.path.join(d, "_toc.yml"))


def book_title(path, fallback):
    cfg = os.path.join(path, "_config.yml")
    if os.path.exists(cfg):
        m = re.search(r"^title:\s*[\"']?(.+?)['\"]?\s*$", open(cfg, encoding="utf-8").read(), re.M)
        if m:
            return m.group(1).strip()
    return fallback


def build_book(src, dst_rel, required=True):
    print("build", src, "->", dst_rel)
    rel = os.path.relpath(src, ROOT)
    try:
        subprocess.run(["jupyter-book", "build", rel], cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        if required:
            raise
        print("  !! skip (build failed):", src)
        return False
    html_dir = os.path.join(src, "_build", "html")
    if not os.path.isdir(html_dir):
        if required:
            raise SystemExit(f"build failed: no output at {html_dir}")
        print("  !! skip (no output):", src)
        return False
    dst = os.path.join(SITE, dst_rel)
    shutil.copytree(html_dir, dst, dirs_exist_ok=True)
    return True


def discover(collection_dir):
    out = []
    for d in sorted(glob.glob(os.path.join(ROOT, collection_dir, "*"))):
        name = os.path.basename(d)
        # skip the copyable example templates (kept in repo only)
        if name.lower().startswith("beispiel") or "template" in name.lower():
            continue
        if os.path.isdir(d) and not name.endswith("README.md") and is_book(d):
            out.append((name, d))
    return out


def card(href, title, header):
    # header: small blue line (author · place · year); title: big serif black
    return (f'<a class="card" href="{_html.escape(href)}">'
            f'<span class="card-meta">{_html.escape(header)}</span>'
            f'<span class="card-title">{_html.escape(title)}</span></a>')


Werkstatt_CSS = """
body{font-family:Georgia,'Times New Roman',serif;max-width:960px;margin:0 auto;padding:2.5rem 1.2rem;color:#1a1a1a;background:#fdfcf9}
a{color:#2a4d8f;text-decoration:none}a:hover{text-decoration:underline}
h1{font-size:1.9rem;margin-bottom:.2rem}
p.leit{color:#555;font-style:italic;max-width:44em}
h2.cluster{margin-top:2.2rem;border-bottom:1px solid #d8d2c4;padding-bottom:.3rem;font-size:1.25rem}
.wcard{background:#fff;border:1px solid #e3ddcf;border-radius:8px;padding:.9rem 1.1rem;margin:.7rem 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.wcard h3{margin:.1rem 0 .3rem;font-size:1.08rem}
.wmeta{font-size:.83rem;color:#6b6353;margin-bottom:.35rem}
.wabs{font-size:.95rem;color:#333}
.wlink{font-size:.85rem}
nav.top{font-size:.9rem;margin-bottom:1.5rem}
footer{margin-top:3rem;font-size:.8rem;color:#8a8272;border-top:1px solid #e3ddcf;padding-top:.8rem}
"""


def werk_card(slug, w):
    bits = [b for b in [w.get("typ", ""), w.get("universitaet", ""), w.get("kurs", "")] if b]
    if w.get("betreuung"):
        bits.append("Betreuung: " + w["betreuung"])
    jy = [b for b in [str(w.get("ort", "") or ""), str(w.get("jahr", "") or "")] if b]
    if jy:
        bits.append(" · ".join(jy))
    meta = _html.escape(" · ".join(bits))
    return (f'<div class="wcard"><h3><a href="./{slug}/">{_html.escape(w["titel"])}</a></h3>'
            f'<div class="wmeta">{meta}</div>'
            f'<div class="wabs">{_html.escape(w["abstract"])}</div></div>')


def build_works_index():
    """Generate _site/works/index.html — the Studienwerkstatt catalogue."""
    import json as _json
    kpath = os.path.join(ROOT, "works", "_katalog.json")
    if not os.path.isfile(kpath):
        return
    kat = _json.load(open(kpath, encoding="utf-8"))
    werke = kat.get("werke", {})
    order = ["Nietzsche-Kreis", "Technik · Singularität · Digitalisierung",
             "Universität & Wissenschaftsforschung", "Einzelgänger",
             "Seminar-Protokolle", "Handouts"]
    clusters = {}
    for slug, w in werke.items():
        clusters.setdefault(w.get("cluster", "Einzelgänger"), []).append((slug, w))
    jahre = [w["jahr"] for w in werke.values() if isinstance(w.get("jahr"), int)]
    span = f"{min(jahre)}–{max(jahre)}" if jahre else ""
    parts = [f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Studienwerkstatt — Die Jahre des Lernens</title><style>{Werkstatt_CSS}</style></head><body>
<nav class="top"><a href="../">← Lebendiges Archiv</a></nav>
<h1>Studienwerkstatt — Die Jahre des Lernens</h1>
<p class="leit">{len(werke)} Arbeiten · {span} · alle von Jonas Hässig (JH), dem Studenten von damals.
Jede Karte nennt Universität, Kurs und Betreuungsperson — die Kommentare der Betreuerinnen und Betreuer
folgen; der Expertendialog bleibt offen.</p>"""]
    for cl in order:
        if cl not in clusters:
            continue
        parts.append(f'<h2 class="cluster">{_html.escape(cl)} ({len(clusters[cl])})</h2>')
        for slug, w in sorted(clusters[cl], key=lambda x: (x[1].get("jahr") or 9999, x[1]["titel"])):
            parts.append(werk_card(slug, w))
    parts.append("<footer>Studienwerkstatt · sajon living archive · generiert aus works/_katalog.json</footer></body></html>")
    os.makedirs(os.path.join(SITE, "works"), exist_ok=True)
    open(os.path.join(SITE, "works", "index.html"), "w", encoding="utf-8").write("\n".join(parts))
    print("wrote works/index.html")


def build_transkripte_index():
    """Generate _site/transkripte/index.html — the Expeditionen shelf."""
    items = [n for n, p in discover("transkripte")]
    cards = "".join(
        f'<div class="wcard"><h3><a href="./{n}/">{_html.escape(n.replace("-", " ").title())}</a></h3>'
        f'<div class="wmeta">Videotranskription</div></div>' for n in items) or \
        '<p class="leit">Die ersten Expeditionen sind unterwegs — Transkripte folgen.</p>'
    page = f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Expeditionen — Videotranskriptionen</title><style>{Werkstatt_CSS}</style></head><body>
<nav class="top"><a href="../">← Lebendiges Archiv</a></nav>
<h1>Expeditionen — Videotranskriptionen</h1>
<p class="leit">Gespräche, Vorträge und Forschungsreisen in Textform — ein Schiff pro Expeditionsfahrt.
Weitere Expeditionen (02–04) sind in Vorbereitung.</p>
{cards}
<footer>Expeditionen · sajon living archive</footer></body></html>"""
    os.makedirs(os.path.join(SITE, "transkripte"), exist_ok=True)
    open(os.path.join(SITE, "transkripte", "index.html"), "w", encoding="utf-8").write(page)
    print("wrote transkripte/index.html")


def matomo_snippet():
    """Return the Matomo tracking snippet, or "" if disabled/unconfigured."""
    import json as _json
    cfg_path = os.path.join(ROOT, "matomo.json")
    try:
        cfg = _json.load(open(cfg_path, encoding="utf-8"))
    except Exception:
        return ""
    if not cfg.get("enabled") or "example.org" in cfg.get("url", ""):
        return ""
    url = cfg["url"].rstrip("/") + "/"
    sid = cfg["site_id"]
    return f"""<!-- Matomo -->
<script>
  var _paq = window._paq = window._paq || [];
  _paq.push(['disableCookies']);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {{
    var u='{url}';
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '{sid}']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  }})();
</script>
<!-- End Matomo Code -->"""


def inject_matomo():
    """Inject the Matomo snippet into every built HTML page (before </head>)."""
    snip = matomo_snippet()
    if not snip:
        print("matomo: disabled or unconfigured — skip injection")
        return
    n = 0
    for dirpath, _dirs, files in os.walk(SITE):
        for f in files:
            if not f.endswith(".html"):
                continue
            fp = os.path.join(dirpath, f)
            t = open(fp, encoding="utf-8", errors="ignore").read()
            if "matomo.php" in t or "</head>" not in t:
                continue
            open(fp, "w", encoding="utf-8").write(t.replace("</head>", snip + "\n</head>", 1))
            n += 1
    print(f"matomo: injected into {n} pages")


def md_to_html(md):
    """Minimal Markdown->HTML for the GaiaOS chapter pages (no external deps)."""
    out, in_code, in_list = [], False, False
    def inline(s):
        s = _html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
        return s
    for line in md.split("\n"):
        if line.strip().startswith("```"):
            if in_code:
                out.append("</code></pre>"); in_code = False
            else:
                if in_list: out.append("</ul>"); in_list = False
                out.append("<pre class='code'><code>"); in_code = True
            continue
        if in_code:
            out.append(_html.escape(line) + "\n"); continue
        s = line.strip()
        if not s:
            if in_list: out.append("</ul>"); in_list = False
            continue
        if s == "---":
            out.append("<hr>"); continue
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); continue
        if s.startswith("> "):
            out.append(f"<blockquote>{inline(s[2:])}</blockquote>"); continue
        if s.startswith("- "):
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(s[2:])}</li>"); continue
        out.append(f"<p>{inline(s)}</p>")
    if in_list: out.append("</ul>")
    if in_code: out.append("</code></pre>")
    return "\n".join(out)


GAIAOS_CSS = """
body{margin:0;background:#F8F7E5;color:#1D1D1D;font-family:Georgia,'Times New Roman',serif;line-height:1.65}
.wrap{max-width:760px;margin:0 auto;padding:3rem 1.3rem}
a{color:#1f6f6b}h1{font-size:1.9rem;line-height:1.25}h2{font-size:1.4rem;margin-top:2.4rem}
h3{font-size:1.12rem;margin-top:1.8rem}
nav.top,nav.prevnext{font-size:.9rem;color:#6b6353}
nav.prevnext{display:flex;justify-content:space-between;margin-top:3rem;border-top:1px solid #ddd5bd;padding-top:1rem}
pre.code{background:#1d1d1d;color:#F8F7E5;padding:1.1rem 1.2rem;border-radius:8px;overflow-x:auto;font-size:.86rem;line-height:1.5}
blockquote{border-left:3px solid #b39c4f;margin:1.2rem 0;padding:.2rem 1rem;color:#4a4436;font-style:italic}
code{background:#ece7d3;padding:.1em .3em;border-radius:4px;font-size:.9em}
pre.code code{background:none;padding:0;color:inherit}
hr{border:none;border-top:1px solid #ddd5bd;margin:2.2rem 0}
.meta{font-size:.85rem;color:#6b6353;font-style:italic}
.toc li{margin:.4rem 0}
footer{margin-top:3rem;border-top:1px solid #ddd5bd;padding-top:1rem;font-size:.8rem;color:#6b6353}
"""


GAIAOS_LANGS = {
    "de": {"dir": "", "hub_title": "GaiaOS — Die Tulpe ist kein Objekt",
           "teile": [("teil-1-2", "gaiaos-rohfassung-1-2.md", "§1–§2 · Der Fund & Anatomie eines Gebets-Programms"),
                     ("teil-3", "gaiaos-rohfassung-3.md", "§3 · Gaia ohne Namen"),
                     ("teil-4", "gaiaos-rohfassung-4.md", "§4 · Kognitive Autopoiesis"),
                     ("teil-5", "gaiaos-rohfassung-5.md", "§5 · Die Ironie der Gegenwart"),
                     ("teil-6", "gaiaos-rohfassung-6.md", "§6 · Coda: Adressat = ALLE")]},
    "zh": {"dir": "zh/", "hub_title": "蓋亞靈樞 — 郁金香非物也",
           "teile": [("teil-1-2", "translations/gaiaos-zh-teil-1-2.md", "§1–§2 · 發現 · 禱儀經解")]},
    "en": {"dir": "en/", "hub_title": "GaiaOS — The Tulip Is No Object",
           "teile": [("teil-1-2", "translations/gaiaos-en-teil-1-2.md", "§1–§2 · The Find & Anatomy of a Prayer-Program")]},
}


def build_gaiaos():
    """Publish GaiaOS chapter 2.2 as designed reading pages (_site/gaiaos/[, zh/, en/])."""
    exp = os.path.join(ROOT, "exposee")
    for lang, cfg in GAIAOS_LANGS.items():
        pages = []
        for slug, fname, titel in cfg["teile"]:
            fp = os.path.join(exp, fname)
            if not os.path.isfile(fp):
                break
            body = md_to_html(open(fp, encoding="utf-8").read())
            pages.append((slug, titel, body))
        if not pages:
            continue
        dst = os.path.join(SITE, "gaiaos", cfg["dir"].rstrip("/"))
        os.makedirs(dst, exist_ok=True)
        n = len(pages)
        for i, (slug, titel, body) in enumerate(pages):
            prev_l = (f'<a href="{pages[i-1][0]}.html">← {pages[i-1][1]}</a>' if i else
                      '<a href="index.html">← Index / 目次 / Übersicht</a>')
            next_l = (f'<a href="{pages[i+1][0]}.html">{pages[i+1][1]} →</a>' if i < n-1 else
                      '<a href="index.html">Index / 目次 →</a>')
            page = f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html.escape(cfg["hub_title"])} — {_html.escape(titel)}</title><style>{GAIAOS_CSS}</style></head><body><div class="wrap">
<nav class="top"><a href="../{'../' if lang != 'de' else ''}">← Living Archive</a> · <a href="index.html">{_html.escape(cfg["hub_title"])}</a></nav>
{body}
<nav class="prevnext">{prev_l}<span>{next_l}</span></nav>
<footer>GaiaOS · Chapter 2.2 of the Living Archive · JH, co-written with Kimi · sajon living archive</footer>
</div></body></html>"""
            open(os.path.join(dst, slug + ".html"), "w", encoding="utf-8").write(page)
        toc = "\n".join(f'<li><a href="{s}.html">{_html.escape(t)}</a></li>' for s, t, _ in pages)
        hub = f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html.escape(cfg["hub_title"])}</title><style>{GAIAOS_CSS}</style></head><body><div class="wrap">
<nav class="top"><a href="../{'../' if lang != 'de' else ''}">← Living Archive</a></nav>
<h1>{_html.escape(cfg["hub_title"])}</h1>
<ul class="toc">{toc}</ul>
<hr>
<p class="meta">Languages: <a href="../">Deutsch</a> · <a href="../zh/">文言</a> · <a href="../en/">Shakespearian English</a></p>
<footer>GaiaOS · Chapter 2.2 · sajon living archive</footer>
</div></body></html>"""
        open(os.path.join(dst, "index.html"), "w", encoding="utf-8").write(hub)
        print(f"wrote gaiaos/{cfg['dir']} ({lang}):", len(pages) + 1, "pages")


def group_for(t):
    tl = t.lower()
    if any(k in tl for k in ["ba-arbeit", "masterarbeit", "hausarbeit", "ma-arbeit",
                             "monismus", "biotech", "digitalisierung"]):
        return "Abschluss- & Hausarbeiten"
    if tl.startswith("protokoll") or "kolloquium" in tl:
        return "Protokolle"
    if tl.startswith("handout"):
        return "Handouts"
    if tl.startswith("lekt"):
        return "Lektüreessays"
    return "Essays & Seminararbeiten"


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE, exist_ok=True)

    # per-work metadata (place, year) for the card headers
    meta = {}
    mpath = os.path.join(ROOT, "works", "_meta.json")
    if os.path.exists(mpath):
        import json as _json
        try:
            meta = _json.load(open(mpath, encoding="utf-8"))
        except Exception:
            meta = {}

    # copy shared assets (logo / optional theme overrides) so the portal can use them
    assets_src = os.path.join(ROOT, "assets")
    if os.path.isdir(assets_src):
        shutil.copytree(assets_src, os.path.join(SITE, "assets"), dirs_exist_ok=True)

    # also publish the standalone interactive single-page book
    interactive = os.path.join(ROOT, "das-lebendige-archiv-buch.html")
    if os.path.exists(interactive):
        shutil.copy2(interactive, os.path.join(SITE, "das-lebendige-archiv-buch.html"))

    # Wissensbasis: statische Seiten & Bibliothek direkt publizieren
    for rel in ("wissensatlas.html", "jonason-lebendiges-archiv.html"):
        src = os.path.join(ROOT, rel)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(SITE, rel))
    # Notizen-Atlas (2008-2026) publizieren
    src = os.path.join(ROOT, "notizen")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "notizen"), dirs_exist_ok=True)

    for rel in ("bibliothek", "infografik"):
        src = os.path.join(ROOT, rel)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(SITE, rel), dirs_exist_ok=True)

    # Methodik-Seite publizieren
    src = os.path.join(ROOT, "methodik")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "methodik"), dirs_exist_ok=True)

    # Expeditionen-Seite publizieren
    src = os.path.join(ROOT, "expeditionen")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "expeditionen"), dirs_exist_ok=True)

    # Studien (Essays mit Quellenapparat) publizieren
    src = os.path.join(ROOT, "studien")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "studien"), dirs_exist_ok=True)

    # Traumwald (interaktive Seite) publizieren
    src = os.path.join(ROOT, "garten")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "garten"), dirs_exist_ok=True)

    # Spenden-Seite publizieren
    src = os.path.join(ROOT, "spenden")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "spenden"), dirs_exist_ok=True)

    # Erschliessung (Quellenkarten) publizieren
    src = os.path.join(ROOT, "erschliessung")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "erschliessung"), dirs_exist_ok=True)

    # Exposés (Kapitel-Entwürfe) publizieren
    src = os.path.join(ROOT, "exposee")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "exposee"), dirs_exist_ok=True)

    # fb_export (Audit-Bericht, ohne Zip) publizieren
    src = os.path.join(ROOT, "fb_export")
    if os.path.isdir(src):
        os.makedirs(os.path.join(SITE, "fb_export"), exist_ok=True)
        for f in ("ABGLEICH-BERICHT.md", "README.md"):
            fp = os.path.join(src, f)
            if os.path.isfile(fp):
                shutil.copy2(fp, os.path.join(SITE, "fb_export", f))

    # Quellen (Textcorpora, gemeinfreie Primärtexte) publizieren
    src = os.path.join(ROOT, "quellen")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(SITE, "quellen"), dirs_exist_ok=True)

    # archive book
    build_book(os.path.join(ROOT, ARCHIVE[0]), "archive")
    archive_cards = card("archive/", ARCHIVE[2], "JH · Der Kern")
    archive_cards += card("notizen/", "Notizen-Atlas · 2008–2026", "JH · 315 Notizen · 10 Themen")
    archive_cards += card("methodik/", "Methodik · Wie aus Notizen Wissenschaft wird", "JH · 7 Arbeitsweisen")
    archive_cards += card("expeditionen/", "Expeditionen · Frühere Forschungsreisen", "JH · 4 Chat-Projekte")
    archive_cards += card("studien/novalis-enzyklopaedistik/", "Studie · Novalis\u2019 Enzyklopädistik", "JH · Essay mit Quellenapparat")
    archive_cards += card("quellen/brouillon/", "Brouillon-Browser · Novalis interaktiv", "JH · 502 Aufzeichnungen · 36 Rubriken")
    archive_cards += card("garten/", "Traumwald · Märchenwald & Traumgenerator", "JH · interaktiv · Ost-Brücke")
    archive_cards += card("erschliessung/", "Erschliessung · 200 Quellenkarten", "JH · Q1–Q200 · Volltext-Novalis")
    archive_cards += card("exposee/", "Exposés · Kapitel-Entwürfe", "JH · GaiaOS & weitere")
    archive_cards += card("gaiaos/", "GaiaOS · Kapitel 2.2 — Die Tulpe ist kein Objekt", "JH · erstes vollständiges Kapitel · §1–§6")
    archive_cards += card("spenden/", "Unterstützen · sajon gmbh", "Patronschaft · Spende · Kontakt")
    archive_cards += card("works/", "Studienwerkstatt · Die Jahre des Lernens", "JH · 37 Arbeiten · 2013–2023")
    archive_cards += card("transkripte/", "Expeditionen · Videotranskriptionen", "JH · in Vorbereitung")

    # collections
    collection_html = []
    n_counts = {"works": 0, "transkripte": 0}
    for src_dir, rel, label in COLLECTIONS:
        items = discover(src_dir)
        n_counts.setdefault(rel, len(items))
        grouped = {}   # group -> list of card html
        for name, path in items:
            if not build_book(path, os.path.join(rel, name), required=False):
                continue   # only show successfully built works
            t = book_title(path, name.replace("-", " ").title())
            m = meta.get(name, {})
            parts = [x for x in [m.get("place", ""), m.get("year", "")] if x]
            header = "JH · " + " · ".join(parts) if parts else "JH"
            g = group_for(t)
            grouped.setdefault(g, []).append(
                card(os.path.join(rel, name) + "/", t, header))
        section = ""
        if grouped:
            order = ["Abschluss- & Hausarbeiten", "Essays & Seminararbeiten",
                     "Lektüreessays", "Protokolle", "Handouts"]
            parts = [f"<h2 class='sec-h'>{_html.escape(label)}</h2>"]
            for g in order:
                if g in grouped:
                    parts.append(f"<h3 class='sub-h'>{_html.escape(g)}</h3>")
                    parts.append(f"<div class='grid'>{''.join(grouped[g])}</div>")
            for g, cards in grouped.items():
                if g not in order:
                    parts.append(f"<h3 class='sub-h'>{_html.escape(g)}</h3>")
                    parts.append(f"<div class='grid'>{''.join(cards)}</div>")
            section = "\n".join(parts)
        collection_html.append(section)

    # catalogue index pages for the two collections
    build_works_index()
    build_transkripte_index()
    build_gaiaos()

    # Matomo-Tracking in alle Seiten injizieren (wenn in matomo.json aktiviert)
    inject_matomo()

    # portal
    portal = (TEMPLATE
              .replace("@ARCHIVE@", archive_cards)
              .replace("@COLLECTIONS@", "\n".join(collection_html))
              .replace("@N_WORKS@", str(n_counts.get("works", 0)))
              .replace("@N_TRANSK@", str(n_counts.get("transkripte", 0))))
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(portal)
    print("wrote", os.path.join(SITE, "index.html"))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Das Lebendige Archiv</title>
<link rel="stylesheet" href="assets/theme.css" />
<link rel="stylesheet" href="assets/la.css" />
<link rel="icon" href="assets/logo.png" />
<style>
  :root{
    --paper:#f6f1e7; --paper-2:#efe7d7; --ink:#1b1712; --ink-soft:#4a4238;
    --muted:#7a7062; --line:#dcd2bf; --brass:#b8742a; --brass-soft:#d9a05b;
    --teal:#1f6f6b; --teal-soft:#3f8f8a; --glow:rgba(217,160,91,.35);
    --card:#fffdf8; --radius:16px; --shadow:0 10px 30px rgba(27,23,18,.10);
    --serif:Georgia,"Iowan Old Style","Times New Roman",serif;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  }
  html.dark{--paper:#16120e;--paper-2:#1d1813;--ink:#f2ead9;--ink-soft:#cfc3ae;
    --muted:#948a77;--line:#3a3228;--card:#201a13;--glow:rgba(217,160,91,.22)}
  *{box-sizing:border-box}
  body{margin:0;font-family:var(--sans);color:var(--ink);background:var(--paper);line-height:1.6;-webkit-font-smoothing:antialiased}
  ::selection{background:var(--brass-soft);color:#fff}
  header{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:1rem;
    padding:.8rem clamp(1rem,4vw,2.5rem);background:color-mix(in srgb,var(--paper) 84%,transparent);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .brand{display:flex;align-items:center;gap:.6rem;font-family:var(--serif);font-weight:700;letter-spacing:.3px}
  .brand img{width:34px;height:34px;border-radius:8px;background:transparent}
  html.dark .brand img{filter:invert(1)}   /* Sajon-Fisch (schwarz) im Dunkelmodus weiss */
  .iconbtn{margin-left:auto;border:1px solid var(--line);background:var(--card);color:var(--ink);
    border-radius:999px;padding:.35rem .7rem;font-size:.85rem;cursor:pointer}
  .hero{padding:clamp(3rem,8vw,6rem) clamp(1rem,5vw,4rem);overflow:hidden;position:relative}
  .hero::before{content:"";position:absolute;inset:-20%;background:
    radial-gradient(circle at 15% 20%,var(--glow),transparent 45%),
    radial-gradient(circle at 85% 70%,rgba(31,111,107,.18),transparent 50%);
    filter:blur(20px);animation:drift 18s ease-in-out infinite alternate}
  @keyframes drift{from{transform:translate(-2%,-1%)}to{transform:translate(2%,2%)}}
  .hero-inner{position:relative;max-width:1080px;margin:0 auto}
  .eyebrow{font-family:var(--mono,ui-monospace,Consolas,monospace);font-size:.76rem;letter-spacing:.18em;
    text-transform:uppercase;color:var(--teal);display:inline-flex;align-items:center;gap:.5rem;margin-bottom:1rem}
  .eyebrow::before{content:"";width:22px;height:1px;background:var(--teal)}
  h1{font-family:var(--serif);font-weight:700;font-size:clamp(1.9rem,4.6vw,3.4rem);line-height:1.08;margin:0 0 1.1rem;letter-spacing:-.02em}
  .lead{font-size:clamp(1rem,1.5vw,1.2rem);color:var(--ink-soft);max-width:64ch;margin:0 0 1.6rem}
  .stats{display:flex;flex-wrap:wrap;gap:2rem;margin-top:.4rem}
  .stat .stat-num{font-family:var(--serif);font-size:2.2rem;font-weight:700;color:var(--brass);line-height:1;display:block}
  .stat .stat-lbl{font-size:.82rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
  main{max-width:1080px;margin:0 auto;padding:clamp(1rem,5vw,3rem) clamp(1rem,5vw,3rem)}
  .sec-h{font-family:var(--serif);font-size:clamp(1.3rem,2.4vw,1.8rem);margin:2.5rem 0 1rem;color:var(--brass)}
  .sub-h{font-family:var(--mono,ui-monospace,Consolas,monospace);font-size:.85rem;letter-spacing:.08em;
    text-transform:uppercase;color:var(--teal);margin:1.6rem 0 .7rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}
  .card{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
    padding:1.2rem 1.3rem;color:var(--ink);text-decoration:none;transition:.22s}
  .card:hover{border-color:var(--brass-soft);transform:translateY(-3px);box-shadow:var(--shadow)}
  .card-meta{display:block;font-family:var(--mono,ui-monospace,Consolas,monospace);font-size:.72rem;
    letter-spacing:.12em;color:var(--teal);text-transform:uppercase;margin-bottom:.5rem}
  .card-title{display:block;font-family:var(--serif);font-size:1.5rem;font-weight:700;color:var(--ink);
    line-height:1.12;letter-spacing:-.01em}
  .card p{color:var(--muted);font-size:.9rem;margin:.4rem 0 0}
  footer{border-top:1px solid var(--line);padding:2rem;text-align:center;color:var(--muted);font-size:.85rem}
</style>
</head>
<body data-section="portal">
<header>
  <span class="brand"><img src="assets/logo.png" alt="Logo" /> Das Lebendige Archiv</span>
  <button class="iconbtn" id="dm" title="Dunkelmodus">&#9681;</button>
</header>

<section class="hero">
  <div class="hero-inner">
    <span class="eyebrow">Portal &middot; sammlungs&uuml;bergreifend</span>
    <h1>Das Lebendige Archiv</h1>
    <p class="lead">Pers&ouml;nliche Aphorismen, Schriften, Videotranskriptionen und Studienarbeiten &mdash;
      jede Sammlung und jede Arbeit als eigenes, lesbares und durchsuchbares Buch.</p>
    <div class="stats">
      <div class="stat"><span class="stat-num">@N_WORKS@</span><span class="stat-lbl">Studienarbeiten</span></div>
      <div class="stat"><span class="stat-num">@N_TRANSK@</span><span class="stat-lbl">Transkriptionen</span></div>
      <div class="stat"><span class="stat-num">1</span><span class="stat-lbl">Aphorismen &amp; Schriften</span></div>
    </div>
  </div>
</section>

<main>
  <h2 class="sec-h">Die Wissensbasis</h2>
  <div class="grid">
    <a class="card" href="wissensatlas.html"><span class="card-meta">Atlas</span><span class="card-title">Der Wissensatlas</span><p>Bibliothek &harr; Plattform: 782 Objekte, 5 Wissenszweige, 8 S&auml;ulen.</p></a>
    <a class="card" href="bibliothek/index.html"><span class="card-meta">782 Objekte</span><span class="card-title">Die Bibliothek</span><p>Durchsuchbarer Index deines Studiums (CAS/MAS ALIS 2024&ndash;2026).</p></a>
    <a class="card" href="infografik/"><span class="card-meta">Software-Mix</span><span class="card-title">Die Infografik</span><p>Das &Ouml;kosystem in Ebenen &mdash; interaktiv &amp; einbettbar.</p></a>
  </div>

  <h2 class="sec-h">Der Kern des Archivs</h2>
  <div class="grid">@ARCHIVE@</div>
  @COLLECTIONS@
</main>

<footer>Das Lebendige Archiv &middot; erweitert sich &mdash; jede Sammlung ist ein eigenes Buch.
  &middot; <a href="das-lebendige-archiv-buch.html" style="color:var(--teal)">Interaktive Einzelseite</a>
  &middot; <a href="jonason-lebendiges-archiv.html" style="color:var(--teal)">Bibliothek der Zukunft (Landing)</a>
  &middot; <a href="https://jonason92.github.io/sajon-publishing/" style="color:var(--teal)">Sajon Publishing ↗</a></footer>

<script>
  var root=document.documentElement;
  if(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches){
    root.classList.add('dark');document.getElementById('dm').textContent='\u25D1';}
  document.getElementById('dm').addEventListener('click',function(){
    var d=root.classList.toggle('dark');
    document.getElementById('dm').textContent=d?'\u25D1':'\u25D0';});
</script>
<script src="assets/la.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
