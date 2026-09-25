#!/usr/bin/env python3
"""
Builds alternate visual themes as standalone previews.

The original site at the repo root is never touched. Each theme gets its own
directory with copies of the four pages and one stylesheet, sharing the same
images, JavaScript and fonts:

    theme-b/   Signwriter  — warm, hand-painted trade signage
    theme-c/   Field Notes — cool, drafting-table technical

Run after tools/stamp-build.py so the themes inherit the current asset version:

    python3 tools/stamp-build.py && python3 tools/make-themes.py
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "services.html", "projects.html", "contact.html"]

THEMES = {
    "theme-b": {
        "label": "B · Signwriter",
        "fonts": ["fraunces-variable.woff2", "karla-variable.woff2"],
        "logo": "logo-b", "favicon": "favicon-b", "chrome": "#14110D",
    },
    "theme-c": {
        "label": "C · Field Notes",
        "fonts": ["familjen-grotesk-variable.woff2", "dm-mono-400.woff2"],
        "logo": "logo-c", "favicon": "favicon-c", "chrome": "#0B1620",
    },
}
ORDER = [("", "A · Original"), ("theme-b", "B · Signwriter"), ("theme-c", "C · Field Notes"),
         ("theme-d", "D · Editorial")]


def switcher(current, page):
    links = []
    for slug, label in ORDER:
        href = (f"../{page}" if slug == "" else f"../{slug}/{page}")
        cls = ' class="is-current"' if slug == current else ""
        links.append(f'<a href="{href}"{cls}>{label}</a>')
    return ('<div class="theme-switch" role="navigation" aria-label="Theme preview">'
            '<span class="theme-switch__label">Preview theme</span>'
            + "".join(links) + "</div>\n")


SWITCH_CSS = """
/* Preview-only theme switcher. Delete this block and the .theme-switch markup
   once a direction is chosen. */
.theme-switch {
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.25rem 0.75rem;
  padding: 0.6rem clamp(1rem, 4vw, 2.5rem);
  background: #14110D; color: rgba(255,255,255,0.68);
  font-family: ui-monospace, "SFMono-Regular", Menlo, monospace;
  font-size: 0.75rem; letter-spacing: 0.04em;
}
.theme-switch__label { text-transform: uppercase; letter-spacing: 0.14em; opacity: 0.55; margin-right: 0.5rem; }
.theme-switch a { color: rgba(255,255,255,0.72); text-decoration: none; padding: 0.15rem 0.5rem; border: 1px solid transparent; }
.theme-switch a:hover { color: #fff; border-color: rgba(255,255,255,0.3); }
.theme-switch a.is-current { color: #14110D; background: #fff; border-color: #fff; }
"""


def build(slug, cfg):
    out = ROOT / slug
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()

    base = (ROOT / "assets" / "css" / "styles.css").read_text()
    # styles.css sits in assets/css/, theme.css sits one level below the root,
    # so its relative font URLs need re-pointing.
    base = base.replace('url("../fonts/', 'url("../assets/fonts/')
    override = (ROOT / "tools" / "themes" / f"{slug[-1]}.css").read_text()
    (out / "theme.css").write_text(base + "\n\n" + override + "\n" + SWITCH_CSS)

    preloads = "\n".join(
        f'<link rel="preload" href="../assets/fonts/{f}" as="font" type="font/woff2" crossorigin>'
        for f in cfg["fonts"])

    for page in PAGES:
        t = (ROOT / page).read_text()
        t = re.sub(r'(?<=["\'(])assets/', '../assets/', t)
        # The stylesheet href carries a ?v= cache-busting query, so match on the
        # path rather than the whole string.
        t, n = re.subn(r'<link rel="stylesheet" href="\.\./assets/css/styles\.css[^"]*">',
                       preloads + '\n<link rel="stylesheet" href="theme.css">', t)
        if n != 1:
            raise SystemExit(f"{slug}/{page}: expected 1 stylesheet link, replaced {n}")
        t = re.sub(r'<link rel="preload" href="\.\./assets/fonts/(?:inter|archivo)[^>]+>\n', '', t)
        t = t.replace('<meta name="theme-color" content="#0E1318">',
                      f'<meta name="theme-color" content="{cfg["chrome"]}">')
        t = t.replace("site/logo-mark-invert.svg", f"site/{cfg['logo']}-invert.svg")
        t = t.replace("site/logo-mark.svg", f"site/{cfg['logo']}.svg")
        t = t.replace("site/favicon.svg", f"site/{cfg['favicon']}.svg")
        t = t.replace("<body>\n", "<body>\n" + switcher(slug, page), 1)
        # canonical/og point at the real site; a preview must not claim them
        t = re.sub(r'<link rel="canonical"[^>]*>\n', '', t)
        t = t.replace("<title>", f"<title>[{cfg['label']}] ")
        (out / page).write_text(t)

    print(f"  {slug}/  {len(PAGES)} pages + theme.css")


for slug, cfg in THEMES.items():
    build(slug, cfg)
print("\nPreview locally:  python3 -m http.server 8000  ->  /theme-b/  and  /theme-c/")
