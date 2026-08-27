# -*- coding: utf-8 -*-
"""Build the runnable interactive book HTML from the_book_2.73_buch.md.

Renders the curated book content into a single-file, self-contained HTML page
using the concept page's design language (warm paper / brass / teal, dark mode)
and its immersion modes (Autor:in, Der Text, Lexikon, Referenzen, Notizen,
Vorlesen).  The content comes from the markdown; no web dependency.
"""
import re, html as _html, os

SRC = "the_book_2.73_buch.md"
OUT = "das-lebendige-archiv-buch.html"

def esc(s: str) -> str:
    return _html.escape(s, quote=True)

# ----------------------------------------------------------------------------
# Parse the markdown into a lightweight structure.
# ----------------------------------------------------------------------------
def parse(text: str):
    lines = text.split("\n")
    title = ""
    lead = ""
    for ln in lines:
        if ln.startswith("# ") and not title:
            title = ln[2:].strip()
        elif ln.startswith(">") and not lead:
            lead = ln[1:].strip()
        if title and lead:
            break

    sections = {}          # top-level heading text -> list of blocks
    order = []             # ordered top-level headings
    cur = None
    for raw in lines:
        s = raw.rstrip()
        if not s.strip():
            continue
        if s.startswith("# "):          # top-level section
            name = s[2:].strip()
            sections[name] = []
            order.append(name)
            cur = name
            continue
        if cur is None:
            continue
        if s.startswith("---"):
            continue
        if s.startswith("## Inhalt"):    # skip the generated markdown TOC
            continue
        if s.startswith("### "):
            sections[cur].append(("h3", s[4:].strip()))
            continue
        if s.startswith("## "):
            sections[cur].append(("h2", s[3:].strip()))
            continue
        if s.startswith("- "):
            sections[cur].append(("bullet", s[2:].strip()))
            continue
        if s.startswith(">"):
            continue
        sections[cur].append(("p", s.strip()))
    return title, lead, order, sections

def render_passage(txt: str) -> str:
    return f"<p>{esc(txt.strip())}</p>"

