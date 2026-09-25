#!/usr/bin/env python3
"""
Builds theme D ("Editorial") into theme-d/.

A clean-room version of the site, written from BRIEF.md rather than from the
existing pages: its own markup, stylesheet (theme-d/d.css) and script
(theme-d/d.js). It shares only the photographs and font files in assets/.

    python3 tools/build-theme-d.py

Nothing outside theme-d/ is written.
"""
import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "theme-d"
NOW = datetime.datetime.now(datetime.timezone.utc)
V = NOW.strftime("%Y%m%d-%H%M")
STAMP = NOW.strftime("%Y-%m-%d %H:%M UTC")

PHONE, TEL = "(555) 014-2300", "+15550142300"
EMAIL = "hello@americanrestorationtech.com"
HIC = "NJ HIC #13VH00000000"


def ac(on):
    """aria-current attribute, kept out of f-string expressions (py3.11)."""
    return ' aria-current="page"' if on else ""


def img(path):
    return f"../assets/img/{path}?v={V}"


def esc(s):
    return html.escape(s, quote=True)


ICON_PHONE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 '
              '19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 '
              '2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2'
              'a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>')
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'

# ---------------------------------------------------------------- content --
SERVICES = [
    ("renovations", "Home renovations", "tile-renovations",
     "Kitchens, baths, basements and additions — designed, permitted and built by one crew.",
     ["Kitchen and bath remodeling", "Basement and attic conversions", "Additions and structural work"]),
    ("water", "Water damage", "tile-water",
     "Burst pipes, sewage backups and storm flooding, answered around the clock.",
     ["Emergency extraction and drying", "Moisture mapping and daily logs", "Insurance-ready documentation"]),
    ("remediation", "Mold remediation", "tile-remediation",
     "Removed to protocol — then we fix the moisture source so it stays gone.",
     ["Containment and HEPA filtration", "Third-party clearance testing", "Crawlspace encapsulation"]),
    ("lead", "Lead paint removal", "tile-lead",
     "EPA Lead-Safe certified abatement for homes built before 1978.",
     ["Testing and risk assessment", "Abatement and encapsulation", "Window and trim replacement"]),
    ("decks", "Decks and porches", "tile-decks",
     "Cedar, composite and hardwood — engineered, permitted and properly flashed.",
     ["Multi-level and wrap-around decks", "Screened porches and pergolas", "Repair and refinishing"]),
    ("landscaping", "Landscaping", "tile-landscaping",
     "Drainage solved first, then patios and planting on ground that will hold.",
     ["Regrading and drainage", "Paver patios and retaining walls", "Planting and full yard renovation"]),
    ("exteriors", "Siding and roofing", "tile-exteriors",
     "The building envelope that keeps every other system dry.",
     ["Roofing, gutters and soffit", "Fiber cement, vinyl and wood siding", "Windows and doors"]),
    ("general", "General contracting", "tile-general",
     "Drawings or an insurance scope in hand? We'll price it, permit it and run it.",
     ["Permitting and inspections", "Trade coordination", "Insurance claim coordination"]),
]

PROJECTS = [
    ("hillside-kitchen", "renovations", "Renovation", "Full kitchen gut and rebuild", "Montclair",
     "Load-bearing wall removed, plumbing and gas relocated, rebuilt with custom cabinetry in six weeks."),
    ("basement-mold", "remediation", "Mold remediation", "Basement mold remediation", "Maplewood",
     "900 sq ft under containment and full drywall replacement. Passed clearance on the first test."),
    ("cedar-deck", "decks", "Deck", "Two-level cedar deck", "Westfield",
     "Rotted deck removed and re-footed to frost depth; 620 sq ft of western red cedar."),
    ("backyard-transform", "landscaping", "Landscaping", "Backyard regrade and patio", "Chatham",
     "Negative grade corrected, French drain installed, finished with an 800 sq ft paver patio."),
    ("burst-pipe", "remediation", "Water damage", "Burst pipe mitigation", "Hoboken",
     "On site in 90 minutes, dried to standard in four days, two ceilings and a kitchen rebuilt."),
    ("victorian-lead", "remediation", "Lead abatement", "Lead paint abatement", "Summit",
     "Full-house assessment, original trim abated and 22 windows replaced. Cleared first pass."),
    ("siding-roof", "exteriors", "Exterior", "Siding and roof replacement", "Ridgewood",
     "Architectural shingle roof, fiber cement siding and new gutters as one coordinated scope."),
    ("basement-finish", "renovations", "Renovation", "Finished basement", "Morristown",
     "Unfinished basement turned into legal living space with egress window, full bath and wet bar."),
]

