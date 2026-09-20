#!/usr/bin/env python3
"""
Stamps the current UTC time into the footer draft notice of every page.

The point is the preview loop: after a push you refresh
https://knappdaddy.github.io/camacho/ and want to know, at a glance, whether
you are looking at the new version or a cached old one. The stamp answers that.

Run it immediately before committing:

    python3 tools/stamp-build.py && git add -A && git commit -m "..." && git push

It lives inside the draft-notice block, so it disappears along with that block
when the real content goes in.
"""
import datetime
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

OLD = re.compile(r'<span data-build>[^<]*</span>')
MARKER = "(class <code>notice</code>) when the real content is in."

changed = 0
for page in sorted(ROOT.glob("*.html")):
    t = page.read_text()
    if OLD.search(t):
        t = OLD.sub(f'<span data-build>{stamp}</span>', t)
    elif MARKER in t:
        t = t.replace(
            MARKER,
            MARKER + f'\n      <br><b>Preview build:</b> <span data-build>{stamp}</span>',
            1)
    else:
        continue
    page.write_text(t)
    changed += 1

print(f"Stamped {changed} page(s): {stamp}")