def build():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    title, lead, order, sections = parse(text)

    # group "Der Text" into chapters (## heading -> blocks)
    grouped = []
    cur_chunk = None
    for blk in sections.get("Der Text", []):
        if blk[0] == "h2":
            cur_chunk = [blk[1], []]
            grouped.append(cur_chunk)
        elif blk[0] == "h3":
            if cur_chunk is None:
                cur_chunk = ["", []]; grouped.append(cur_chunk)
            cur_chunk[1].append(("h3", blk[1]))
        elif blk[0] == "p":
            if cur_chunk is None:
                cur_chunk = ["", []]; grouped.append(cur_chunk)
            cur_chunk[1].append(("p", blk[1]))
        elif blk[0] == "bullet":
            if cur_chunk is None:
                cur_chunk = ["", []]; grouped.append(cur_chunk)
            cur_chunk[1].append(("bullet", blk[1]))

    # chapter TOC + rendered sections
    toc_links, text_parts = [], []
    for i, (name, blocks) in enumerate(grouped, 1):
        anchor = f"kap-{i}"
        toc_links.append(f'<a class="toc-link" href="#{anchor}">{esc(name)}</a>')
        body = [f'<section class="chapter" id="{anchor}">',
                f'<h3 class="ch-title"><span class="ch-idx">{i:02d}</span> {esc(name)}</h3>']
        for b in blocks:
            if b[0] == "p":
                body.append(render_passage(b[1]))
            elif b[0] == "h3":
                body.append(f"<h4>{esc(b[1])}</h4>")
            elif b[0] == "bullet":
                body.append(f"<p class='list-item'>{esc(b[1])}</p>")
        body.append("</section>")
        text_parts.append("\n".join(body))
    toc_links = "\n".join(toc_links)
    text_body = "\n".join(text_parts)
    n_chapters = len(grouped)

    # render plain-passage sections (Autor:in, Notizen)
    def render_passages(name):
        out = []
        for blk in sections.get(name, []):
            if blk[0] == "p":
                out.append(render_passage(blk[1]))
            elif blk[0] == "h3":
                out.append(f"<h4>{esc(blk[1])}</h4>")
            elif blk[0] == "bullet":
                out.append(f"<p class='list-item'>{esc(blk[1])}</p>")
        return "\n".join(out)

    autor_html = render_passages("Autor:in")
    notizen_html = render_passages("Notizen")

    # lexicon
    lexicon = []
    for blk in sections.get("Lexikon", []):
        if blk[0] == "bullet":
            m = re.match(r"\*\*(.+?)\*\*\s*:\s*(.+)", blk[1])
            if m:
                lexicon.append((m.group(1).strip(), m.group(2).strip()))
            else:
                lexicon.append((blk[1], ""))
    lex_cards = []
    for term, gloss in lexicon:
        lex_cards.append(
            f'<button class="lex-card" data-term="{esc(term)}">'
            f'<span class="lex-term">{esc(term)}</span>'
            f'<span class="lex-gloss">{esc(gloss)}</span></button>')
    lexicon_html = "\n".join(lex_cards)

    # references
    refs = {"named": [], "literature": []}
    ref_mode = "named"
    for blk in sections.get("Referenzen & Quellen", []):
        if blk[0] == "p":
            if "Weiterführende Literatur" in blk[1]:
                ref_mode = "literature"
            elif "genannte Quellen" in blk[1] or "Genannte Quellen" in blk[1]:
                ref_mode = "named"
        elif blk[0] == "bullet":
            m = re.match(r"\*\*(.+?)\*\*\s*[–—]\s*„(.+?)“\s*:\s*(.+)", blk[1])
            if m:
                refs[ref_mode].append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
            else:
                m2 = re.match(r"\*\*(.+?)\*\*:(.+)", blk[1])
                if m2:
                    refs[ref_mode].append((m2.group(1).strip(), "", m2.group(2).strip()))
                else:
                    refs[ref_mode].append((blk[1], "", ""))
    ref_parts = ["<h4>Im Text genannte Quellen</h4>"]
    for author, ti, note in refs["named"]:
        t = f"&ndash; &bdquo;{esc(ti)}&ldquo;" if ti else ""
        ref_parts.append(f"<p class='list-item'><strong>{esc(author)}</strong>{t}: {esc(note)}</p>")
    ref_parts.append("<h4>Weiterführende Literatur</h4>")
    for author, ti, note in refs["literature"]:
        t = f"&ndash; &bdquo;{esc(ti)}&ldquo;" if ti else ""
        ref_parts.append(f"<p class='list-item'><strong>{esc(author)}</strong>{t}: {esc(note)}</p>")
    refs_html = "\n".join(ref_parts)

    # nav
    navmap = [("Autor:in","autorin"),("Der Text","text"),("Lexikon","lexikon"),
              ("Referenzen & Quellen","referenzen"),("Notizen","notizen")]
    nav = "\n".join(f'<a href="#{aid}">{esc(label)}</a>' for label, aid in navmap)

    doc = (TEMPLATE
           .replace("@TITLE@", esc(title))
           .replace("@LEAD@", esc(lead))
           .replace("@NAV@", nav)
           .replace("@TOCC@", toc_links)
           .replace("@AUTOR@", autor_html)
           .replace("@TEXTBODY@", text_body)
           .replace("@NCHAP@", str(n_chapters))
           .replace("@LEXICON@", lexicon_html)
           .replace("@REFS@", refs_html)
           .replace("@NOTIZEN@", notizen_html))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", OUT, "bytes:", os.path.getsize(OUT), "chapters:", n_chapters, "lexicon:", len(lexicon))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>@TITLE@</title>
