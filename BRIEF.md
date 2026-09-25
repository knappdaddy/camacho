# Site brief — American Restoration Tech

Every direction the owner has given, in one place. Any version of the site
(A, B, C, D, or whatever comes next) is checked against this list. If a new
instruction arrives, add it here first.

## The business

- **American Restoration Tech** — a general contractor.
- Services: home renovations, environmental remediation (mold, water
  mitigation), lead-based paint removal, deck building, landscaping, and other
  general contracting.
- **Works exclusively in New Jersey.** No other states anywhere on the site.
  Any example town is a New Jersey town.
- Licensing is a New Jersey Home Improvement Contractor registration
  (`NJ HIC #13VH…`), not a Maryland MHIC or Virginia number.

## What the site must do

1. **Show off the work.** Lots of before-and-after photography of real jobs.
2. **Before/after comparisons are the centrepiece.** A slider you drag between
   before and after of the same project, *and* a side-by-side option. Every
   comparison needs context — what the project was and where.
3. **List the services** — all of them, every competency above.
4. **Contact form**, plus the other things a best-in-class contractor site has:
   click-to-call on mobile, emergency response, credentials, reviews, process.
5. **It is a consumer website.** Customers will mostly see it on a phone.

## How it must feel

- **Photography-forward.** Photos behind text, large images everywhere.
- **Extremely modern and clean**, following best practice for contractor
  marketing sites.
- **Handmade, not AI-generated.** The first version's colours and fonts read as
  generic (Inter/Archivo, charcoal + orange, pills, soft shadows, glass
  badges). New directions should commit to a real craft reference instead.
- **A professional logo** — and each design direction gets its own logo.
- **Short.** Content was cut by half because the site took too long to get
  through. Keep it at roughly that length: same competencies, fewer words.

## Specific corrections already made (don't regress these)

- The featured before/after under the hero must **not touch the section above**
  and must **have a heading and description** saying what it is.
- Before/after pairs from stock photography may be **approximate** — two
  similar rooms is acceptable until real job photos exist.
- Placeholder content must be obviously placeholder: a draft notice in the
  footer, reviews marked "Placeholder Name", and a pre-launch checklist.

## How we work

- **Don't overwrite what exists.** New directions are built alongside as
  separate previews (`/theme-b/`, `/theme-c/`, `/theme-d/`), linked by a
  switcher bar.
- **Every change is previewable by refreshing** https://knappdaddy.github.io/camacho/
  — push to `main` after every change; the footer build stamp shows which
  version is loaded.
- Photos come from Pexels via the **Fetch photos** GitHub Actions workflow
  (the build sandbox cannot reach image sites). Real job photos replace them
  later via `tools/import-photos.py`.

## Quality bar (verified on every version)

- Text over photographs clears WCAG AAA contrast, measured on rendered pixels,
  on desktop and phone.
- No horizontal scrolling on phones down to 320px.
- Sliders drag, click, and work by keyboard; side-by-side toggle works.
- Form validates; says honestly that it is in demo mode until wired up.
- Homepage first view under ~1 MB on a phone.

## Lessons already paid for

- Asset URLs need a `?v=` cache-busting query, or refreshes show stale images.
- A hover animation on the slider must stop the moment the visitor touches it.
- The sticky header's hidden label must not escape the viewport.
- Long unbroken strings (email addresses) must wrap on phones.
