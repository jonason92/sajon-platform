# -*- coding: utf-8 -*-
"""Transcribe videos/audio with Faster-Whisper (free / open source) and write
each transcript as MyST markdown into transkripte/<slug>/ so the portal lists it.

CAUTION: The source videos currently live in the C: kDrive (YT-Material) and
should NOT be opened/downloaded until there is enough disk space.  Run this only
when the videos are available locally (e.g. after moving them to D:/ or freeing
space), and adjust VIDEO_DIR.

Layout expected per video directory/group:
  VIDEO_DIR/<name>/<name>.mp4  or  VIDEO_DIR/<name>.mp4
Output:
  transkripte/<slug>/_config.yml, _toc.yml, transkript.md, intro.md
"""
import os, re, subprocess, shutil

VIDEO_DIR = r"D:\transkripte-videos"   # adjust when videos are available
AUTHOR = "JH"

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def main():
    from faster_whisper import WhisperModel   # locale import (free, open source)
    model = WhisperModel("small", device="auto", compute_type="auto")
    items = sorted(os.listdir(VIDEO_DIR))
    made = 0
    for name in items:
        src = os.path.join(VIDEO_DIR, name)
        if os.path.isdir(src):
            videos = [f for f in os.listdir(src) if f.lower().endswith((".mp4", ".mkv", ".webm", ".mov"))]
            if not videos:
                continue
            video = os.path.join(src, videos[0])
            slug = slugify(name)
        elif name.lower().endswith((".mp4", ".mkv", ".webm", ".mov")):
            video = src
            slug = slugify(os.path.splitext(name)[0])
        else:
            continue
        out = os.path.join("transkripte", slug)
        if os.path.isdir(out):
            continue
        segments, _ = model.transcribe(video, language="de")
        lines = [f"[{seg.start:07.2f}] {seg.text.strip()}" for seg in segments]
        block = "\n\n".join(lines)
        os.makedirs(out, exist_ok=True)
        # transkript.md
        with open(os.path.join(out, "transkript.md"), "w", encoding="utf-8") as f:
            f.write(f'---\ntitle: "{name}"\n---\n\n# {name}\n\n{block}\n')
        # toc + config
        with open(os.path.join(out, "_toc.yml"), "w", encoding="utf-8") as f:
            f.write("format: jb-book\nroot: transkript\n")
        with open(os.path.join(out, "_config.yml"), "w", encoding="utf-8") as f:
            f.write(f'title: "{name}"\nauthor: {AUTHOR}\ncopyright: ""\n'
                    f'logo: ../../assets/logo.png\nonly_build_toc_files: true\n\n'
                    f'execute:\n  execute_notebooks: off\n\nhtml:\n  use_repository_button: true\n'
                    f'  use_issues_button: true\n  home_page_in_navbar: false\n\nrepository:\n'
                    f'  url: https://github.com/jonason92/sajon-platform\n  branch: main\n'
                    f'  path_to_book: transkripte/{slug}\n')
        made += 1
        print("transcribed:", name, "->", slug)
    print("done, created", made, "transcription books")

if __name__ == "__main__":
    main()
