# -*- coding: utf-8 -*-
"""Extract textual posts from a Facebook "Download Your Information" export,
strip ALL external URLs / FB links, and write them to facebook_posts.md so the
living-archive pipeline (_restructure_book.py) can merge them.

Expected input (place into ./fb_export/):
  - newer JSON export: fb_export/**/your_posts*.json   ({"data":[{"post":{...}}]})
  - classic HTML export: fb_export/**/posts_*.html / your_posts_*.html
"""
import os, re, json, glob, html as _html

SRC_DIR = "fb_export"
OUT = "facebook_posts.md"


def clean_text(t):
    t = _html.unescape(t)
    # drop everything that looks like a URL (external AND facebook links)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"www\.\S+", "", t)
    t = re.sub(r"\[[^\]]*\]\(https?://[^)]*\)", "", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"\s*\n\s*", " ", t).strip()
    return t


def extract_json(path):
    posts = []
    with open(path, encoding="utf-8") as fh:
        parsed = json.load(fh)

    def walk(obj):
        if isinstance(obj, dict):
            # post text lives under 'post' (newer export) or 'title'
            p = obj.get("post")
            if isinstance(p, str) and len(p.strip()) > 3:
                posts.append(p)
            else:
                title = obj.get("title")
                if isinstance(title, str) and len(title.strip()) > 3 \
                        and not title.strip().lower().startswith("your facebook"):
                    posts.append(title)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(parsed)
    return posts


def extract_html(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    txt = re.sub(r"<script.*?</script>", " ", txt, flags=re.S)
    txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = _html.unescape(txt)
    txt = re.sub(r"https?://\S+", " ", txt)
    txt = re.sub(r"www\.\S+", " ", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt).strip()
    return [txt] if txt else []


def main():
    posts = []
    for p in sorted(glob.glob(os.path.join(SRC_DIR, "**", "*.json"), recursive=True)):
        if "your_posts" in p.lower() or "posts" in p.lower():
            try:
                posts += extract_json(p)
            except Exception as e:
                print("skip json", p, e)
    for p in sorted(glob.glob(os.path.join(SRC_DIR, "**", "*.html"), recursive=True)):
        if "post" in p.lower():
            try:
                posts += extract_html(p)
            except Exception as e:
                print("skip html", p, e)

    seen, out = set(), []
    for p in posts:
        c = clean_text(p)
        n = c.lower()
        if not c or n in seen:
            continue
        seen.add(n)
        out.append(c)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n\n".join(out))
    print("posts extracted:", len(out), "->", OUT)


if __name__ == "__main__":
    main()
