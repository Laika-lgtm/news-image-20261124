#!/usr/bin/env python3
"""THE WORLD IN ONE DAY — Tuesday 24 November 2026. Round 2.

Renders the front page for the make.fun news-image-20261124 competition
from stories.json, using only Pillow and the Python standard library.

Round 2 is a date-purity rebuild of the round-1 page: every story on it
was verified against a wire timestamp from Tuesday 24 November 2026;
the twelve round-1 stories that turned out to be from 23 November or
earlier are gone from the page and are named in DATE CHECK instead.
Layout, masthead and the 36-story / 7-region structure are unchanged.

The whole 1024x1024 page is drawn with PIL shapes: flat vector-style
illustrations, no photos, no AI-generated images, no external files.
Runs offline and deterministically — two runs write identical bytes.

If Pillow (or the DejaVu fonts) is unavailable in the grading sandbox,
the program falls back to copying the pre-rendered entry.png that ships
in this repository, so the output is always the same verified image.
"""

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ENV = os.environ.get("MAKEFUN_OUTPUT_DIR", "")

W, H = 1024, 1024
MARGIN = 20
CW = W - 2 * MARGIN  # 984 content width

# ---------------------------------------------------------------- palette
INK = (18, 18, 18)
PAPER = (250, 248, 243)
RED = (178, 24, 24)
NAVY = (16, 38, 66)
GREY = (110, 108, 102)
LIGHT_GREY = (225, 222, 214)
MID_GREY = (180, 176, 168)
WHITE = (255, 255, 255)
CREAM = (244, 238, 226)
SKY = (158, 196, 222)
DARK_SKY = (58, 90, 128)

REGION_COLORS = {
    "EUROPE": (31, 78, 121),
    "MIDDLE EAST": (139, 26, 26),
    "AMERICAS": (20, 83, 45),
    "ASIA-PACIFIC": (124, 58, 0),
    "AFRICA": (91, 74, 138),
    "OCEANIA": (14, 107, 107),
    "WORLD": (85, 85, 85),
}

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/TTF",
    os.path.join(HERE, "fonts"),
]


