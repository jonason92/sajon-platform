# -*- coding: utf-8 -*-
"""Remove empty 'chapters:' entries from works/*/_toc.yml (sphinx-external-toc
rejects an empty non-list). A 'chapters:' line with no following '- file:' is
dropped, leaving just 'format: jb-book / root: intro'."""
import glob

fixed = 0
for f in glob.glob("works/*/_toc.yml"):
    lines = open(f, encoding="utf-8").read().splitlines()
    out = []
    i = 0
    changed = False
    while i < len(lines):
        if lines[i].strip() == "chapters:":
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            has_files = j < len(lines) and lines[j].strip().startswith("-")
            if has_files:
                out.append(lines[i])
            else:
                changed = True      # drop empty chapters line
            i += 1
        else:
            out.append(lines[i])
            i += 1
    if changed:
        open(f, "w", encoding="utf-8").write("\n".join(out) + "\n")
        fixed += 1
print("fixed", fixed, "toc files")
