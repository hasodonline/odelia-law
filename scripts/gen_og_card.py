#!/usr/bin/env python3
"""
Generate images/og-card.jpg — the 1200x630 social-share card.

Why this exists: og:image must be a *landscape* ~1200x630 image, but the portrait
(full_portrait.jpeg) is 599x1024 (vertical). Pointing og:image straight at the portrait
while declaring 1200x630 lies to WhatsApp/Facebook/LinkedIn and breaks the preview.
This composites the portrait onto a softened crop of the hero background at the true size.

Run from the repo root:   python3 scripts/gen_og_card.py
Then rebuild + redeploy:  python3 build.py && npx wrangler pages deploy dist ...
"""
from PIL import Image, ImageFilter, ImageEnhance

W, H = 1200, 630
BG_SRC = "images/hero-bg.jpg"
PORTRAIT_SRC = "images/full_portrait.jpeg"
OUT = "images/og-card.jpg"

# background: cover-crop to 1200x630, then soften + darken so the portrait pops
bg = Image.open(BG_SRC).convert("RGB")
scale = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * scale), round(bg.height * scale)), Image.LANCZOS)
left, top = (bg.width - W) // 2, (bg.height - H) // 2
bg = bg.crop((left, top, left + W, top + H))
bg = bg.filter(ImageFilter.GaussianBlur(6))
bg = ImageEnhance.Brightness(bg).enhance(0.55)

# portrait: fit to card height with a margin, placed on the right (RTL site)
p = Image.open(PORTRAIT_SRC).convert("RGB")
target_h = H - 60
pw = round(p.width * (target_h / p.height))
p = p.resize((pw, target_h), Image.LANCZOS)
bg.paste(p, (W - pw - 70, (H - target_h) // 2))

bg.save(OUT, "JPEG", quality=88, optimize=True)
print(f"wrote {OUT}  {W}x{H}")
