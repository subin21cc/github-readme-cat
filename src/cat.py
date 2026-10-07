#!/usr/bin/env python3
"""Generate an animated pixel-art cat SVG that walks across a GitHub README.

Pure CSS animation, no JavaScript, so it renders inside GitHub's <img> sandbox.
"""
import argparse

S = 8                  # size of one pixel (px)
W, H = 26, 18          # cat sprite grid
CAT_W = W * S
OUTLINE = "#2b2b2b"
IDLE_GAP = 16           # space between standing cats (px)
MAX_CATS = 3
DEFAULT_WIDTH = 720     # one fixed lane shared by every cat

# Ready-made cats. Any option can be overridden per cat, see parse_cat().
PRESETS = {
    "orange":  dict(fur="#f4a259", stripe="#c9733a", belly="#fff3e0", eyes="#2b2b2b", pattern="tabby"),
    "black":   dict(fur="#3a3a44", stripe="#2c2c34", belly="#4d4d59", eyes="#f2c94c", pattern="solid"),
    "tabby":   dict(fur="#9c9a96", stripe="#5e5b57", belly="#f1efea", eyes="#2b2b2b", pattern="tabby"),
    "gray":    dict(fur="#8d99ae", stripe="#6b7690", belly="#edf2f4", eyes="#2b2b2b", pattern="tabby"),
    "white":   dict(fur="#f8f8f6", stripe="#e4e2dc", belly="#ffffff", eyes="#4a90d9", pattern="solid"),
    "tuxedo":  dict(fur="#34343c", stripe="#34343c", belly="#f6f6f2", eyes="#8bc34a", pattern="tuxedo"),
    "calico":  dict(fur="#f4a259", stripe="#3a3a44", belly="#fbf7f0", eyes="#d4a017", pattern="calico"),
    "siamese": dict(fur="#efe3cf", stripe="#5a4636", belly="#f7f0e4", eyes="#4a90d9", pattern="siamese"),
}
PATTERNS = ("tabby", "solid", "tuxedo", "calico", "siamese")
EARS = ("pointed", "fold")
TAILS = ("long", "short")
COLOR_NAMES = {
    "black": "#2b2b2b", "white": "#ffffff", "gray": "#8d99ae", "cream": "#f3e5c8",
    "brown": "#7a5230", "orange": "#f4a259", "red": "#e5484d", "pink": "#ff8fa3",
    "purple": "#8e6cd8", "blue": "#4a90d9", "green": "#5cb85c", "yellow": "#f2c94c",
    "amber": "#d4a017", "copper": "#b87333",
}


def parse_color(value):
    v = COLOR_NAMES.get(value.lower(), value)
    if v.startswith("#") and len(v) == 4:
        v = "#" + "".join(ch * 2 for ch in v[1:])
    try:
        if len(v) == 7 and v[0] == "#":
            int(v[1:], 16)
            return v.lower()
    except ValueError:
        pass
    raise ValueError(f"bad color '{value}' (use #rrggbb or one of: {', '.join(COLOR_NAMES)})")


def parse_cat(spec):
    """'calico ears=fold collar=red' -> cat options. The bare word picks a preset."""
    base, opts = "orange", {}
    for token in spec.split():
        if "=" not in token:
            if token not in PRESETS:
                raise ValueError(f"unknown preset '{token}' (choose from {', '.join(PRESETS)})")
            base = token
            continue
        key, value = token.split("=", 1)
        if key in ("fur", "stripe", "belly"):
            opts[key] = parse_color(value)
        elif key == "eyes":
            opts[key] = "/".join(parse_color(v) for v in value.split("/")[:2])
        elif key == "collar":
            opts[key] = None if value == "none" else parse_color(value)
        elif key in ("pattern", "ears", "tail"):
            allowed = {"pattern": PATTERNS, "ears": EARS, "tail": TAILS}[key]
            if value not in allowed:
                raise ValueError(f"{key} must be one of: {', '.join(allowed)}")
            opts[key] = value
        else:
            raise ValueError(f"unknown option '{key}' "
                             "(fur, stripe, belly, eyes, pattern, ears, tail, collar)")
    cat = dict(PRESETS[base], ears="pointed", tail="long", collar=None)
    cat.update(opts)
    return cat


# Contributions in the period -> mood
MOODS = {
    #        step(s)  speed(px/s)
    "idle": (None,    0),
    "walk": (1.2,     25),
    "run":  (0.6,     55),
}


def mood_for(contributions):
    if contributions <= 0:
        return "idle"
    return "walk" if contributions < 10 else "run"


