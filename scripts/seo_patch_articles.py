#!/usr/bin/env python3
"""
SEO pass over articles/article-1..13.html.

Fixes, in order of value:
  1. Real conversion CTAs (tel: + wa.me) in every article. Until now the only CTA was a
     link back to index.html#contact — so `generate_lead` (analytics.js binds it to tel:/wa.me
     clicks) could never fire from an article, and Ads could not attribute a single article lead.
  2. Related-article clusters + a link to the article index. The 13 articles previously linked
     only to the homepage: no article→article link existed anywhere.
  3. BreadcrumbList JSON-LD (דף הבית › מאמרים › <title>).
  4. `&quot;` leaking literally into the JSON-LD strings (invalid values) → Hebrew gershayim ״.
  5. Brand name in the nav was JS-injected only; hardcode it.
  6. fetchpriority on the LCP hero image.

Run from the repo root:  python3 scripts/seo_patch_articles.py
"""
import re, pathlib

PHONE_LINK = "tel:+9720502899933"
WA_LINK = "https://wa.me/9720502899933"

TITLES = {
    1: "מה חשוב לדעת לפני חתימה על הסכם גירושין",
    2: "ייפוי כוח מתמשך – למה לא כדאי לחכות לרגע האחרון",
    3: "מה ההבדל בין צוואה רגילה לייפוי כוח מתמשך",
    4: "הסכם הורות משותפת – הנקודות שחייבים להסדיר מראש",
    5: "מתי כדאי לפנות להליך גישור במקום לבית המשפט",
    6: "טעויות נפוצות בעריכת צוואה",
    7: "איך מתמודדים עם הפרת הסכם",
    8: "מה חשוב לבדוק לפני חתימה על הסכם מסחרי",
    9: "זכויות צרכניות – מתי כדאי להגיש תביעה",
    10: "ניהול סיכונים משפטיים – למה חשוב לטפל נכון כבר מהשלב הראשון",
    11: "אחריות דירקטורים ונושאי משרה – מה חשוב לדעת",
    12: "ליווי משפטי לחברות – טעויות נפוצות בתחילת הדרך",
    13: "חשיבות ממשל תאגידי תקין בחברות ובתאגידים",
}

# topic clusters — each article links to its 3 closest siblings
CLUSTERS = [[2, 3, 6], [1, 4, 5], [7, 8, 9], [10, 11, 12, 13]]
RELATED = {}
for cluster in CLUSTERS:
    for n in cluster:
        sibs = [m for m in cluster if m != n]
        # top up to 3 from the nearest other cluster so nothing has fewer than 3 links
        if len(sibs) < 3:
            pool = [m for c in CLUSTERS if n not in c for m in c]
            sibs += pool[: 3 - len(sibs)]
        RELATED[n] = sibs[:3]

ROOT = pathlib.Path(__file__).resolve().parent.parent


def related_block(n: int) -> str:
    items = "\n".join(
        f'                <li><a href="article-{m}.html">{TITLES[m]}</a></li>'
        for m in RELATED[n]
    )
    return f"""
        <!-- Related articles -->
        <aside class="article-related">
            <h3>מאמרים קשורים</h3>
            <ul>
{items}
            </ul>
            <p><a href="../articles.html">לכל המאמרים &larr;</a></p>
        </aside>
"""


def breadcrumb(n: int) -> str:
    return f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "דף הבית", "item": "__BASE_URL__/"}},
        {{"@type": "ListItem", "position": 2, "name": "מאמרים", "item": "__BASE_URL__/articles.html"}},
        {{"@type": "ListItem", "position": 3, "name": "{TITLES[n]}", "item": "__BASE_URL__/articles/article-{n}.html"}}
      ]
    }}
    </script>
"""


for n in range(1, 14):
    fp = ROOT / "articles" / f"article-{n}.html"
    s = orig = fp.read_text(encoding="utf-8")

    # 1. conversion CTA — replace the single index.html#contact button
    s = re.sub(
        r'<a href="\.\./index\.html#contact" class="btn btn-primary" id="cta-button">[^<]*</a>',
        f'<a href="{PHONE_LINK}" class="btn btn-primary" id="cta-button">חייגו 050-2899933</a>\n'
        f'            <a href="{WA_LINK}" class="btn btn-secondary" target="_blank" rel="noopener">שלחו הודעת וואטסאפ</a>',
        s,
    )

    # 2a. related-articles block, immediately before the CTA box
    if "article-related" not in s:
        s = s.replace(
            '        <!-- CTA Box -->',
            related_block(n) + '\n        <!-- CTA Box -->',
            1,
        )
    # 2b. link the article index from the nav
    s = s.replace(
        '            <a href="../index.html" class="article-nav-back">חזרה לדף הבית &larr;</a>',
        '            <a href="../articles.html" class="article-nav-back">כל המאמרים</a>\n'
        '            <a href="../index.html" class="article-nav-back">חזרה לדף הבית &larr;</a>',
        1,
    )

    # 3. breadcrumbs
    if "BreadcrumbList" not in s:
        s = s.replace("</head>", breadcrumb(n) + "</head>", 1)

    # 4. &quot; is NOT decoded inside <script type="application/ld+json"> — it lands in the value
    def fix_ldjson(m):
        return m.group(0).replace("&quot;", "״")  # ״ HEBREW PUNCTUATION GERSHAYIM

    s = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        fix_ldjson,
        s,
        flags=re.S,
    )

    # 5. brand name in nav was rendered by JS only — put it in the HTML
    s = s.replace(
        '<span id="nav-lawyer-title"></span>',
        '<span id="nav-lawyer-title">עו״ד</span>',
    ).replace(
        '<span id="nav-lawyer-name" style="font-size:1.3rem;color:#fff;"></span>',
        '<span id="nav-lawyer-name" style="font-size:1.3rem;color:#fff;">אודליה אייזנקייט</span>',
    )

    # 6. the article hero image is the LCP element
    s = re.sub(
        r'(<img src="\.\./images/article-%d\.jpg")' % n,
        r'\1 fetchpriority="high"',
        s,
    )

    if s != orig:
        fp.write_text(s, encoding="utf-8")
        print(f"patched article-{n}.html  → related: {RELATED[n]}")
