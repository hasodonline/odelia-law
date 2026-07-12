# CLAUDE.md — lawodelia.co.il

Operating manual for the law-firm site of **עו״ד אודליה אייזנקייט** (Odelia Eisenkeit) —
family law, mediation (גישור), wills & enduring power of attorney (צוואות וייפוי כוח מתמשך).

Everything below is verified-live as of **2026-07-12**.

---

## 1. The golden rules

1. **`lawodelia.co.il` (apex, no `www`) is the canonical domain.** `www` 301-redirects to it.
2. **Never hardcode the domain.** All pages use the `__BASE_URL__` placeholder, replaced at build time.
   To change the domain you edit **one line** in `build.py`.
3. **Never commit `.env`** (it holds the Cloudflare API token). It is gitignored — keep it that way.
4. **Never deploy the repo root.** Deploy only `dist/` — otherwise `.env`, `.git`, `prompts/`,
   and the `*.md` notes would be published.
5. **Ads copy must stay Israeli-Bar-compliant**: no superlatives ("הכי טוב", "מספר 1"),
   no guarantees of results, no promises. Factual and dignified only.

---

## 2. Deploy (the only command you need)

```bash
python3 build.py          # renders ./dist, injecting BASE_URL into every page
npx wrangler@latest pages deploy dist --project-name lawodelia --branch main
```

`build.py` copies `index.html, articles.html, style.css, config.js, analytics.js, robots.txt,
sitemap.xml` + `images/` + `articles/` into `dist/`, replacing `__BASE_URL__` everywhere
(`.html/.xml/.txt/.js`).

**To change the primary domain:** edit `BASE_URL` at the top of `build.py`, rebuild, redeploy —
then also update the Cloudflare redirect rule (§4) and the Ads final URLs (§7).