def shade(hex_color, f=0.88):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def palette(cat):
    left, _, right = cat["eyes"].partition("/")
    return {
        "K": OUTLINE, "P": "#ff8fa3", "H": "#ffffff", "Y": "#f2c94c",
        "O": cat["fur"], "D": cat["stripe"], "W": cat["belly"],
        "E": left, "F": right or left, "C": cat["collar"] or OUTLINE,
        "o": shade(cat["fur"]), "d": shade(cat["stripe"]), "w": shade(cat["belly"]),  # far legs
    }


def recolor(r, c, ch, pattern, part):
    """Where the fur, stripe and belly colors go for each coat pattern."""
    if ch not in "ODWodw":
        return ch
    far, ch = ch.islower(), ch.upper()
    if pattern == "solid":
        ch = "O"
    elif pattern == "tuxedo":
        ch = "W" if ch == "W" else "O"
    elif pattern == "calico" and ch != "W":
        if part == "body" and c <= 10:      # head: one patch of each color
            ch = "O" if c <= 4 and r <= 5 else "D" if c >= 6 and r <= 4 else "W"
        elif part == "body":
            ch = "D" if c <= 13 else "O"
        else:
            ch = "O"
    elif pattern == "siamese":
        ch = "W" if ch == "W" else "O"
        point = (part == "tail" or (part == "legs" and r >= 15) or r <= 2
                 or (part == "body" and 7 <= r <= 9 and 3 <= c <= 7))
        if point:
            ch = "D"
    return ch.lower() if far else ch


def paint(px, cat, part):
    out = {}
    for (r, c), ch in px.items():
        if ch == "E" and c >= 6:
            ch = "F"            # right eye, for odd eyes
        out[(r, c)] = recolor(r, c, ch, cat["pattern"], part)
    return out


BODY = [
    "..K.....K..",
    ".KPK...KPK.",
    ".KOOKKKOOK.",
    "KOOODODOOOK",
    "KOOOOOOOOOK",
    "KOOOOOOOOOK",
    "KOEHOOOEHOKKKKKKKKKK",
    "KOEEOOOEEOKOODOODOOK",
    "KWWOOPOOWWKOODOODOOK",
    ".KWWWKWWWKOOOOOOOOOK",
    "..KWWWWWWOOOOOOOOOOK",
    "..KWWWWWOOOOOOOOOOOK",
    "..KWWWWWWWWWWWWWWOOK",
]
BLINK = [""] * 6 + ["KOOOOOOOOOK", "KOKKOOOKKOK"]
FOLD_EARS = ["", "..KKK.KKK.."]


def body_px(cat):
    rows = list(BODY)
    if cat["ears"] == "fold":
        rows[:2] = FOLD_EARS
    px = grid(rows)
    if cat["collar"]:
        px.update({(10, c): "C" for c in range(3, 9)})
        px[(11, 5)] = "Y"   # bell
    return px


def body_empty(r, c):
    return r < 0 or r >= len(BODY) or c >= len(BODY[r]) or BODY[r][c] == "."


def sprite(fill, outline_if=lambda r, c: True, diagonal=True):
    """Wrap a {(row, col): color} fill with an outline."""
    out = {}
    for (r, c) in fill:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if not diagonal and dr and dc:
                    continue
                p = (r + dr, c + dc)
                if p not in fill and outline_if(*p):
                    out[p] = "K"
    out.update(fill)
    return out


# Legs: 4-beat lateral-sequence walk, 8 frames. Thin legs with a long stride.
# A pose is a horizontal offset per row (negative = forward).
# 5 rows = paw on the ground, 4 rows = paw lifted.
LEG_TOP = 12
LEG_W = [2, 2, 1, 1, 1]   # leg thickness per row: thicker at the top, slim lower leg
STAND = [0] * 5
FRONT_CYCLE = [
    [0, -1, -1, -2, -2],  # reach and plant
    [0, 0, -1, -1, -1],
    [0, 0, 0, 0, 0],      # under the body
    [0, 0, 1, 1, 1],
    [0, 1, 1, 2, 3],      # push off
    [0, 1, 2, 1],         # wrist folds, paw lifts
    [0, 0, 0, -1],        # swing forward
    [0, -1, -1, -2],
]
HIND_CYCLE = [
    [0, -1, -1, -2, -2],
    [0, 0, -1, -1, -1],
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 2],
    [0, 1, 2, 2, 3],      # push off
    [0, 1, 2, 3],         # toe flick
    [0, 1, 1, 0],         # hock bends
    [0, 0, -1, -1],
]
LEGS = [  # (x, leg color, paw color, far side, cycle, phase)
    (3, "W", "W", False, FRONT_CYCLE, 2),
    (7, "w", "w", True, FRONT_CYCLE, 6),
    (13, "o", "w", True, HIND_CYCLE, 4),
    (17, "O", "W", False, HIND_CYCLE, 0),
]
GAIT = [[cyc[(f - ph) % 8] for (*_, cyc, ph) in LEGS] for f in range(8)]


