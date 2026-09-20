#!/usr/bin/env python3
"""
Generates every placeholder image on the site as a drawn vector scene.

These are illustrations, not photographs, but they depict the actual subject —
a moldy basement wall, a rotted deck, a stained ceiling, a dated kitchen — so
the site can be judged with something close to real content in place.

Each before/after pair is drawn from the SAME camera with the SAME geometry and
differs only in condition and light. That is what makes a wipe slider read
correctly; mismatched pairs are the usual reason these sliders look wrong.

Usage:  python3 tools/make-placeholders.py
"""
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"


# --------------------------------------------------------------- utilities --
def rng(seed_text):
    state = 2166136261
    for ch in str(seed_text):
        state = ((state ^ ord(ch)) * 16777619) & 0xFFFFFFFF

    def nxt(lo=0.0, hi=1.0):
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return lo + (state / 0x7FFFFFFF) * (hi - lo)
    return nxt


def _rgb(c):
    """Accepts #rgb or #rrggbb."""
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(c1, c2, t):
    """Blend two colours."""
    a, b = _rgb(c1), _rgb(c2)
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


def rect(x, y, w, h, fill, o=1.0, rx=0):
    op = f' fill-opacity="{o:.3f}"' if o < 1 else ""
    r = f' rx="{rx:.1f}"' if rx else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{max(h,0):.1f}" fill="{fill}"{op}{r}/>'