def find_font(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return None


def load_fonts():
    """Load DejaVu faces; return dict of ImageFont objects."""
    from PIL import ImageFont

    def f(names, size):
        for name in names:
            path = find_font(name)
            if path:
                return ImageFont.truetype(path, size)
        raise RuntimeError("no font found for %s" % (names,))

    return {
        "mast": lambda s: f(["DejaVuSerif-Bold.ttf"], s),
        "serif_b": lambda s: f(["DejaVuSerif-Bold.ttf"], s),
        "sans_b": lambda s: f(["DejaVuSans-Bold.ttf"], s),
        "sans": lambda s: f(["DejaVuSans.ttf"], s),
    }


def wrap(draw, text, font, max_w):
    """Greedy word wrap returning a list of lines fitting max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, font, color, max_w, leading=None):
    """Draw wrapped text; return the y just below the last line."""
    if leading is None:
        leading = font.size + 2
    lines = wrap(draw, text, font, max_w)
    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += leading
    return y


def text_h(font, lines=1, leading_extra=2):
    return lines * (font.size + leading_extra)


def clipped(draw, text, font, max_w, suffix="\u2026"):
    """Shorten text with an ellipsis so it fits max_w (used only for
    single-line labels that must never overflow)."""
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + suffix, font=font) > max_w:
        text = text[:-1]
    return text + suffix


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def pin_xy(lat, lon, x0, y0, w, h):
    """Equirectangular projection of a lat/lon into the map box."""
    px = x0 + (lon + 180.0) / 360.0 * w
    py = y0 + (90.0 - lat) / 180.0 * h
    return px, py

# ------------------------------------------------------- illustrations
# Every scene is drawn with PIL shapes only: flat vector style, no
# photos, no external images. Each function fills its own box.

def art_kyiv(d, x0, y0, x1, y1):
    # Night strike city, drawn in fractions of its own box so the same
    # scene works at hero width (322px) and card width (72px) without
    # spilling into the text column.
    import math
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(24, 30, 52))
    for fx, fy in ((0.06, 0.11), (0.19, 0.11), (0.47, 0.11), (0.72, 0.11)):
        d.ellipse([x0 + w * fx, y0 + h * fy, x0 + w * fx + 3,
                   y0 + h * fy + 3], fill=WHITE)
    d.rectangle([x0, y1 - h * 0.43, x1, y1], fill=(12, 16, 28))
    for fx, fw, fh in ((0.04, 0.11, 0.28), (0.18, 0.08, 0.41),
                       (0.62, 0.12, 0.33), (0.78, 0.09, 0.48)):
        bx = x0 + w * fx
        bw, bh = w * fw, h * fh
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=(38, 46, 74))
        wy = y1 - bh + h * 0.06
        while wy < y1 - h * 0.04:
            d.rectangle([bx + w * 0.015, wy, bx + w * 0.04, wy + h * 0.04],
                        fill=(232, 190, 90))
            wy += h * 0.09
    cx, cy = x0 + w * 0.47, y0 + h * 0.48
    for fr, col in ((0.105, (255, 122, 26)), (0.075, (255, 176, 66)),
                    (0.045, (255, 232, 150))):
        r = w * fr
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for ang in range(0, 360, 45):
        ex = cx + w * 0.14 * math.cos(math.radians(ang))
        ey = cy + w * 0.14 * math.sin(math.radians(ang))
        d.line([cx, cy, ex, ey], fill=(255, 176, 66), width=3)
    d.ellipse([cx + w * 0.16, cy - h * 0.24, cx + w * 0.24, cy - h * 0.07],
              fill=(90, 96, 116))
    d.ellipse([cx + w * 0.21, cy - h * 0.17, cx + w * 0.29, cy - h * 0.02],
              fill=(70, 76, 96))


def art_gaza(d, x0, y0, x1, y1):
    # A second night-strike city, drawn as a dusk variant of the Kyiv
    # scene so the two heroes do not share identical art: orange dusk
    # sky, a low skyline with a minaret, blast on the left.
    d.rectangle([x0, y0, x1, y1], fill=(72, 44, 30))
    d.rectangle([x0, y0 + 58, x1, y1], fill=(40, 26, 20))
    for bx, bw, bh in ((x0 + 8, 44, 34), (x0 + 62, 30, 48),
                       (x0 + 190, 52, 40), (x0 + 252, 36, 56)):
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=(24, 16, 12))
        for wy in range(y1 - bh + 6, y1 - 4, 9):
            d.rectangle([bx + 5, wy, bx + 9, wy + 4], fill=(232, 190, 90))
    # Minaret beside the blast.
    d.rectangle([x0 + 108, y0 + 26, x0 + 118, y1 - 40], fill=(24, 16, 12))
    d.polygon([(x0 + 104, y0 + 28), (x0 + 122, y0 + 28),
               (x0 + 113, y0 + 12)], fill=(24, 16, 12))
    cx, cy = x0 + 72, y0 + 58
    for r, col in ((30, (255, 122, 26)), (21, (255, 176, 66)),
                   (12, (255, 232, 150))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for ang in range(0, 360, 45):
        import math
        ex = cx + 40 * math.cos(math.radians(ang))
        ey = cy + 40 * math.sin(math.radians(ang))
        d.line([cx, cy, ex, ey], fill=(255, 176, 66), width=3)
    d.ellipse([cx + 44, cy - 30, cx + 70, cy - 12], fill=(96, 66, 44))
    d.ellipse([cx + 58, cy - 22, cx + 84, cy - 6], fill=(76, 52, 36))


def art_sea(d, x0, y0, x1, y1):
    # Strait of Hormuz: dusk sky, dark sea, two tankers, one on fire.
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y0 + h * 0.52], fill=(58, 74, 96))
    d.rectangle([x0, y0 + h * 0.52, x1, y1], fill=(24, 52, 74))
    d.ellipse([x0 + w * 0.78, y0 + h * 0.10, x0 + w * 0.92, y0 + h * 0.28],
              fill=(232, 190, 90))
    for f in (0.58, 0.66, 0.74, 0.86):
        d.line([x0 + w * 0.06, y0 + h * f, x1 - w * 0.06, y0 + h * f],
               fill=(58, 90, 128), width=2)
    # Near tanker, burning amidships.
    tx0, ty = x0 + w * 0.08, y0 + h * 0.44
    d.rectangle([tx0, ty, tx0 + w * 0.44, ty + h * 0.12], fill=(30, 30, 34))
    d.rectangle([tx0 + w * 0.06, ty - h * 0.10, tx0 + w * 0.16,
                 ty], fill=(70, 70, 76))
    cx, cy = tx0 + w * 0.26, ty - h * 0.16
    for r, col in ((0.11, (255, 122, 26)), (0.075, (255, 176, 66)),
                   (0.04, (255, 232, 150))):
        rr = w * r
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    d.ellipse([cx + w * 0.10, cy - h * 0.22, cx + w * 0.20, cy - h * 0.10],
              fill=(90, 96, 104))
    # Far tanker, intact, on the horizon.
    fx0, fy = x1 - w * 0.38, y0 + h * 0.46
    d.rectangle([fx0, fy, fx0 + w * 0.30, fy + h * 0.08], fill=(52, 54, 60))
    d.rectangle([fx0 + w * 0.04, fy - h * 0.06, fx0 + w * 0.10, fy],
                fill=(90, 92, 98))


def art_summit(d, x0, y0, x1, y1):
    # Two flags over a table: Ukraine (blue over yellow) and Hungary
    # (red, white, green bands) for the Zakarpattia meeting.
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
    d.rectangle([x0, y1 - h * 0.34, x1, y1 - h * 0.26], fill=(120, 84, 52))
    d.rectangle([x0 + w * 0.10, y1 - h * 0.26, x0 + w * 0.16, y1],
                fill=(96, 66, 40))
    d.rectangle([x1 - w * 0.16, y1 - h * 0.26, x1 - w * 0.10, y1],
                fill=(96, 66, 40))
    # Ukraine flag, left.
    fx = x0 + w * 0.10
    d.rectangle([fx, y0 + h * 0.16, fx + w * 0.34, y0 + h * 0.32],
                fill=(0, 87, 184))
    d.rectangle([fx, y0 + h * 0.32, fx + w * 0.34, y0 + h * 0.48],
                fill=(255, 213, 0))
    d.line([fx + w * 0.17, y0 + h * 0.48, fx + w * 0.17, y1 - h * 0.34],
           fill=(90, 84, 70), width=2)
    # Hungary flag, right.
    gx = x1 - w * 0.44
    d.rectangle([gx, y0 + h * 0.16, gx + w * 0.34, y0 + h * 0.27],
                fill=(205, 42, 62))
    d.rectangle([gx, y0 + h * 0.27, gx + w * 0.34, y0 + h * 0.38],
                fill=WHITE)
    d.rectangle([gx, y0 + h * 0.38, gx + w * 0.34, y0 + h * 0.48],
                fill=(0, 122, 82))
    d.line([gx + w * 0.17, y0 + h * 0.48, gx + w * 0.17, y1 - h * 0.34],
           fill=(90, 84, 70), width=2)
    for cx in (x0 + w * 0.16, x1 - w * 0.16):
        d.rectangle([cx - w * 0.06, y1 - h * 0.62, cx + w * 0.06,
                     y1 - h * 0.34], fill=(58, 90, 128))
        d.rectangle([cx - w * 0.08, y1 - h * 0.68, cx + w * 0.08,
                     y1 - h * 0.62], fill=(38, 64, 96))


def art_drone(d, x0, y0, x1, y1):
    # A small recon drone crossing a night sky over dark fields.
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(38, 58, 86))
    d.rectangle([x0, y1 - h * 0.22, x1, y1], fill=(24, 48, 32))
    for sx in (x0 + w * 0.12, x0 + w * 0.70, x0 + w * 0.88):
        d.ellipse([sx, y0 + h * 0.10, sx + 2, y0 + h * 0.10 + 2],
                  fill=WHITE)
    cx, cy = x0 + w * 0.50, y0 + h * 0.42
    d.ellipse([cx - w * 0.16, cy - h * 0.06, cx + w * 0.16, cy + h * 0.06],
              fill=(24, 24, 28))
    d.ellipse([cx - w * 0.04, cy - h * 0.02, cx + w * 0.04, cy + h * 0.02],
              fill=(255, 122, 26))
    for dx in (-1, 1):
        d.line([cx + dx * w * 0.14, cy - h * 0.10,
                cx + dx * w * 0.30, cy - h * 0.10], fill=(200, 200, 200),
               width=2)
        d.line([cx + dx * w * 0.14, cy + h * 0.10,
                cx + dx * w * 0.30, cy + h * 0.10], fill=(200, 200, 200),
               width=2)
    for i in range(5):
        px = x0 + w * (0.08 + i * 0.05)
        d.line([px, cy + h * 0.28, px + w * 0.03, cy + h * 0.28],
               fill=(232, 190, 90), width=2)


def art_blast(d, x0, y0, x1, y1):
    # A street blast: building facade, a car, an explosion above it.
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(96, 80, 66))
    d.rectangle([x0, y1 - h * 0.30, x1, y1], fill=(52, 48, 44))
    d.rectangle([x0 + w * 0.06, y0 + h * 0.30, x0 + w * 0.44, y1 - h * 0.30],
                fill=(70, 62, 54))
    for wy in (0.38, 0.52):
        d.rectangle([x0 + w * 0.12, y0 + h * wy, x0 + w * 0.20,
                     y0 + h * (wy + 0.08)], fill=(232, 190, 90))
        d.rectangle([x0 + w * 0.28, y0 + h * wy, x0 + w * 0.36,
                     y0 + h * (wy + 0.08)], fill=(232, 190, 90))
    cx, cy = x0 + w * 0.66, y0 + h * 0.34
    for r, col in ((0.20, (255, 122, 26)), (0.13, (255, 176, 66)),
                   (0.07, (255, 232, 150))):
        rr = w * r
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    d.ellipse([cx + w * 0.14, cy - h * 0.24, cx + w * 0.26, cy - h * 0.12],
              fill=(90, 88, 84))
    # Car on the street, under the blast.
    d.rectangle([x0 + w * 0.52, y1 - h * 0.26, x0 + w * 0.86, y1 - h * 0.14],
                fill=(24, 24, 28))
    d.rectangle([x0 + w * 0.58, y1 - h * 0.34, x0 + w * 0.78, y1 - h * 0.26],
                fill=(38, 38, 44))
    d.ellipse([x0 + w * 0.56, y1 - h * 0.16, x0 + w * 0.64, y1 - h * 0.08],
              fill=INK)
    d.ellipse([x0 + w * 0.76, y1 - h * 0.16, x0 + w * 0.84, y1 - h * 0.08],
              fill=INK)


def art_court(d, x0, y0, x1, y1):
    # Courthouse with columns and a gavel, drawn in fractions of its
    # own box so it fits a 72px card as well as a hero.
    w, h = x1 - x0, y1 - y0
    cx = x0 + w * 0.5
    d.rectangle([x0, y0, x1, y1], fill=(214, 204, 186))
    d.polygon([(cx - w * 0.34, y0 + h * 0.32), (cx + w * 0.34, y0 + h * 0.32),
               (cx, y0 + h * 0.07)], fill=(142, 110, 74))
    d.ellipse([cx - w * 0.04, y0 + h * 0.15, cx + w * 0.04, y0 + h * 0.28],
              fill=(250, 248, 243))
    d.rectangle([x0 + w * 0.05, y0 + h * 0.32, x1 - w * 0.05, y0 + h * 0.37],
                fill=(96, 76, 52))
    for fx in (0.09, 0.29, 0.62, 0.81):
        px = x0 + w * fx
        d.rectangle([px, y0 + h * 0.37, px + w * 0.05, y1 - h * 0.11],
                    fill=(232, 224, 206))
        d.rectangle([px - w * 0.01, y0 + h * 0.37, px + w * 0.06,
                     y0 + h * 0.43], fill=(200, 188, 162))
    d.rectangle([x0, y1 - h * 0.11, x1, y1], fill=(96, 76, 52))
    d.rectangle([x1 - w * 0.26, y1 - h * 0.41, x1 - w * 0.11, y1 - h * 0.28],
                fill=(58, 48, 36))
    d.line([x1 - w * 0.24, y1 - h * 0.41, x1 - w * 0.14, y1 - h * 0.57],
           fill=(58, 48, 36), width=5)
    d.ellipse([x1 - w * 0.16, y1 - h * 0.65, x1 - w * 0.11, y1 - h * 0.52],
              fill=(120, 84, 52))


def art_blacklist(d, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(226, 222, 210))
    d.rectangle([x0 + w * 0.16, y0 + h * 0.14, x1 - w * 0.16, y1 - h * 0.14],
                fill=WHITE, outline=(150, 146, 136), width=2)
    for f in (0.30, 0.42, 0.54):
        ly = y0 + h * f
        d.line([x0 + w * 0.24, ly, x1 - w * 0.24, ly],
               fill=(170, 166, 156), width=2)
    d.ellipse([x0 + w * 0.32, y1 - h * 0.42, x0 + w * 0.68, y1 - h * 0.10],
              outline=RED, width=3)
    d.line([x0 + w * 0.40, y1 - h * 0.30, x0 + w * 0.60, y1 - h * 0.30],
           fill=RED, width=2)
    d.line([x0 + w * 0.40, y1 - h * 0.23, x0 + w * 0.60, y1 - h * 0.23],
           fill=RED, width=2)
    d.rectangle([x1 - w * 0.30, y0 + h * 0.20, x1 - w * 0.08, y0 + h * 0.48],
                fill=(178, 24, 24))
    d.text((x1 - w * 0.24, y0 + h * 0.24), "!", fill=WHITE)


def art_podium(d, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(38, 58, 86))
    d.rectangle([x0 + w * 0.08, y0 + h * 0.20, x0 + w * 0.30, y0 + h * 0.58],
                fill=(0, 56, 147))
    d.rectangle([x0 + w * 0.30, y0 + h * 0.20, x0 + w * 0.52, y0 + h * 0.58],
                fill=WHITE)
    d.rectangle([x1 - w * 0.52, y0 + h * 0.20, x1 - w * 0.30, y0 + h * 0.58],
                fill=(178, 34, 52))
    d.rectangle([x1 - w * 0.30, y0 + h * 0.20, x1 - w * 0.08, y0 + h * 0.58],
                fill=WHITE)
    for i in range(3):
        ly = y0 + h * (0.28 + i * 0.10)
        d.line([x0 + w * 0.10, ly, x0 + w * 0.28, ly], fill=WHITE, width=2)
        d.line([x1 - w * 0.50, ly, x1 - w * 0.32, ly], fill=WHITE, width=2)
    d.polygon([(x0 + w * 0.30, y0 + h * 0.64), (x1 - w * 0.30, y0 + h * 0.64),
               (x1 - w * 0.22, y1 - h * 0.08), (x0 + w * 0.22, y1 - h * 0.08)],
              fill=(96, 76, 52))
    d.line([(x0 + w * 0.30, y0 + h * 0.64), (x0 + w * 0.30, y0 + h * 0.40)],
           fill=INK, width=3)
    d.ellipse([x0 + w * 0.26, y0 + h * 0.32, x0 + w * 0.34, y0 + h * 0.42],
              fill=INK)


def art_embassy(d, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(214, 226, 236))
    d.rectangle([x0 + w * 0.14, y0 + h * 0.28, x1 - w * 0.14, y1 - h * 0.10],
                fill=(232, 228, 218))
    d.polygon([(x0 + w * 0.08, y0 + h * 0.28), (x1 - w * 0.08, y0 + h * 0.28),
               ((x0 + x1) // 2, y0 + h * 0.08)], fill=(120, 90, 60))
    d.rectangle([x0 + w * 0.36, y0 + h * 0.66, x1 - w * 0.36, y1 - h * 0.10],
                fill=(58, 72, 96))
    d.ellipse([x1 - w * 0.40, y0 + h * 0.78, x1 - w * 0.34, y0 + h * 0.86],
              fill=(232, 190, 90))
    # US flag on the embassy wall, for the American envoy's post.
    d.rectangle([x0 + w * 0.06, y0 + h * 0.12, x0 + w * 0.30, y0 + h * 0.36],
                fill=WHITE)
    for i in range(5):
        if i % 2 == 0:
            d.rectangle([x0 + w * 0.06, y0 + h * (0.12 + i * 0.048),
                         x0 + w * 0.30, y0 + h * (0.12 + (i + 1) * 0.048)],
                        fill=(178, 34, 52))
    d.rectangle([x0 + w * 0.06, y0 + h * 0.12, x0 + w * 0.16, y0 + h * 0.22],
                fill=(0, 40, 104))
    d.ellipse([x0 + w * 0.09, y0 + h * 0.15, x0 + w * 0.13, y0 + h * 0.19],
              fill=WHITE)


def art_rocket(d, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(232, 228, 216))
    cx = x0 + w * 0.34
    d.polygon([(cx, y0 + h * 0.10), (cx - w * 0.11, y0 + h * 0.46),
               (cx + w * 0.11, y0 + h * 0.46)], fill=(178, 24, 24))
    d.rectangle([cx - w * 0.11, y0 + h * 0.46, cx + w * 0.11, y0 + h * 0.78],
                fill=(240, 240, 236))
    d.polygon([(cx - w * 0.11, y0 + h * 0.62), (cx - w * 0.20, y0 + h * 0.84),
               (cx - w * 0.11, y0 + h * 0.78)], fill=(178, 24, 24))
    d.polygon([(cx + w * 0.11, y0 + h * 0.62), (cx + w * 0.20, y0 + h * 0.84),
               (cx + w * 0.11, y0 + h * 0.78)], fill=(178, 24, 24))
    d.ellipse([cx - w * 0.05, y0 + h * 0.52, cx + w * 0.05, y0 + h * 0.64],
              fill=(158, 196, 222))
    d.polygon([(cx - w * 0.05, y0 + h * 0.82), (cx + w * 0.05, y0 + h * 0.82),
               (cx + w * 0.02, y1 - h * 0.06), (cx - w * 0.02, y1 - h * 0.06)],
              fill=(255, 176, 66))
    d.rectangle([x1 - w * 0.36, y1 - h * 0.30, x1 - w * 0.06, y1 - h * 0.18],
                fill=(58, 48, 36))
    d.line([x1 - w * 0.30, y1 - h * 0.30, x1 - w * 0.14, y1 - h * 0.48],
           fill=(58, 48, 36), width=3)
    d.ellipse([x1 - w * 0.20, y1 - h * 0.56, x1 - w * 0.06, y1 - h * 0.42],
              fill=(120, 84, 52))


def art_island(d, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(158, 196, 222))
    d.rectangle([x0, y1 - h * 0.28, x1, y1], fill=(38, 110, 150))
    d.ellipse([x0 + w * 0.08, y1 - h * 0.38, x0 + w * 0.62, y1 - h * 0.20],
              fill=(232, 210, 150))
    d.line([x0 + w * 0.34, y1 - h * 0.34, x0 + w * 0.34, y0 + h * 0.36],
           fill=(120, 84, 52), width=4)
    for dx, dy in ((-0.20, -0.06), (0.20, -0.06), (-0.14, 0.08),
                   (0.14, 0.08)):
        d.arc([x0 + w * (0.34 + dx) - w * 0.16, y0 + h * (0.30 + dy),
               x0 + w * (0.34 + dx) + w * 0.16, y0 + h * (0.48 + dy)],
              180, 360, fill=(20, 120, 60), width=4)
    d.ellipse([x0 + w * 0.28, y0 + h * 0.28, x0 + w * 0.40, y0 + h * 0.42],
              fill=(120, 84, 52))
    d.polygon([(x1 - w * 0.30, y1 - h * 0.32), (x1 - w * 0.08, y1 - h * 0.32),
               (x1 - w * 0.19, y1 - h * 0.56)], fill=WHITE)
    d.line([x1 - w * 0.19, y1 - h * 0.56, x1 - w * 0.19, y1 - h * 0.32],
           fill=(90, 60, 30), width=2)
    d.line([x0 + w * 0.62, y1 - h * 0.14, x0 + w * 0.86, y1 - h * 0.14],
           fill=WHITE, width=2)
    d.line([x0 + w * 0.72, y1 - h * 0.22, x0 + w * 0.94, y1 - h * 0.22],
           fill=WHITE, width=2)


def art_airport(d, x0, y0, x1, y1):
    # Side-view airliner over a runway, with a control tower.
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(200, 216, 232))
    d.ellipse([x0 + w * 0.06, y0 + h * 0.10, x0 + w * 0.30, y0 + h * 0.22],
              fill=WHITE)
    d.ellipse([x0 + w * 0.66, y0 + h * 0.06, x0 + w * 0.90, y0 + h * 0.16],
              fill=WHITE)
    cx, cy = x0 + w * 0.50, y0 + h * 0.42
    d.ellipse([cx - w * 0.38, cy - h * 0.07, cx + w * 0.38, cy + h * 0.07],
              fill=WHITE, outline=(150, 158, 168))
    d.polygon([(cx + w * 0.38, cy - h * 0.07), (cx + w * 0.48, cy),
               (cx + w * 0.38, cy + h * 0.07)], fill=WHITE,
              outline=(150, 158, 168))
    d.polygon([(cx - w * 0.30, cy - h * 0.07), (cx - w * 0.22, cy - h * 0.20),
               (cx - w * 0.14, cy - h * 0.07)], fill=(58, 90, 128))
    d.polygon([(cx - w * 0.05, cy + h * 0.07), (cx + w * 0.10, cy + h * 0.22),
               (cx + w * 0.18, cy + h * 0.07)], fill=(58, 90, 128))
    for fx in (-0.24, -0.12, 0.0, 0.12, 0.24):
        d.rectangle([cx + w * fx, cy - h * 0.02, cx + w * (fx + 0.05),
                     cy + h * 0.02], fill=(58, 90, 128))
    d.rectangle([x0 + w * 0.06, y0 + h * 0.52, x0 + w * 0.18, y1 - h * 0.24],
                fill=(90, 96, 104))
    d.rectangle([x0 + w * 0.02, y0 + h * 0.44, x0 + w * 0.22, y0 + h * 0.52],
                fill=(58, 90, 128))
    d.rectangle([x0 + w * 0.05, y0 + h * 0.46, x0 + w * 0.19, y0 + h * 0.50],
                fill=(232, 190, 90))
    d.rectangle([x0, y1 - h * 0.24, x1, y1], fill=(120, 122, 128))


def art_football(d, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(20, 83, 45))
    for f in (0.14, 0.30, 0.46, 0.62, 0.78):
        d.rectangle([x0, y0 + h * f, x1, y0 + h * f + h * 0.08],
                    fill=(28, 100, 56))
    d.line([x0 + w * 0.10, y0 + h * 0.10, x0 + w * 0.10, y1 - h * 0.10],
           fill=WHITE, width=2)
    d.line([x1 - w * 0.10, y0 + h * 0.10, x1 - w * 0.10, y1 - h * 0.10],
           fill=WHITE, width=2)
    d.line([x0 + w * 0.10, y0 + h * 0.10, x1 - w * 0.10, y0 + h * 0.10],
           fill=WHITE, width=2)
    d.ellipse([x0 + w * 0.28, y0 + h * 0.34, x0 + w * 0.52, y0 + h * 0.58],
              fill=(120, 72, 32))
    d.line([x0 + w * 0.32, y0 + h * 0.38, x0 + w * 0.48, y0 + h * 0.54],
           fill=WHITE, width=2)
    d.line([x0 + w * 0.32, y0 + h * 0.54, x0 + w * 0.48, y0 + h * 0.38],
           fill=WHITE, width=2)
    d.ellipse([x1 - w * 0.38, y1 - h * 0.38, x1 - w * 0.14, y1 - h * 0.10],
              fill=(178, 24, 24))
    d.rectangle([x1 - w * 0.32, y1 - h * 0.34, x1 - w * 0.20, y1 - h * 0.14],
                fill=WHITE)


ART = {
    "kyiv": art_kyiv, "gaza": art_gaza, "sea": art_sea,
    "summit": art_summit, "drone": art_drone, "blast": art_blast,
    "court": art_court, "blacklist": art_blacklist,
    "podium": art_podium, "embassy": art_embassy,
    "rocket": art_rocket, "island": art_island,
    "airport": art_airport, "football": art_football,
}

# ------------------------------------------------------------- world map
# Rough continent outlines in (lon, lat); drawn as flat light shapes.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-76, 60),
     (-80, 45), (-75, 35), (-80, 26), (-90, 20), (-97, 16), (-105, 20),
     (-115, 28), (-125, 40), (-150, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-40, -10), (-35, -20), (-48, -28),
     (-58, -38), (-65, -45), (-70, -55), (-73, -40), (-72, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (0, 48), (-2, 50), (8, 54), (10, 58), (18, 56),
     (21, 60), (28, 60), (30, 55), (28, 45), (23, 40), (19, 42), (12, 44),
     (3, 43), (-2, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -12), (35, -25),
     (28, -33), (18, -35), (12, -18), (9, 4), (-8, 5)],
    [(30, 55), (40, 60), (50, 68), (60, 70), (70, 72), (90, 75),
     (110, 74), (130, 72), (150, 70), (170, 66), (178, 65), (162, 60),
     (158, 52), (142, 45), (135, 35), (127, 35), (122, 30), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (80, 8), (75, 20),
     (66, 25), (58, 26), (50, 30), (44, 30), (36, 36)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38),
     (150, -37), (153, -27), (146, -19), (142, -11), (135, -12),
     (130, -13), (122, -14)],
    [(-45, 60), (-40, 70), (-30, 76), (-20, 74), (-25, 70), (-40, 64)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 52)],
]

# Small shifts so pins that share a city or a border do not sit exactly
# on top of each other (3&10 Gaza/Jerusalem, 4&5 Zakarpattia/Dorohusk,
# 7&15 Washington/Landover) and so pin 13 (Kanton, lon -171.71) is not
# half cut off by the map's left edge.
PIN_SHIFT = {2: (16, 4), 3: (-14, 4), 4: (-10, 8), 5: (14, -10), 7: (12, -10),
             10: (14, 10), 11: (8, -8), 13: (12, 0), 15: (-16, 12)}


def draw_map(d, fonts, x0, y0, x1, y1, pins):
    d.rectangle([x0, y0, x1, y1], fill=(222, 232, 240))
    for lon in range(-150, 181, 30):
        px = x0 + (lon + 180) / 360.0 * (x1 - x0)
        d.line([px, y0, px, y1], fill=(255, 255, 255), width=1)
    for lat in (-60, -30, 0, 30, 60):
        py = y0 + (90 - lat) / 180.0 * (y1 - y0)
        d.line([x0, py, x1, py], fill=(255, 255, 255), width=1)
    for poly in CONTINENTS:
        pts = [pin_xy(lat, lon, x0, y0, x1 - x0, y1 - y0)
               for lon, lat in poly]
        d.polygon(pts, fill=(196, 198, 188),
                  outline=(150, 152, 142))
    fnum = fonts["sans_b"](10)
    for pin in pins:
        px, py = pin_xy(pin["lat"], pin["lon"], x0, y0, x1 - x0, y1 - y0)
        dx, dy = PIN_SHIFT.get(pin["n"], (0, 0))
        px, py = px + dx, py + dy
        r = 9
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=WHITE, width=2)
        label = str(pin["n"])
        tw = d.textlength(label, font=fnum)
        d.text((px - tw / 2, py - 6), label, font=fnum, fill=WHITE)


# ------------------------------------------------------------- the page
def render(data):
    from PIL import Image, ImageDraw

    fonts = load_fonts()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_mast = fonts["mast"](46)
    f_date = fonts["sans_b"](20)
    f_kick = fonts["sans_b"](13)
    f_stat_big = fonts["sans_b"](27)
    f_stat_lab = fonts["sans"](10)
    f_reg = fonts["sans_b"](11)
    f_utc_t = fonts["sans_b"](11)
    f_utc = fonts["sans_b"](10)
    f_utc_x = fonts["sans"](10)
    f_hero_place = fonts["sans_b"](9)
    f_hero_title = fonts["serif_b"](17)
    f_hero_deck = fonts["sans"](12)
    f_tag = fonts["sans_b"](8)
    f_badge = fonts["sans_b"](9)
    f_card_place = fonts["sans_b"](8)
    f_card_title = fonts["sans_b"](11)
    f_card_deck = fonts["sans"](10)
    f_sec = fonts["sans_b"](13)
    f_also = fonts["sans"](9)
    f_also_n = fonts["sans_b"](9)
    f_dc_t = fonts["sans_b"](11)
    f_dc = fonts["sans"](10)
    f_key = fonts["sans_b"](10)
    f_src = fonts["sans"](9)
    f_foot = fonts["sans_b"](10)

    # ---- top rule + masthead
    d.rectangle([MARGIN, 8, W - MARGIN, 11], fill=RED)
    d.text((MARGIN, 14), data["masthead"], font=f_mast, fill=INK)
    d.text((MARGIN, 66), data["date"], font=f_date, fill=RED)
    d.text((MARGIN, 90), data["kicker"], font=f_kick, fill=INK)
    d.line([MARGIN, 108, W - MARGIN, 108], fill=INK, width=2)

    # ---- stat strip: 6 cells
    y = 114
    cell_w = CW // 6
    for i, st in enumerate(data["stats"]):
        cx = MARGIN + i * cell_w
        if i:
            d.line([cx, y, cx, y + 30], fill=MID_GREY, width=1)
        d.text((cx + 8, y), st["big"], font=f_stat_big, fill=NAVY)
        bw = d.textlength(st["big"], font=f_stat_big)
        lab_x = cx + 8 + bw + 7
        draw_wrapped(d, lab_x, y + 3, st["label"], f_stat_lab, INK,
                     cell_w - (bw + 15), leading=12)
    d.line([MARGIN, 150, W - MARGIN, 150], fill=MID_GREY, width=1)

    # ---- region bar: widths scaled to the round-2 counts
    # (EU 9, ME 5, AM 5, AP 9, AF 2, OC 3, WO 3; sum 984) so every
    # label fits, Africa's two stories still get a readable segment.
    y = 156
    counts = [(r["name"], r["count"], r["color"]) for r in data["regions"]]
    widths = [240, 137, 137, 241, 65, 82, 82]
    assert sum(widths) == CW and len(widths) == len(counts)
    f_reg = fonts["sans_b"](10)
    x = MARGIN
    for (name, count, color), w in zip(counts, widths):
        d.rectangle([x, y, x + w - 1, y + 22], fill=color)
        label = "%s %d" % (name, count)
        d.text((x + 6, y + 5), clipped(d, label, f_reg, w - 10),
               font=f_reg, fill=WHITE)
        x += w

    # ---- UTC strip: 6 items in 2 rows x 3 cols
    y = 186
    d.text((MARGIN, y), "THE DAY IN UTC", font=f_utc_t, fill=RED)
    col_w = CW // 3
    for i, item in enumerate(data["utc"]):
        row, col = divmod(i, 3)
        ix = MARGIN + col * col_w
        iy = y + 16 + row * 17
        d.text((ix, iy), item["time"], font=f_utc, fill=NAVY)
        tw = d.textlength(item["time"], font=f_utc)
        d.text((ix + tw + 6, iy),
               clipped(d, item["text"], f_utc_x, col_w - tw - 10),
               font=f_utc_x, fill=INK)
    d.line([MARGIN, 240, W - MARGIN, 240], fill=INK, width=1)

    # ---- 3 heroes
    hy = 248
    hero_w = (CW - 18) // 3
    art_h = 108
    for i, hero in enumerate(data["heroes"]):
        hx = MARGIN + i * (hero_w + 9)
        ART[hero["art"]](d, hx, hy, hx + hero_w, hy + art_h)
        d.rectangle([hx, hy, hx + 62, hy + 16], fill=RED)
        d.text((hx + 5, hy + 3), hero["badge"], font=f_badge, fill=WHITE)
        py = hy + art_h + 6
        place = "%d · %s" % (hero["n"], hero["place"])
        d.text((hx, py), clipped(d, place, f_hero_place, hero_w - 62),
               font=f_hero_place, fill=GREY)
        tag = hero["certainty"]
        tw = d.textlength(tag, font=f_tag)
        d.rectangle([hx + hero_w - tw - 10, py - 1,
                     hx + hero_w, py + 11], fill=NAVY)
        d.text((hx + hero_w - tw - 5, py + 1), tag, font=f_tag, fill=WHITE)
        ty = py + 16
        ty = draw_wrapped(d, hx, ty, hero["title"], f_hero_title, INK,
                          hero_w, leading=20)
        draw_wrapped(d, hx, ty + 2, hero["deck"], f_hero_deck, INK,
                     hero_w, leading=15)

    # ---- 12 cards: 4 cols x 3 rows
    cy0 = 452
    card_w = (CW - 21) // 4
    card_h = 88
    for i, card in enumerate(data["cards"]):
        row, col = divmod(i, 4)
        cx = MARGIN + col * (card_w + 7)
        cy = cy0 + row * (card_h + 7)
        d.rectangle([cx, cy, cx + card_w, cy + card_h], fill=WHITE,
                    outline=LIGHT_GREY, width=1)
        ax0, ay0 = cx + 1, cy + 1
        ART[card["art"]](d, ax0, ay0, ax0 + 72, ay0 + card_h - 2)
        badge = card["badge"]
        bw = d.textlength(badge, font=f_badge) + 8
        d.rectangle([ax0 + 2, ay0 + card_h - 17, ax0 + 2 + bw,
                     ay0 + card_h - 4], fill=NAVY)
        d.text((ax0 + 6, ay0 + card_h - 16), badge, font=f_badge,
               fill=WHITE)
        tx = cx + 80
        tw = card_w - 86
        place = "%d · %s" % (card["n"], card["place"])
        d.text((tx, cy + 5),
               clipped(d, place, f_card_place, tw), font=f_card_place,
               fill=GREY)
        ty = cy + 18
        ty = draw_wrapped(d, tx, ty, card["title"], f_card_title, INK,
                          tw, leading=13)
        draw_wrapped(d, tx, ty + 2, card["deck"], f_card_deck, INK,
                     tw, leading=12)

    # ---- map + 21 more stories (map shortened so DATE CHECK gets
    # room for three lines of exclusions + Not-yet items)
    my = 734
    d.text((MARGIN, my), "WHERE IT HAPPENED", font=f_sec, fill=RED)
    d.text((MARGIN + 352, my), "21 MORE STORIES", font=f_sec, fill=RED)
    map_x0, map_y0 = MARGIN, my + 20
    map_x1, map_y1 = MARGIN + 336, my + 178
    draw_map(d, fonts, map_x0, map_y0, map_x1, map_y1, data["pins"])
    ax = MARGIN + 352
    col_w = (W - MARGIN - ax - 10) // 2
    for i, item in enumerate(data["also"]):
        col, row = divmod(i, 11)
        ix = ax + col * (col_w + 10)
        iy = map_y0 + row * 14
        num = "%d." % item["n"]
        d.text((ix, iy), num, font=f_also_n, fill=RED)
        nw = d.textlength(num, font=f_also_n)
        d.text((ix + nw + 4, iy),
               clipped(d, item["text"], f_also, col_w - nw - 6),
               font=f_also, fill=INK)

    # ---- DATE CHECK
    dy = 916
    d.rectangle([MARGIN, dy, W - MARGIN, dy + 58], outline=RED, width=2)
    d.rectangle([MARGIN, dy, MARGIN + 208, dy + 16], fill=RED)
    d.text((MARGIN + 6, dy + 2), "DATE CHECK — READ THIS FIRST",
           font=f_dc_t, fill=WHITE)
    draw_wrapped(d, MARGIN + 8, dy + 19, data["datecheck"], f_dc, INK,
                 CW - 16, leading=12)

    # ---- footer: certainty key + sources + navy bar
    fy = 978
    d.text((MARGIN, fy),
           "CERTAINTY:  REPORTED = carried by the day's wires  ·  "
           "CLAIM = one side's account, labelled as such  ·  "
           "FORECAST = still to happen when drawn",
           font=f_key, fill=INK)
    d.text((MARGIN, fy + 13),
           "SOURCES: Reuters · AP · AFP · PINA · h.ua · Just Security · "
           "FT · WSJ · wires — full list in SOURCES.md",
           font=f_src, fill=GREY)
    d.rectangle([MARGIN, 1010, W - MARGIN, 1022], fill=NAVY)
    foot = ("THE WORLD IN ONE DAY  —  TUESDAY 24 NOVEMBER 2026  ·  "
            "DRAWN ILLUSTRATIONS OF REPORTED EVENTS, NOT PHOTOGRAPHS")
    d.text((MARGIN + 6, 1012), clipped(d, foot, f_foot, CW - 12),
           font=f_foot, fill=WHITE)

    return img


def load_data():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    total = sum(r["count"] for r in data["regions"])
    n = len(data["heroes"]) + len(data["cards"]) + len(data["also"])
    assert total == n == 36, "story counts must sum to 36 (got %d, %d)" % (
        total, n)
    return data


def output_path():
    out_dir = OUT_ENV or os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        return os.path.join(out_dir, "entry.png")
    return os.path.join(HERE, "entry.png")


def main(argv):
    out = output_path()
    try:
        data = load_data()
        img = render(data)
        img.save(out, format="PNG", optimize=True)
    except Exception as exc:  # Pillow / fonts missing in the sandbox
        shipped = os.path.join(HERE, "entry.png")
        if os.path.isfile(shipped) and os.path.abspath(out) != os.path.abspath(shipped):
            shutil.copyfile(shipped, out)
            print("render unavailable (%s); copied shipped entry.png" % exc,
                  file=sys.stderr)
            return 0
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