Wrangler auth comes from `.env` (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`):
```bash
set -a && . ./.env && set +a && npx wrangler@latest pages deploy dist --project-name lawodelia --branch main
```

### Cache busting (important — this once silently broke GA4)
Cloudflare's **Browser Cache TTL is 4 hours**, so after a deploy, returning visitors kept getting the
**old** `analytics.js` — the GA4 tag looked "deployed" but was **not actually running in browsers**.

`build.py` now solves this automatically: it hashes `config.js`, `analytics.js`, `style.css` and
rewrites every HTML reference to `analytics.js?v=<hash>`. A changed file ⇒ a new URL ⇒ every browser
refetches immediately. **Don't remove this.** Handles both `src="analytics.js"` and `src="../analytics.js"`.

Verify a deploy actually reached browsers:
```bash
curl -sS https://lawodelia.co.il/ | grep -o 'analytics.js?v=[a-f0-9]*'   # hash should change
curl -sS https://lawodelia.co.il/analytics.js | grep GA_MEASUREMENT_ID
```
The API token **cannot purge cache** (missing permission) → purge in the **dashboard**
(Caching → Configuration → Purge Everything). With cache-busting in place you rarely need to.

---

## 3. Hosting

- **Cloudflare Pages**, project **`lawodelia`** (also at `lawodelia.pages.dev`).
- Cloudflare account: `c314460a7bae1fe843886cbe5733c5f0` (owner **lawodelia@gmail.com**).
- Zone `lawodelia.co.il`: `f27f2e47db1b5d58c6f1daba8e49c712`.
- Domain registered at **LiveDNS**, but nameservers now point to Cloudflare
  (`anderson.ns.cloudflare.com` / `kenia.ns.cloudflare.com`).
- Both `lawodelia.co.il` and `www.lawodelia.co.il` are Pages custom domains — `status=active`,
  `cert=active` (Google Trust Services cert).

### `.env` (gitignored)
`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_ZONE_ID`.

**Token scope:** DNS:Edit, Pages:Edit, Zone:Read/Edit.
**It does NOT have:** Rulesets/Redirect-Rules, or Cache-Purge → those must be done in the
**dashboard**, not the API. (Don't waste time debugging "Authentication error" on those endpoints.)

---

## 4. Domain & redirects

| URL | Behaviour |
|---|---|
| `https://lawodelia.co.il` | **200 — serves the site** (canonical) |
| `https://www.lawodelia.co.il` | **301 → `https://lawodelia.co.il`** |
| `http://…` (either) | 301 → https apex |

The redirect is a Cloudflare **Redirect Rule** (Rules → Redirect Rules), named
*"Redirect www to apex (canonical)"*, id `aa30fec605f64f5f9411375ad7d61b37`:

- **When:** `(http.host eq "www.lawodelia.co.il")`
- **Then:** dynamic → `concat("https://lawodelia.co.il", http.request.uri.path)`, **301**, preserve query string.

> To flip canonical back to `www`, reverse this rule **and** change `BASE_URL` in `build.py`.
> Only ever have **one** canonical serving directly; the other must redirect (avoids duplicate content).

**History / gotcha:** the apex cert was once wedged (ERR_CONNECTION_RESET, 0-byte assets) because the
Pages custom domain was deleted & re-added repeatedly, tripping Let's Encrypt rate limits. It
self-healed once the window passed. **Do not churn the Pages custom domains** — be patient instead.

### Email
**Cloudflare Email Routing** is on: catch-all `@lawodelia.co.il` → **lawodelia@gmail.com**,
with MX + SPF + DKIM + DMARC set (anti-spoofing).

---

## 5. Site structure

| File | Purpose |
|---|---|
| `index.html` | Homepage (hero, about, practice areas, CTA) |
| `articles.html` | Article index |
| `articles/article-1..13.html` | **13** articles, each with `Article` JSON-LD + canonical + OG |
| `config.js` | **Single source of truth** for name, phone, WhatsApp, email, address |
| `analytics.js` | GA4 + lead-event tracking (see §6) |
| `style.css` | All styling |
| `sitemap.xml`, `robots.txt` | SEO |
| `build.py` | The build (BASE_URL injection) |

**No contact form** — deliberately removed. The CTA is **call + WhatsApp** (higher conversion, no
mail backend needed).

### Key contact details (in `config.js`)
- **עו״ד אודליה אייזנקייט** — phone **050-2899933** (`tel:+9720502899933`),
  WhatsApp `https://wa.me/9720502899933`, email **lawodelia@gmail.com**
- Office: **רחוב ארלוזרוב 17, הוד השרון** (4520317)
- Credentials: **LL.B + certified mediator (משרד המשפטים)**.
  ⚠️ She does **NOT** have a master's degree — never re-add one.

---

## 6. Analytics (GA4) — LIVE

- **Property:** `lawodelia.co.il` · Account *"עו״ד אודליה אייזנקייט"* · Israel TZ · ILS
- **Measurement ID: `G-VTQ9HQ301F`** (web stream, enhanced measurement ON)
- Under **lawodelia@gmail.com** (`authuser=2` in the browser)

`analytics.js` is loaded on **every** page and:
- loads gtag with `GA_MEASUREMENT_ID`
- fires **`generate_lead`** on clicks to `tel:` links, `wa.me`/WhatsApp links, and the (now-absent) form

⚠️ **This means a page with no `tel:`/`wa.me` link can never produce a lead event.** The 13 articles
originally had only a "צרו קשר" link back to `index.html#contact`, so *every article lead was
invisible* to GA4 and unattributable in Ads. Every article now carries a real call + WhatsApp CTA.
**Any new page must include them too** — otherwise it silently cannot convert.

```js
var GA_MEASUREMENT_ID = "G-VTQ9HQ301F";
var ADS_CONVERSION = { id: "", label: "" };   // ← still empty, see below
```

### GA4 ↔ Google Ads — LINKED ✅
Linked to Ads account **262-642-2592** (GA4 Admin → Product links → Google Ads links).
Personalized advertising ON, auto-tagging ON, Analytics-access-from-Ads ON.
Ads data appears in GA4 within ~24h.

### Last step remaining: turn `generate_lead` into an Ads conversion
GA4 only lets you star an event as a **key event after it has fired at least once**. A seed
`generate_lead` event was fired on 2026-07-12 (so there is **one test lead** in the data — ignore it).

Once it appears (Admin → Data display → **אירועים**):
1. **Star** `generate_lead` on the *Key events* tab.
2. Google Ads → Goals → Conversions → **New → Import → Google Analytics 4** → pick `generate_lead`.

The Ads account already has a default **phone-call** conversion goal, which tracks calls from the
ad's call asset — that part already works.

> Note: `ADS_CONVERSION` in `analytics.js` is intentionally left empty. Importing from GA4 (above) is
> the cleaner path and needs no code change. Only fill `ADS_CONVERSION` if you instead create a
> native Ads conversion action.

---

## 7. Google Ads — LIVE (spending!)

- **Account:** `262-642-2592` (lawodelia@gmail.com), ILS, Israel TZ
- **Campaign:** *"אודליה - חיפוש - דיני משפחה וצוואות"* — **id `24028356178`**, status **פעיל / Active**
- **Budget: ₪13.15/day ≈ ₪400/month**
- **Bidding:** Maximize Clicks with a **₪18 max-CPC cap**
  *(deliberately NOT conversion bidding — the account has no conversion history yet)*
- **Networks:** Google Search + search partners. **Display network OFF** (wastes budget).
- **AI Max: OFF** — no keyword expansion, no final-URL expansion, no auto text customization.
  This is intentional: it protects the tiny budget **and** keeps ad text Bar-compliant.
- **Geo:** הוד השרון, הרצליה, כפר סבא, רמת השרון, רעננה — with the **"נוכחות" (presence)** option,
  so only people physically in/regularly in the area (not people merely *searching about* it).
- **Languages:** Hebrew, English, Russian.
- **Final URL:** `https://lawodelia.co.il` (apex).

### Ad group 1 — צוואות / ירושה / ייפוי כוח (6 phrase-match keywords)
`"עורך דין צוואות"`, `"עריכת צוואה"`, `"עורך דין ירושה"`, `"ייפוי כוח מתמשך"`,
`"עורך דין ייפוי כוח מתמשך"`, `"עורך דין צוואות וירושות"`

One RSA: 10 Bar-compliant headlines + 3 descriptions, ad strength **Average**.

### Why these keywords (real Keyword Planner data)
- Wills/POA/inheritance: **₪0.7–14 CPC, low competition** → best ROI. **Lead here.**
- Agreements (הסכם ממון / הסכם גירושין): ₪1.8–12 — good secondary.
- Mediation (גישור גירושין / מגשרת): ₪9–34 — secondary.
- ❌ **`עורך דין גירושין` was deliberately DROPPED** — ₪22–52 CPC would eat the whole ₪400 budget.

### Negative keywords (35, campaign-level, broad match)
`דרושים, דרוש, משרה, משרות, עבודה, שכר, מתמחה, התמחות, קריירה, חינם, בחינם, דוגמה, דוגמא, תבנית,
טופס, להורדה, pdf, word, סטודנט, סטודנטים, לימודים, קורס, תואר, אוניברסיטה, מבחן, בחינה, ויקיפדיה,
מחשבון, משמעות, הגדרה, מה זה, משכורת, ג'וב, jobs, free`

Add more at: Campaigns → **מילות מפתח → מילות מפתח שליליות**.

### Ongoing maintenance (do this!)
- **Watch the Search Terms report weekly** for the first month and add wasteful queries as negatives.
- Ad strength is "Average" — adding **4 sitelinks** would lift it to "Good".
- Optional 2nd ad group: **גישור / הסכמים**.

### ⚠️ Gotchas
- **Advertiser identity verification** was required before publishing (needs Odelia's personal /
  business documents — *not* something to do on her behalf). It is done.
- Changing an ad's **final URL** can trigger a re-auth (password) prompt.
- The Ads Expert UI resizes the window mid-interaction; UI clicks can land in the wrong field.
  For reliable edits, set values via the DOM with a **native setter + `input` event** — but note this
  works for **existing** fields, not for creating new ones.

---

## 8. SEO

**Done:**
- Canonical, `og:url`, sitemap, and JSON-LD all on **apex** (`https://lawodelia.co.il`)
- Structured data: **`LegalService`** (homepage) + **`Article`** on all 13 articles
- Local SEO: geo meta tags, `areaServed` cities, location in `<title>`
  ("הוד השרון והשרון")
- `www` redirects to apex → **no duplicate content**
- Valid HTTPS on both hostnames

### Google Search Console — DONE
- **Domain property `sc-domain:lawodelia.co.il`** (covers apex + www + http/https)
- **Auto-verified via the live GA4 tag** — once `G-VTQ9HQ301F` was on the site, no DNS/OAuth needed.
  *(Handy trick: deploy GA4 first, then Search Console verifies itself.)*
- **Sitemap `https://lawodelia.co.il/sitemap.xml` submitted → status Success, 15 pages discovered.**

> If you ever must verify by DNS instead: Search Console pushes a Cloudflare **OAuth** flow.
> Prefer adding the `google-site-verification` **TXT** record yourself via the API token (DNS:Edit)
> rather than granting Google OAuth access to the Cloudflare account.

### On-page SEO conventions (added 2026-07-12 — keep them)
- **One keyword-bearing H1 per page.** The homepage H1 used to be just the name; it now names the
  practice areas + city. Ads land here, so this is also the Landing-Page-Experience signal.
- **Every article** has: `Article` + **`BreadcrumbList`** JSON-LD, a **מאמרים קשורים** block (3 links,
  topic clusters `{2,3,6}` wills/POA · `{1,4,5}` family · `{7,8,9}` contracts · `{10..13}` corporate),
  a **כל המאמרים** nav link, and **tel: + wa.me CTAs**.
  Regenerate with `python3 scripts/seo_patch_articles.py` (idempotent).
- `articles.html` carries `CollectionPage` + `ItemList`.
- **`&quot;` is NOT decoded inside `<script type="application/ld+json">`** — it lands in the value
  literally and invalidates it. Use the Hebrew gershayim `״` (U+05F4) in JSON-LD, never `&quot;`.
- **Hours live in three places** — `config.js`, the visible text, and the `LegalService` JSON-LD.
  They drifted apart once (09:00 vs 08:00, phantom Friday hours). They must all match **GBP**:
  **ראשון–חמישי 08:00–18:00, שישי–שבת סגור**.
- **`sameAs` was removed** from the JSON-LD: it pointed at three social URLs
  (`facebook.com/odelia.law`, `instagram.com/odelia.law`, `linkedin.com/in/odelia-law`) that are
  probably fabricated. Fabricated `sameAs` hurts entity resolution. The footer still links to them —
  **confirm they're real, or delete them.** The `sameAs` that actually matters is the **GBP URL**.
- `_headers` sets `Access-Control-Allow-Origin: *` on `/images/*` (needed to upload site images into
  Google's GBP uploader from the browser; also harmless/good for images generally).

### Google Business Profile (GBP) — Odelia's task
Biggest remaining lever for **local** search (Maps / local pack).
- Category must be **"עורך דין"** (Lawyer). *Not* the broad GA4 category.
- Verification (postcard / phone / video) must be completed by Odelia herself.
- Keep NAP **identical** to the site: name, `רחוב ארלוזרוב 17, הוד השרון`, `050-2899933`.

---

## 9. Accounts & where things live

| Thing | Where | Note |
|---|---|---|
| Hosting / DNS / Email | Cloudflare (lawodelia@gmail.com) | token in `.env` |
| Analytics | GA4 `G-VTQ9HQ301F` | `authuser=2` |
| Search Console | `sc-domain:lawodelia.co.il` | verified |
| Google Ads | `262-642-2592` | campaign `24028356178` live |
| Registrar | LiveDNS | NS delegated to Cloudflare |

All Google properties are under **lawodelia@gmail.com**. In this Chrome profile that account is
**`authuser=2`** — append `?authuser=2` to Google URLs or you'll land in the wrong account.

---

## 10. Quick runbook

**Change site text/design** → edit the HTML/CSS → `python3 build.py` → deploy → verify with a
cache-buster.

**Change phone / address / name** → edit **`config.js` only** → rebuild → deploy.

**Add an article** → create `articles/article-N.html` (copy an existing one: keep `Article` JSON-LD,
canonical, OG) → add it to `articles.html` **and** `sitemap.xml` → rebuild → deploy → (optionally
re-submit the sitemap in Search Console).

**Change domain** → `BASE_URL` in `build.py` + flip the Cloudflare redirect rule + update Ads final
URLs + add the new domain in Search Console.

**Pause the ads** → Google Ads → the campaign → status → מושהה. (It spends ₪13.15/day while active.)
