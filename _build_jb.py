# -*- coding: utf-8 -*-
"""Generate a Jupyter Book (Executable Books) project in ./book from
the_book_2.73_buch.md.  Splits the curated book content into MyST markdown
pages (intro, autorin, per-chapter, lexicon, references, notes) plus
_config.yml / _toc.yml.  Build/deploy is handled by GitHub Actions.
"""
import re, os, shutil

SRC = "the_book_2.73_buch.md"
BOOK = "book"

def parse(text):
    lines = text.split("\n")
    title = lead = ""
    for ln in lines:
        if ln.startswith("# ") and not title:
            title = ln[2:].strip()
        elif ln.startswith(">") and not lead:
            lead = ln[1:].strip()
        if title and lead:
            break
    sections = {}
    cur = None
    for raw in lines:
        s = raw.rstrip()
        if not s.strip():
            continue
        if s.startswith("# "):
            name = s[2:].strip()
            sections[name] = []
            cur = name
            continue
        if cur is None:
            continue
        if s.startswith("---") or s.startswith("## Inhalt") or s.startswith(">"):
            continue
        if s.startswith("### "):
            sections[cur].append(("h3", s[4:].strip()))
        elif s.startswith("## "):
            sections[cur].append(("h2", s[3:].strip()))
        elif s.startswith("- "):
            sections[cur].append(("bullet", s[2:].strip()))
        else:
            sections[cur].append(("p", s.strip()))
    return title, lead, sections

def write_page(path, title, body):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: \"{title}\"\n---\n\n# {title}\n\n{body}")

def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    title, lead, sections = parse(text)

    # ensure book dir
    os.makedirs(BOOK, exist_ok=True)

    # group "Der Text" into chapters
    grouped = []
    cur = None
    for blk in sections.get("Der Text", []):
        if blk[0] == "h2":
            cur = [blk[1], []]
            grouped.append(cur)
        else:
            if cur is None:
                cur = ["", []]; grouped.append(cur)
            cur[1].append(blk)

    # intro
    intro_body = f"> {lead}\n\n"
    intro_body += "Dieses Buch versammelt die Gedanken in thematischen Kapiteln, ergänzt um Autor:in-Information, ein Lexikon, Referenzen & Quellen sowie Notizen. Weiter geht es über das Inhaltsverzeichnis.\n"
    write_page(os.path.join(BOOK, "intro.md"), "Das Lebendige Archiv", intro_body)

    # autorin
    aut = "\n\n".join(p for k, p in sections.get("Autor:in", []) if k == "p")
    write_page(os.path.join(BOOK, "autorin.md"), "Autor:in", aut)

    # chapters
    toc = ["format: jb-book", "root: intro", "chapters:"]
    ch_pages = []
    for i, (name, blk2) in enumerate(grouped, 1):
        fname = f"kap{i:02d}"
        ch_pages.append((name, fname))
        name_clean = re.sub(r"^\d+\.\s*", "", name).strip()
        body_parts = []
        for b in blk2:
            if b[0] == "p":
                body_parts.append(b[1])
            elif b[0] == "h3":
                body_parts.append(f"### {b[1]}")
            elif b[0] == "bullet":
                body_parts.append(f"- {b[1]}")
        write_page(os.path.join(BOOK, f"{fname}.md"), f"{i}. {name_clean}", "\n\n".join(body_parts))

    # lexicon as a definition list
    lex_terms = []
    for blk in sections.get("Lexikon", []):
        if blk[0] == "bullet":
            m = re.match(r"\*\*(.+?)\*\*\s*:\s*(.+)", blk[1])
            if m:
                lex_terms.append((m.group(1).strip(), m.group(2).strip()))
    lex_body = "\n\n".join(f"{t}\n:   {g}" for t, g in lex_terms)
    write_page(os.path.join(BOOK, "lexikon.md"), "Lexikon", lex_body)

    # references
    ref_parts = []
    mode = "named"
    ref_lines = {"named": [], "literature": []}
    for blk in sections.get("Referenzen & Quellen", []):
        if blk[0] == "p":
            if "Weiterführende Literatur" in blk[1]:
                mode = "literature"
            elif "Quellen" in blk[1]:
                mode = "named"
        elif blk[0] == "bullet":
            ref_lines[mode].append(blk[1])
    ref_parts.append("## Im Text genannte Quellen\n")
    ref_parts.append("\n".join(f"- {x}" for x in ref_lines["named"]))
    ref_parts.append("\n\n## Weiterführende Literatur\n")
    ref_parts.append("\n".join(f"- {x}" for x in ref_lines["literature"]))
    write_page(os.path.join(BOOK, "referenzen.md"), "Referenzen & Quellen", "\n\n".join(ref_parts))

    # notizen
    notz = "\n\n".join(p for k, p in sections.get("Notizen", []) if k == "p")
    write_page(os.path.join(BOOK, "notizen.md"), "Notizen", notz)

    # toc
    toc.append("- file: autorin")
    for name, fname in ch_pages:
        toc.append(f"- file: {fname}")
    toc.append("- file: lexikon")
    toc.append("- file: referenzen")
    toc.append("- file: notizen")
    with open(os.path.join(BOOK, "_toc.yml"), "w", encoding="utf-8") as f:
        f.write("\n".join(toc) + "\n")

    print("book/ pages:", len(ch_pages), "lexicon:", len(lex_terms))
    for n in sorted(os.listdir(BOOK)):
        print("  ", n)

if __name__ == "__main__":
    main()
