#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt bibliothek/index.html: durchsuchbarer Index der Zotero-Bibliografie."""
import json, re

SRC = 'D:/jonason/bibliothek/casmas-alis-2024-2026.json'
OUT = 'D:/jonason/bibliothek/index.html'

with open(SRC, encoding='utf-8') as f:
    records = json.load(f)

TYPE_LABELS = {
  'article-journal':'Zeitschriftenartikel','book':'Buch','chapter':'Buchkapitel',
  'paper-conference':'Konferenzbeitrag','thesis':'Abschlussarbeit','report':'Bericht',
  'webpage':'Webseite','post-weblog':'Blog','post':'Forum','document':'Dokument',
  'manuscript':'Manuskript','speech':'Vortrag','software':'Software',
  'motion_picture':'Video','song':'Audio','broadcast':'Podcast','article':'Artikel',
  'article-newspaper':'Zeitungsartikel','article-magazine':'Magazinartikel',
  'entry-encyclopedia':'Lexikonartikel','entry-dictionary':'Wörterbucheintrag',
  'dataset':'Datensatz','standard':'Norm','patent':'Patent','interview':'Interview',
  'graphic':'Bild','map':'Karte','personal_communication':'Persönl. Mitteilung',
  'legal_case':'Rechtsfall','legislation':'Gesetz','hearing':'Anhörung'
}
BRANCH_LABELS = {'0':'0 · Quellen','1':'1 · Informationswissenschaft','2':'2 · Archivistik',
                 '3':'3 · Bibliothekswissenschaft','4':'4 · Modulbibliografien','':'ohne Sammlung'}

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
    items.append({
        't': rec.get('title','(ohne Titel)'),
        'au': authors_str(rec),
        'y': year_of(rec),
        'ty': rec.get('type','document'),
        'src': rec.get('container-title',''),
        'link': link,
        'tags': (rec.get('keyword') or '').split('; '),
        'br': b,
        'coll': '; '.join(colls),
        'abs': rec.get('abstract','')
    })

items.sort(key=lambda x: (x['y'] or '9999', x['t'].lower()))

