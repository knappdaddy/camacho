#!/usr/bin/env python3
"""
Drops real photographs into the site.

Put your images in  incoming/  named after the slot they fill — the slot names
are listed in PHOTO-BRIEF.md and printed by this script with --list. Then:

    python3 tools/import-photos.py            # show what's there and what's missing
    python3 tools/import-photos.py --apply    # copy them in and update the HTML

Any of .jpg / .jpeg / .png / .webp works. Anything you don't supply keeps its
illustrated placeholder, so you can bring photos in a few at a time.
"""
import re
import shutil
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
INBOX = ROOT / "incoming"
EXTS = (".jpg", ".jpeg", ".png", ".webp")

# slot name -> path under assets/img (without extension)
SLOTS = {
    # homepage + shared
    "hero-bg": "site/hero-bg",
    "hero-before": "site/hero-before",
    "hero-after": "site/hero-after",
    "cta-bg": "site/cta-bg",
    "band-process": "site/band-process",
    "band-quote": "site/band-quote",
    "about-wide": "site/about-wide",
    "about-jobsite": "site/about-jobsite",
    "og-image": "site/og-image",
    # page headers
    "head-services": "site/head-services",
    "head-projects": "site/head-projects",
    "head-contact": "site/head-contact",
    # service tiles
    "tile-renovations": "site/tile-renovations",
    "tile-water": "site/tile-water",
    "tile-remediation": "site/tile-remediation",
    "tile-lead": "site/tile-lead",
    "tile-decks": "site/tile-decks",
    "tile-landscaping": "site/tile-landscaping",
    "tile-exteriors": "site/tile-exteriors",
    "tile-general": "site/tile-general",
}
for slug in ["hillside-kitchen", "basement-mold", "cedar-deck", "backyard-transform",
             "burst-pipe", "victorian-lead", "siding-roof", "basement-finish"]:
    SLOTS[f"{slug}-before"] = f"projects/{slug}-before"
    SLOTS[f"{slug}-after"] = f"projects/{slug}-after"


def find(slot):
    for ext in EXTS:
        p = INBOX / (slot + ext)
        if p.exists():
            return p
    return None


def main():
    apply = "--apply" in sys.argv
    if "--list" in sys.argv:
        for slot, dest in SLOTS.items():
            print(f"  incoming/{slot}.jpg   ->  assets/img/{dest}")
        return

    INBOX.mkdir(exist_ok=True)
    found, missing = [], []
    for slot, dest in SLOTS.items():
        src = find(slot)
        (found if src else missing).append((slot, dest, src))

    print(f"{len(found)} of {len(SLOTS)} slots supplied.\n")

    # A photo wiped against an illustration looks obviously broken, in a way
    # two merely-different photos do not. Catch half-supplied pairs early.
    supplied = {slot for slot, _, src in found if src}
    half = [s[:-7] for s in SLOTS
            if s.endswith("-before") and (s[:-7] + "-after") in SLOTS
            and (s in supplied) != ((s[:-7] + "-after") in supplied)]
    if half:
        print("WARNING — only one half of these before/after pairs is supplied.")
        print("The other half stays an illustration, which looks wrong when the")
        print("slider wipes between them. Supply both, or neither:")
        for slug in half:
            print(f"  {slug}")
        print()
    if not apply:
        if found:
            print("Ready to import:")
            for slot, dest, src in found:
                print(f"  {src.name:36} -> assets/img/{dest}{src.suffix}")
        if missing:
            print("\nStill using illustrations:")
            for slot, _, _ in missing:
                print(f"  {slot}")
        print("\nRun with --apply to import.")
        return

    html = list(ROOT.glob("*.html"))
    texts = {f: f.read_text() for f in html}
    changed = 0

    for slot, dest, src in found:
        target = ROOT / "assets" / "img" / (dest + src.suffix)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        old_ref = f"assets/img/{dest}.svg"
        new_ref = f"assets/img/{dest}{src.suffix}"
        if old_ref != new_ref:
            # References may carry a ?v=... cache-busting query (see
            # tools/stamp-build.py), so match the path and keep whatever follows.
            pattern = re.compile(re.escape(old_ref) + r'(\?v=[^"]*)?')
            for f in html:
                texts[f] = pattern.sub(new_ref, texts[f])
            stale = ROOT / "assets" / "img" / (dest + ".svg")
            stale.unlink(missing_ok=True)
        changed += 1
        print(f"  imported {src.name}")

    for f, t in texts.items():
        f.write_text(t)

    print(f"\n{changed} image(s) imported and referenced.")
    print("Check the pages, then delete the footer draft notice when the rest of")
    print("the placeholder content (phone, licence numbers, reviews) is real too.")


if __name__ == "__main__":
    main()
