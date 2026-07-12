#!/usr/bin/env python3
"""
Generate the site's imagery with fal.ai `gpt-image-2` and write it to ./images.

    export FAL_KEY=...          # or it is read from ../Hamashpianit/.env
    python3 scripts/gen_images.py            # all missing images
    python3 scripts/gen_images.py hero 7 10  # only these keys
    python3 scripts/gen_images.py --force    # re-generate even if the file exists

ART DIRECTION
-------------
One coherent editorial still-life system, so the 13 cards read as a single set
in the grid rather than 13 unrelated stock photos:

  * every shot is a still life on a dark walnut desk, one warm directional
    light, deep navy shadows, brass/gold accents — the site's own --navy /
    --gold palette;
  * the SUBJECT carries the article's idea (a metaphor, not a caption);
  * no people and no legible text, ever. Faces would imply real clients, and a
    generative model writing English words onto a document is actively wrong on
    a Hebrew RTL site — so paper is always blurred, illegible texture.

The gavel is deliberately absent: Israeli courts don't use one. It's a US TV
prop and would read as stock-photo filler to the audience this site is for.
"""
import os, sys, json, pathlib, concurrent.futures, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
ENDPOINT = "https://fal.run/fal-ai/gpt-image-2"

# ── the shared look. Appended to every subject prompt. ────────────────────────
STYLE = (
    "Editorial still-life photograph on the dark walnut desk of a modern law office. "
    "A single warm directional light from the left rakes across the scene, catching gold "
    "and brass highlights and falling off into deep, rich navy-black shadow. "
    "Restrained palette: deep navy, warm brass gold, cream, warm brown — nothing else. "
    "Shallow depth of field, calm, premium, cinematic, understated. "
    "Photorealistic high-end commercial photography, natural film grain. "
    "ABSOLUTELY NO PEOPLE, no hands, no faces, no body parts. "
    "ABSOLUTELY NO TEXT of any kind — no letters, no words, no numbers, no handwriting, "
    "no logos, no signage, no watermark. Any paper or document in frame must be shown at an "
    "angle or out of focus so its surface is only soft, illegible abstract texture. "
    "Composed as a wide 2:1 crop with the subject slightly off-center and generous empty "
    "negative space, so the image survives a tight center crop."
)

HERO_STYLE = (
    "Wide-angle architectural interior photograph, ultra high quality, photorealistic. "
    "Warm golden late-afternoon light, deep navy shadows, brass accents, cream stone. "
    "Calm, spacious, expensive, understated. Shallow depth of field with soft bokeh. "
    "NO PEOPLE. NO TEXT, no letters, no words, no logos, no signage anywhere."
)