def leg_frame(offsets):
    px = {(LEG_TOP + 1, c): "K" for c in range(2, 20)}  # belly line, legs cover it
    for i in sorted(range(4), key=lambda i: not LEGS[i][3]):  # far legs first
        x, col, paw = LEGS[i][:3]
        last = len(offsets[i]) - 1
        fill = {}
        for k, off in enumerate(offsets[i]):
            for dx in range(LEG_W[k]):
                if k and off != offsets[i][k - 1]:   # bridge the step so the leg stays connected
                    fill[(LEG_TOP + k, x + offsets[i][k - 1] + dx)] = col
                fill[(LEG_TOP + k, x + off + dx)] = paw if k == last else col
        px.update(sprite(fill, lambda r, c: r > LEG_TOP, diagonal=False))
    return px


# Tail: a thin tail rising from the rump, swaying and curling at the tip.
TAIL_SHAPES = {  # (row, col) of each tail pixel, tip first; the root (6, 19) joins the body
    "back":  [(0, 22), (1, 22), (2, 21), (3, 21), (4, 20), (5, 20), (6, 19)],
    "hook":  [(0, 20), (0, 21), (1, 22), (2, 22), (3, 21), (4, 21), (5, 20), (6, 19)],
    "front": [(0, 19), (1, 19), (2, 20), (3, 20), (4, 20), (5, 20), (6, 19)],
    "curl":  [(0, 24), (1, 23), (2, 22), (3, 22), (4, 21), (5, 20), (6, 19)],
}
TAIL_PATHS = [TAIL_SHAPES[k] for k in ("back", "hook", "front", "hook", "back", "curl")]


def tail_frame(cells, short=False):
    if short:
        cells = [(r, c) for r, c in cells if r >= 4]
    fill = {(r, c): "D" if r in (2, 4) else "O" for r, c in cells}
    return sprite(fill, body_empty)


def grid(rows):
    return {(y, x): c for y, row in enumerate(rows) for x, c in enumerate(row) if c != "."}


def rects(px, pal):
    return "".join(
        f'<rect x="{c*S}" y="{r*S}" width="{S}" height="{S}" fill="{pal[ch]}"/>'
        for (r, c), ch in sorted(px.items())
    )


def frames(cls, items, sec, pal, offset=0.0):
    """Show items one at a time, evenly spread over sec seconds."""
    n = len(items)
    return "".join(
        f'<g class="{cls}" style="animation-delay:-{((n - i) % n * sec / n + offset) % sec:g}s">'
        f'{rects(f, pal)}</g>'
        for i, f in enumerate(items)
    )


def cat_svg(cat, mood, width, index, count, pace=1.0):
    pal = palette(cat)
    step, speed = MOODS[mood]
    step *= pace  # pace > 1 slows the legs down without changing the walking speed
    tail_sec = 2 if mood != "idle" else 3
    offset = index * 0.37  # so several cats don't move in lockstep

    standing = rects(paint(leg_frame([STAND] * 4), cat, "legs"), pal)
    if step:
        # Walking legs while moving; legs stand still while the cat pauses to turn around
        legs = (f'<g class="moving" style="{{sync}}">'
                f'{frames("l", [paint(leg_frame(g), cat, "legs") for g in GAIT], step, pal, offset)}</g>'
                f'<g class="paused" style="{{sync}}">{standing}</g>')
    else:
        legs = standing
    body = (
        f'<g class="bob">{rects(paint(body_px(cat), cat, "body"), pal)}'
        f'<g class="blink" style="animation-delay:-{index * 1.3:g}s">{rects(paint(grid(BLINK), cat, "body"), pal)}</g>'
        f'{frames("t", [paint(tail_frame(p, cat["tail"] == "short"), cat, "tail") for p in TAIL_PATHS],
                 tail_sec, pal, offset)}</g>'
    )

    if step:
        far = width - CAT_W
        walk_sec = 2 * far / speed / 0.9
        delay = walk_sec * index / count
        style = f"animation:walk-{mood} {walk_sec:.2f}s linear infinite;animation-delay:-{delay:.2f}s"
        legs = legs.replace("{sync}", f"animation-duration:{walk_sec:.2f}s;animation-delay:-{delay:.2f}s")
    else:
        slot = width / count  # min_width() guarantees CAT_W + IDLE_GAP per cat
        x = int(index * slot + (slot - CAT_W) / 2)
        style = f"transform:translateX({x}px)"
    return f'<g class="cat" style="{style}">{legs}{body}</g>'


