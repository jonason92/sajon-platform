# -*- coding: utf-8 -*-
"""Convert a .docx into a Jupyter Book folder under works/<slug>/.

Uses only the standard library (zipfile + ElementTree). Maps Word styles:
  berschrift1 / Heading1 -> chapter, berschrift2 / Heading2 -> ##,
  body -> paragraphs, Listenabsatz -> list items.
Skips the generated table of contents (Inhaltsverzeichnis + Verzeichnis*) and
footnote-only paragraphs.
"""
import sys, os, re, zipfile
import xml.etree.ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def paragraphs(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(xml)
    out = []
    for p in root.iter("{%s}p" % NS["w"]):
        style = ""
        ppr = p.find("w:pPr", NS)
        if ppr is not None:
            pst = ppr.find("w:pStyle", NS)
            if pst is not None:
                style = pst.get("{%s}val" % NS["w"], "")
        texts = [t.text or "" for t in p.iter("{%s}t" % NS["w"])]
        txt = "".join(texts).strip()
        out.append((style, txt))
    return out


def style_kind(style):
    s = style.lower()
    if "inhaltsverzeichnis" in s or s.startswith("verzeichnis"):
        return "toc"
    if "funotentext" in s:
        return "skip"
    m = re.search(r"berschrift(\d)?", s) or re.search(r"heading(\d)?", s)
    if m:
        lvl = int(m.group(1)) if m.group(1) else 1
        return f"h{min(lvl, 3)}"
    if "formatvorlage1" in s:
        return "title"
    if "listenabsatz" in s:
        return "list"
    return "norm"


def md_escape(t):
    return t.replace("\\", "\\\\").strip()


def main():
    src = sys.argv[1]
    slug = sys.argv[2] if len(sys.argv) > 2 else "arbeit"
    title_override = sys.argv[3] if len(sys.argv) > 3 else ""
    out = os.path.join("works", slug)
    os.makedirs(out, exist_ok=True)

    ps = paragraphs(src)
    # split into intro (before first h1) and chapters (each h1 -> its own page)
    intro = []          # (kind, text)
    chapters = []       # list of (title, [(kind,text)])
    cur = None
    for style, txt in ps:
        kind = style_kind(style)
        if kind == "toc" or kind == "skip":
            continue
        if kind == "title":
            intro.append(("title", txt))
            continue
        if kind == "h1":
            if not txt:
                continue
            cur = [txt, []]
            chapters.append(cur)
            continue
        if cur is None:
            intro.append((kind, txt))
        else:
            cur[1].append((kind, txt))

    def render(blocks):
        out_lines = []
        for kind, txt in blocks:
            if not txt:
                continue
            if kind == "title":
                continue
            elif kind == "h1":
                out_lines.append(f"## {md_escape(txt)}\n")
            elif kind == "h2":
                out_lines.append(f"### {md_escape(txt)}\n")
            elif kind == "h3":
                out_lines.append(f"#### {md_escape(txt)}\n")
            elif kind == "list":
                out_lines.append(f"- {md_escape(txt)}")
            else:
                out_lines.append(md_escape(txt))
        return "\n\n".join(out_lines).strip()

    # title from Formatvorlage1 (first title paragraph), fallback to slug
    work_title = "Monismus"
    for kind, txt in intro:
        if kind == "title" and txt:
            work_title = txt
            break
    if title_override:
        work_title = title_override

    # intro.md
    intro_body = []
    for kind, txt in intro:
        if kind == "title":
            continue
        intro_body.append(md_escape(txt))
    with open(os.path.join(out, "intro.md"), "w", encoding="utf-8") as f:
        f.write(f'---\ntitle: "{work_title}"\n---\n\n# {work_title}\n\n' + "\n\n".join(intro_body))

    # chapter pages
    toc = ["format: jb-book", "root: intro", "chapters:"]
    for i, (title, blk) in enumerate(chapters, 1):
        fname = f"kapitel-{i}"
        body = render(blk)
        with open(os.path.join(out, f"{fname}.md"), "w", encoding="utf-8") as f:
            f.write(f'---\ntitle: "{md_escape(title)}"\n---\n\n# {md_escape(title)}\n\n{body}\n')
        toc.append(f"- file: {fname}")

    with open(os.path.join(out, "_toc.yml"), "w", encoding="utf-8") as f:
        f.write("\n".join(toc) + "\n")

    # _config.yml
    cfg = f"""title: "{work_title}"
author: jonas
copyright: ""
logo: ../../assets/logo.svg
only_build_toc_files: true

execute:
  execute_notebooks: off

html:
  use_repository_button: true
  use_issues_button: true
  home_page_in_navbar: false

repository:
  url: https://github.com/jonason92/sajon-platform
  branch: main
  path_to_book: works/{slug}
"""
    with open(os.path.join(out, "_config.yml"), "w", encoding="utf-8") as f:
        f.write(cfg)

    print("wrote", out, "chapters:", len(chapters), "work_title:", work_title)


if __name__ == "__main__":
    main()