# key -> (filename, width, height, subject prompt)
# width/height must be multiples of 16; total px between 655,360 and 8,294,400.
JOBS = {
    # Hero — sits at opacity .15 behind navy, so it must be a *texture*, not a busy scene.
    "hero": ("hero-bg.jpg", 2048, 1152,
        "The corner of a quiet, empty modern law office at golden hour. Floor-to-ceiling "
        "windows on the left throw long warm light across a polished dark walnut table. "
        "Behind, a wall of leather-bound books sits far out of focus in soft bokeh. "
        "Simple, uncluttered, mostly shadow and light — an atmospheric backdrop, not a busy scene. "
        + HERO_STYLE),

    # 1 — divorce agreement. Two rings, apart: the separation is the whole point.
    "1": ("article-1.jpg", 1280, 640,
        "Two plain gold wedding bands resting on a folded document, deliberately set apart "
        "from each other with a clear gap of empty desk between them. A slim fountain pen lies "
        "to one side. Quiet, dignified, a little melancholy — never harsh. " + STYLE),

    # 2 — enduring power of attorney. Time running out on a decision people defer.
    "2": ("article-2.jpg", 1280, 640,
        "An elegant antique hourglass with brass caps, its sand mid-fall, standing beside a "
        "single folded document closed with a dark gold wax seal. The hourglass is the hero of "
        "the frame. A sense of time quietly passing while a decision waits. " + STYLE),

    # 3 — will vs. enduring POA. A comparison: two documents, deliberately distinct.
    "3": ("article-3.jpg", 1280, 640,
        "Two clearly distinct folded documents laid side by side on the desk, parallel and "
        "evenly spaced: the left one closed with a deep red-gold wax seal, the right one bound "
        "with a thin navy silk ribbon. A study in two things people confuse for each other. " + STYLE),

    # 4 — co-parenting agreement. One document, two parties, a child implied not shown.
    "4": ("article-4.jpg", 1280, 640,
        "A single document centered on the desk with two identical fountain pens resting on it "
        "from opposite sides, perfectly symmetrical — two parties, one shared agreement. Far "
        "behind, thrown well out of focus, a single small wooden toy building block catches the "
        "warm light. Tender, hopeful, orderly. " + STYLE),

    # 5 — mediation. Dialogue across a table, not confrontation across a courtroom.
    "5": ("article-5.jpg", 1280, 640,
        "Two simple ceramic coffee cups placed facing each other across a polished round table, "
        "with one closed folder resting on the table between them. Two empty chairs are just "
        "visible, softly out of focus. Warm, human, conversational — the mood of people working "
        "it out in a room together rather than fighting in a courtroom. " + STYLE),

    # 6 — mistakes when drafting a will. Craft, care, the cost of a slip.
    "6": ("article-6.jpg", 1280, 640,
        "A single formal document on the desk beside a pair of folded reading glasses and an "
        "antique fountain pen with its cap off. A brass seal stamp rests nearby. Intimate, "
        "close, careful — the atmosphere of exacting work where one small slip matters. " + STYLE),

    # 7 — breach of contract. The single strongest, most legible metaphor in the set.
    "7": ("article-7.jpg", 1280, 640,
        "One document torn cleanly into two halves, the two pieces lying slightly apart on the "
        "dark desk, the ragged torn edges catching a bright rim of warm light. Stark, graphic, "
        "unmistakable. Everything else in frame is empty desk. " + STYLE),

    # 8 — reviewing a commercial agreement. Due diligence = looking closer.
    "8": ("article-8.jpg", 1280, 640,
        "An antique brass magnifying glass resting on a thick, dense multi-page contract, its "
        "lens catching the warm light and throwing a small bright caustic onto the page beneath. "
        "The paper beneath the lens is soft and unreadable. The mood of careful scrutiny before "
        "signing. " + STYLE),

    # 9 — consumer rights. Consumer vs. business, weighed.
    "9": ("article-9.jpg", 1280, 640,
        "A small antique brass balance scale on the desk, its two pans slightly out of balance. "
        "On the lower pan sits a small plain cardboard parcel; the other pan is empty. Clean, "
        "graphic, quietly hopeful. " + STYLE),

    # 10 — legal risk management. Risk you didn't know you were carrying.
    "10": ("article-10.jpg", 1280, 640,
        "A tall tower of stacked pale wooden blocks standing on the dark desk, with one single "
        "block pulled halfway out near the base, caught in a bright rim of warm light. The tower "
        "is still standing — for now. Tense, precise, quiet. " + STYLE),

    # 11 — director & officer liability. The seat carries the weight.
    "11": ("article-11.jpg", 1280, 640,
        "A single empty dark leather executive chair at the head of a long polished boardroom "
        "table, seen from across the room. Warm light falls on the chair; the rest of the "
        "boardroom recedes into navy shadow and soft focus. The weight of an empty seat. "
        "NO PEOPLE. NO TEXT. Photorealistic, cinematic, deep navy and warm gold palette, "
        "shallow depth of field, generous negative space, wide 2:1 crop."),

    # 12 — legal counsel for young companies. Get the foundations right.
    "12": ("article-12.jpg", 1280, 640,
        "A folded architectural blueprint-style plan on the desk — its lines soft and abstract, "
        "never legible — with a brass drafting compass and a fountain pen resting on top. The "
        "idea of building something properly from the foundation up. " + STYLE),

    # 13 — corporate governance: the machinery of formal accountability.
    # (An earlier take shot this top-down as a symmetric boardroom; it read as CGI wallpaper and
    #  broke the desk-still-life language every other card speaks. Kept in the system instead.)
    "13": ("article-13.jpg", 1280, 640,
        "A heavy antique brass corporate seal embosser standing on the dark desk, its arm raised, "
        "catching a bright rim of warm light. Beside it, a neat squared-off stack of three "
        "leather-bound company registers. The instrument of formal accountability. " + STYLE),
}


def fal_key() -> str:
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"]
    donor = ROOT.parent / "Hamashpianit" / ".env"
    if donor.exists():
        for line in donor.read_text(encoding="utf-8").splitlines():
            if line.startswith("FAL_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("No FAL_KEY in the environment and none found in ../Hamashpianit/.env")


KEY = fal_key()


def generate(item):
    key, (fname, w, h, prompt) = item
    body = json.dumps({
        "prompt": prompt,
        "image_size": {"width": w, "height": h},
        "output_format": "jpeg",
        "num_images": 1,
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        return key, fname, f"HTTP {e.code}: {e.read().decode()[:300]}"

    images = out.get("images") or []
    if not images:
        return key, fname, f"no image in response: {json.dumps(out)[:300]}"

    dest = IMAGES / fname
    with urllib.request.urlopen(images[0]["url"], timeout=300) as r:
        dest.write_bytes(r.read())
    return key, fname, f"OK  {dest.stat().st_size // 1024} KB  {w}x{h}"


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv

    jobs = {k: v for k, v in JOBS.items() if not argv or k in argv}
    if not force:
        jobs = {k: v for k, v in jobs.items() if not (IMAGES / v[0]).exists()}

    if not jobs:
        print("Nothing to do — every requested image already exists (use --force to redo).")
        return

    IMAGES.mkdir(exist_ok=True)
    print(f"Generating {len(jobs)} image(s) with fal-ai/gpt-image-2 …\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for key, fname, status in pool.map(generate, jobs.items()):
            print(f"  [{key:>4}] {fname:<18} {status}")


if __name__ == "__main__":
    main()
