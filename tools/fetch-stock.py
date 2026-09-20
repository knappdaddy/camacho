#!/usr/bin/env python3
"""
Fills incoming/ with photographs from Pexels and/or Unsplash.

This cannot run inside the Claude Code sandbox — its egress policy denies both
(403 on the proxy CONNECT). Run it on your own machine, then commit the result.

    export PEXELS_API_KEY=...             # free: https://www.pexels.com/api/
    export UNSPLASH_ACCESS_KEY=...        # free: https://unsplash.com/developers
    python3 tools/fetch-stock.py
    # review incoming/_candidates/, copy keepers into incoming/ as <slot>.jpg
    python3 tools/import-photos.py --apply

Either key alone is enough; whichever are set get queried. Standard library
only — no pip install.

Which source is better here is an open question, which is why it queries both
and lets you choose. Pexels tends to carry more practical, workmanlike imagery
(job sites, damage, crews) and allows 200 requests/hour; Unsplash is stronger on
polished interiors but a demo key is capped at 50/hour, which 36 slots will
exceed. Filenames are suffixed -px / -us so you can see which came from where.

Licensing: both licences permit commercial use without attribution. Crediting
the photographer is required by the Unsplash API Guidelines and good practice
either way, so incoming/CREDITS.md is written for everything downloaded.
"""
import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
INBOX = ROOT / "incoming"
APP = "american_restoration_tech"

# slot -> (query, orientation, target width)
SLOTS = {
    "hero-bg":          ("renovated modern kitchen interior daylight", "landscape", 2400),
    "cta-bg":           ("warm modern living room interior", "landscape", 2400),
    "band-process":     ("carpenter framing house construction interior", "landscape", 2400),
    "band-quote":       ("bright renovated home interior", "landscape", 2400),
    "head-services":    ("construction tools contractor work site", "landscape", 2400),
    "head-projects":    ("wooden deck backyard house exterior", "landscape", 2400),
    "head-contact":     ("bright modern home interior living", "landscape", 2400),
    "about-wide":       ("home renovation construction site interior", "landscape", 2400),
    "about-jobsite":    ("carpenter working tools construction", "portrait", 1200),
    "og-image":         ("renovated kitchen interior", "landscape", 1200),

    "tile-renovations": ("renovated kitchen interior cabinets", "portrait", 1200),
    "tile-water":       ("water damage ceiling leak stain", "portrait", 1200),
    "tile-remediation": ("mold damp wall damage", "portrait", 1200),
    "tile-lead":        ("peeling paint old window frame", "portrait", 1200),
    "tile-decks":       ("wooden deck railing backyard", "portrait", 1200),
    "tile-landscaping": ("paver patio backyard landscaping garden", "portrait", 1200),
    "tile-exteriors":   ("house siding roof exterior suburban", "portrait", 1200),
    "tile-general":     ("construction worker tools site", "portrait", 1200),
}

# Stock cannot give you the same room in two conditions, so these are
# approximations. Each side is phrased in parallel ("wide interior", "close up",
# "exterior") to pull compositions that sit together tolerably when the slider
# wipes between them. Pick the two candidates whose framing is closest.
PAIR_SLOTS = {
    "hillside-kitchen": ("dated old kitchen oak cabinets wide interior",
                         "modern white kitchen island wide interior"),
    "basement-mold": ("mold damp basement wall close up",
                      "clean white painted basement wall close up"),
    "cedar-deck": ("old weathered wooden deck boards railing",
                   "new cedar wooden deck boards railing"),
    "backyard-transform": ("bare muddy backyard dirt lawn",
                           "landscaped backyard patio lawn"),
    "burst-pipe": ("water stained damaged ceiling room interior",
                   "clean white ceiling room interior"),
    "victorian-lead": ("peeling paint wooden window frame close up",
                       "freshly painted white window frame close up"),
    "siding-roof": ("old worn house exterior siding roof",
                    "new house exterior siding roof"),
    "basement-finish": ("unfinished basement concrete joists interior",
                        "finished basement room interior"),
}


def get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


class Pexels:
    tag, env = "px", "PEXELS_API_KEY"

    def __init__(self, key):
        self.h = {"Authorization": key}

    def search(self, query, orientation, n):
        url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
            {"query": query, "orientation": orientation, "per_page": max(n, 5)})
        out = []
        for p in get_json(url, self.h).get("photos", [])[:n]:
            out.append({
                "src": p["src"]["original"],
                "credit": (f'Photo by [{p["photographer"]}]({p["photographer_url"]}) '
                           f'on [Pexels]({p["url"]})'),
                "headers": {},
                "after": None,
            })
        return out


