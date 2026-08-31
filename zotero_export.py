#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero-Export: liest die lokale zotero.sqlite (read-only) und exportiert
die Bibliografie der Gruppe "CAS/MAS ALIS 2024-2026" (groupID 4815832,
libraryID 2) als BibTeX, CSL-JSON und Markdown-Index.
"""
import sqlite3, json, re, os, unicodedata
from collections import defaultdict, OrderedDict

DB = 'file:D:/Zotero/zotero.sqlite?mode=ro'
OUT = 'D:/jonason/bibliothek'
LIB = 2  # libraryID der Gruppe CAS/MAS ALIS 2024-2026

os.makedirs(OUT, exist_ok=True)
db = sqlite3.connect(DB, uri=True)
c = db.cursor()

# --- Basis-Mappings ---
types = {r[0]: r[1] for r in c.execute("SELECT itemTypeID, typeName FROM itemTypes")}
fields = {r[0]: r[1] for r in c.execute("SELECT fieldID, fieldName FROM fields")}
ctypes = {r[0]: r[1] for r in c.execute("SELECT creatorTypeID, creatorType FROM creatorTypes")}

# --- Items der Gruppe ---
items = {}
for itemID, itemTypeID, key, dateAdded in c.execute(
    "SELECT itemID, itemTypeID, key, dateAdded FROM items WHERE libraryID=? ORDER BY dateAdded", (LIB,)):
    items[itemID] = {'itemID': itemID, 'typeID': itemTypeID, 'type': types.get(itemTypeID,'attachment'),
                     'key': key, 'dateAdded': dateAdded, 'fields': defaultdict(list), 'creators': []}

# --- Feldwerte ---
for itemID, fieldID, value in c.execute(
    "SELECT id.itemID, id.fieldID, idv.value FROM itemData id "
    "JOIN items it ON it.itemID=id.itemID "
    "JOIN itemDataValues idv ON idv.valueID=id.valueID "
    "WHERE it.libraryID=?", (LIB,)):
    if itemID in items and fieldID in fields and value not in (None, ''):
        items[itemID]['fields'][fields[fieldID]].append(value)

# --- Creators ---
for itemID, orderIndex, ctypeID, firstName, lastName, fieldMode in c.execute(
    "SELECT ic.itemID, ic.orderIndex, ic.creatorTypeID, cr.firstName, cr.lastName, cr.fieldMode "
    "FROM itemCreators ic JOIN items it ON it.itemID=ic.itemID "
    "JOIN creators cr ON cr.creatorID=ic.creatorID WHERE it.libraryID=? ORDER BY ic.itemID, ic.orderIndex", (LIB,)):
    if itemID in items:
        name = {'family': (lastName or '').strip(), 'given': (firstName or '').strip(), 'fieldMode': fieldMode} if fieldMode==0 else                {'family': (lastName or '').strip(), 'given': '', 'fieldMode': fieldMode}
        items[itemID]['creators'].append((ctypes.get(ctypeID,'author'), name))

# --- Collections ---
coll_names = {r[0]: r[1] for r in c.execute("SELECT collectionID, collectionName FROM collections WHERE libraryID=?", (LIB,))}
item_colls = defaultdict(list)
for collectionID, itemID in c.execute(
    "SELECT ci.collectionID, ci.itemID FROM collectionItems ci "
    "JOIN items it ON it.itemID=ci.itemID WHERE it.libraryID=?", (LIB,)):
    if itemID in items and collectionID in coll_names:
        item_colls[itemID].append(coll_names[collectionID])

# --- Tags ---
item_tags = defaultdict(list)
for itemID, tagName in c.execute(
    "SELECT itg.itemID, t.name FROM itemTags itg JOIN items it ON it.itemID=itg.itemID "
    "JOIN tags t ON t.tagID=itg.tagID WHERE it.libraryID=? AND itg.type=1", (LIB,)):
    if itemID in items and tagName:
        item_tags[itemID].append(tagName)
db.close()

# --- Filter: nur bibliografische Objekte (keine attachments/notes/annotations) ---
SKIP = {'attachment','note','annotation'}
bib = [it for it in items.values() if it['type'] not in SKIP]
print("Gesamt-Items (Gruppe):", len(items))
print("Davon bibliografisch:", len(bib))
print("Ausgeschlossen (Anhang/Notiz/Annotation):", len(items)-len(bib))

# --- Hilfsfunktionen ---
def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).encode('ascii','ignore').decode()

def parse_date(s):
    s = (s or '').strip()
    if not s: return None
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m: return (m.group(1), m.group(2).zfill(2), m.group(3).zfill(2))
    m = re.search(r'(\d{4})-(\d{1,2})', s)
    if m: return (m.group(1), m.group(2).zfill(2))
    m = re.search(r'(\d{4})', s)
    if m: return (m.group(1),)
    return None

def year_of(s):
    d = parse_date(s)
    return d[0] if d else ''

def creators_by_type(it, ctype):
    return [nm for (ct, nm) in it['creators'] if ct == ctype]

def author_list(it):
    return creators_by_type(it, 'author') or creators_by_type(it, 'editor') or creators_by_type(it, 'contributor')

def bibtex_name(nm):
    if nm.get('given'):
        return nm['family'] + ', ' + nm['given']
    return nm['family']

# CSL-Typ-Mapping
CSL = {'journalArticle':'article-journal','book':'book','bookSection':'chapter',
       'conferencePaper':'paper-conference','thesis':'thesis','report':'report',
       'webpage':'webpage','blogPost':'post-weblog','forumPost':'post','document':'document',
       'manuscript':'manuscript','presentation':'speech','computerProgram':'software',
       'videoRecording':'motion_picture','audioRecording':'song','podcast':'broadcast',
       'newspaperArticle':'article-newspaper','magazineArticle':'article-magazine',
       'encyclopediaArticle':'entry-encyclopedia','dictionaryEntry':'entry-dictionary',
       'preprint':'article','workingPaper':'report','map':'map','patent':'patent',
       'dataset':'dataset','standard':'standard','interview':'interview','artwork':'graphic',
       'film':'motion_picture','email':'personal_communication','instantMessage':'personal_communication',
       'case':'legal_case','statute':'legislation','hearing':'hearing','letter':'personal_communication'}
# BibTeX-Typ-Mapping
BIBT = {'journalArticle':'article','book':'book','bookSection':'incollection',
        'conferencePaper':'inproceedings','thesis':'phdthesis','report':'techreport',
        'webpage':'misc','blogPost':'misc','forumPost':'misc','document':'misc',
        'manuscript':'unpublished','presentation':'misc','computerProgram':'misc',
        'videoRecording':'misc','audioRecording':'misc','podcast':'misc',
        'newspaperArticle':'article','magazineArticle':'article',
        'encyclopediaArticle':'incollection','dictionaryEntry':'incollection',
        'preprint':'misc','workingPaper':'unpublished','map':'misc','patent':'misc',
        'dataset':'misc','standard':'misc','interview':'misc','artwork':'misc',
        'film':'misc','email':'misc','instantMessage':'misc','case':'misc',
        'statute':'misc','hearing':'misc','letter':'misc'}

def f(it, name):
    v = it['fields'].get(name)
    return v[0] if v else ''

def esc_tex(s):
    s = (s or '').replace('\\','\\\\').replace('&','\\&').replace('%','\\%').replace('_','\\_').replace('#','\\#')
    return s

used_keys = set()
def citekey(it):
    au = author_list(it)
    a = fold(au[0]['family']) if au else 'anon'
    a = re.sub(r'[^a-z0-9]+','', a.lower()) or 'anon'
    y = year_of(f(it,'date')) or 'nd'
    t = re.sub(r'[^a-z0-9]+','', fold(f(it,'title')).lower())[:24] or 'x'
    base = a + y + t
    k = base; n = 0
    while k in used_keys:
        n += 1; k = base + chr(96+n)
    used_keys.add(k)
    return k

def build_csl(it):
    au = [{'family': nm['family'], 'given': nm['given']} for (ct, nm) in it['creators'] if ct=='author']
    ed = [{'family': nm['family'], 'given': nm['given']} for (ct, nm) in it['creators'] if ct=='editor']
    if not au:
        au = [{'family': nm['family'], 'given': nm['given']} for (ct, nm) in it['creators'] if ct in ('contributor','')][:0] or []
    d = parse_date(f(it,'date'))
    rec = OrderedDict()
    rec['id'] = it['key']
    rec['type'] = CSL.get(it['type'], 'document')
    if f(it,'title'): rec['title'] = f(it,'title')
    if au: rec['author'] = au
    if ed: rec['editor'] = ed
    if d:
        rec['issued'] = {'date-parts': [[int(x) for x in d]]}
    if f(it,'publicationTitle'): rec['container-title'] = f(it,'publicationTitle')
    if f(it,'bookTitle'): rec['container-title'] = f(it,'bookTitle')
    if f(it,'publisher'): rec['publisher'] = f(it,'publisher')
    if f(it,'place'): rec['publisher-place'] = f(it,'place')
    if f(it,'volume'): rec['volume'] = f(it,'volume')
    if f(it,'issue'): rec['issue'] = f(it,'issue')
    if f(it,'pages'): rec['page'] = f(it,'pages')
    if f(it,'DOI'): rec['DOI'] = f(it,'DOI')
    if f(it,'url'): rec['URL'] = f(it,'url')
    if f(it,'ISBN'): rec['ISBN'] = f(it,'ISBN')
    if f(it,'ISSN'): rec['ISSN'] = f(it,'ISSN')
    if f(it,'abstractNote'): rec['abstract'] = f(it,'abstractNote')
    if item_tags.get(it['itemID']): rec['keyword'] = '; '.join(item_tags[it['itemID']])
    if item_colls.get(it['itemID']): rec['note'] = 'Sammlungen: ' + '; '.join(item_colls[it['itemID']])
    return rec

def build_bibtex(it):
    k = citekey(it)
    t = BIBT.get(it['type'], 'misc')
    au = author_list(it)
    eds = creators_by_type(it,'editor')
    lines = ['@%s{%s,' % (t, k)]
    if au: lines.append('  author = {%s},' % ' and '.join(bibtex_name(n) for n in au))
    if eds and not au: lines.append('  editor = {%s},' % ' and '.join(bibtex_name(n) for n in eds))
    if f(it,'title'): lines.append('  title = {%s},' % esc_tex(f(it,'title')))
    if f(it,'publicationTitle'): lines.append('  journal = {%s},' % esc_tex(f(it,'publicationTitle')))
    if f(it,'bookTitle'): lines.append('  booktitle = {%s},' % esc_tex(f(it,'bookTitle')))
    if year_of(f(it,'date')): lines.append('  year = {%s},' % year_of(f(it,'date')))
    if f(it,'publisher'): lines.append('  publisher = {%s},' % esc_tex(f(it,'publisher')))
    if f(it,'place'): lines.append('  address = {%s},' % esc_tex(f(it,'place')))
    if f(it,'volume'): lines.append('  volume = {%s},' % esc_tex(f(it,'volume')))
    if f(it,'issue'): lines.append('  number = {%s},' % esc_tex(f(it,'issue')))
    if f(it,'pages'): lines.append('  pages = {%s},' % esc_tex(f(it,'pages')))
    if f(it,'DOI'): lines.append('  doi = {%s},' % f(it,'DOI'))
    if f(it,'url'): lines.append('  url = {%s},' % f(it,'url'))
    if f(it,'ISBN'): lines.append('  isbn = {%s},' % esc_tex(f(it,'ISBN')))
    if f(it,'ISSN'): lines.append('  issn = {%s},' % esc_tex(f(it,'ISSN')))
    if item_tags.get(it['itemID']): lines.append('  keywords = {%s},' % esc_tex(', '.join(item_tags[it['itemID']])))
    lines.append('}')
    return '\n'.join(lines)

# --- Statistiken ---
by_type = defaultdict(int)
by_year = defaultdict(int)
for it in bib:
    by_type[it['type']] += 1
    by_year[year_of(f(it,'date')) or 'ohne Jahr'] += 1
print("\n--- Typen ---")
for t, n in sorted(by_type.items(), key=lambda x:-x[1]):
    print("  %-22s %d" % (t, n))
print("--- Jahrgänge (Top 12) ---")
for y, n in sorted(by_year.items(), key=lambda x:-x[1])[:12]:
    print("  %s: %d" % (y, n))

# --- Schreiben ---
bib_lines = []
for it in bib:
    bib_lines.append(build_bibtex(it))
with open(os.path.join(OUT,'casmas-alis-2024-2026.bib'),'w',encoding='utf-8') as fh:
    fh.write('\n\n'.join(bib_lines) + '\n')

csl = [build_csl(it) for it in bib]
with open(os.path.join(OUT,'casmas-alis-2024-2026.json'),'w',encoding='utf-8') as fh:
    json.dump(csl, fh, ensure_ascii=False, indent=1)

# Markdown-Index (gruppiert nach Typ)
grouped = defaultdict(list)
for it in bib:
    grouped[it['type']].append(it)
md = ['# CAS/MAS ALIS 2024-2026 — Bibliografischer Index', '',
      'Export aus der lokalen Zotero-Datenbank (Gruppe 4815832). %d bibliografische Objekte.' % len(bib), '']
order = sorted(grouped.items(), key=lambda x: -len(x[1]))
for typ, its in order:
    md.append('## %s (%d)' % (typ, len(its)))
    md.append('')
    for it in sorted(its, key=lambda x: (year_of(f(x,'date')), f(x,'title').lower())):
        au = author_list(it)
        names = '; '.join((nm['family']+', '+nm['given']).strip(' ,') for nm in au[:3])
        if len(au) > 3: names += ' et al.'
        if not names: names = '(ohne Autor)'
        y = year_of(f(it,'date')) or 'o. J.'
        title = f(it,'title') or '(ohne Titel)'
        src = f(it,'publicationTitle') or f(it,'bookTitle') or ''
        doi = f(it,'DOI'); url = f(it,'url')
        link = 'https://doi.org/' + doi if doi else url
        line = '- %s (%s). *%s*' % (names, y, title)
        if src: line += '. %s' % src
        if link: line += '. [Link](%s)' % link
        md.append(line)
    md.append('')
with open(os.path.join(OUT,'index.md'),'w',encoding='utf-8') as fh:
    fh.write('\n'.join(md))

print("\nGeschrieben nach:", OUT)
print("  casmas-alis-2024-2026.bib  (%d Einträge)" % len(bib_lines))
print("  casmas-alis-2024-2026.json (%d Einträge)" % len(csl))
print("  index.md")
