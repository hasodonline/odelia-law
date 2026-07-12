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
import os, shutil, glob, re, hashlib

# ─────────────────────────────────────────────────────────────
#  THE ONE PLACE TO CHANGE THE SITE'S PRIMARY DOMAIN (no trailing slash)
BASE_URL = "https://lawodelia.co.il"
# ─────────────────────────────────────────────────────────────

# Assets that get a ?v=<content-hash> appended to their references in the HTML.
# Without this, Cloudflare's 4h Browser-Cache-TTL keeps serving the OLD file to
# returning visitors after a deploy (this silently broke GA4 once — don't remove).
CACHE_BUSTED = ["config.js", "analytics.js", "style.css"]

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

# ── clean URLs: Cloudflare Pages serves pages EXTENSIONLESS and 308-redirects the
#    ".html" form (/articles/article-1.html -> /articles/article-1). If our canonical /
#    og:url / sitemap / internal links keep saying ".html", every one of them is a
#    redirect and the canonical points away from the page Google actually lands on.
#    So emit the extensionless URLs the server really serves. (Files on disk keep .html.)
def _strip(u: str) -> str:
    if u.endswith("index.html"):
        return u[: -len("index.html")] or "./"     # index.html -> the directory itself
    return u[:-5] if u.endswith(".html") else u

cleaned = 0
for root, _, files in os.walk(DIST):
    for fn in files:
        if not fn.endswith((".html", ".xml")):
            continue
        fp = os.path.join(root, fn)
        s = orig = open(fp, encoding="utf-8").read()

        # absolute URLs on our own domain (canonical, og:url, sitemap <loc>, JSON-LD)
        s = re.sub(r'(%s/[^"\'<>\s]*?)\.html\b' % re.escape(BASE_URL),
                   lambda m: _strip(m.group(1) + ".html"), s)
        # relative internal links:  href="articles/article-1.html", href="../index.html", ...
        s = re.sub(r'(href=")((?!https?:|mailto:|tel:)[^"]*?\.html)(")',
                   lambda m: m.group(1) + _strip(m.group(2)) + m.group(3), s)

        if s != orig:
            open(fp, "w", encoding="utf-8").write(s)
            cleaned += 1

# ── cache-busting: append ?v=<hash of the file's contents> to asset references ──
hashes = {}
for name in CACHE_BUSTED:
    with open(os.path.join(DIST, name), "rb") as fh:
        hashes[name] = hashlib.sha256(fh.read()).hexdigest()[:8]

busted = 0
for root, _, files in os.walk(DIST):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        fp = os.path.join(root, fn)
        s = orig = open(fp, encoding="utf-8").read()
        for name, h in hashes.items():
            # matches  src="analytics.js"  and  src="../analytics.js"  (same for href=)
            s = re.sub(
                r'((?:src|href)=")((?:\.\./)?%s)(\?[^"]*)?(")' % re.escape(name),
                lambda m: f'{m.group(1)}{m.group(2)}?v={h}{m.group(4)}',
                s,
            )
        if s != orig:
            open(fp, "w", encoding="utf-8").write(s)
            busted += 1

print(f"Built ./dist with BASE_URL={BASE_URL}  ({templated} templated, {cleaned} url-cleaned, {busted} cache-busted)")
print("  asset versions: " + ", ".join(f"{n}?v={h}" for n, h in hashes.items()))
