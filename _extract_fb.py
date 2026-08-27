# -*- coding: utf-8 -*-
"""Extract only the FB post-text JSON files (no media/messages) from the big
export zip into fb_export/, preserving a simple structure."""
import os, zipfile

ZIP = "facebook-sajon92-27.08.2026-BuQQGj1c.zip"
OUT = "fb_export"

WANT = [
    "your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.json",
    "your_facebook_activity/posts/posts_on_other_pages_and_profiles.json",
    "your_facebook_activity/posts/edits_you_made_to_posts.json",
    "your_facebook_activity/posts/content_sharing_links_you_have_created.json",
    "your_facebook_activity/posts/your_uncategorized_photos.json",
    "apps_and_websites_off_of_facebook/posts_from_apps_and_websites.json",
]

os.makedirs(OUT, exist_ok=True)
with zipfile.ZipFile(ZIP) as z:
    for name in WANT:
        try:
            info = z.getinfo(name)
            data = z.read(info)
            # write into fb_export preserving the basename (flat, simple)
            base = os.path.basename(name)
            with open(os.path.join(OUT, base), "wb") as f:
                f.write(data)
            print("extracted", base, len(data), "bytes")
        except KeyError:
            print("not found:", name)

# quick peek at structure of the main posts file
main = os.path.join(OUT, "your_posts__check_ins__photos_and_videos_1.json")
import json
with open(main, encoding="utf-8") as f:
    d = json.load(f)
print("\n--- structure of", os.path.basename(main), "---")
print("top-level keys:", list(d.keys())[:10])
data = d.get("data", [])
print("num posts:", len(data))
if data:
    p = data[0]
    print("post keys:", list(p.keys()))
    print("title:", repr(p.get("title", "")[:120]))
    for a in p.get("data", [])[:2]:
        print("  data key(s):", list(a.keys()) if isinstance(a, dict) else type(a))
        if isinstance(a, dict):
            print("    post:", repr(a.get("post", ""))[:120])
