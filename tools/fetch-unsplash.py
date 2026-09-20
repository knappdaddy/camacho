#!/usr/bin/env python3
"""
Fills incoming/ with photographs from Unsplash.

This cannot run inside the Claude Code sandbox — its egress policy denies
unsplash.com. Run it on your own machine, then commit what it produces.

    export UNSPLASH_ACCESS_KEY=...        # free: https://unsplash.com/developers
    python3 tools/fetch-unsplash.py --candidates 3
    # look through incoming/_candidates/, copy the ones you like into incoming/
    python3 tools/import-photos.py --apply

Standard library only — no pip install.

Licensing: the Unsplash License permits commercial use without attribution, but
the API Guidelines require crediting the photographer and triggering the
download endpoint. This script does both and writes incoming/CREDITS.md.
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
INBOX = ROOT / "incoming"
API = "https://api.unsplash.com"
APP = "american_restoration_tech"

# slot -> (search query, orientation, target width)
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

# Stock cannot supply a matched before/after of the same room, and a mismatched
# pair makes the wipe slider look broken. These stay illustrated unless you pass
# --include-pairs, which fetches unmatched images purely as rough stand-ins.
PAIR_SLOTS = {
    "hillside-kitchen": ("dated old kitchen interior", "renovated modern kitchen island"),
    "basement-mold":    ("mold damp basement wall", "clean finished basement wall"),
    "cedar-deck":       ("old weathered rotten deck", "new cedar deck railing"),
    "backyard-transform": ("muddy bare backyard dirt", "paver patio backyard lawn"),
    "burst-pipe":       ("water damage ceiling stain", "clean white ceiling room"),
    "victorian-lead":   ("peeling paint window trim", "freshly painted window trim"),
    "siding-roof":      ("old worn house siding roof", "new house siding roof exterior"),
    "basement-finish":  ("unfinished basement joists", "finished basement living space"),
}


def api_get(path, key, **params):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Client-ID {key}",
        "Accept-Version": "v1",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search(query, orientation, key, n):
    data = api_get("/search/photos", key, query=query, orientation=orientation,
                   per_page=max(n, 5), content_filter="high")
    return data.get("results", [])[:n]


def grab(photo, dest, width, key):
    raw = photo["urls"]["raw"]
    url = raw + ("&" if "?" in raw else "?") + urllib.parse.urlencode(
        {"w": width, "q": "80", "fm": "jpg", "fit": "max"})
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    # Required by the Unsplash API Guidelines.
    try:
        api_get(urllib.parse.urlparse(photo["links"]["download_location"]).path, key,
                **dict(urllib.parse.parse_qsl(
                    urllib.parse.urlparse(photo["links"]["download_location"]).query)))
    except Exception:
        pass
    return (f'Photo by [{photo["user"]["name"]}]'
            f'({photo["user"]["links"]["html"]}?utm_source={APP}&utm_medium=referral) '
            f'on [Unsplash](https://unsplash.com/?utm_source={APP}&utm_medium=referral)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("UNSPLASH_ACCESS_KEY"))
    ap.add_argument("--candidates", type=int, default=1,
                    help="save N options per slot into incoming/_candidates/ instead of 1 pick")
    ap.add_argument("--include-pairs", action="store_true",
                    help="also fetch before/after slots (unmatched — see the note in this file)")
    ap.add_argument("--only", help="comma-separated slot names")
    args = ap.parse_args()

    if not args.key:
        sys.exit("No API key. Get a free one at https://unsplash.com/developers, then:\n"
                 "  export UNSPLASH_ACCESS_KEY=your_access_key")

    wanted = dict(SLOTS)
    if args.include_pairs:
        for slug, (qb, qa) in PAIR_SLOTS.items():
            wanted[f"{slug}-before"] = (qb, "landscape", 1600)
            wanted[f"{slug}-after"] = (qa, "landscape", 1600)
    if args.only:
        keep = {s.strip() for s in args.only.split(",")}
        wanted = {k: v for k, v in wanted.items() if k in keep}

    INBOX.mkdir(exist_ok=True)
    credits, failures = [], []
    multi = args.candidates > 1
    outdir = INBOX / "_candidates" if multi else INBOX

    for slot, (query, orientation, width) in wanted.items():
        try:
            hits = search(query, orientation, args.key, args.candidates)
        except Exception as e:
            failures.append((slot, f"search failed: {e}"))
            continue
        if not hits:
            failures.append((slot, "no results"))
            continue
        for i, photo in enumerate(hits, 1):
            name = f"{slot}-{i}.jpg" if multi else f"{slot}.jpg"
            try:
                credit = grab(photo, outdir / name, width, args.key)
                credits.append(f"- `{name}` — {credit}")
                print(f"  {name:34} {query}")
            except Exception as e:
                failures.append((slot, f"download failed: {e}"))

    (INBOX / "CREDITS.md").write_text(
        "# Photo credits\n\nImages from Unsplash. The Unsplash License allows "
        "commercial use without attribution, but crediting the photographer is "
        "required when images are obtained through the API, and is good practice "
        "regardless.\n\n" + "\n".join(credits) + "\n")

    print(f"\n{len(credits)} image(s) saved to {outdir.relative_to(ROOT)}/")
    if multi:
        print("Review them, copy the keepers into incoming/ as <slot>.jpg, then run:")
    else:
        print("Then run:")
    print("  python3 tools/import-photos.py --apply")
    if failures:
        print("\nProblems:")
        for slot, why in failures:
            print(f"  {slot}: {why}")
        print("\nMold, water damage and lead paint are thin on Unsplash — expect to")
        print("pick those by hand, or leave them illustrated.")


if __name__ == "__main__":
    main()
