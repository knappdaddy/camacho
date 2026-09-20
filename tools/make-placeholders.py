#!/usr/bin/env python3
"""
Generates every placeholder image on the site.

These are not grey boxes: each one is a tonal abstract "scene" (wall plane,
floor line, window light, vignette) at the exact aspect ratio the layout
expects. The point is that the page can be judged for composition and text
contrast now, and each file swapped for a real photograph later.

Usage:  python3 tools/make-placeholders.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# Tonal families. (sky/wall top, wall bottom, floor, light accent, ambience)
TONES = {
    # dim, cool, unloved — reads as a "before"
    "before": ("#4A5058", "#313740", "#262B31", "#8A94A0", "#A5B0BD"),
    # warm, lit, finished — reads as an "after"
    "after":  ("#4A5560", "#2E3842", "#232B33", "#EFA25E", "#FFC98E"),
    # bright interior — for photographs that sit behind a scrim
    "airy":   ("#8A97A5", "#5A6470", "#46505B", "#E8A263", "#FFD9A8"),
    # deep and rich — where a darker frame suits the composition
    "deep":   ("#2A343E", "#151C22", "#0E1318", "#D9884A", "#F0A867"),
    # lighter, open — feature bands on pale sections
    "light":  ("#7C8794", "#525C67", "#3C444D", "#DE9760", "#F5BE8B"),
}

def rng(seed_text):
    """Tiny deterministic PRNG so every slug gets a stable, varied scene."""
    state = 2166136261
    for ch in seed_text:
        state = ((state ^ ord(ch)) * 16777619) & 0xFFFFFFFF

    def nxt(lo=0.0, hi=1.0):
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return lo + (state / 0x7FFFFFFF) * (hi - lo)

    return nxt


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def scene(path, w, h, tone, seed, label=None, tag=None, caption="REPLACE WITH PHOTO"):
    top, bottom, floor, accent, glow = TONES[tone]
    r = rng(seed)
    uid = path.stem.replace(".", "-")
    k = min(w, h) / 900.0            # scale factor for strokes and type

    horizon = h * r(0.58, 0.70)
    lightx = w * r(0.18, 0.78)

    # Window / cabinet / opening rectangles along the wall.
    panels = []
    count = int(r(2, 5))
    gap = w / (count + 1)
    for i in range(count):
        pw = gap * r(0.30, 0.52)
        ph = horizon * r(0.34, 0.62)
        px = gap * (i + 1) - pw / 2 + gap * r(-0.12, 0.12)
        py = horizon - ph - horizon * r(0.06, 0.26)
        op = r(0.16, 0.42)
        panels.append(
            f'<rect x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}" '
            f'rx="{3 * k:.0f}" fill="url(#pane-{uid})" fill-opacity="{op:.2f}"/>'
            f'<rect x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}" '
            f'rx="{3 * k:.0f}" fill="none" stroke="{glow}" stroke-opacity="{op * 0.55:.2f}" '
            f'stroke-width="{1.6 * k:.1f}"/>')
    panels = "".join(panels)

    # A soft shaft of light falling across the floor.
    sx = lightx
    shaft = (f'<path d="M{sx - w * 0.08:.0f} {horizon:.0f} L{sx + w * 0.10:.0f} {horizon:.0f} '
             f'L{sx + w * 0.34:.0f} {h:.0f} L{sx - w * 0.30:.0f} {h:.0f} Z" '
             f'fill="url(#shaft-{uid})" fill-opacity="0.5"/>')

    text_block = ""
    if label:
        ty = h * 0.5
        text_block = f'''
  <text x="{w / 2:.0f}" y="{ty:.0f}" text-anchor="middle"
        font-family="Inter, Helvetica, Arial, sans-serif" font-size="{34 * k:.0f}"
        font-weight="650" fill="#FFFFFF" fill-opacity="0.90">{esc(label)}</text>
  <text x="{w / 2:.0f}" y="{ty + 42 * k:.0f}" text-anchor="middle"
        font-family="Inter, Helvetica, Arial, sans-serif" font-size="{20 * k:.0f}"
        font-weight="500" letter-spacing="{2 * k:.1f}"
        fill="#FFFFFF" fill-opacity="0.40">{esc(caption)}</text>'''

    tag_block = ""
    if tag:
        tw = 30 * k + len(tag) * 17 * k
        tag_block = f'''
  <g>
    <rect x="{32 * k:.0f}" y="{32 * k:.0f}" width="{tw:.0f}" height="{50 * k:.0f}"
          rx="{25 * k:.0f}" fill="{accent}" fill-opacity="0.95"/>
    <text x="{32 * k + tw / 2:.0f}" y="{32 * k + 33 * k:.0f}" text-anchor="middle"
          font-family="Inter, Helvetica, Arial, sans-serif" font-size="{21 * k:.0f}"
          font-weight="700" letter-spacing="{2.6 * k:.1f}" fill="#0B0E12">{esc(tag)}</text>
  </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"
     role="img" aria-label="{esc(label or seed)} — placeholder image">
  <defs>
    <linearGradient id="wall-{uid}" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>
    </linearGradient>
    <linearGradient id="floor-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{floor}" stop-opacity="0.92"/>
      <stop offset="1" stop-color="{floor}"/>
    </linearGradient>
    <linearGradient id="pane-{uid}" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0" stop-color="{glow}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{glow}" stop-opacity="0.12"/>
    </linearGradient>
    <linearGradient id="shaft-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{glow}" stop-opacity="0.34"/>
      <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="lamp-{uid}" cx="{lightx / w:.3f}" cy="{(horizon / h) * 0.55:.3f}" r="0.62">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.30"/>
      <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vig-{uid}" cx="0.5" cy="0.48" r="0.78">
      <stop offset="0.45" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.55"/>
    </radialGradient>
  </defs>

  <rect width="{w}" height="{h}" fill="url(#wall-{uid})"/>
  {panels}
  <rect y="{horizon:.0f}" width="{w}" height="{h - horizon:.0f}" fill="url(#floor-{uid})"/>
  <rect y="{horizon:.0f}" width="{w}" height="{1.6 * k:.1f}" fill="{glow}" fill-opacity="0.18"/>
  {shaft}
  <rect width="{w}" height="{h}" fill="url(#lamp-{uid})"/>
  <rect width="{w}" height="{h}" fill="url(#vig-{uid})"/>{text_block}{tag_block}
</svg>
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


PROJECTS = [
    ("hillside-kitchen", "Kitchen Gut & Rebuild"),
    ("cedar-deck", "Two-Level Cedar Deck"),
    ("basement-mold", "Basement Mold Remediation"),
    ("burst-pipe", "Burst Pipe Water Mitigation"),
    ("victorian-lead", "Lead Paint Abatement"),
    ("backyard-transform", "Backyard Regrade & Patio"),
    ("primary-bath", "Primary Bath Renovation"),
    ("front-yard", "Front Yard Curb Appeal"),
    ("siding-roof", "Siding & Roof Replacement"),
    ("crawlspace", "Crawlspace Encapsulation"),
    ("basement-finish", "Finished Basement"),
    ("screened-porch", "Screened Porch Addition"),
]

for slug, title in PROJECTS:
    scene(IMG / "projects" / f"{slug}-before.svg", 1600, 1067, "before", slug + "b", title, "BEFORE")
    scene(IMG / "projects" / f"{slug}-after.svg", 1600, 1067, "after", slug + "a", title, "AFTER")

# Service tiles — tall 4:5 crops, text sits over the bottom third.
TILES = [
    ("renovations", "Home Renovations"),
    ("water", "Water Mitigation"),
    ("remediation", "Mold Remediation"),
    ("lead", "Lead Paint Removal"),
    ("decks", "Decks & Porches"),
    ("landscaping", "Landscaping"),
    ("exteriors", "Siding & Roofing"),
    ("general", "General Contracting"),
]
for slug, title in TILES:
    scene(IMG / "site" / f"tile-{slug}.svg", 1200, 1500, "airy", "tile" + slug, title)

# Wide photographs that sit behind text — deliberately dark so a scrim works.
scene(IMG / "site" / "hero-bg.svg", 2400, 1500, "airy", "herobg", "Hero Photograph", caption="REPLACE WITH YOUR BEST PHOTO")
scene(IMG / "site" / "cta-bg.svg", 2400, 1000, "airy", "ctabg", "Wide Photograph")
scene(IMG / "site" / "band-process.svg", 2400, 1200, "airy", "bandproc", "Crew At Work")
scene(IMG / "site" / "band-quote.svg", 2400, 1200, "deep", "bandquote", "Finished Interior")
scene(IMG / "site" / "head-services.svg", 2400, 1100, "airy", "headsvc", "Services Header")
scene(IMG / "site" / "head-projects.svg", 2400, 1100, "airy", "headproj", "Gallery Header")
scene(IMG / "site" / "head-about.svg", 2400, 1100, "airy", "headabout", "About Header")
scene(IMG / "site" / "head-contact.svg", 2400, 1100, "airy", "headcontact", "Contact Header")

# Featured before/after on the homepage.
scene(IMG / "site" / "hero-before.svg", 1600, 1067, "before", "featb", "Featured Project", "BEFORE")
scene(IMG / "site" / "hero-after.svg", 1600, 1067, "after", "feata", "Featured Project", "AFTER")

# About page imagery.
scene(IMG / "site" / "about-team.svg", 1600, 1200, "light", "aboutteam", "Team Photograph")
scene(IMG / "site" / "about-jobsite.svg", 1200, 1500, "deep", "aboutjob", "Jobsite Photograph")
scene(IMG / "site" / "about-wide.svg", 2400, 1200, "airy", "aboutwide", "Wide Jobsite Photograph")

scene(IMG / "site" / "og-image.svg", 1200, 630, "deep", "og", "American Restoration Tech", caption="SOCIAL SHARE IMAGE")

files = sorted(IMG.rglob("*.svg"))
total = sum(f.stat().st_size for f in files)
print(f"Wrote {len(files)} placeholder images ({total // 1024} KB total)")