<style>
  :root{
    --paper:#f6f1e7; --paper-2:#efe7d7; --ink:#1b1712; --ink-soft:#4a4238;
    --muted:#7a7062; --line:#dcd2bf; --brass:#b8742a; --brass-soft:#d9a05b;
    --teal:#1f6f6b; --teal-soft:#3f8f8a; --glow:rgba(217,160,91,.35);
    --card:#fffdf8; --radius:16px; --shadow:0 10px 30px rgba(27,23,18,.10);
    --serif:Georgia,"Iowan Old Style","Times New Roman",serif;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:ui-monospace,"Cascadia Code",Consolas,monospace;
  }
  html.dark{
    --paper:#16120e; --paper-2:#1d1813; --ink:#f2ead9; --ink-soft:#cfc3ae;
    --muted:#948a77; --line:#3a3228; --card:#201a13; --glow:rgba(217,160,91,.22);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;font-family:var(--sans);color:var(--ink);background:var(--paper);line-height:1.65;-webkit-font-smoothing:antialiased}
  ::selection{background:var(--brass-soft);color:#fff}

  header{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:1.2rem;
    padding:.8rem clamp(1rem,4vw,2.5rem);background:color-mix(in srgb,var(--paper) 84%,transparent);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .brand{display:flex;align-items:center;gap:.5rem;font-family:var(--serif);font-weight:700;letter-spacing:.3px}
  .brand .mark{width:24px;height:24px;border-radius:6px;background:linear-gradient(135deg,var(--brass),var(--teal));display:inline-block}
  nav{margin-left:auto;display:flex;gap:1rem;font-size:.9rem;flex-wrap:wrap}
  nav a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent;padding-bottom:2px}
  nav a:hover,nav a.active{color:var(--brass);border-color:var(--brass)}
  .iconbtn{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;
    padding:.35rem .7rem;font-size:.8rem;cursor:pointer}
  .iconbtn:hover{border-color:var(--brass);color:var(--brass)}

  .hero{position:relative;padding:clamp(3rem,8vw,6rem) clamp(1rem,5vw,4rem);overflow:hidden}
  .hero::before{content:"";position:absolute;inset:-20%;background:
    radial-gradient(circle at 15% 20%,var(--glow),transparent 45%),
    radial-gradient(circle at 85% 70%,rgba(31,111,107,.18),transparent 50%);
    filter:blur(20px);animation:drift 18s ease-in-out infinite alternate}
  @keyframes drift{from{transform:translate(-2%,-1%)}to{transform:translate(2%,2%)}}
  .hero-inner{position:relative;max-width:1080px;margin:0 auto}
  .eyebrow{font-family:var(--mono);font-size:.76rem;letter-spacing:.18em;text-transform:uppercase;
    color:var(--teal);display:inline-flex;align-items:center;gap:.5rem;margin-bottom:1rem}
  .eyebrow::before{content:"";width:22px;height:1px;background:var(--teal)}
  h1{font-family:var(--serif);font-weight:700;font-size:clamp(1.9rem,4.6vw,3.4rem);line-height:1.08;margin:0 0 1.1rem;letter-spacing:-.02em}
  .lead{font-size:clamp(1rem,1.5vw,1.2rem);color:var(--ink-soft);max-width:64ch;margin:0 0 1.6rem}
  .ctas{display:flex;flex-wrap:wrap;gap:.7rem}
  .btn{display:inline-flex;align-items:center;gap:.5rem;padding:.7rem 1.25rem;border-radius:999px;font-weight:600;
    font-size:.92rem;text-decoration:none;border:1px solid transparent;transition:.2s;cursor:pointer}
  .btn-primary{background:var(--ink);color:var(--paper);border-color:var(--ink)}
  .btn-primary:hover{background:var(--brass);border-color:var(--brass);color:#fff}
  .btn-ghost{border-color:var(--line);color:var(--ink)}
  .btn-ghost:hover{border-color:var(--brass);color:var(--brass)}

  .layout{max-width:1080px;margin:0 auto;padding:clamp(2rem,5vw,3.5rem) clamp(1rem,5vw,3rem);display:grid;
    grid-template-columns:250px 1fr;gap:2.5rem;align-items:start}
  .toc{position:sticky;top:76px;max-height:calc(100vh - 90px);overflow:auto;padding-right:.5rem}
  .toc h2{font-family:var(--serif);font-size:1.05rem;margin:0 0 .7rem;color:var(--brass)}
  .toc-link{display:block;padding:.35rem .5rem;border-radius:8px;color:var(--ink-soft);text-decoration:none;
    font-size:.88rem;border-left:2px solid transparent}
  .toc-link:hover,.toc-link.active{color:var(--brass);border-left-color:var(--brass);background:var(--paper-2)}

  .content section{scroll-margin-top:80px}
  .content .pane{margin-bottom:2.4rem}
  .pane h2{font-family:var(--serif);font-size:clamp(1.5rem,2.6vw,2rem);margin:0 0 1rem;letter-spacing:-.01em;display:flex;align-items:center;gap:.8rem}
  .pane h2 .idx{font-family:var(--serif);font-size:1.4rem;color:var(--brass-soft);opacity:.6}
  .chapter{margin-bottom:2.6rem;padding:1.4rem 1.5rem;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 0 0 transparent;transition:.25s}
  .chapter:hover{box-shadow:var(--shadow);border-color:var(--brass-soft)}
  .ch-title{font-family:var(--serif);font-size:1.25rem;margin:0 0 .8rem;display:flex;align-items:center;gap:.7rem}
  .ch-idx{font-family:var(--mono);font-size:.75rem;color:var(--teal);letter-spacing:.1em}
  .chapter p{margin:.6rem 0;color:var(--ink-soft);font-size:.98rem}
  .chapter h4{margin:.9rem 0 .4rem;font-family:var(--serif);font-size:1rem;color:var(--brass)}
  .chapter .list-item{margin:.35rem 0;padding-left:1rem;border-left:2px solid var(--line)}

  .lex-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1rem}
  .lex-card{text-align:left;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem;
    cursor:pointer;transition:.2s;font-family:var(--sans)}
  .lex-card:hover{border-color:var(--brass-soft);transform:translateY(-2px);box-shadow:var(--shadow)}
  .lex-term{display:block;font-family:var(--serif);font-weight:700;font-size:1rem;color:var(--ink);margin-bottom:.25rem}
  .lex-gloss{display:block;font-size:.85rem;color:var(--muted);line-height:1.4}
  .search{width:100%;max-width:340px;padding:.6rem .9rem;border:1px solid var(--line);border-radius:999px;
    font-size:.9rem;margin-bottom:1.2rem;background:var(--card);color:var(--ink)}
  .search:focus{outline:none;border-color:var(--brass)}
  .refs h4{font-family:var(--serif);margin:1.4rem 0 .6rem;font-size:1.05rem;color:var(--brass)}
  .refs .list-item{margin:.4rem 0;padding-left:1rem;border-left:2px solid var(--line);color:var(--ink-soft);font-size:.92rem}
  .pane>p{color:var(--ink-soft)}

  footer{border-top:1px solid var(--line);padding:2rem clamp(1rem,4vw,3rem);text-align:center;color:var(--muted);font-size:.85rem}

  .modal{position:fixed;inset:0;background:rgba(27,23,18,.5);display:none;align-items:center;justify-content:center;z-index:100;padding:1rem}
  .modal.show{display:flex}
  .modal-card{background:var(--card);border-radius:var(--radius);max-width:520px;width:100%;padding:1.6rem 1.8rem;box-shadow:var(--shadow)}
  .modal-card h3{font-family:var(--serif);margin:0 0 .5rem}
  .modal-card p{color:var(--ink-soft);margin:0}
  .modal-close{float:right;border:none;background:none;font-size:1.4rem;color:var(--muted);cursor:pointer}

  .hamb{display:none;margin-left:.6rem}
  @media (max-width:820px){
    .layout{grid-template-columns:1fr}
    .toc{position:static;max-height:none;display:none}
    .toc.open{display:block;margin-bottom:1.5rem}
    .hamb{display:inline-flex}
  }
</style>
</head>
<body>

<header>
  <span class="brand"><span class="mark"></span> Das Lebendige Archiv</span>
  <nav>@NAV@</nav>
  <button class="iconbtn" id="darkToggle" title="Dunkelmodus umschalten">◐</button>
  <button class="hamb iconbtn" id="hamb" title="Inhalt">☰</button>
</header>

<section class="hero">
  <div class="hero-inner">
    <span class="eyebrow">Ausführbares interaktives Buch</span>
    <h1>@TITLE@</h1>
    <p class="lead">@LEAD@</p>
    <div class="ctas">
      <a class="btn btn-primary" href="#kap-1">Zum Text</a>
      <a class="btn btn-ghost" href="#lexikon">Lexikon</a>
      <a class="btn btn-ghost" href="#autorin">Autor:in</a>
      <button class="btn btn-ghost" id="readAll">&#9654; Vorlesen</button>
    </div>
  </div>
</section>

<div class="layout">
  <aside class="toc" id="toc">
    <h2>Inhalt</h2>
    @TOCC@
  </aside>

  <main class="content">
    <section class="pane" id="autorin"><h2><span class="idx">A</span>Autor:in</h2>@AUTOR@</section>
    <section class="pane" id="text"><h2><span class="idx">B</span>Der Text &mdash; @NCHAP@ Kapitel</h2>@TEXTBODY@</section>
    <section class="pane" id="lexikon"><h2><span class="idx">C</span>Lexikon</h2>
      <p style="margin-top:-.5rem">Klicke einen Begriff für die Erklärung.</p>
      <input class="search" id="lexSearch" type="search" placeholder="Begriff suchen&hellip;" />
      <div class="lex-grid" id="lexGrid">@LEXICON@</div>
    </section>
    <section class="pane refs" id="referenzen"><h2><span class="idx">D</span>Referenzen &amp; Quellen</h2>@REFS@</section>
    <section class="pane" id="notizen"><h2><span class="idx">E</span>Notizen</h2>@NOTIZEN@</section>
  </main>
</div>

<footer>
  Aus dem Projekt „Das Lebendige Archiv“ &middot; erzeugt aus <code>the_book_2.73_buch.md</code> &middot; Inhalte im Originalton.
</footer>

<div class="modal" id="lexModal">
  <div class="modal-card">
    <button class="modal-close" id="lexClose" aria-label="Schließen">&times;</button>
    <h3 id="lexModalTerm"></h3>
    <p id="lexModalGloss"></p>
  </div>
</div>

<script>
  var root = document.documentElement;
  var toc = document.getElementById('toc');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.chapter'));
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc-link'));

  // initial + toggle dark mode
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    root.classList.add('dark');
    document.getElementById('darkToggle').textContent = '\u25D1';
  }
  document.getElementById('darkToggle').addEventListener('click', function () {
    var dark = root.classList.toggle('dark');
    document.getElementById('darkToggle').textContent = dark ? '\u25D1' : '\u25D0';
  });

  // mobile TOC
  document.getElementById('hamb').addEventListener('click', function () { toc.classList.toggle('open'); });

  // scrollspy
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        tocLinks.forEach(function (l) { l.classList.remove('active'); });
        var link = tocLinks.filter(function (l) { return l.getAttribute('href') === '#' + e.target.id; })[0];
        if (link) link.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  cards.forEach(function (c) { spy.observe(c); });

  // lexikon search
  document.getElementById('lexSearch').addEventListener('input', function () {
    var q = this.value.toLowerCase();
    document.querySelectorAll('.lex-card').forEach(function (card) {
      card.style.display = card.textContent.toLowerCase().indexOf(q) > -1 ? '' : 'none';
    });
  });

  // lexikon modal
  var modal = document.getElementById('lexModal');
  var mt = document.getElementById('lexModalTerm');
  var mg = document.getElementById('lexModalGloss');
  document.querySelectorAll('.lex-card').forEach(function (card) {
    card.addEventListener('click', function () {
      mt.textContent = card.querySelector('.lex-term').textContent;
      mg.textContent = card.querySelector('.lex-gloss').textContent;
      modal.classList.add('show');
    });
  });
  document.getElementById('lexClose').addEventListener('click', function () { modal.classList.remove('show'); });
  modal.addEventListener('click', function (e) { if (e.target === modal) modal.classList.remove('show'); });

  // Vorlesen (SpeechSynthesis)
  var speaking = false;
  function readText(txt) {
    if (!('speechSynthesis' in window)) { alert('Text-to-Speech wird von diesem Browser nicht unterst\u00FCtzt.'); return; }
    if (speaking) { window.speechSynthesis.cancel(); speaking = false; return; }
    var u = new SpeechSynthesisUtterance(txt);
    u.lang = 'de-DE'; u.rate = 0.95;
    u.onend = function () { speaking = false; };
    u.onerror = function () { speaking = false; };
    window.speechSynthesis.speak(u); speaking = true;
  }
  document.getElementById('readAll').addEventListener('click', function () {
    readText(document.getElementById('text').innerText);
  });
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
