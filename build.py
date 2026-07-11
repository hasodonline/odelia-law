#!/usr/bin/env python3
"""
Build the static site into ./dist, injecting the site's primary domain.

▶ To change the site's primary domain, edit BASE_URL below and re-run:
      python3 build.py
  then deploy ./dist :
      npx wrangler pages deploy dist --project-name lawodelia --branch main

All canonical / Open Graph / sitemap / schema URLs in the source use the
placeholder __BASE_URL__ ; this script replaces it everywhere in one pass.
"""
import os, shutil, glob

# ─────────────────────────────────────────────────────────────
#  THE ONE PLACE TO CHANGE THE SITE'S PRIMARY DOMAIN (no trailing slash)
BASE_URL = "https://www.lawodelia.co.il"
# ─────────────────────────────────────────────────────────────

SRC = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(SRC, "dist")
ASSETS = ["index.html", "articles.html", "style.css", "config.js",
          "analytics.js", "robots.txt", "sitemap.xml"]
DIRS = ["images", "articles"]
TEXT_EXT = (".html", ".xml", ".txt", ".js")

shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(DIST)
for f in ASSETS:
    shutil.copy(os.path.join(SRC, f), DIST)
for d in DIRS:
    shutil.copytree(os.path.join(SRC, d), os.path.join(DIST, d))
for p in glob.glob(os.path.join(DIST, "**", ".DS_Store"), recursive=True):
    os.remove(p)

templated = 0
for root, _, files in os.walk(DIST):
    for fn in files:
        if fn.endswith(TEXT_EXT):
            fp = os.path.join(root, fn)
            s = open(fp, encoding="utf-8").read()
            if "__BASE_URL__" in s:
                open(fp, "w", encoding="utf-8").write(s.replace("__BASE_URL__", BASE_URL))
                templated += 1

print(f"Built ./dist with BASE_URL={BASE_URL}  ({templated} files templated)")
