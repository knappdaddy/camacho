#!/usr/bin/env python3
"""
Stamps a build version into every page and cache-busts the assets.

Two jobs, both in service of one thing: you push, you refresh, you see the new
version. No hard refresh, no "is this cached?".

1. A UTC timestamp in the footer draft notice, so you can confirm at a glance
   which build you are looking at.
2. A ?v=<build> query on every stylesheet, script and image reference. Asset
   filenames stay stable across edits — hero-bg.svg is always hero-bg.svg — so
   without this a browser keeps serving whatever it cached the first time, even
   though the file changed. The query makes each build a distinct URL.

Fonts are deliberately excluded: they never change, and a query would break the
match between the <link rel="preload"> and the @font-face request, causing the
font to download twice.

Run it immediately before committing:

    python3 tools/stamp-build.py && git add -A && git commit -m "..." && git push
"""
import datetime
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
now = datetime.datetime.now(datetime.timezone.utc)
human = now.strftime("%Y-%m-%d %H:%M UTC")
version = now.strftime("%Y%m%d-%H%M")

STAMP = re.compile(r'<span data-build>[^<]*</span>')
MARKER = "(class <code>notice</code>) when the real content is in."
# href/src pointing at assets/css, assets/js or assets/img — not assets/fonts.
ASSET = re.compile(r'((?:href|src)=")(assets/(?:css|js|img)/[^"?]+)(?:\?v=[^"]*)?(")')

changed = 0
for page in sorted(ROOT.glob("*.html")):
    original = page.read_text()
    t = ASSET.sub(rf'\1\2?v={version}\3', original)

    if STAMP.search(t):
        t = STAMP.sub(f'<span data-build>{human}</span>', t)
    elif MARKER in t:
        t = t.replace(MARKER,
                      MARKER + f'\n      <br><b>Preview build:</b> <span data-build>{human}</span>',
                      1)

    if t != original:
        page.write_text(t)
        changed += 1

busted = sum(len(ASSET.findall(p.read_text())) for p in ROOT.glob("*.html"))
print(f"Stamped {changed} page(s) as {human}")
print(f"Cache-busted {busted} asset reference(s) with ?v={version}")