def poly(points, fill, o=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    op = f' fill-opacity="{o:.3f}"' if o < 1 else ""
    return f'<polygon points="{pts}" fill="{fill}"{op}/>'


def line(x1, y1, x2, y2, stroke, wdt=1.0, o=1.0, cap="butt"):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{wdt:.2f}" stroke-opacity="{o:.3f}" stroke-linecap="{cap}"/>')


def blob(cx, cy, rx, ry, seed, fill, o=1.0, wobble=0.42, n=11):
    """An irregular organic shape — mold colonies, water stains, puddles."""
    r = rng(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + r(-wobble, wobble)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        d += f" Q{p[0]:.1f},{p[1]:.1f} {mx:.1f},{my:.1f}"
    return f'<path d="{d} Z" fill="{fill}" fill-opacity="{o:.3f}"/>'


def grain_defs(uid, amount=0.55):
    return f'''<filter id="gr{uid}" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7" result="n"/>
      <feColorMatrix in="n" type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="linear" slope="{amount}"/></feComponentTransfer>
    </filter>'''


def vignette_defs(uid, strength=0.42):
    return f'''<radialGradient id="vg{uid}" cx="0.5" cy="0.48" r="0.76">
      <stop offset="0.42" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="{strength}"/>
    </radialGradient>'''


def lingrad(uid, name, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<linearGradient id="{name}{uid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def wrap(path, w, h, label, defs, body, uid, vig=0.42, grain=0.5):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"
     role="img" aria-label="{label} — illustrated placeholder">
  <defs>
{defs}
{grain_defs(uid, grain)}
{vignette_defs(uid, vig)}
  </defs>
{body}
  <rect width="{w}" height="{h}" filter="url(#gr{uid})" opacity="0.5" style="mix-blend-mode:overlay"/>
  <rect width="{w}" height="{h}" fill="url(#vg{uid})"/>
</svg>
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


# ------------------------------------------------------------------ palette --
def pal(state):
    """Condition-driven palette. 'before' is cool, dim and grimy."""
    if state == "before":
        return dict(wall="#8E9095", wall2="#6E7176", floor="#5E6166", floor2="#45484D",
                    light="#C9CBCE", warm="#9AA0A6", trim="#B7B9BC", dark="#2B2E33",
                    accent="#7E848B", sky="#9AA6B4", grime="#3A3C36")
    return dict(wall="#E9E3D9", wall2="#CFC7BA", floor="#B0885C", floor2="#8A6944",
                light="#FFF3DF", warm="#F0C089", trim="#FFFFFF", dark="#3A3027",
                accent="#E2743B", sky="#BCD3E4", grime="#8A6944")


# ---------------------------------------------------------------- interiors --
def interior_shell(w, h, hz, p, uid, warm_light=True):
    """Back wall, floor, baseboard and a pool of light. Shared by all rooms."""
    d = [
        lingrad(uid, "wall", [(0, p["wall"], 1), (1, p["wall2"], 1)]),
        lingrad(uid, "flr", [(0, p["floor"], 1), (1, p["floor2"], 1)]),
    ]
    b = [
        rect(0, 0, w, hz, f"url(#wall{uid})"),
        rect(0, hz, w, h - hz, f"url(#flr{uid})"),
        rect(0, hz - h * 0.022, w, h * 0.022, p["trim"], 0.85),
        # side shading gives the flat elevation some depth
        poly([(0, 0), (w * 0.14, 0), (w * 0.1, h), (0, h)], "#000", 0.13),
        poly([(w, 0), (w * 0.86, 0), (w * 0.9, h), (w, h)], "#000", 0.08),
    ]
    if warm_light:
        b.append(poly([(w * 0.28, hz), (w * 0.72, hz), (w * 0.9, h), (w * 0.1, h)],
                      p["light"], 0.13))
    return d, b


def window(x, y, ww, wh, p, uid, bright=True, cracked=False):
    glow = p["light"] if bright else "#9FB0BE"
    out = [
        rect(x - ww * 0.05, y - wh * 0.04, ww * 1.1, wh * 1.08, p["trim"], 0.95, rx=2),
        rect(x, y, ww, wh, glow, 0.92),
        rect(x, y, ww, wh * 0.5, "#FFFFFF", 0.18),
        line(x + ww / 2, y, x + ww / 2, y + wh, p["trim"], ww * 0.05, 0.9),
        line(x, y + wh / 2, x + ww, y + wh / 2, p["trim"], wh * 0.045, 0.9),
    ]
    if cracked:
        out.append(line(x + ww * 0.2, y + wh * 0.15, x + ww * 0.62, y + wh * 0.8, "#6E7176", 2, 0.7))
    return out


def scene_kitchen(w, h, state, seed):
    p, r, uid = pal(state), rng(seed), "k" + str(abs(hash(seed)) % 9999)
    hz = h * 0.70
    d, b = interior_shell(w, h, hz, p, uid, warm_light=(state == "after"))

    cab = "#B08A56" if state == "before" else "#2F3A42"
    upper = "#B08A56" if state == "before" else "#F4F1EB"
    counter = "#8E8B82" if state == "before" else "#E9E5DE"
    pull = "#6B5738" if state == "before" else "#C9A227"

    x0, x1 = w * 0.05, w * 0.58
    up_y, up_h = h * 0.15, h * 0.21
    # upper cabinets, with door panels and handles
    b.append(rect(x0, up_y, x1 - x0, up_h, upper))
    for i in range(5):
        cx = x0 + (x1 - x0) * i / 5
        cw = (x1 - x0) / 5
        b.append(rect(cx + cw * 0.08, up_y + up_h * 0.10, cw * 0.84, up_h * 0.80,
                      mix(upper, "#000", 0.07)))
        b.append(rect(cx + cw * 0.12, up_y + up_h * 0.14, cw * 0.76, up_h * 0.72,
                      mix(upper, "#fff", 0.10)))
        b.append(rect(cx + cw * 0.72, up_y + up_h * 0.62, cw * 0.16, up_h * 0.035, pull, 0.9, rx=2))
        b.append(line(cx, up_y, cx, up_y + up_h, "#000", 1.2, 0.16))
    b.append(rect(x0, up_y + up_h, x1 - x0, h * 0.010, "#000", 0.20))

    # range hood over the middle
    hx = x0 + (x1 - x0) * 0.42
    b.append(poly([(hx, up_y + up_h), (hx + w * 0.13, up_y + up_h),
                   (hx + w * 0.11, up_y + up_h + h * 0.05), (hx + w * 0.02, up_y + up_h + h * 0.05)],
                  "#B9BCC0" if state == "after" else "#9C9A94"))

    # backsplash
    bs_y, bs_h = up_y + up_h + h * 0.012, h * 0.13
    b.append(rect(x0, bs_y, x1 - x0, bs_h, mix(upper, "#ffffff", 0.42 if state == "after" else 0.12)))
    if state == "after":
        for i in range(13):
            b.append(line(x0 + (x1 - x0) * i / 13, bs_y, x0 + (x1 - x0) * i / 13, bs_y + bs_h, "#000", 1, 0.08))
        for j in range(1, 3):
            b.append(line(x0, bs_y + bs_h * j / 3, x1, bs_y + bs_h * j / 3, "#000", 1, 0.08))

    # counter + base run
    ct_y = bs_y + bs_h
    b.append(rect(x0 - w * 0.006, ct_y, (x1 - x0) + w * 0.012, h * 0.030, counter))
    b.append(rect(x0 - w * 0.006, ct_y + h * 0.030, (x1 - x0) + w * 0.012, h * 0.006, "#000", 0.18))
    base_y = ct_y + h * 0.036
    b.append(rect(x0, base_y, x1 - x0, hz - base_y, cab))
    for i in range(5):
        cx = x0 + (x1 - x0) * i / 5
        cw = (x1 - x0) / 5
        b.append(rect(cx + cw * 0.08, base_y + h * 0.012, cw * 0.84, (hz - base_y) * 0.80,
                      mix(cab, "#fff", 0.06)))
        b.append(rect(cx + cw * 0.30, base_y + h * 0.028, cw * 0.40, h * 0.010, pull, 0.9, rx=2))
    b.append(rect(x0, hz - h * 0.022, x1 - x0, h * 0.022, "#000", 0.28))   # toe kick

    # sink under the window
    b.append(rect(x0 + (x1 - x0) * 0.62, ct_y + h * 0.004, (x1 - x0) * 0.24, h * 0.022,
                  mix(counter, "#000", 0.28), rx=3))

    b += window(w * 0.66, h * 0.19, w * 0.22, h * 0.27, p, uid, bright=(state == "after"))

    if state == "after":
        ix, iw = w * 0.26, w * 0.44
        iy = hz + (h - hz) * 0.18
        b.append(rect(ix - iw * 0.04, iy, iw * 1.08, h * 0.030, counter))
        b.append(rect(ix - iw * 0.04, iy + h * 0.030, iw * 1.08, h * 0.006, "#000", 0.20))
        b.append(rect(ix, iy + h * 0.036, iw, h * 0.185, cab))
        b.append(rect(ix, iy + h * 0.036, iw, h * 0.185, "#000", 0.08))
        for k in (0.22, 0.5, 0.78):
            b.append(rect(ix + iw * k - iw * 0.06, iy + h * 0.075, iw * 0.12, h * 0.008, pull, 0.85, rx=2))
        b.append(rect(ix, iy + h * 0.215, iw, h * 0.012, "#000", 0.30))
        for k in (0.30, 0.70):
            px = ix + iw * k
            b.append(line(px, h * 0.06, px, h * 0.285, p["dark"], 2.2, 0.55))
            b.append(poly([(px - w * 0.024, h * 0.330), (px + w * 0.024, h * 0.330),
                           (px + w * 0.010, h * 0.285), (px - w * 0.010, h * 0.285)], p["accent"]))
            b.append(f'<ellipse cx="{px:.1f}" cy="{h*0.332:.1f}" rx="{w*0.024:.1f}" ry="{h*0.009:.1f}" fill="{p["light"]}"/>')
            b.append(f'<ellipse cx="{px:.1f}" cy="{h*0.36:.1f}" rx="{w*0.05:.1f}" ry="{h*0.03:.1f}" fill="{p["light"]}" fill-opacity="0.18"/>')
        for i in range(9):
            b.append(line(0, hz + (h - hz) * (i + 1) / 9, w, hz + (h - hz) * (i + 1) / 9, "#000", 1.2, 0.09))
    else:
        # dated fridge, worn lino, grime
        fx = w * 0.62
        b.append(rect(fx, hz - h * 0.30, w * 0.15, h * 0.30, "#AEB0AB"))
        b.append(rect(fx, hz - h * 0.30, w * 0.15, h * 0.010, "#8D8F8A"))
        b.append(line(fx + w * 0.012, hz - h * 0.22, fx + w * 0.012, hz - h * 0.06, "#8D8F8A", 4, 0.9))
        b.append(line(fx, hz - h * 0.11, fx + w * 0.15, hz - h * 0.11, "#8D8F8A", 2, 0.7))
        for i in range(6):
            b.append(line(0, hz + (h - hz) * (i + 1) / 6, w, hz + (h - hz) * (i + 1) / 6, "#000", 1, 0.07))
        for i in range(7):
            b.append(blob(r(w * 0.05, w * 0.95), r(hz + h * 0.02, h * 0.96),
                          w * r(0.02, 0.05), h * r(0.01, 0.025), f"{seed}st{i}", p["grime"], 0.18))
        b.append(blob(w * 0.10, h * 0.20, w * 0.07, h * 0.06, seed + "wall", "#6E6F68", 0.25))
        b.append(blob(w * 0.90, h * 0.62, w * 0.05, h * 0.05, seed + "wall2", "#6E6F68", 0.20))
    return d, b, uid


def scene_basement(w, h, state, seed, finished=False):
    """Basement wall — mold and damp when 'before', clean/finished when 'after'."""
    p, r, uid = pal(state), rng(seed), "b" + str(abs(hash(seed)) % 9999)
    hz = h * 0.78
    d = [lingrad(uid, "wall", [(0, mix(p["wall"], "#ffffff", 0.05), 1), (1, p["wall2"], 1)]),
         lingrad(uid, "flr", [(0, "#8B8E91" if state == "before" else p["floor"], 1),
                              (1, "#6C6F72" if state == "before" else p["floor2"], 1)])]
    b = [rect(0, 0, w, hz, f"url(#wall{uid})"), rect(0, hz, w, h - hz, f"url(#flr{uid})")]

    # drywall seams
    for i in range(1, 4):
        b.append(line(w * i / 4, 0, w * i / 4, hz, "#000", 1.6, 0.07))

    if state == "before":
        # rising damp band + efflorescence
        b.append(rect(0, hz - h * 0.26, w, h * 0.26, "#5F6A63", 0.30))
        b.append(rect(0, hz - h * 0.27, w, h * 0.012, "#4A5750", 0.45))
        # mold colonies, densest in the corner and along the floor
        for i in range(34):
            cx = r(0, w) ** 1.0
            bias = r(0, 1) ** 2
            cy = hz - bias * h * 0.34
            rx = w * r(0.012, 0.055)
            col = ["#2F3A2C", "#3D4A33", "#25301F", "#4A5138"][int(r(0, 3.99))]
            b.append(blob(cx, cy, rx, rx * r(0.5, 0.95), f"{seed}m{i}", col, r(0.30, 0.72)))
        for i in range(14):
            b.append(blob(r(0, w * 0.45), r(h * 0.10, hz * 0.8), w * r(0.02, 0.06),
                          h * r(0.02, 0.05), f"{seed}mc{i}", "#333D2B", r(0.18, 0.45)))
        # water streaks
        for i in range(7):
            x = r(0, w)
            b.append(line(x, r(0, h * 0.25), x + r(-8, 8), hz, "#4C5A52", r(2, 7), 0.20))
        # exposed stud bay
        b.append(rect(w * 0.70, h * 0.18, w * 0.22, hz - h * 0.18, "#6E7176", 0.55))
        for i in range(3):
            b.append(rect(w * 0.70 + w * 0.22 * i / 3, h * 0.18, w * 0.018, hz - h * 0.18, "#8A8377", 0.8))
        b.append(rect(0, hz, w, h - hz, "#000", 0.10))
    else:
        b.append(rect(0, 0, w, hz, "#FFFFFF", 0.30))
        b.append(rect(0, hz - h * 0.03, w, h * 0.03, p["trim"], 0.95))
        if finished:
            for i in range(8):
                b.append(line(0, hz + (h - hz) * (i + 1) / 8, w, hz + (h - hz) * (i + 1) / 8, "#000", 1.2, 0.10))
            b += window(w * 0.72, h * 0.18, w * 0.18, h * 0.22, p, uid)
            # wet bar
            b.append(rect(w * 0.08, hz - h * 0.30, w * 0.34, h * 0.03, "#E7E3DC"))
            b.append(rect(w * 0.08, hz - h * 0.27, w * 0.34, h * 0.27, "#2F3A42"))
            for i in range(3):
                b.append(line(w * 0.08 + w * 0.34 * (i + 1) / 4, hz - h * 0.27,
                              w * 0.08 + w * 0.34 * (i + 1) / 4, hz, "#000", 1.4, 0.2))
        else:
            b.append(poly([(w * 0.25, hz), (w * 0.75, hz), (w * 0.92, h), (w * 0.08, h)], p["light"], 0.14))
            b += window(w * 0.72, h * 0.16, w * 0.20, h * 0.20, p, uid)
            for i in range(7):
                b.append(line(0, hz + (h - hz) * (i + 1) / 7, w, hz + (h - hz) * (i + 1) / 7, "#000", 1.2, 0.10))
            b.append(rect(w * 0.14, hz - h * 0.09, w * 0.025, h * 0.045, "#E7E3DC", 0.9, rx=2))
            b.append(rect(w * 0.08, h * 0.12, w * 0.30, h * 0.34, "#000", 0.05))
        for k in (0.3, 0.7):
            b.append(f'<ellipse cx="{w*k:.1f}" cy="{h*0.06:.1f}" rx="{w*0.035:.1f}" ry="{h*0.014:.1f}" fill="{p["light"]}" fill-opacity="0.85"/>')
    return d, b, uid


def scene_framing(w, h, state, seed):
    """Unfinished basement / framing — 'before' open joists, 'after' finished room."""
    if state == "after":
        return scene_basement(w, h, "after", seed, finished=True)
    p, r, uid = pal("before"), rng(seed), "f" + str(abs(hash(seed)) % 9999)
    hz = h * 0.80
    d = [lingrad(uid, "wall", [(0, "#6A6C70", 1), (1, "#4E5155", 1)])]
    b = [rect(0, 0, w, hz, f"url(#wall{uid})"), rect(0, hz, w, h - hz, "#7C7F82")]
    # ceiling joists
    b.append(rect(0, 0, w, h * 0.20, "#3E4145"))
    for i in range(14):
        b.append(rect(w * i / 14, 0, w * 0.022, h * 0.20, "#9A8F7C", 0.85))
    b.append(rect(0, h * 0.195, w, h * 0.012, "#2F3236"))
    # bare bulb
    b.append(line(w * 0.52, h * 0.20, w * 0.52, h * 0.30, "#2F3236", 2, 0.8))
    b.append(f'<circle cx="{w*0.52:.1f}" cy="{h*0.325:.1f}" r="{w*0.016:.1f}" fill="#F4E2B8" fill-opacity="0.95"/>')
    b.append(f'<circle cx="{w*0.52:.1f}" cy="{h*0.325:.1f}" r="{w*0.07:.1f}" fill="#F4E2B8" fill-opacity="0.10"/>')
    # stud wall on the left
    b.append(rect(0, h * 0.20, w * 0.30, hz - h * 0.20, "#5A5D61", 0.6))
    for i in range(5):
        b.append(rect(w * 0.30 * i / 5, h * 0.20, w * 0.016, hz - h * 0.20, "#9A8F7C", 0.8))
    # boxes / clutter
    for i, (bx, bw) in enumerate([(0.62, 0.14), (0.78, 0.10), (0.70, 0.08)]):
        by = hz - h * (0.10 + 0.05 * (i % 2))
        b.append(rect(w * bx, by, w * bw, hz - by, "#8A7E6B", 0.9))
        b.append(line(w * bx, by + (hz - by) * 0.45, w * (bx + bw), by + (hz - by) * 0.45, "#6B6154", 2, 0.6))
    b.append(rect(0, hz, w, h - hz, "#000", 0.08))
    return d, b, uid


def scene_ceiling_leak(w, h, state, seed):
    """Water damage: stained sagging ceiling and standing water on the floor."""
    p, r, uid = pal(state), rng(seed), "w" + str(abs(hash(seed)) % 9999)
    hz = h * 0.74
    d, b = interior_shell(w, h, hz, p, uid, warm_light=(state == "after"))
    # ceiling plane
    ch = h * 0.20
    b.insert(1, rect(0, 0, w, ch, mix(p["wall"], "#ffffff", 0.45 if state == "after" else 0.1)))
    b.insert(2, poly([(0, ch), (w, ch), (w, ch + h * 0.012), (0, ch + h * 0.012)], "#000", 0.10))
    b += window(w * 0.74, h * 0.30, w * 0.18, h * 0.24, p, uid, bright=(state == "after"))

    if state == "before":
        # brown ceiling stain with concentric rings
        for i, (rr, op, col) in enumerate([(0.17, 0.30, "#8A6A45"), (0.12, 0.38, "#7A5A38"),
                                           (0.075, 0.55, "#5E4327"), (0.035, 0.7, "#4A3420")]):
            b.append(blob(w * 0.36, ch * 0.62, w * rr, ch * rr * 2.3, f"{seed}c{i}", col, op))
        b.append(blob(w * 0.60, ch * 0.5, w * 0.07, ch * 0.34, seed + "c2", "#7A5A38", 0.28))
        # drip
        b.append(line(w * 0.36, ch * 0.9, w * 0.36, hz, "#6E7A78", 2.5, 0.35))
        # standing water
        b.append(f'<ellipse cx="{w*0.42:.1f}" cy="{h*0.90:.1f}" rx="{w*0.40:.1f}" ry="{h*0.085:.1f}" fill="#5A6A70" fill-opacity="0.55"/>')
        b.append(f'<ellipse cx="{w*0.42:.1f}" cy="{h*0.90:.1f}" rx="{w*0.40:.1f}" ry="{h*0.085:.1f}" fill="#AEC3CB" fill-opacity="0.18"/>')
        for i in range(5):
            b.append(line(w * r(0.12, 0.72), h * r(0.86, 0.94), w * r(0.12, 0.72), h * r(0.86, 0.94),
                          "#DCE7EC", r(1, 2.4), 0.30))
        # buckled boards
        for i in range(6):
            yy = hz + (h - hz) * (i + 1) / 7
            b.append(line(0, yy, w, yy + r(-4, 4), "#000", 1.4, 0.13))
        b.append(blob(w * 0.12, hz - h * 0.06, w * 0.06, h * 0.05, seed + "wm", "#3D4A33", 0.35))
    else:
        b.append(rect(0, 0, w, ch, "#FFFFFF", 0.22))
        for i in range(8):
            b.append(line(0, hz + (h - hz) * (i + 1) / 8, w, hz + (h - hz) * (i + 1) / 8, "#000", 1.2, 0.10))
        for k in (0.24, 0.52):
            b.append(f'<circle cx="{w*k:.1f}" cy="{ch*0.5:.1f}" r="{w*0.012:.1f}" fill="{p["light"]}" fill-opacity="0.9"/>')
            b.append(f'<ellipse cx="{w*k:.1f}" cy="{ch*0.62:.1f}" rx="{w*0.07:.1f}" ry="{h*0.05:.1f}" fill="{p["light"]}" fill-opacity="0.12"/>')
        b.append(rect(w * 0.06, ch + h * 0.02, w * 0.015, hz - ch - h * 0.02, p["trim"], 0.9))
        b.append(rect(w * 0.075, ch + h * 0.02, w * 0.16, hz - ch - h * 0.02, mix(p["wall"], "#fff", 0.25)))
        b.append(rect(w * 0.235, ch + h * 0.02, w * 0.015, hz - ch - h * 0.02, p["trim"], 0.9))
        b.append(rect(w * 0.42, hz - h * 0.11, w * 0.16, h * 0.11, "#D8D3CA", 0.95, rx=3))
        for i in range(6):
            b.append(line(w * (0.43 + 0.025 * i), hz - h * 0.10, w * (0.43 + 0.025 * i), hz - h * 0.01, "#B3AEA4", 3, 0.9))
    return d, b, uid


def scene_living(w, h, state, seed):
    """Living room — the aspirational hero shot."""
    p, r, uid = pal(state), rng(seed), "l" + str(abs(hash(seed)) % 9999)
    hz = h * 0.70
    d, b = interior_shell(w, h, hz, p, uid, warm_light=(state == "after"))

    # fireplace: surround, firebox, mantel
    fx, fw = w * 0.34, w * 0.32
    sur = mix(p["wall"], "#ffffff", 0.34 if state == "after" else 0.06)
    b.append(rect(fx, h * 0.20, fw, hz - h * 0.20, sur))
    b.append(rect(fx, h * 0.20, fw, hz - h * 0.20, "#000", 0.05))
    fb_x, fb_w = fx + fw * 0.24, fw * 0.52
    fb_y, fb_h = hz - h * 0.26, h * 0.26
    b.append(rect(fb_x, fb_y, fb_w, fb_h, "#22262B"))
    if state == "after":
        b.append(rect(fb_x + fb_w * 0.10, fb_y + fb_h * 0.42, fb_w * 0.80, fb_h * 0.52, p["accent"], 0.75))
        b.append(rect(fb_x + fb_w * 0.22, fb_y + fb_h * 0.58, fb_w * 0.56, fb_h * 0.36, p["warm"], 0.85))
        b.append(f'<ellipse cx="{fb_x + fb_w/2:.1f}" cy="{fb_y + fb_h*0.7:.1f}" rx="{fb_w*0.9:.1f}" ry="{fb_h*0.7:.1f}" fill="{p["warm"]}" fill-opacity="0.13"/>')
    # mantel
    b.append(rect(fx - fw * 0.05, fb_y - h * 0.045, fw * 1.10, h * 0.028,
                  p["trim"] if state == "after" else "#A6A8A4"))
    b.append(rect(fx - fw * 0.05, fb_y - h * 0.017, fw * 1.10, h * 0.008, "#000", 0.18))

    b += window(w * 0.04, h * 0.17, w * 0.22, h * 0.36, p, uid, bright=(state == "after"))
    b += window(w * 0.74, h * 0.17, w * 0.22, h * 0.36, p, uid, bright=(state == "after"))

    if state == "after":
        b.append(f'<ellipse cx="{w*0.50:.1f}" cy="{h*0.90:.1f}" rx="{w*0.36:.1f}" ry="{h*0.075:.1f}" fill="{p["accent"]}" fill-opacity="0.16"/>')
        for i in range(8):
            b.append(line(0, hz + (h - hz) * (i + 1) / 8, w, hz + (h - hz) * (i + 1) / 8, "#000", 1.2, 0.08))

    # sofa, seen from behind-ish: back, seat cushions, arms, legs
    sx, sw = w * 0.28, w * 0.44
    sy = hz + (h - hz) * 0.16
    sofa = "#7E8288" if state == "before" else "#CBBCA4"
    b.append(rect(sx + sw * 0.02, sy - h * 0.085, sw * 0.96, h * 0.095, mix(sofa, "#000", 0.10), rx=8))
    for k in (0.28, 0.68):                                   # back cushions
        b.append(rect(sx + sw * k - sw * 0.20, sy - h * 0.075, sw * 0.38, h * 0.072,
                      mix(sofa, "#fff", 0.08), rx=6))
    b.append(rect(sx, sy, sw, h * 0.055, mix(sofa, "#000", 0.04), rx=5))
    b.append(rect(sx - w * 0.018, sy - h * 0.055, w * 0.042, h * 0.11, mix(sofa, "#000", 0.20), rx=6))
    b.append(rect(sx + sw - w * 0.024, sy - h * 0.055, w * 0.042, h * 0.11, mix(sofa, "#000", 0.20), rx=6))
    for k in (0.04, 0.94):
        b.append(rect(sx + sw * k, sy + h * 0.055, w * 0.012, h * 0.022, "#5A4A36" if state == "after" else "#5E6166"))
    if state == "after":
        for k in (0.10, 0.86):                               # throw cushions
            b.append(rect(sx + sw * k, sy - h * 0.062, sw * 0.10, h * 0.055, p["accent"], 0.75, rx=5))
        # coffee table
        b.append(rect(w * 0.40, h * 0.955, w * 0.20, h * 0.016, "#8A6A45", rx=3))
        b.append(rect(w * 0.415, h * 0.971, w * 0.012, h * 0.025, "#7A5C3C"))
        b.append(rect(w * 0.573, h * 0.971, w * 0.012, h * 0.025, "#7A5C3C"))
        # plant
        b.append(poly([(w * 0.90, hz + (h - hz) * 0.30), (w * 0.95, hz + (h - hz) * 0.30),
                       (w * 0.941, h * 0.97), (w * 0.909, h * 0.97)], "#B08258"))
        for i in range(8):
            a = -math.pi / 2 + r(-1.15, 1.15)
            cx = w * 0.925 + math.cos(a) * w * 0.032
            cy = hz + (h - hz) * 0.30 + math.sin(a) * h * 0.055
            b.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{w*0.013:.1f}" ry="{h*0.030:.1f}" '
                     f'fill="#4E7A52" transform="rotate({math.degrees(a)+90:.0f} {cx:.1f} {cy:.1f})"/>')
    else:
        for i in range(6):
            b.append(line(0, hz + (h - hz) * (i + 1) / 6, w, hz + (h - hz) * (i + 1) / 6, "#000", 1, 0.07))
        for i in range(5):
            b.append(blob(r(0, w), r(h * 0.12, hz), w * r(0.03, 0.07), h * r(0.02, 0.045),
                          f"{seed}s{i}", "#6E6F68", 0.20))
    return d, b, uid


# ---------------------------------------------------------------- exteriors --
def sky_and_trees(w, h, hz, p, uid, state, d, b):
    d.append(lingrad(uid, "sky", [(0, mix(p["sky"], "#ffffff", 0.25), 1), (1, p["sky"], 1)]))
    b.append(rect(0, 0, w, hz, f"url(#sky{uid})"))
    r = rng(uid + "trees")
    tree = "#54604F" if state == "before" else "#4C6B4A"
    for i in range(13):
        cx, ry = w * i / 12 + r(-w * 0.03, w * 0.03), h * r(0.05, 0.10)
        b.append(f'<ellipse cx="{cx:.1f}" cy="{hz - ry*0.35:.1f}" rx="{w*r(0.05,0.09):.1f}" ry="{ry:.1f}" '
                 f'fill="{tree}" fill-opacity="{r(0.35,0.6):.2f}"/>')
    return d, b


def scene_deck(w, h, state, seed):
    p, r, uid = pal(state), rng(seed), "d" + str(abs(hash(seed)) % 9999)
    hz = h * 0.34
    d, b = [], []
    d, b = sky_and_trees(w, h, hz, p, uid, state, d, b)
    # house wall behind
    b.append(rect(0, 0, w * 0.30, hz + h * 0.10, "#C6BDB0" if state == "after" else "#9A9A96"))
    for i in range(9):
        b.append(line(0, (hz + h * 0.10) * i / 9, w * 0.30, (hz + h * 0.10) * i / 9, "#000", 1.4, 0.10))

    board = "#7E8380" if state == "before" else "#B4793F"
    rows = 16
    for i in range(rows):
        t = i / rows
        y = hz + (h - hz) * (t ** 1.25)
        hh = (h - hz) * (1.1 / rows) * (0.6 + t)
        inset = w * 0.10 * (1 - t)
        shade = mix(board, "#000", 0.16 * (1 - t))
        if state == "before" and i in (6, 11):
            shade = mix(shade, "#3B3F3C", 0.55)          # rotted / missing board
        b.append(rect(inset, y, w - inset * 2, hh, shade))
        b.append(line(inset, y, w - inset, y, "#000", 1.2, 0.18))
    if state == "before":
        for i in range(16):
            b.append(blob(r(0, w), r(hz + h * 0.12, h), w * r(0.02, 0.06), h * r(0.008, 0.02),
                          f"{seed}rot{i}", "#4A4F49", r(0.18, 0.4)))
        for i in range(9):  # weeds pushing through
            x, y = r(0, w), r(hz + h * 0.25, h * 0.98)
            b.append(line(x, y, x + r(-9, 9), y - h * r(0.03, 0.07), "#5C6B4A", 2.4, 0.7))

    # railing
    ry0 = hz - h * 0.08
    b.append(rect(w * 0.30, ry0, w * 0.70, h * 0.022, mix(board, "#000", 0.25)))
    posts = 6
    for i in range(posts):
        x = w * 0.32 + (w * 0.66) * i / (posts - 1)
        skew = r(-6, 6) if state == "before" else 0
        b.append(f'<polygon points="{x:.1f},{ry0:.1f} {x+w*0.012:.1f},{ry0:.1f} '
                 f'{x+w*0.012+skew:.1f},{hz+h*0.09:.1f} {x+skew:.1f},{hz+h*0.09:.1f}" '
                 f'fill="{mix(board, "#000", 0.3)}"/>')
    if state == "after":
        for k in range(4):                                  # cable infill
            yy = ry0 + h * 0.025 + k * h * 0.028
            b.append(line(w * 0.31, yy, w * 0.98, yy, "#D9D4CC", 1.8, 0.75))
        for i in range(5):                                  # pergola beams
            x = w * 0.34 + w * 0.15 * i
            b.append(rect(x, 0, w * 0.018, hz - h * 0.06, mix(board, "#000", 0.12)))
        b.append(rect(w * 0.30, 0, w * 0.70, h * 0.022, mix(board, "#000", 0.28)))
        b.append(rect(w * 0.06, hz + h * 0.20, w * 0.10, h * 0.12, "#8A6A45"))   # planter
        for i in range(6):
            b.append(f'<circle cx="{w*(0.07+0.016*i):.1f}" cy="{hz + h*0.19 - r(0,h*0.03):.1f}" '
                     f'r="{w*0.018:.1f}" fill="#4E7A52" fill-opacity="0.9"/>')
    else:
        for i in range(posts - 1):                          # broken balusters
            x = w * 0.36 + (w * 0.60) * i / (posts - 1)
            if i != 2:
                b.append(line(x, ry0 + h * 0.02, x + r(-4, 4), hz + h * 0.085, mix(board, "#000", 0.35), 3, 0.8))
    return d, b, uid


def scene_yard(w, h, state, seed):
    p, r, uid = pal(state), rng(seed), "y" + str(abs(hash(seed)) % 9999)
    hz = h * 0.36
    d, b = [], []
    d, b = sky_and_trees(w, h, hz, p, uid, state, d, b)
    # fence
    b.append(rect(0, hz - h * 0.10, w, h * 0.12, "#8A7F6E" if state == "after" else "#77756E"))
    for i in range(26):
        b.append(line(w * i / 26, hz - h * 0.10, w * i / 26, hz + h * 0.02, "#000", 1.6, 0.16))

    ground = "#6E6A5E" if state == "before" else "#5E8A4E"
    b.append(rect(0, hz, w, h - hz, ground))
    if state == "before":
        for i in range(30):                                  # bare mud patches
            b.append(blob(r(0, w), r(hz, h), w * r(0.03, 0.10), h * r(0.02, 0.05),
                          f"{seed}mud{i}", "#6A5B47", r(0.25, 0.6)))
        b.append(f'<ellipse cx="{w*0.52:.1f}" cy="{h*0.80:.1f}" rx="{w*0.26:.1f}" ry="{h*0.10:.1f}" fill="#5C6B70" fill-opacity="0.75"/>')
        b.append(f'<ellipse cx="{w*0.52:.1f}" cy="{h*0.80:.1f}" rx="{w*0.26:.1f}" ry="{h*0.10:.1f}" fill="#AEC3CB" fill-opacity="0.22"/>')
        b.append(f'<path d="M{w*0.1:.1f},{h*0.98:.1f} Q{w*0.4:.1f},{h*0.72:.1f} {w*0.95:.1f},{h*0.62:.1f}" '
                 f'stroke="#5A4E3D" stroke-width="{h*0.035:.1f}" fill="none" stroke-opacity="0.55"/>')
        for i in range(22):                                  # sparse grass tufts
            x, y = r(0, w), r(hz + h * 0.05, h)
            b.append(line(x, y, x + r(-5, 5), y - h * 0.02, "#6E7A52", 2, 0.5))
    else:
        b.append(poly([(w * 0.14, h * 0.60), (w * 0.86, h * 0.60), (w, h), (0, h)], "#B9B2A6"))
        cols, rowsn = 9, 6
        for j in range(rowsn + 1):
            t = j / rowsn
            yy = h * 0.60 + (h * 0.40) * t
            x0 = w * 0.14 * (1 - t)
            b.append(line(x0, yy, w - x0, yy, "#8E8779", 2, 0.55))
        for i in range(cols + 1):
            b.append(line(w * (0.14 + 0.72 * i / cols), h * 0.60,
                          w * (i / cols), h, "#8E8779", 2, 0.45))
        b.append(rect(0, h * 0.575, w, h * 0.03, "#9A9284"))
        for i in range(9):                                   # shrubs along the fence
            cx = w * (0.05 + 0.11 * i)
            b.append(f'<ellipse cx="{cx:.1f}" cy="{hz + h*0.06:.1f}" rx="{w*0.045:.1f}" ry="{h*0.045:.1f}" fill="#47703F"/>')
            b.append(f'<ellipse cx="{cx - w*0.015:.1f}" cy="{hz + h*0.045:.1f}" rx="{w*0.03:.1f}" ry="{h*0.03:.1f}" fill="#5A8A4C" fill-opacity="0.8"/>')
    return d, b, uid


def scene_house(w, h, state, seed):
    """House elevation — siding, roof and gutters."""
    p, r, uid = pal(state), rng(seed), "h" + str(abs(hash(seed)) % 9999)
    hz = h * 0.86
    d, b = [], []
    d, b = sky_and_trees(w, h, hz, p, uid, state, d, b)
    b.append(rect(0, hz, w, h - hz, "#6E6A5E" if state == "before" else "#5E8A4E"))

    wallc = "#A9A69D" if state == "before" else "#D8D2C6"
    roofc = "#5A5A58" if state == "before" else "#3C4247"
    x0, x1, top = w * 0.08, w * 0.92, h * 0.40
    # roof
    b.append(poly([(w * 0.50, h * 0.10), (x1 + w * 0.03, top), (x0 - w * 0.03, top)], roofc))
    for i in range(9):                                       # shingle courses
        t = (i + 1) / 10
        y = h * 0.10 + (top - h * 0.10) * t
        half = (x1 - x0 + w * 0.06) * t / 2
        b.append(line(w * 0.50 - half, y, w * 0.50 + half, y, "#000", 2, 0.16))
    if state == "before":
        for i in range(6):                                   # missing shingles
            t = r(0.3, 0.9)
            y = h * 0.10 + (top - h * 0.10) * t
            half = (x1 - x0 + w * 0.06) * t / 2
            xx = w * 0.50 + r(-half * 0.85, half * 0.85)
            b.append(rect(xx, y, w * r(0.02, 0.045), h * 0.018, "#3A3A38", 0.9))
        b.append(blob(w * 0.66, h * 0.30, w * 0.09, h * 0.05, seed + "rs", "#4C5148", 0.35))
    # walls + siding
    b.append(rect(x0, top, x1 - x0, hz - top, wallc))
    for i in range(14):
        b.append(line(x0, top + (hz - top) * (i + 1) / 14, x1, top + (hz - top) * (i + 1) / 14, "#000", 1.6, 0.12))
    # gutter
    gy = top + h * 0.005
    if state == "before":
        b.append(f'<path d="M{x0-w*0.03:.1f},{gy:.1f} Q{w*0.5:.1f},{gy+h*0.035:.1f} {x1+w*0.03:.1f},{gy:.1f}" '
                 f'stroke="#8E8B84" stroke-width="{h*0.014:.1f}" fill="none"/>')
        for i in range(10):
            b.append(blob(r(x0, x1), r(top, hz), w * r(0.02, 0.05), h * r(0.015, 0.035),
                          f"{seed}dirt{i}", "#7A7568", r(0.2, 0.45)))
    else:
        b.append(rect(x0 - w * 0.03, gy, x1 - x0 + w * 0.06, h * 0.014, "#EDEAE4"))
    # openings
    for k in (0.18, 0.38, 0.62, 0.82):
        b += window(w * k - w * 0.055, top + h * 0.06, w * 0.11, h * 0.16, p, uid, bright=(state == "after"))
    b.append(rect(w * 0.46, hz - h * 0.20, w * 0.09, h * 0.20, p["accent"] if state == "after" else "#7E7A72"))
    b.append(rect(w * 0.46, hz - h * 0.205, w * 0.09, h * 0.012, p["trim"], 0.9))
    if state == "after":
        for i in range(7):
            b.append(f'<ellipse cx="{w*(0.10+0.13*i):.1f}" cy="{hz+h*0.02:.1f}" rx="{w*0.035:.1f}" ry="{h*0.022:.1f}" fill="#47703F"/>')
    return d, b, uid


def scene_lead(w, h, state, seed):
    """Close-up of painted trim and clapboard — lead-paint work."""
    p, r, uid = pal(state), rng(seed), "p" + str(abs(hash(seed)) % 9999)
    base = "#B9B3A6" if state == "before" else "#EDE9E1"
    d = [lingrad(uid, "sd", [(0, mix(base, "#ffffff", 0.12), 1), (1, mix(base, "#000", 0.10), 1)])]
    b = [rect(0, 0, w, h, f"url(#sd{uid})")]
    for i in range(12):                                      # clapboard laps
        y = h * (i + 1) / 12
        b.append(line(0, y, w, y, "#000", 2.2, 0.13))
        b.append(line(0, y + 2.5, w, y + 2.5, "#FFFFFF", 2, 0.10))
    # window with sill
    wx, wy, ww, wh = w * 0.30, h * 0.16, w * 0.44, h * 0.56
    b.append(rect(wx - w * 0.035, wy - h * 0.035, ww + w * 0.07, wh + h * 0.07,
                  "#C8C2B4" if state == "before" else "#FFFFFF"))
    b.append(rect(wx, wy, ww, wh, "#5E6E76" if state == "before" else "#8FB3C6", 0.9))
    b.append(rect(wx, wy, ww, wh * 0.45, "#FFFFFF", 0.12))
    b.append(line(wx + ww / 2, wy, wx + ww / 2, wy + wh, "#C8C2B4" if state == "before" else "#FFFFFF", ww * 0.05))
    b.append(line(wx, wy + wh / 2, wx + ww, wy + wh / 2, "#C8C2B4" if state == "before" else "#FFFFFF", wh * 0.045))
    b.append(rect(wx - w * 0.06, wy + wh + h * 0.035, ww + w * 0.12, h * 0.045,
                  "#BDB6A7" if state == "before" else "#FFFFFF"))

    if state == "before":
        for i in range(46):                                  # peeling paint flakes
            cx, cy = r(0, w), r(0, h)
            s = w * r(0.012, 0.045)
            pts = [(cx + math.cos(2 * math.pi * k / 6) * s * r(0.5, 1.3),
                    cy + math.sin(2 * math.pi * k / 6) * s * r(0.4, 1.1)) for k in range(6)]
            b.append(poly(pts, "#8E7F66", r(0.30, 0.68)))
            b.append(poly([(x + 2, y + 2) for x, y in pts], "#000", 0.10))
        for i in range(10):
            b.append(blob(r(0, w), r(0, h), w * r(0.03, 0.08), h * r(0.02, 0.05),
                          f"{seed}wz{i}", "#6E6455", r(0.15, 0.35)))
        b.append(line(wx + ww * 0.1, wy + wh + h * 0.04, wx + ww * 0.8, wy + wh + h * 0.052, "#6E6455", 3, 0.6))
    else:
        b.append(rect(0, 0, w, h, "#FFFFFF", 0.10))
    return d, b, uid


def scene_jobsite(w, h, state, seed):
    """Crew at work — used for process and header bands."""
    p, r, uid = pal("after"), rng(seed), "j" + str(abs(hash(seed)) % 9999)
    hz = h * 0.80
    d = [lingrad(uid, "wall", [(0, "#DCD5C8", 1), (1, "#B8B0A2", 1)])]
    b = [rect(0, 0, w, hz, f"url(#wall{uid})"), rect(0, hz, w, h - hz, "#9A8F7C")]
    for i in range(9):                                       # stud wall
        b.append(rect(w * i / 9, h * 0.10, w * 0.020, hz - h * 0.10, "#C9AE82", 0.9))
    b.append(rect(0, h * 0.10, w, h * 0.022, "#C9AE82"))
    b.append(rect(0, hz - h * 0.02, w, h * 0.022, "#C9AE82"))
    b.append(poly([(w * 0.55, 0), (w * 0.92, 0), (w * 0.74, hz), (w * 0.40, hz)], "#FFFFFF", 0.10))
    # ladder
    lx = w * 0.16
    b.append(line(lx, h * 0.14, lx - w * 0.03, hz, "#C0C3C6", 5, 0.9))
    b.append(line(lx + w * 0.07, h * 0.14, lx + w * 0.04, hz, "#C0C3C6", 5, 0.9))
    for i in range(6):
        y = h * 0.18 + (hz - h * 0.2) * i / 6
        b.append(line(lx - w * 0.005 * i, y, lx + w * 0.07 - w * 0.005 * i, y, "#C0C3C6", 4, 0.9))
    # sawhorse + board
    sx = w * 0.60
    b.append(line(sx, hz, sx - w * 0.04, h * 0.98, "#8A6A45", 6, 0.95))
    b.append(line(sx + w * 0.10, hz, sx + w * 0.14, h * 0.98, "#8A6A45", 6, 0.95))
    b.append(rect(sx - w * 0.10, hz - h * 0.02, w * 0.32, h * 0.025, "#C9AE82"))
    b.append(rect(w * 0.80, hz - h * 0.10, w * 0.10, h * 0.10, "#E2743B", 0.9))
    b.append(rect(0, hz, w, h - hz, "#000", 0.06))
    return d, b, uid


# ------------------------------------------------------------------- driver --
# Set to False (or pass --clean) to drop the small corner tag once you are
# confident nobody will mistake these illustrations for real photographs.
WATERMARK = "--clean" not in __import__("sys").argv


def tag(w, h, text):
    k = min(w, h) / 900.0
    fs = max(11, 17 * k)
    pad = max(10, 16 * k)
    return (f'<text x="{w - pad:.0f}" y="{h - pad:.0f}" text-anchor="end" '
            f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="{fs:.0f}" '
            f'font-weight="600" letter-spacing="{1.4*k:.1f}" fill="#FFFFFF" fill-opacity="0.34">{text}</text>')


def render(path, w, h, fn, state, seed, label, vig=0.42, grain=0.5):
    d, b, uid = fn(w, h, state, seed)
    if WATERMARK:
        b.append(tag(w, h, "PLACEHOLDER"))
    wrap(path, w, h, label, "\n".join(d), "\n".join(b), uid, vig, grain)


PROJECTS = [
    ("hillside-kitchen", scene_kitchen, "Kitchen gut and rebuild"),
    ("basement-mold", scene_basement, "Basement mold remediation"),
    ("cedar-deck", scene_deck, "Two-level cedar deck"),
    ("backyard-transform", scene_yard, "Backyard regrade and patio"),
    ("burst-pipe", scene_ceiling_leak, "Burst pipe water mitigation"),
    ("victorian-lead", scene_lead, "Lead paint abatement"),
    ("siding-roof", scene_house, "Siding and roof replacement"),
    ("basement-finish", scene_framing, "Finished basement"),
]

for slug, fn, label in PROJECTS:
    render(IMG / "projects" / f"{slug}-before.svg", 1600, 1067, fn, "before", slug + "b", f"Before: {label}")
    render(IMG / "projects" / f"{slug}-after.svg", 1600, 1067, fn, "after", slug + "a", f"After: {label}")

# Service tiles — portrait 4:5. Remediation services show the problem, build
# services show the result, because that is what each one has to communicate.
TILES = [
    ("renovations", scene_kitchen, "after", "Home renovations"),
    ("water", scene_ceiling_leak, "before", "Water damage mitigation"),
    ("remediation", scene_basement, "before", "Mold remediation"),
    ("lead", scene_lead, "before", "Lead paint removal"),
    ("decks", scene_deck, "after", "Decks and porches"),
    ("landscaping", scene_yard, "after", "Landscaping"),
    ("exteriors", scene_house, "after", "Siding and roofing"),
    ("general", scene_jobsite, "after", "General contracting"),
]
for slug, fn, state, label in TILES:
    render(IMG / "site" / f"tile-{slug}.svg", 1200, 1500, fn, state, "tile" + slug, label)

# Wide photographs that sit behind text.
render(IMG / "site" / "hero-bg.svg", 2400, 1500, scene_living, "after", "herobg", "Finished living room")
render(IMG / "site" / "cta-bg.svg", 2400, 1000, scene_kitchen, "after", "ctabg", "Finished kitchen")
render(IMG / "site" / "band-process.svg", 2400, 1200, scene_jobsite, "after", "bandproc", "Crew on site")
render(IMG / "site" / "band-quote.svg", 2400, 1200, scene_living, "after", "bandquote", "Finished interior")
render(IMG / "site" / "head-services.svg", 2400, 1100, scene_jobsite, "after", "headsvc", "Crew on site")
render(IMG / "site" / "head-projects.svg", 2400, 1100, scene_deck, "after", "headproj", "Finished deck")
render(IMG / "site" / "head-contact.svg", 2400, 1100, scene_living, "after", "headcontact", "Finished interior")
render(IMG / "site" / "about-wide.svg", 2400, 1200, scene_jobsite, "after", "aboutwide", "Crew on site")
render(IMG / "site" / "about-jobsite.svg", 1200, 1500, scene_jobsite, "after", "aboutjob", "Crew on site")

# The featured homepage comparison.
render(IMG / "site" / "hero-before.svg", 1600, 1067, scene_living, "before", "featb", "Before: living room")
render(IMG / "site" / "hero-after.svg", 1600, 1067, scene_living, "after", "feata", "After: living room")

render(IMG / "site" / "og-image.svg", 1200, 630, scene_kitchen, "after", "og", "American Restoration Tech")

files = sorted(IMG.rglob("*.svg"))
total = sum(f.stat().st_size for f in files)
print(f"Wrote {len(files)} illustrated placeholders ({total // 1024} KB total)")