def min_width(count):
    """Narrowest lane where `count` cats can stand side by side without overlapping."""
    return count * (CAT_W + IDLE_GAP)


def build(cats, contributions, width, theme, pace=1.0):
    mood = mood_for(contributions)
    step = MOODS[mood][0] * pace
    far = width - CAT_W
    halo = ""
    if theme == "dark":
        c = "#d0d0d0"
        halo = (f".cat{{filter:drop-shadow(1px 0 0 {c}) drop-shadow(-1px 0 0 {c}) "
                f"drop-shadow(0 1px 0 {c}) drop-shadow(0 -1px 0 {c})}}")
    drawn = "".join(cat_svg(c, mood, width, i, len(cats), pace) for i, c in enumerate(cats))
    height = (H + 1) * S + 4  # one spare row on top for the tail tip outline
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" shape-rendering="crispEdges">
<title>pixel cat ({mood}, {contributions} contributions)</title>
<style>
.t{{animation:ft {2 if mood != "idle" else 3}s steps(1) infinite}}
.l{{animation:fl {step or 1}s steps(1) infinite}}
.blink{{animation:blink 4s steps(1) infinite}}
.bob{{animation:bob {(step or 2.4) / 2:g}s steps(1) infinite}}
@keyframes ft{{0%{{opacity:1}}{100 / len(TAIL_PATHS):g}%{{opacity:0}}}}
@keyframes fl{{0%{{opacity:1}}12.5%{{opacity:0}}}}
@keyframes blink{{0%{{opacity:0}}92%{{opacity:1}}97%{{opacity:0}}}}
@keyframes bob{{0%{{transform:translateY(0)}}50%{{transform:translateY(1px)}}}}
.moving{{animation:legs-go 1s steps(1) infinite}}
.paused{{animation:legs-rest 1s steps(1) infinite}}
@keyframes legs-go{{0%{{opacity:1}}45%{{opacity:0}}50%{{opacity:1}}95%{{opacity:0}}}}
@keyframes legs-rest{{0%{{opacity:0}}45%{{opacity:1}}50%{{opacity:0}}95%{{opacity:1}}}}
/* walk to an edge, stop for a moment, then turn around in a single frame */
@keyframes walk-{mood}{{
0%{{transform:translateX({far}px) scaleX(1)}}
45%{{transform:translateX(0) scaleX(1)}}
49.99%{{transform:translateX(0) scaleX(1)}}
50%{{transform:translateX({CAT_W}px) scaleX(-1)}}
95%{{transform:translateX({width}px) scaleX(-1)}}
99.99%{{transform:translateX({width}px) scaleX(-1)}}
100%{{transform:translateX({far}px) scaleX(1)}}
}}
{halo}
</style>
<g transform="translate(0,{S + 2})">{drawn}</g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--coats", default="orange",
                    help=f"comma-separated cats, up to {MAX_CATS}. Each is a preset "
                         f"({', '.join(PRESETS)}) and/or options like 'ears=fold collar=red'")
    ap.add_argument("--contributions", type=int, default=5,
                    help="recent contributions: 0 = idle, 1-9 = walk, 10+ = run")
    ap.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="lane width in px")
    ap.add_argument("--pace", type=float, default=1.0,
                    help="leg speed multiplier; 2 makes each step take twice as long")
    ap.add_argument("--theme", choices=["light", "dark"], default="light")
    ap.add_argument("--out", default="cat.svg")
    a = ap.parse_args()

    specs = [c.strip() for c in a.coats.split(",") if c.strip()]
    if not specs:
        ap.error("no cats given")
    if len(specs) > MAX_CATS:
        ap.error(f"at most {MAX_CATS} cats, got {len(specs)}")
    try:
        cats = [parse_cat(spec) for spec in specs]
    except ValueError as e:
        ap.error(str(e))
    if a.pace <= 0:
        ap.error("--pace must be greater than 0")
    if a.width < min_width(len(cats)):
        ap.error(f"--width must be at least {min_width(len(cats))} for {len(cats)} cat(s)")
    with open(a.out, "w") as f:
        f.write(build(cats, a.contributions, a.width, a.theme, a.pace))
    print(f"wrote {a.out} ({mood_for(a.contributions)}, {len(cats)} cat(s))")


if __name__ == "__main__":
    main()
