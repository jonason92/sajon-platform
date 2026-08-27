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

    # archive book
    build_book(os.path.join(ROOT, ARCHIVE[0]), "archive")
    archive_cards = card("archive/", ARCHIVE[2], "JH · Der Kern")

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
<body>
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
  <h2 class="sec-h">Der Kern des Archivs</h2>
  <div class="grid">@ARCHIVE@</div>
  @COLLECTIONS@
</main>

<footer>Das Lebendige Archiv &middot; erweitert sich &mdash; jede Sammlung ist ein eigenes Buch.
  &middot; <a href="das-lebendige-archiv-buch.html" style="color:var(--teal)">Interaktive Einzelseite</a></footer>

<script>
  var root=document.documentElement;
  if(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches){
    root.classList.add('dark');document.getElementById('dm').textContent='\u25D1';}
  document.getElementById('dm').addEventListener('click',function(){
    var d=root.classList.toggle('dark');
    document.getElementById('dm').textContent=d?'\u25D1':'\u25D0';});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