class Unsplash:
    tag, env = "us", "UNSPLASH_ACCESS_KEY"

    def __init__(self, key):
        self.key = key
        self.h = {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"}

    def search(self, query, orientation, n):
        url = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(
            {"query": query, "orientation": orientation,
             "per_page": max(n, 5), "content_filter": "high"})
        out = []
        for p in get_json(url, self.h).get("results", [])[:n]:
            u = p["user"]
            out.append({
                "src": p["urls"]["raw"],
                "credit": (f'Photo by [{u["name"]}]({u["links"]["html"]}'
                           f'?utm_source={APP}&utm_medium=referral) on '
                           f'[Unsplash](https://unsplash.com/?utm_source={APP}'
                           f'&utm_medium=referral)'),
                "headers": {},
                # Required by the Unsplash API Guidelines.
                "after": p["links"]["download_location"],
            })
        return out

    def ping(self, url):
        try:
            get_json(url, self.h)
        except Exception:
            pass


def download(hit, dest, width):
    src = hit["src"]
    url = src + ("&" if "?" in src else "?") + urllib.parse.urlencode(
        {"w": width, "q": "80", "fm": "jpg", "fit": "max"})
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=hit["headers"] or {})
    with urllib.request.urlopen(req, timeout=90) as r, open(dest, "wb") as f:
        f.write(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["pexels", "unsplash", "both"], default="both")
    ap.add_argument("--candidates", type=int, default=3,
                    help="options to save per slot per source (default 3)")
    ap.add_argument("--skip-pairs", action="store_true",
                    help="leave the before/after slots illustrated")
    ap.add_argument("--only", help="comma-separated slot names")
    args = ap.parse_args()

    providers = []
    for cls in (Pexels, Unsplash):
        if args.source in ("both", cls.__name__.lower()):
            key = os.environ.get(cls.env)
            if key:
                providers.append(cls(key))
            else:
                print(f"note: {cls.env} not set — skipping {cls.__name__}")
    if not providers:
        sys.exit("No API keys set.\n"
                 "  Pexels   (free, 200/hr): https://www.pexels.com/api/\n"
                 "  Unsplash (free, 50/hr):  https://unsplash.com/developers\n"
                 "Export PEXELS_API_KEY and/or UNSPLASH_ACCESS_KEY, then re-run.")

    wanted = dict(SLOTS)
    if not args.skip_pairs:
        for slug, (qb, qa) in PAIR_SLOTS.items():
            wanted[f"{slug}-before"] = (qb, "landscape", 1600)
            wanted[f"{slug}-after"] = (qa, "landscape", 1600)
    if args.only:
        keep = {s.strip() for s in args.only.split(",")}
        wanted = {k: v for k, v in wanted.items() if k in keep}

    outdir = INBOX / "_candidates"
    outdir.mkdir(parents=True, exist_ok=True)
    credits, failures, got = [], [], 0

    for slot, (query, orientation, width) in wanted.items():
        for prov in providers:
            try:
                hits = prov.search(query, orientation, args.candidates)
            except urllib.error.HTTPError as e:
                failures.append((slot, prov.tag, f"HTTP {e.code}"
                                 + (" — rate limit, try --source pexels" if e.code == 429 else "")))
                continue
            except Exception as e:
                failures.append((slot, prov.tag, str(e)))
                continue
            if not hits:
                failures.append((slot, prov.tag, "no results"))
                continue
            for i, hit in enumerate(hits, 1):
                name = f"{slot}-{prov.tag}{i}.jpg"
                try:
                    download(hit, outdir / name, width)
                    if hit["after"] and hasattr(prov, "ping"):
                        prov.ping(hit["after"])
                    credits.append(f"- `{name}` — {hit['credit']}")
                    got += 1
                    print(f"  {name:38} {query}")
                except Exception as e:
                    failures.append((slot, prov.tag, f"download failed: {e}"))
            time.sleep(0.3)

    (INBOX / "CREDITS.md").write_text(
        "# Photo credits\n\nBoth the Pexels and Unsplash licences permit commercial "
        "use without attribution. Crediting the photographer is required when images "
        "come through the Unsplash API, and is good practice either way.\n\n"
        "Trim this list to the images you actually kept.\n\n"
        + "\n".join(credits) + "\n")

    print(f"\n{got} image(s) in incoming/_candidates/")
    print("Copy the ones you want into incoming/ named <slot>.jpg, then:")
    print("  python3 tools/import-photos.py --apply")
    if not args.skip_pairs:
        print("\nFor the before/after pairs, choose the two whose framing is closest —")
        print("similar distance and angle. They will not match exactly; they only need")
        print("to sit together when the slider wipes.")
    if failures:
        print("\nProblems:")
        for slot, tag, why in failures:
            print(f"  {slot} ({tag}): {why}")
        print("\nMold, water damage and lead paint are thin on both libraries —")
        print("expect to hand-pick those, or leave them illustrated.")


if __name__ == "__main__":
    main()