FAQ = [
    ("Do you charge for estimates?",
     "No. Walk-throughs and written estimates are free for residential projects in our service area."),
    ("How fast can you get here for a water emergency?",
     "Our line is answered 24/7 and we are typically on site within two hours. If water is actively "
     "coming in, call rather than using the form."),
    ("Do you work with insurance companies?",
     "Constantly. We document readings and photos from day one, write scopes the way adjusters expect, "
     "and meet your adjuster on site. We work for you, not the carrier."),
    ("Are you licensed, insured and warrantied?",
     "Registered in New Jersey, bonded, and carrying general liability and workers' compensation. "
     "Workmanship is warranted for two years, in writing."),
]

NAV = [("index.html", "Home"), ("services.html", "Services"),
       ("projects.html", "Before &amp; After"), ("contact.html", "Contact")]


# ------------------------------------------------------------------ chrome --
def switcher(page):
    items = [("", "A · Original"), ("theme-b", "B · Signwriter"),
             ("theme-c", "C · Field Notes"), ("theme-d", "D · Editorial")]
    links = "".join(
        f'<a href="{"../" + page if s == "" else "../" + s + "/" + page}"'
        f'{ac(s == "theme-d")}>{l}</a>' for s, l in items)
    return (f'<div class="switch" role="navigation" aria-label="Design preview">'
            f'<span>Preview</span>{links}</div>\n')


