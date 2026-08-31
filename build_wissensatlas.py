#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt wissensatlas.html: thematische Brücke Bibliothek <-> Plattform."""
import json, re
from collections import Counter

SRC = 'D:/jonason/bibliothek/casmas-alis-2024-2026.json'
OUT = 'D:/jonason/wissensatlas.html'

with open(SRC, encoding='utf-8') as f:
    records = json.load(f)

BRANCH_LABELS = {'0':'Quellen','1':'Informationswissenschaft','2':'Archivistik',
                 '3':'Bibliothekswissenschaft','4':'Modulbibliografien','':'ohne Sammlung'}

def esc(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def authors_str(rec):
    aus = rec.get('author') or rec.get('editor') or []
    out = []
    for a in aus:
        fam = a.get('family',''); giv = a.get('given','')
        n = fam if fam else ''
        if giv: n = (n + ', ' + giv) if n else giv
        if n: out.append(n)
    return '; '.join(out)

def year_of(rec):
    iss = rec.get('issued') or {}
    dp = iss.get('date-parts') or []
    if dp and dp[0] and dp[0][0]:
        return str(dp[0][0])
    return ''

def branch_of(rec):
    note = rec.get('note','')
    colls = []
    if note.startswith('Sammlungen: '):
        colls = [c.strip() for c in note[len('Sammlungen: '):].split(';') if c.strip()]
    b = ''
    for c in colls:
        m = re.match(r'^(\d)\.', c)
        if m: b = m.group(1); break
    return b, colls

items = []
for rec in records:
    b, colls = branch_of(rec)
    doi = rec.get('DOI',''); url = rec.get('URL','')
    link = ('https://doi.org/' + doi) if doi else url
    items.append({'t': rec.get('title','(ohne Titel)'), 'au': authors_str(rec),
                  'y': year_of(rec), 'ty': rec.get('type','document'), 'link': link, 'br': b})

bc = Counter(it['br'] for it in items)
total = len(items)
years = [int(it['y']) for it in items if it['y'].isdigit()]
yr_span = (str(min(years)) + '–' + str(max(years))) if years else '—'
n_books = sum(1 for it in items if it['ty']=='book')
n_art = sum(1 for it in items if it['ty']=='article-journal')
n_web = sum(1 for it in items if it['ty']=='webpage')

TYPE_PRIO = {'book':0,'article-journal':1,'chapter':2,'paper-conference':3,'thesis':4,'report':5,'webpage':6,'post-weblog':7,'document':8}

def works_for(b, n=3):
    ws = [it for it in items if it['br']==b and it['t'] and it['t']!='(ohne Titel)']
    ws.sort(key=lambda x: (TYPE_PRIO.get(x['ty'],9), -(int(x['y']) if x['y'].isdigit() else 0)))
    return ws[:n]

# --- Wissenszweige ---
branches_html = ''
for b in ['0','1','2','3','4']:
    branches_html += ('<a class="branch" href="bibliothek/index.html?branch=' + b + '">'
        '<span class="b-n">' + b + '</span><span class="b-name">' + BRANCH_LABELS[b] + '</span>'
        '<span class="b-count">' + str(bc.get(b,0)) + '</span></a>')

# --- Säulen ---
PILLARS = [
 {'n':'I','t':'Das Lebendige Buch','sub':'Interaktive &amp; lebende E-Books','desc':'Die neue Art, wie wir Bücher lesen, entsteht vor unseren Augen. Das Buch wird ausführbar: Autor:in-Ebene, Lexikon, Referenzen, Notizen, Szene, Diskussion — jede Ausgabe ein kleines Kunstwerk.','branches':['3','4']},
 {'n':'II','t':'Wissensdienstleistungen','sub':'Archiv- &amp; Bibliotheksbereich','desc':'Professionelle Dienste, informationswissenschaftlich fundiert: Erschließung, Katalogisierung, Bestandsaufbau, Langzeitarchivierung.','branches':['2','3']},
 {'n':'III','t':'Wissensmanagement','sub':'neu definiert','desc':'Aufbau einer neuartigen Plattform, die Wissensmanagement neu definiert — vom bibliografischen Objekt zum vernetzten, lebendigen Wissensraum.','branches':['1','4']},
 {'n':'IV','t':'Education','sub':'Lehre &amp; Vermittlung','desc':'Vermittlung und Lehre im Bibliotheks- und Informationsbereich — strukturierte Wissenspfade für die nächste Generation.','branches':['4','3']},
 {'n':'V','t':'Scientific Experimentation','sub':'Forschung &amp; Experiment','desc':'Wissenschaftliches Experimentieren: Information Retrieval, Digital Humanities, datengetriebene Textanalyse.','branches':['4','1']},
 {'n':'VI','t':'Textwissenschaft','sub':'kritische Textarbeit','desc':'Kritische Edition, Kommentar, Querverweise — die Textwissenschaft als Rückgrat der geistigen Arbeit.','branches':['1','4']},
 {'n':'VII','t':'Interface Mensch · KI','sub':'High-Grade Computation','desc':'Integration neuer Informationstechnologien im Interface von Mensch, Hochleistungsrechnen und KI — Digitalisierung, Retrieval, Agenten (MCP).','branches':['4','3']},
 {'n':'VIII','t':'Geistige Wiederbelebung','sub':'der Querschnitt','desc':'Das verbindende Anliegen: Wissen als lebendige Substanz — für eine geistige Wiederbelebung. (Magischer Idealismus.)','branches':['0','1','2','3','4']},
]

pillars_html = ''
for i, p in enumerate(PILLARS):
    ws = []; seen = set()
    for b in p['branches']:
        for it in works_for(b, 3):
            if it['t'] not in seen:
                seen.add(it['t']); ws.append(it)
        if len(ws) >= 4: break
    ws = ws[:4]
    works_html = ''
    for it in ws:
        y = ' (' + it['y'] + ')' if it['y'] else ''
        au = it['au']
        if it['link']:
            works_html += '<li><a href="' + esc(it['link']) + '" target="_blank" rel="noopener">' + esc(it['t']) + '</a><span class="m">' + esc(au) + y + '</span></li>'
        else:
            works_html += '<li><span>' + esc(it['t']) + '</span><span class="m">' + esc(au) + y + '</span></li>'
    if not works_html:
        works_html = '<li class="none">—</li>'
    links_html = ''.join('<a class="lnk" href="bibliothek/index.html?branch=' + b + '">' + BRANCH_LABELS[b] + ' ↗</a>' for b in p['branches'])
    open_cls = ' open' if i == 0 else ''
    pillars_html += (
        '<article class="pillar' + open_cls + '">'
        '<div class="p-head"><span class="p-n">' + p['n'] + '</span><div class="p-titles"><h3>' + p['t'] + '</h3><span class="p-sub">' + p['sub'] + '</span></div><span class="p-toggle">+</span></div>'
        '<div class="p-body"><p class="p-desc">' + p['desc'] + '</p>'
        '<div class="p-works"><span class="lbl">Beispielwerke</span><ul>' + works_html + '</ul></div>'
        '<div class="p-links">' + links_html + '</div></div>'
        '</article>'
    )

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Der Wissensatlas — Die Lebendige Bibliothek</title>
<style>
  :root{--paper:#f4eee2;--paper2:#ece3d0;--ink:#1c1713;--soft:#4a4237;--muted:#7a6f5e;--line:#d9ceb8;--red:#8c3a2e;--gold:#a8813c;--blue:#2f4858}
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;font-family:Georgia,"Iowan Old Style","Palatino Linotype","Book Antiqua",serif;background:var(--paper);color:var(--ink);line-height:1.65;-webkit-font-smoothing:antialiased}
  body::before{content:"";position:fixed;inset:0;pointer-events:none;background:radial-gradient(circle at 1px 1px, rgba(28,23,19,.045) 1px, transparent 0) 0 0/26px 26px;z-index:0}
  .wrap{max-width:1080px;margin:0 auto;padding:0 clamp(1rem,4vw,2.5rem);position:relative;z-index:1}
  header{border-bottom:1px solid var(--line);padding:1.6rem 0;display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap}
  header .mark{font-size:.78rem;letter-spacing:.32em;text-transform:uppercase;color:var(--red);font-family:system-ui,sans-serif;font-weight:600}
  header .title{font-size:1.35rem;font-style:italic;font-weight:700}
  .hero{padding:clamp(3rem,8vw,6rem) 0 2rem}
  .eyebrow{font-family:system-ui,sans-serif;font-size:.74rem;letter-spacing:.28em;text-transform:uppercase;color:var(--gold);margin-bottom:1.1rem}
  h1{font-size:clamp(2.1rem,5.5vw,3.7rem);line-height:1.06;font-weight:700;margin:0 0 1.3rem;letter-spacing:-.01em}
  h1 em{font-style:italic;color:var(--red)}
  .lede{font-size:clamp(1.05rem,1.7vw,1.25rem);color:var(--soft);max-width:62ch;font-style:italic}
  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border-block:1px solid var(--line);margin:2rem 0}
  .stat{padding:1.1rem .6rem;text-align:center}
  .stat + .stat{border-left:1px solid var(--line)}
  .stat .num{font-size:1.7rem;font-weight:700;color:var(--red)}
  .stat .lbl{font-family:system-ui,sans-serif;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
  .sec{padding:3.2rem 0}
  .sec-head{display:flex;align-items:baseline;gap:1rem;margin-bottom:1.6rem}
  .sec-head .rn{font-size:2.2rem;color:var(--gold);font-style:italic}
  .sec-head h2{font-size:clamp(1.5rem,3vw,2rem);margin:0}
  .sec-head .tag{margin-left:auto;font-family:system-ui,sans-serif;font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
  .branches{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.8rem}
  .branch{display:flex;align-items:center;gap:.7rem;text-decoration:none;color:var(--ink);background:var(--paper2);border:1px solid var(--line);padding:.9rem 1rem;border-radius:12px;transition:.2s}
  .branch:hover{border-color:var(--gold);transform:translateY(-2px)}
  .branch .b-n{font-size:1.4rem;font-style:italic;color:var(--red);min-width:1.2em}
  .branch .b-name{font-size:1rem;font-weight:600}
  .branch .b-count{margin-left:auto;font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted);background:var(--paper);border-radius:999px;padding:.15rem .6rem}
  .pillars{display:flex;flex-direction:column;gap:.8rem}
  .pillar{background:var(--paper2);border:1px solid var(--line);border-radius:14px;overflow:hidden}
  .pillar .p-head{display:flex;align-items:center;gap:1rem;padding:1rem 1.2rem;cursor:pointer}
  .pillar .p-n{font-size:1.6rem;font-style:italic;color:var(--gold);min-width:1.6em}
  .pillar .p-titles h3{margin:0;font-size:1.15rem}
  .pillar .p-sub{font-family:system-ui,sans-serif;font-size:.74rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
  .pillar .p-toggle{margin-left:auto;font-size:1.3rem;color:var(--red);transition:transform .25s;line-height:1}
  .pillar.open .p-toggle{transform:rotate(45deg)}
  .pillar .p-body{max-height:0;overflow:hidden;transition:max-height .4s ease}
  .pillar.open .p-body{max-height:600px}
  .pillar .p-body > *{margin:0 1.2rem 1rem}
  .pillar .p-desc{color:var(--soft);font-style:italic;padding-top:.2rem}
  .pillar .lbl{font-family:system-ui,sans-serif;font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
  .pillar .p-works ul{list-style:none;margin:.3rem 0 0;padding:0}
  .pillar .p-works li{padding:.25rem 0;border-bottom:1px dotted var(--line);font-size:.95rem}
  .pillar .p-works li a{color:var(--ink);text-decoration:none}
  .pillar .p-works li a:hover{color:var(--red)}
  .pillar .p-works li .m{display:block;font-family:system-ui,sans-serif;font-size:.76rem;color:var(--muted)}
  .pillar .p-works li.none{color:var(--muted)}
  .pillar .p-links{margin-top:.4rem}
  .pillar .p-links a{display:inline-block;font-family:system-ui,sans-serif;font-size:.78rem;color:var(--blue);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:.25rem .7rem;margin:0 .3rem .3rem 0}
  .pillar .p-links a:hover{border-color:var(--blue);color:var(--red)}
  .dive{background:linear-gradient(120deg,var(--blue),var(--red));color:#f4eee2;border-radius:16px;padding:1.6rem 1.8rem}
  .dive h3{margin:0 0 .5rem;font-size:1.3rem}
  .dive p{margin:0 0 1rem;opacity:.9}
  .dive a{display:inline-block;font-family:system-ui,sans-serif;color:#f4eee2;border:1px solid rgba(244,238,226,.5);border-radius:999px;padding:.4rem .9rem;text-decoration:none;margin-right:.5rem}
  .dive a:hover{background:rgba(244,238,226,.15)}
  footer{border-top:1px solid var(--line);margin-top:3rem;padding:1.6rem 0 3rem;color:var(--muted);font-size:.85rem;font-style:italic}
  .reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease, transform .6s ease}
  .reveal.in{opacity:1;transform:none}
  @media (max-width:640px){.stat + .stat{border-left:0}.p-head{flex-wrap:wrap}}
</style>
</head>
<body>
<div class="wrap">

  <header><span class="mark">Wissensatlas</span><span class="title">Die Lebendige Bibliothek</span></header>

  <section class="hero reveal">
    <div class="eyebrow">Akademisch · Informationswissenschaftlich fundiert</div>
    <h1>Die neue Art, wie wir Bücher lesen,<br>entsteht <em>vor unseren Augen</em>.</h1>
    <p class="lede">Interaktive und lebende E-Books — die Revolution des Lesens. Professionelle Wissensdienstleistungen im Archiv- und Bibliotheksbereich. Eine Plattform, die Wissensmanagement neu definiert: Services, Education, Scientific Experimentation, Textwissenschaft — und die Integration neuer Informationstechnologien im Interface von Mensch, Hochleistungsrechnen und KI. Für eine geistige Wiederbelebung.</p>
  </section>

  <div class="stats reveal">
    <div class="stat"><div class="num">__TOTAL__</div><div class="lbl">Objekte</div></div>
    <div class="stat"><div class="num">__BOOKS__</div><div class="lbl">Bücher</div></div>
    <div class="stat"><div class="num">__ART__</div><div class="lbl">Artikel</div></div>
    <div class="stat"><div class="num">__WEB__</div><div class="lbl">Webressourcen</div></div>
    <div class="stat"><div class="num">__YRS__</div><div class="lbl">Zeitraum</div></div>
  </div>

  <section class="sec reveal">
    <div class="sec-head"><span class="rn">I</span><h2>Die Wissenszweige</h2><span class="tag">782 Objekte · 5 Zweige</span></div>
    <div class="branches">__BRANCHES__</div>
  </section>

  <section class="sec reveal">
    <div class="sec-head"><span class="rn">II</span><h2>Der Atlas der Plattform</h2><span class="tag">8 Säulen</span></div>
    <div class="pillars">__PILLARS__</div>
  </section>

  <section class="sec reveal">
    <div class="sec-head"><span class="rn">III</span><h2>In die Bibliothek eintauchen</h2><span class="tag">Deep-Links</span></div>
    <div class="dive">
      <h3>Die lebendige Substanz hinter den Säulen</h3>
      <p>Jede Säule ruht auf kuratierten Werken deines Studiums. Durchsuche die 782 Objekte — gefiltert nach Zweig, Typ oder Jahr.</p>
      <a href="bibliothek/index.html">Gesamte Bibliothek ↗</a>
      <a href="bibliothek/index.html?branch=2">Archivistik ↗</a>
      <a href="bibliothek/index.html?branch=3">Bibliothekswissenschaft ↗</a>
      <a href="bibliothek/index.html?branch=1">Informationswissenschaft ↗</a>
      <a href="bibliothek/index.html?type=book">Nur Bücher ↗</a>
    </div>
  </section>

  <footer>Der Wissensatlas · sajon-platform · verknüpft mit der Zotero-Bibliothek CAS/MAS ALIS 2024–2026.</footer>

</div>
<script>
var heads = document.querySelectorAll('.p-head');
for(var i=0;i<heads.length;i++){
  heads[i].addEventListener('click', function(){
    var p = this.parentElement;
    p.classList.toggle('open');
  });
}
var obs = new IntersectionObserver(function(entries){
  entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); obs.unobserve(e.target); } });
}, {threshold: 0.08});
document.querySelectorAll('.reveal').forEach(function(el){ obs.observe(el); });
</script>
</body>
</html>
"""

html = (HTML
    .replace('__TOTAL__', str(total))
    .replace('__BOOKS__', str(n_books))
    .replace('__ART__', str(n_art))
    .replace('__WEB__', str(n_web))
    .replace('__YRS__', yr_span)
    .replace('__BRANCHES__', branches_html)
    .replace('__PILLARS__', pillars_html))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print("wissensatlas.html geschrieben:", len(html), "Zeichen;", total, "Objekte")
