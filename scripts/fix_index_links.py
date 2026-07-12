#!/usr/bin/env python3
"""
index.html's featured-article links were written against an older article numbering,
so 4 of the 6 homepage cards (and the 4 matching footer links) open the WRONG article.
Verified against the <h1> of each articles/article-N.html:

    card / footer title                  linked to        actually is
    הסכם הורות משותפת                    article-3   ->   article-4
    מתי כדאי לפנות להליך גישור           article-4   ->   article-5
    טעויות נפוצות בעריכת צוואה           article-5   ->   article-6
    מה חשוב לבדוק לפני הסכם מסחרי        article-6   ->   article-8

Remap in ONE pass (sequential replaces would collide), then re-derive each card's
image from the now-correct link.
"""
import re, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
REMAP = {3: 4, 4: 5, 5: 6, 6: 8}

s = INDEX.read_text(encoding="utf-8")

# 1. Fix the hrefs (cards + footer) in a single simultaneous pass.
s, n = re.subn(
    r'articles/article-(\d+)\.html',
    lambda m: f'articles/article-{REMAP.get(int(m.group(1)), int(m.group(1)))}.html',
    s,
)

# 2. Drop the <img> tags so wire_images.py can re-insert them from the corrected hrefs.
s, k = re.subn(r'\s*<img src="images/article-\d+\.jpg"[^>]*>', "", s)

INDEX.write_text(s, encoding="utf-8")
print(f"index.html: remapped {n} article link(s), cleared {k} image(s) for re-wiring")

# 3. Re-wire images from the corrected links.
subprocess.run([sys.executable, str(ROOT / "scripts" / "wire_images.py")], check=True)