def head(page, title, desc, extra=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>[D · Editorial] {title}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{img("site/og-image.jpg")}">
<meta name="theme-color" content="#1F3A2E">
<link rel="icon" href="{img("site/favicon-d.svg")}" type="image/svg+xml">
<link rel="preload" href="../assets/fonts/newsreader-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fonts/schibsted-grotesk-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="d.css?v={V}">
{extra}</head>
<body>
{switcher(page)}<a class="skip" href="#main">Skip to content</a>
<p class="alert"><span class="alert__dot" aria-hidden="true"></span>Water or mold emergency? <a href="tel:{TEL}">Call {PHONE}</a> — answered 24/7</p>
<header class="hdr">
  <div class="wrap hdr__in">
    <a class="brand" href="index.html">
      <img src="{img("site/logo-d.svg")}" alt="" width="40" height="40">
      <span class="brand__txt"><span class="brand__name">American Restoration Tech</span><span class="brand__sub">General contractor · New Jersey</span></span>
    </a>
    <nav class="nav" aria-label="Primary">
      {"".join(f'<a href="{h}"{ac(h == page)}>{l}</a>' for h, l in NAV)}
    </nav>
    <a class="hdr__phone" href="tel:{TEL}">{PHONE}</a>
    <a class="btn btn--sm hdr__cta" href="contact.html">Free estimate</a>
    <a class="hdr__call" href="tel:{TEL}" aria-label="Call us at {PHONE}">{ICON_PHONE}</a>
    <button class="hdr__menu" type="button" aria-expanded="false" aria-controls="menu"><span></span><span></span><span class="sr">Menu</span></button>
  </div>
</header>
<div class="menu" id="menu" hidden>
  {"".join(f'<a href="{h}"{ac(h == page)}>{l}</a>' for h, l in NAV)}
  <a class="btn" href="contact.html">Get a free estimate</a>
  <a class="btn btn--line" href="tel:{TEL}">Call {PHONE}</a>
</div>
<main id="main">
'''


def foot():
    return f'''</main>
<div class="callbar">
  <a href="tel:{TEL}">{ICON_PHONE}Call now</a>
  <a href="contact.html">Free estimate</a>
</div>
<footer class="ftr">
  <div class="wrap">
    <div class="ftr__grid">
      <div>
        <a class="brand brand--inv" href="index.html">
          <img src="{img("site/logo-d-invert.svg")}" alt="" width="40" height="40">
          <span class="brand__txt"><span class="brand__name">American Restoration Tech</span><span class="brand__sub">General contractor · New Jersey</span></span>
        </a>
        <p>Renovation, restoration and remediation across northern and central New Jersey.</p>
      </div>
      <div>
        <h2 class="ftr__h">Services</h2>
        <ul>{"".join(f'<li><a href="services.html#{s[0]}">{s[1]}</a></li>' for s in SERVICES[:6])}</ul>
      </div>
      <div>
        <h2 class="ftr__h">Contact</h2>
        <ul>
          <li><a href="tel:{TEL}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>Mon–Fri 7am–6pm · Emergencies 24/7</li>
        </ul>
      </div>
    </div>
    <p class="draft"><b>Draft:</b> photographs, phone number, registration number, reviews and figures are placeholders — see <code>README.md</code> and <code>BRIEF.md</code>. Preview build <span data-build>{STAMP}</span>.</p>
    <div class="ftr__base">
      <p>© <span data-year>2026</span> American Restoration Tech</p>
      <p>{HIC} · EPA Lead-Safe Certified Firm</p>
    </div>
  </div>
</footer>
<script src="d.js?v={V}"></script>
</body>
</html>
'''


def page_head(img_name, label, h1, lede):
    return f'''<section class="phead">
  <img class="phead__img" src="{img("site/" + img_name + ".jpg")}" alt="" width="2000" height="1333" fetchpriority="high">
  <div class="wrap phead__in">
    <p class="label">{label}</p>
    <h1>{h1}</h1>
    <p class="phead__lede">{lede}</p>
  </div>
</section>
'''


def compare(slug, label, before_alt, after_alt, eager=False):
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return f'''<figure class="ba">
  <div class="ba__frame" data-ba data-label="{esc(label)}">
    <img data-before src="{img(slug + "-before.jpg")}" alt="Before: {esc(before_alt)}" width="1400" height="934"{load}>
    <img data-after src="{img(slug + "-after.jpg")}" alt="After: {esc(after_alt)}" width="1400" height="934"{load}>
  </div>
  <figcaption class="ba__bar"><span class="ba__hint">Drag the handle, or switch to side by side.</span></figcaption>
</figure>'''


def project_card(p, wide=False):
    slug, cat, catlabel, title, town, blurb = p
    return f'''<article class="work{" work--wide" if wide else ""}" data-category="{cat}">
  {compare("projects/" + slug, title, f"the {title.lower()} before work began", f"the finished {title.lower()}")}
  <p class="work__meta">{catlabel} · {town}, NJ</p>
  <h3>{title}</h3>
  <p>{blurb}</p>
</article>'''


def cta():
    return f'''<section class="cta">
  <img class="cta__img" src="{img("site/cta-bg.jpg")}" alt="" width="2000" height="1333" loading="lazy">
  <div class="wrap cta__in">
    <h2>Tell us what's going on with your house.</h2>
    <p>Send a few photos and we'll come back with a real number, usually within one business day.</p>
    <div class="row">
      <a class="btn" href="contact.html">Request an estimate</a>
      <a class="btn btn--line-inv" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>
'''


# ------------------------------------------------------------------- pages --
def home():
    schema = json.dumps({
        "@context": "https://schema.org", "@type": "GeneralContractor",
        "name": "American Restoration Tech", "telephone": "+1-555-014-2300", "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressLocality": "Montclair",
                    "addressRegion": "NJ", "postalCode": "07042", "addressCountry": "US"},
        "areaServed": [f"{c} County, NJ" for c in ("Essex", "Union", "Morris", "Bergen", "Somerset", "Hudson")],
    }, indent=1)
    tiles = "\n".join(f'''    <a class="svc" href="services.html#{sid}">
      <span class="svc__img"><img src="{img("site/" + im + ".jpg")}" alt="" width="900" height="1125" loading="lazy"></span>
      <span class="svc__n">{i:02d}</span>
      <span class="svc__t">{title}</span>
      <span class="svc__d">{blurb}</span>
    </a>''' for i, (sid, title, im, blurb, _) in enumerate(SERVICES, 1))
    work = "\n".join(project_card(p, wide=(i == 0)) for i, p in enumerate(PROJECTS[:3]))
    return head("index.html", "American Restoration Tech | New Jersey General Contractor",
                "Renovation, water and mold remediation, lead paint removal, decks and landscaping "
                "from one registered New Jersey contractor.",
                f'<script type="application/ld+json">\n{schema}\n</script>\n') + f'''
<section class="hero">
  <img class="hero__img" src="{img("site/hero-bg.jpg")}" alt="" width="2000" height="1333" fetchpriority="high">
  <div class="wrap hero__in">
    <p class="label label--inv">General contractor · Northern &amp; Central New Jersey</p>
    <h1>Put right. <em>Made better.</em></h1>
    <p class="hero__lede">Renovation, water and mold remediation, lead-safe paint removal, decks and landscaping — one registered New Jersey crew from the first call to the final walk-through.</p>
    <div class="row">
      <a class="btn" href="contact.html">Get a free estimate</a>
      <a class="btn btn--line-inv" href="tel:{TEL}">Call {PHONE}</a>
    </div>
    <ul class="hero__trust"><li>Registered NJ contractor</li><li>EPA Lead-Safe certified</li><li>24/7 emergency line</li></ul>
  </div>
  <p class="hero__cap">Kitchen renovation, Montclair</p>
</section>

<section class="sec" aria-labelledby="featured">
  <div class="wrap">
    <header class="shead">
      <p class="label">01 · Featured project</p>
      <div>
        <h2 id="featured">Living room restoration, Glen Ridge</h2>
        <p>Plaster repaired, original trim rebuilt and the floors refinished — four weeks from walk-through to punch list.</p>
      </div>
    </header>
    {compare("site/hero", "the Glen Ridge living room", "the living room at intake, with damaged plaster and worn floors", "the restored living room with repaired plaster, rebuilt trim and refinished floors", eager=True)}
  </div>
</section>

<section class="sec sec--tint" aria-labelledby="services">
  <div class="wrap">
    <header class="shead">
      <p class="label">02 · What we do</p>
      <div>
        <h2 id="services">Eight trades, one crew.</h2>
        <p>Most jobs touch more than one trade. We handle the damage and the rebuild under one contract, so one team answers for the whole job.</p>
      </div>
    </header>
    <div class="svcs">
{tiles}
    </div>
  </div>
</section>

<section class="urgent" aria-labelledby="urgent">
  <img class="urgent__img" src="{img("site/tile-water.jpg")}" alt="A burst pipe leaking water" width="900" height="1125" loading="lazy">
  <div class="urgent__body">
    <p class="label label--inv">03 · Emergency response</p>
    <h2 id="urgent">Water in the house? Call now.</h2>
    <p>A person answers day or night, and a crew is usually on site within two hours with extraction and drying equipment.</p>
    <a class="btn" href="tel:{TEL}">{ICON_PHONE}Call {PHONE}</a>
  </div>
</section>

<section class="sec" aria-labelledby="work">
  <div class="wrap">
    <header class="shead">
      <p class="label">04 · Before &amp; after</p>
      <div>
        <h2 id="work">Selected work</h2>
        <p>Same rooms, before and after. Drag across, or switch every project to side by side.</p>
      </div>
      <div class="viewall" role="group" aria-label="Show comparisons as">
        <button type="button" data-view-all="slide" aria-pressed="true">Slider</button>
        <button type="button" data-view-all="split" aria-pressed="false">Side by side</button>
      </div>
    </header>
    <div class="works">
{work}
    </div>
    <p class="more"><a class="link" href="projects.html">See all eight projects {ARROW}</a></p>
  </div>
</section>

<figure class="plate">
  <img src="{img("site/about-wide.jpg")}" alt="A room mid-demolition, down to brick and subfloor" width="2000" height="1333" loading="lazy">
  <figcaption>Mid-demolition, Morristown. The part of the job nobody photographs — and the part that decides how it turns out.</figcaption>
</figure>

<section class="sec" aria-labelledby="how">
  <div class="wrap split">
    <img class="split__img" src="{img("site/band-process.jpg")}" alt="A carpenter working on roof framing" width="2000" height="1333" loading="lazy">
    <div>
      <p class="label">05 · How we work</p>
      <h2 id="how">No surprise invoices. No disappearing crews.</h2>
      <ol class="steps">
        <li><b>Free walk-through.</b> We measure, photograph and listen. No pressure to decide on the spot.</li>
        <li><b>A written, line-item scope.</b> Materials, allowances and a schedule, before anything starts.</li>
        <li><b>One named project lead.</b> Clean sites and photo updates every week.</li>
        <li><b>A two-year warranty.</b> We close the punch list together and put it in writing.</li>
      </ol>
    </div>
  </div>
</section>

<section class="sec sec--green" aria-labelledby="proof">
  <div class="wrap">
    <header class="shead">
      <p class="label label--inv">06 · Eighteen years in New Jersey</p>
      <div>
        <h2 id="proof">Registered, insured, and still answering the phone.</h2>
        <p>Essex, Union, Morris, Bergen, Somerset and Hudson counties.</p>
      </div>
    </header>
    <dl class="figs">
      <div><dt>Years in business</dt><dd>18+</dd></div>
      <div><dt>Projects completed</dt><dd>1,400+</dd></div>
      <div><dt>Average rating</dt><dd>4.9</dd></div>
      <div><dt>Emergency response</dt><dd>2 hr</dd></div>
    </dl>
    <div class="quotes">
      <figure class="quote">
        <blockquote>Our basement flooded at eleven on a Sunday night. They had fans running before midnight and the whole thing rebuilt in three weeks.</blockquote>
        <figcaption>Placeholder Name — water damage, Maplewood</figcaption>
      </figure>
      <figure class="quote">
        <blockquote>A 1918 house and two small kids, so the lead paint was non-negotiable. They tested, contained, abated and re-tested — and left it cleaner than they found it.</blockquote>
        <figcaption>Placeholder Name — lead abatement, Summit</figcaption>
      </figure>
    </div>
  </div>
</section>
''' + cta() + foot()


def services():
    rows = "\n".join(f'''  <article class="srow" id="{sid}">
    <img class="srow__img" src="{img("site/" + im + ".jpg")}" alt="" width="900" height="1125" loading="lazy">
    <div class="srow__body">
      <p class="srow__n">{i:02d}</p>
      <h2>{title}</h2>
      <p>{blurb}</p>
      <ul>{"".join(f"<li>{b}</li>" for b in bullets)}</ul>
      <a class="link" href="contact.html?service={sid}">Estimate for {title.lower()} {ARROW}</a>
    </div>
  </article>''' for i, (sid, title, im, blurb, bullets) in enumerate(SERVICES, 1))
    return head("services.html", "Services | American Restoration Tech",
                "Renovation, water damage, mold remediation, lead paint removal, decks, landscaping, "
                "siding and roofing from one registered New Jersey contractor.") + page_head(
        "head-services", "Services",
        "Everything from an emergency dry-out to a whole-home renovation.",
        "Remediation and reconstruction under one registered New Jersey contractor — one team stops "
        "the damage, cleans it up properly and rebuilds it.") + f'''
<section class="sec">
  <div class="wrap srows">
{rows}
  </div>
</section>
''' + cta() + foot()


def projects():
    cards = "\n".join(project_card(p, wide=(i == 0)) for i, p in enumerate(PROJECTS))
    filters = [("all", "All work"), ("renovations", "Renovation"), ("remediation", "Remediation"),
               ("decks", "Decks"), ("landscaping", "Landscaping"), ("exteriors", "Exteriors")]
    return head("projects.html", "Before &amp; After | American Restoration Tech",
                "Before-and-after comparisons of renovation, remediation, deck, landscaping and "
                "exterior projects across New Jersey.") + page_head(
        "head-projects", "Before &amp; after",
        "Drag the handle. See the difference.",
        "Every project is a before-and-after pair. Filter by trade, drag across any photo, or "
        "switch the whole page to side by side.") + f'''
<section class="sec">
  <div class="wrap">
    <div class="tools">
      <div class="filters" data-filters role="group" aria-label="Filter by trade">
        {"".join(f'<button type="button" data-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in filters)}
      </div>
      <div class="viewall" role="group" aria-label="Show comparisons as">
        <button type="button" data-view-all="slide" aria-pressed="true">Slider</button>
        <button type="button" data-view-all="split" aria-pressed="false">Side by side</button>
      </div>
    </div>
    <p class="count" aria-live="polite"><span data-count>{len(PROJECTS)} projects</span></p>
    <div class="works">
{cards}
    </div>
  </div>
</section>
''' + cta() + foot()


def contact():
    faq_json = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]})
    options = "".join(f'<option value="{s[0]}">{s[1]}</option>' for s in SERVICES)
    faqs = "\n".join(f'''      <details><summary>{q}</summary><p>{a}</p></details>''' for q, a in FAQ)
    return head("contact.html", "Contact | American Restoration Tech",
                "Request a free estimate, or call the 24/7 emergency line for water and mold damage "
                "anywhere in northern and central New Jersey.",
                f'<script type="application/ld+json">{faq_json}</script>\n') + page_head(
        "head-contact", "Contact",
        "Tell us what's going on.",
        "We reply within one business day. If water is coming into the house, call — it's faster.") + f'''
<section class="sec">
  <div class="wrap contact">
    <form class="form" data-form data-endpoint="REPLACE_WITH_YOUR_FORM_ENDPOINT" novalidate>
      <h2>Request a free estimate</h2>
      <p class="form__intro">Five questions. We'll come back with next steps.</p>
      <div class="form__two">
        <label class="f"><span>Full name</span><input name="name" autocomplete="name" required><em class="f__err"></em></label>
        <label class="f"><span>Phone</span><input name="phone" type="tel" autocomplete="tel" required><em class="f__err"></em></label>
      </div>
      <label class="f"><span>Email</span><input name="email" type="email" autocomplete="email" required><em class="f__err"></em></label>
      <label class="f"><span>What do you need?</span><select name="service" required><option value="">Choose a service…</option>{options}</select><em class="f__err"></em></label>
      <label class="f"><span>Tell us about the project</span><textarea name="message" rows="5" required></textarea><em class="f__err"></em></label>
      <p class="f__hint">Photos help. Email them to {EMAIL} and we can often quote without a visit.</p>
      <button class="btn" type="submit">Send request</button>
      <p class="form__status" role="status" hidden></p>
    </form>
    <aside class="reach">
      <dl>
        <div><dt>Phone — 24/7 emergencies</dt><dd><a href="tel:{TEL}">{PHONE}</a></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
        <div><dt>Hours</dt><dd>Mon–Fri 7am–6pm, Sat 8am–2pm</dd></div>
        <div><dt>Where we work</dt><dd>Essex, Union, Morris, Bergen, Somerset and Hudson counties</dd></div>
      </dl>
      <img src="{img("site/about-jobsite.jpg")}" alt="Tools on a job site workbench" width="1000" height="1250" loading="lazy">
    </aside>
  </div>
</section>

<section class="sec sec--tint" aria-labelledby="faq">
  <div class="wrap narrow">
    <p class="label">Questions</p>
    <h2 id="faq">Asked every week.</h2>
    <div class="faq">
{faqs}
    </div>
  </div>
</section>
''' + foot()


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in [("index.html", home), ("services.html", services),
                     ("projects.html", projects), ("contact.html", contact)]:
        (OUT / name).write_text(fn())
    print(f"theme-d/ built — 4 pages, version {V}")
