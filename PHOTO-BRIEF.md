# Photo brief

Everything on the site is currently a drawn illustration. This is the list of
what to replace, and a prompt for each if you're generating images.

## Option A — pull from stock (fastest)

Pexels and Unsplash are both free for commercial use with no attribution
required. `tools/fetch-stock.py` queries both and saves several candidates per
slot so you can pick.

**It must run on your own machine** — the Claude Code sandbox denies both hosts
(403 on the proxy CONNECT), so this cannot be done from a session.

```bash
export PEXELS_API_KEY=...                 # free, 200/hr: https://www.pexels.com/api/
export UNSPLASH_ACCESS_KEY=...            # free, 50/hr:  https://unsplash.com/developers
python3 tools/fetch-stock.py
# review incoming/_candidates/ — filenames are suffixed -px / -us by source
# copy the keepers into incoming/ as <slot>.jpg
python3 tools/import-photos.py --apply
git add -A && git commit -m "Real photography" && git push
```

Either key alone works. Pexels is the better bet for this subject matter —
more practical, workmanlike imagery, and a rate limit that 36 slots won't blow
through. Unsplash is stronger on polished interiors. Hence: query both, choose.

**About the before/after pairs.** Stock can't give you the same room in two
conditions, so these are approximations — a dated kitchen next to a different
modern kitchen. The queries are phrased in parallel on each side to pull similar
framing, but they won't line up the way a real pair does. When choosing
candidates, pick the two whose distance and angle are closest to each other;
that matters more than either photo being the nicest on its own.

`--skip-pairs` leaves those sixteen slots illustrated if you'd rather.

Mold, water damage and lead paint are thin on both libraries. Expect to
hand-pick those, or keep the illustrations — the drawn versions of those three
are arguably better than what stock returns.

---

## Option B — generate them

**How to use it:** produce the images, name each file after its slot, drop them
in `incoming/`, then run:

```bash
python3 tools/import-photos.py           # shows what's there, what's missing
python3 tools/import-photos.py --apply   # imports and rewires the HTML
```

`.jpg`, `.jpeg`, `.png` and `.webp` all work. Anything you skip keeps its
illustration, so you can go a few at a time.

---

## Two rules that matter more than the prompts

**1. Before/after pairs must share a camera.** Generate the *after* first. Then
feed that image back into the model and ask it to edit that same room into the
before condition — don't write two prompts from scratch. Two independently
generated images will have different geometry and the wipe slider will look
broken. Same rule applies to real photography: mark the floor with tape on day
one and shoot the after from the same spot.

**2. Sizes are guidance, not requirements.** Every image is displayed with
`object-fit: cover`, so anything reasonably large and roughly the right shape
works. Aim for the listed dimensions or bigger, export around quality 80, and
keep files under ~400 KB so pages stay fast.

---

## Style line

Prepend this to every prompt so the set looks like one photographer shot it:

> Photorealistic architectural photography, natural daylight, wide-angle lens
> around 24mm, eye-level, neutral white balance, no people, no text or logos,
> realistic mid-market American suburban home, shot for a contractor's portfolio.

---

## The shot list


### Before/after pairs — 3:2, 1600×1067 or larger

| Slot | Subject |
|---|---|
| `hillside-kitchen-before` / `-after` | **Before:** dated 1990s oak cabinets, laminate counters, vinyl floor, old white fridge, dim. **After:** same room — white shaker uppers, deep navy base cabinets, quartz counters, large island with two pendant lights, tile backsplash, oak floors, bright. |
| `basement-mold-before` / `-after` | **Before:** finished basement wall with black and green mold spreading up from the floor, water staining, warped drywall, exposed studs where a section was cut out. **After:** same wall clean, new drywall, freshly painted white, dry concrete floor. |
| `cedar-deck-before` / `-after` | **Before:** rotted grey pressure-treated deck, warped and split boards, gaps, wobbly railing with missing balusters, weeds beneath. **After:** same footprint in new western red cedar, horizontal cable railing, pergola overhead, planter box. |
| `backyard-transform-before` / `-after` | **Before:** patchy muddy backyard, standing puddle against the foundation, erosion channel, bare soil, dated wood fence. **After:** same yard with a large paver patio, fresh sod, shrub border along the fence. |
| `burst-pipe-before` / `-after` | **Before:** large brown water stain with concentric rings on a sagging ceiling, standing water on hardwood, buckled boards. **After:** same room, clean flat ceiling, dry refinished floor. |
| `victorian-lead-before` / `-after` | **Before:** close-up of old clapboard siding and a double-hung window, paint badly peeling and alligatored, bare weathered wood showing, cracked glazing putty. **After:** same window, crisp fresh white paint, sound glazing. |
| `siding-roof-before` / `-after` | **Before:** two-storey house front, faded chalky siding, missing and curled shingles, sagging gutter, staining. **After:** same house with new fiber-cement siding, new architectural shingle roof, clean gutters, foundation planting. |
| `basement-finish-before` / `-after` | **Before:** unfinished basement — exposed floor joists, bare bulb, concrete floor and walls, stored boxes. **After:** same space finished — drywalled and painted, recessed lights, luxury vinyl plank floor, wet bar with dark cabinets. |

### Service tiles — portrait 4:5, 1200×1500

Remediation services show the **problem**; build services show the **result**.

| Slot | Subject |
|---|---|
| `tile-renovations` | Finished kitchen or bathroom, warm and bright |
| `tile-water` | Water-damaged ceiling or flooded floor, drying fans in place |
| `tile-remediation` | Mold on a basement wall, containment sheeting visible |
| `tile-lead` | Peeling paint on old window trim, close-up |
| `tile-decks` | Finished cedar deck with railing |
| `tile-landscaping` | Paver patio with planting and fresh lawn |
| `tile-exteriors` | New siding and roof on a suburban house |
| `tile-general` | Crew on a job site — framing, ladders, tools |

### Backgrounds — wide, text sits over these

| Slot | Size | Subject | Note |
|---|---|---|---|
| `hero-bg` | 2400×1500 | The single best finished space you have | Keep the **left third simple** — the headline sits there under a dark gradient |
| `cta-bg` | 2400×1000 | Warm finished interior | |
| `band-process` | 2400×1200 | Crew working on site | |
| `band-quote` | 2400×1200 | Finished interior | |
| `head-services` | 2400×1100 | Job site or crew | |
| `head-projects` | 2400×1100 | Finished exterior project | |
| `head-contact` | 2400×1100 | Finished interior | |
| `about-wide` | 2400×1200 | Job site, floor protection down | |
| `about-jobsite` | 1200×1500 | Job site, portrait | |
| `hero-before` / `hero-after` | 1600×1067 | The featured homepage comparison — use your most dramatic pair | |
| `og-image` | 1200×630 | Best finished space — this is the social share thumbnail | |

After swapping the backgrounds, re-check that headlines are still readable over
them. The scrims were tuned against the current images; if a headline gets hard
to read, pick a calmer frame or deepen that section's gradient in `styles.css`
(search `__media::after`).

---

## If you generate these with AI

Fine for a draft. Two things to be careful about:

- **Don't present generated images as his completed jobs.** A portfolio is a
  claim about work you actually did. Generated before/afters captioned
  "Bethesda, MD — six weeks" are fabricated credentials, and it's the same
  problem as the placeholder reviews currently on the site. Use them to hold the
  layout while the real photos get shot, not to fill the gallery permanently.
- **Six fingers, melted railings, impossible stair geometry.** Check every image
  at full size. Contractors' customers look closely at construction details.