data_json = json.dumps(items, ensure_ascii=False).replace('</', '<\\/')

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Bibliothek — CAS/MAS ALIS 2024–2026 (Suche)</title>
<style>
  :root{--bg:#f6f1e7;--paper:#fffdf8;--ink:#1b1712;--soft:#4a4238;--muted:#7a7062;--line:#dcd2bf;--brass:#b8742a;--teal:#1f6f6b}
  *{box-sizing:border-box}
  body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
  header{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:.8rem clamp(.8rem,3vw,1.6rem)}
  header h1{font-family:Georgia,serif;font-size:1.25rem;margin:0}
  header .sub{font-size:.82rem;color:var(--muted)}
  .controls{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;margin-top:.6rem}
  .controls input[type=search]{flex:1;min-width:200px;padding:.55rem .8rem;border:1px solid var(--line);border-radius:10px;background:var(--paper);font-size:.95rem;color:var(--ink)}
  .controls select{padding:.55rem .6rem;border:1px solid var(--line);border-radius:10px;background:var(--paper);font-size:.88rem;color:var(--ink)}
  .controls button{padding:.55rem .8rem;border:1px solid var(--line);border-radius:10px;background:var(--paper);cursor:pointer;font-size:.88rem}
  .controls button:hover{border-color:var(--brass);color:var(--brass)}
  .count{font-size:.85rem;color:var(--muted);margin:.6rem clamp(.8rem,3vw,1.6rem)}
  #results{max-width:1000px;margin:0 auto;padding:0 clamp(.8rem,3vw,1.6rem) 3rem}
  .entry{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem;margin-bottom:.6rem}
  .entry .badge{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.03em;text-transform:uppercase;border:1px solid;border-radius:999px;padding:.1rem .55rem;margin-right:.4rem}
  .entry .branch{display:inline-block;font-size:.72rem;color:var(--muted);background:var(--bg);border-radius:999px;padding:.1rem .55rem}
  .entry .title{font-weight:600;margin:.35rem 0 .1rem}
  .entry .title a{color:var(--ink);text-decoration:none}
  .entry .title a:hover{color:var(--brass);text-decoration:underline}
  .entry .meta{font-size:.85rem;color:var(--soft)}
  .entry .tags{margin-top:.3rem}
  .chip{display:inline-block;font-size:.7rem;color:var(--teal);background:var(--bg);border-radius:999px;padding:.05rem .5rem;margin:.1rem .3rem 0 0}
  .entry .abs{font-size:.85rem;color:var(--muted);margin:.4rem 0 0}
  .entry .more{background:none;border:0;color:var(--brass);cursor:pointer;font-size:.8rem;padding:0;margin-top:.2rem}
  .empty{text-align:center;color:var(--muted);padding:3rem 0}
  footer{text-align:center;color:var(--muted);font-size:.8rem;padding:1.5rem}
  @media (prefers-color-scheme:dark){:root{--bg:#16120e;--paper:#201a13;--ink:#f2ead9;--soft:#cfc3ae;--muted:#948a77;--line:#3a3228;--brass:#d9a05b;--teal:#4fb3ad}}
</style>
</head>
<body>
<header>
  <h1>Bibliothek — CAS/MAS ALIS 2024–2026</h1>
  <div class="sub">Durchsuchbarer Index · Zotero-Gruppe 4815832</div>
  <div class="controls">
    <input type="search" id="q" placeholder="Suchen: Titel, Autor:in, Schlagwort, Abstract …" />
    <select id="f-type"><option value="all">Alle Typen</option></select>
    <select id="f-year"><option value="all">Alle Jahre</option></select>
    <select id="f-branch">
      <option value="all">Alle Sammlungen</option>
      <option value="0">0 · Quellen</option>
      <option value="1">1 · Informationswissenschaft</option>
      <option value="2">2 · Archivistik</option>
      <option value="3">3 · Bibliothekswissenschaft</option>
      <option value="4">4 · Modulbibliografien</option>
      <option value="">ohne Sammlung</option>
    </select>
    <select id="f-sort">
      <option value="year">Sortierung: Jahr</option>
      <option value="title">Sortierung: Titel</option>
      <option value="author">Sortierung: Autor:in</option>
    </select>
    <button id="reset">Zurücksetzen</button>
  </div>
</header>
<div class="count" id="count"></div>
<div id="results"></div>
<footer>Erzeugt aus der lokalen Zotero-Datenbank · casmas-alis-2024-2026.json</footer>
<script>
var DATA = __DATA__;

var LABELS = {__LABELS__};
var BRANCH = {'0':'0 · Quellen','1':'1 · Informationswissenschaft','2':'2 · Archivistik','3':'3 · Bibliothekswissenschaft','4':'4 · Modulbibliografien','':'ohne Sammlung'};

var state = {q:'', type:'all', year:'all', branch:'all', sort:'year'};

function colorOf(t){
  var m = {'article-journal':'#b8742a','book':'#1f6f6b','chapter':'#8a4f9c','paper-conference':'#4f8a3c','thesis':'#c0503a','report':'#2f6fbf','webpage':'#5b6b7a','post-weblog':'#5b6b7a','document':'#7a7062'};
  return m[t] || '#7a7062';
}

function searchStr(it){
  return (it.t + ' ' + it.au + ' ' + it.src + ' ' + it.tags.join(' ') + ' ' + it.coll + ' ' + it.abs).toLowerCase();
}

function matches(it){
  if(state.q && searchStr(it).indexOf(state.q.toLowerCase()) < 0) return false;
  if(state.type !== 'all' && it.ty !== state.type) return false;
  if(state.year !== 'all' && it.y !== state.year) return false;
  if(state.branch !== 'all' && it.br !== state.branch) return false;
  return true;
}

function card(it){
  var d = document.createElement('div'); d.className = 'entry';
  var head = document.createElement('div');
  var badge = document.createElement('span'); badge.className='badge'; badge.textContent = LABELS[it.ty]||it.ty;
  badge.style.color = colorOf(it.ty); badge.style.borderColor = colorOf(it.ty);
  head.appendChild(badge);
  if(it.br && it.br !== ''){
    var b = document.createElement('span'); b.className='branch'; b.textContent = BRANCH[it.br]||it.br; head.appendChild(b);
  }
  d.appendChild(head);
  var title = document.createElement('div'); title.className='title';
  if(it.link){
    var a = document.createElement('a'); a.href=it.link; a.target='_blank'; a.rel='noopener'; a.textContent=it.t; title.appendChild(a);
  } else { title.textContent = it.t; }
  d.appendChild(title);
  var meta = document.createElement('div'); meta.className='meta';
  var parts = [];
  if(it.au) parts.push(it.au);
  if(it.y) parts.push(it.y);
  if(it.src) parts.push(it.src);
  meta.textContent = parts.join(' · ');
  d.appendChild(meta);
  if(it.tags && it.tags.length && it.tags[0]){
    var tg = document.createElement('div'); tg.className='tags';
    for(var i=0;i<it.tags.length && i<5;i++){ var s=document.createElement('span'); s.className='chip'; s.textContent=it.tags[i]; tg.appendChild(s); }
    d.appendChild(tg);
  }
  if(it.abs){
    var abs = document.createElement('p'); abs.className='abs';
    var full = it.abs; var short = full.length>260 ? full.slice(0,260)+' …' : full;
    abs.textContent = short;
    d.appendChild(abs);
    if(full.length>260){
      var btn = document.createElement('button'); btn.className='more'; btn.textContent='Mehr';
      btn.onclick = function(){
        if(btn.getAttribute('data-open')==='1'){ abs.textContent=short; btn.textContent='Mehr'; btn.setAttribute('data-open','0'); }
        else { abs.textContent=full; btn.textContent='Weniger'; btn.setAttribute('data-open','1'); }
      };
      d.appendChild(btn);
    }
  }
  return d;
}

function render(){
  var list = DATA.filter(matches);
  if(state.sort==='title'){ list.sort(function(a,b){ return a.t.toLowerCase() < b.t.toLowerCase() ? -1 : 1; }); }
  else if(state.sort==='author'){ list.sort(function(a,b){ return a.au < b.au ? -1 : 1; }); }
  else { list.sort(function(a,b){ return (b.y||'0') - (a.y||'0'); }); }
  var box = document.getElementById('results');
  box.innerHTML = '';
  document.getElementById('count').textContent = list.length + ' von ' + DATA.length + ' Einträgen';
  if(list.length===0){ var e=document.createElement('div'); e.className='empty'; e.textContent='Keine Treffer.'; box.appendChild(e); return; }
  for(var i=0;i<list.length;i++){ box.appendChild(card(list[i])); }
}

function populate(){
  var types = {}; var years = {};
  DATA.forEach(function(it){ types[it.ty]=1; if(it.y) years[it.y]=1; });
  var tsel = document.getElementById('f-type');
  Object.keys(types).sort(function(a,b){ return (LABELS[a]||a) < (LABELS[b]||b) ? -1 : 1; }).forEach(function(t){
    var o=document.createElement('option'); o.value=t; o.textContent=LABELS[t]||t; tsel.appendChild(o);
  });
  var ysel = document.getElementById('f-year');
  Object.keys(years).sort(function(a,b){ return b-a; }).forEach(function(y){
    var o=document.createElement('option'); o.value=y; o.textContent=y; ysel.appendChild(o);
  });
}

document.getElementById('q').addEventListener('input', function(e){ state.q=e.target.value; render(); });
document.getElementById('f-type').addEventListener('change', function(e){ state.type=e.target.value; render(); });
document.getElementById('f-year').addEventListener('change', function(e){ state.year=e.target.value; render(); });
document.getElementById('f-branch').addEventListener('change', function(e){ state.branch=e.target.value; render(); });
document.getElementById('f-sort').addEventListener('change', function(e){ state.sort=e.target.value; render(); });
document.getElementById('reset').addEventListener('click', function(){
  state = {q:'', type:'all', year:'all', branch:'all', sort:'year'};
  document.getElementById('q').value=''; document.getElementById('f-type').value='all';
  document.getElementById('f-year').value='all'; document.getElementById('f-branch').value='all';
  document.getElementById('f-sort').value='year';
  render();
});

populate();
render();
</script>
</body>
</html>
"""

labels_json = json.dumps(TYPE_LABELS, ensure_ascii=False)
html = HTML.replace('__DATA__', data_json).replace('__LABELS__', labels_json)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html geschrieben:", len(items), "Einträge,", len(html), "Zeichen")
