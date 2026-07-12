#!/usr/bin/env python3
"""
Wire the generated images into the site:

  1. articles.html + index.html — swap each card's placeholder SVG for its real <img>.
  2. articles/article-N.html    — per-article og:image, twitter:image and Article-schema
                                  "image" (they all pointed at the *portrait* photo), plus a
                                  header image at the top of the article body.

Idempotent: safe to re-run.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Hebrew alt text — describes the picture, since these are decorative-but-meaningful.
ALT = {
    1:  "שתי טבעות נישואין מונחות בנפרד על מסמך הסכם, לצד עט נובע",
    2:  "שעון חול עתיק לצד מסמך חתום בחותם שעווה",
    3:  "שני מסמכים שונים זה לצד זה – אחד חתום בחותם שעווה ואחד קשור בסרט",
    4:  "מסמך יחיד ועליו שני עטים נובעים משני צדדיו, בסימטריה מלאה",
    5:  "שני ספלי קפה זה מול זה סביב שולחן עגול, עם תיק מסמכים ביניהם",
    6:  "מסמך צוואה לצד משקפי קריאה, עט נובע וחותמת שעווה",
    7:  "מסמך שנקרע לשני חצאים המונחים זה לצד זה על שולחן עץ כהה",
    8:  "זכוכית מגדלת מונחת על חוזה מסחרי עבה",
    9:  "מאזני צדק מפליז ועליהם חבילת קרטון קטנה",
    10: "מגדל קוביות עץ ובו קובייה אחת שנשלפה מהבסיס",
    11: "כיסא מנהלים ריק בראש שולחן דיונים מלוטש",
    12: "תוכנית אדריכלית מקופלת לצד מחוגה ועט נובע",
    13: "חותמת תאגיד מפליז לצד ערימת פנקסי חברה כרוכים",
}

CARD_RE = re.compile(
    r'(<div class="article-image">\s*)'
    r'<div class="article-image-placeholder">.*?</div>'
    r'(\s*)',
    re.S,
)


def wire_cards(path: pathlib.Path, img_prefix: str) -> int:
    s = path.read_text(encoding="utf-8")
    out, n, pos = [], 0, 0
    for m in CARD_RE.finditer(s):
        # Which article does this card link to? Look ahead to the next article-N.html href.
        link = re.search(r'articles?/?(?:article-)?(\d+)\.html|article-(\d+)\.html',
                         s[m.end(): m.end() + 2500])
        if not link:
            continue
        num = int(link.group(1) or link.group(2))
        img = (f'<img src="{img_prefix}article-{num}.jpg" '
               f'alt="{ALT[num]}" loading="lazy" decoding="async" width="1280" height="640">')
        out.append(s[pos:m.start()] + m.group(1) + img + m.group(2))
        pos = m.end()
        n += 1
    out.append(s[pos:])
    path.write_text("".join(out), encoding="utf-8")
    return n


def wire_article(num: int) -> list:
    path = ROOT / "articles" / f"article-{num}.html"
    s = path.read_text(encoding="utf-8")
    done = []

    # og:image / twitter:image / schema "image" → this article's own picture (was the portrait).
    new = re.sub(r'(<meta property="og:image" content=")__BASE_URL__/images/full_portrait\.jpeg(">)',
                 rf'\g<1>__BASE_URL__/images/article-{num}.jpg\g<2>', s)
    new = re.sub(r'(<meta name="twitter:image" content=")__BASE_URL__/images/full_portrait\.jpeg(">)',
                 rf'\g<1>__BASE_URL__/images/article-{num}.jpg\g<2>', new)
    new = re.sub(r'("image":\s*")__BASE_URL__/images/full_portrait\.jpeg(")',
                 rf'\g<1>__BASE_URL__/images/article-{num}.jpg\g<2>', new)
    if new != s:
        done.append("meta+schema")
        s = new

    # Header image at the top of the article body.
    if 'class="article-page-image"' not in s:
        fig = (f'\n        <figure class="article-page-image">\n'
               f'            <img src="../images/article-{num}.jpg" alt="{ALT[num]}" '
               f'width="1280" height="640" decoding="async">\n'
               f'        </figure>\n')
        s2 = s.replace('<main class="article-page-content">',
                       '<main class="article-page-content">' + fig, 1)
        if s2 != s:
            done.append("header image")
            s = s2

    path.write_text(s, encoding="utf-8")
    return done


print("cards:")
print(f"  articles.html  {wire_cards(ROOT / 'articles.html', 'images/')} card(s)")
print(f"  index.html     {wire_cards(ROOT / 'index.html', 'images/')} card(s)")
print("article pages:")
for i in range(1, 14):
    print(f"  article-{i:<2} {', '.join(wire_article(i)) or 'already wired'}")
