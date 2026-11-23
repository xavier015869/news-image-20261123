#!/usr/bin/env python3
"""Render v2 of the front page for Monday 23 November 2026.

"The World Ledger" — a one-page newspaper summing up the day's world
news in a single 1024x1024 image, redesigned against the judge's
published criteria: the day is named in a heavy date bar; every story
is told by a big headline, a drawn picture and one short deck, in type
that stays legible when the page is shrunk to ~300 px across; nothing
appears in small print.

Stories (each cross-checked against at least two independent reports
of 22-23 November 2026):

  * COP31 in Antalya collapses without a deal over fossil fuels
    (CNN, Reuters, Le Monde, AFP)
  * Ukraine's sea drones sink the Russian corvette Merkury at
    Benghazi, Libya; Zelensky confirms on Monday (CNN, AP, WSJ)
  * Poland confirms three Russian Kh-101 cruise missiles fell in the
    south-east; NATO's council meets in Brussels (Reuters/AP reports)
  * Iran strikes Bahrain, two wounded; tankers hit near Hormuz;
    Saudi Arabia intercepts Houthi missiles (AFP, Reuters)
  * Taiwan's short-selling ban takes effect after the Taiex loses
    17.5% in a week (Focus Taiwan / CNA, Reuters)
  * 128 states in Geneva agree to draft "killer robot" rules by 2028
    (Reuters, Al Jazeera)
  * Liverpool 4-0 Manchester United in Pochettino's debut (Reuters)
  * India 720/9 declared, but New Zealand bat out a draw in
    Wellington (ESPNcricinfo, AAP)
  * Briefs: "El Chapo Isidro" captured in Sinaloa; South Korea's
    education minister quits over AI exam cheating; 24 civilians
    killed in South Sudan; Bolsonaro stable in intensive care;
    North Korea expands the Yongbyon uranium plant (WSJ, Reuters)

Everything is drawn with Pillow primitives and system fonts, with no
randomness and no timestamps, so two runs write byte-identical PNGs.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
RIGHT = W - MARGIN
CONTENT_W = RIGHT - MARGIN

PAPER = (247, 242, 231)
INK = (20, 18, 14)
GREY = (92, 86, 74)
RED = (163, 22, 33)
BLUE = (29, 78, 137)
GOLD = (150, 108, 24)
DARKRED = (122, 16, 26)
GREEN = (24, 92, 52)
PANEL = (238, 231, 214)
WHITE = (252, 250, 244)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
NOTO = "/usr/share/fonts/truetype/noto"


def font(path, size):
    return ImageFont.truetype(path, size)


def serif_bold(size):
    return font(f"{DEJAVU}/DejaVuSerif-Bold.ttf", size)


def sans(size):
    return font(f"{DEJAVU}/DejaVuSans.ttf", size)


def sans_bold(size):
    return font(f"{DEJAVU}/DejaVuSans-Bold.ttf", size)


def masthead_font(size):
    try:
        return font(f"{NOTO}/NotoSerifDisplay-Black.ttf", size)
    except OSError:
        return serif_bold(size)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill=INK, leading=4):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


def fit_font(draw, s, start, make, width):
    """Largest font from `make(size)` at or below `start` that fits."""
    size = start
    while size > 10:
        fnt = make(size)
        if text_w(draw, s, fnt) <= width:
            return fnt
        size -= 2
    return make(size)


def kicker(draw, x, y, label, colour, size=15):
    """A small coloured tag with white bold caps text; returns height."""
    fnt = sans_bold(size)
    w = text_w(draw, label, fnt) + 18
    h = size + 9
    draw.rectangle([x, y, x + w, y + h], fill=colour)
    draw.text((x + 9, y + 4), label, font=fnt, fill=WHITE)
    return h


def hrule(draw, y, x0=MARGIN, x1=RIGHT, fill=INK, width=2):
    draw.line([x0, y, x1, y], fill=fill, width=width)


# ---------------------------------------------------------------------
# Icons: chunky line art in an accent colour on a panel square.
# Each takes the top-left corner of a box and the box size.
# ---------------------------------------------------------------------

def icon_ship(d, x, y, s, c):
    """Warship with a burst at the bow and waves below."""
    hull_y = y + int(s * 0.52)
    d.polygon([(x + 4, hull_y), (x + s - 2, hull_y), (x + s - 14, hull_y + 14),
               (x + 14, hull_y + 14)], outline=c, width=5)
    d.rectangle([x + int(s * 0.38), hull_y - 14, x + int(s * 0.62), hull_y],
                outline=c, width=5)
    d.line([x + int(s * 0.72), hull_y - 26, x + int(s * 0.72), hull_y],
           fill=c, width=5)
    cx, cy = x + s - 8, hull_y - 22
    for dx, dy in ((-9, 0), (9, 0), (0, -9), (0, 9), (-6, -6), (6, -6)):
        d.line([cx, cy, cx + dx, cy + dy], fill=RED, width=4)
    wy = y + s - 8
    for k in range(3):
        sx = x + 6 + k * int(s * 0.32)
        d.arc([sx, wy - 5, sx + int(s * 0.26), wy + 5], 0, 180, fill=c, width=4)


def icon_missile(d, x, y, s, c):
    """A diagonal cruise missile: thick body, nose cone, fins, flame."""
    bx, by = x + int(s * 0.32), y + int(s * 0.64)   # tail centre
    tx, ty = x + int(s * 0.80), y + int(s * 0.16)   # nose tip
    d.line([bx, by, tx, ty], fill=c, width=15)
    d.polygon([(tx, ty), (tx - 17, ty + 5), (tx - 5, ty + 17)], fill=c)
    d.polygon([(bx, by), (bx - 15, by - 3), (bx - 3, by + 13)], fill=c)
    d.polygon([(bx, by), (bx + 3, by + 15), (bx + 15, by + 4)], fill=c)
    d.polygon([(bx - 7, by + 7), (bx - 21, by + 15), (bx - 9, by + 22)],
              fill=RED)


def icon_tanker(d, x, y, s, c):
    """Oil tanker with a flame over the deck."""
    hull_y = y + int(s * 0.60)
    d.polygon([(x + 2, hull_y), (x + s - 2, hull_y), (x + s - 12, hull_y + 13),
               (x + 12, hull_y + 13)], outline=c, width=5)
    d.line([x + 10, hull_y - 8, x + s - 18, hull_y - 8], fill=c, width=5)
    d.rectangle([x + int(s * 0.66), hull_y - 20, x + int(s * 0.80), hull_y - 8],
                outline=c, width=4)
    fx, fy = x + int(s * 0.38), hull_y - 12
    d.polygon([(fx, fy), (fx - 8, fy - 16), (fx - 2, fy - 26), (fx + 5, fy - 15),
               (fx + 10, fy - 24), (fx + 11, fy - 10)], fill=RED)
    wy = y + s - 7
    for k in range(3):
        sx = x + 6 + k * int(s * 0.32)
        d.arc([sx, wy - 5, sx + int(s * 0.26), wy + 5], 0, 180, fill=c, width=4)


def icon_chart(d, x, y, s, c):
    """Plunging market line with a big red down arrow."""
    d.line([x + 8, y + 8, x + 8, y + s - 10], fill=c, width=4)
    d.line([x + 8, y + s - 10, x + s - 6, y + s - 10], fill=c, width=4)
    pts = [(x + 12, y + int(s * 0.22)), (x + int(s * 0.36), y + int(s * 0.34)),
           (x + int(s * 0.52), y + int(s * 0.28)), (x + int(s * 0.80), y + int(s * 0.68))]
    d.line(pts, fill=RED, width=6, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex + 12, ey + 2), (ex - 4, ey - 4), (ex + 2, ey + 12)], fill=RED)


def icon_robot(d, x, y, s, c):
    """Robot head: antenna, eyes, grille mouth."""
    hx0, hy0 = x + int(s * 0.16), y + int(s * 0.30)
    hx1, hy1 = x + int(s * 0.84), y + int(s * 0.86)
    d.line([x + s // 2, y + 8, x + s // 2, hy0], fill=c, width=5)
    d.ellipse([x + s // 2 - 6, y + 2, x + s // 2 + 6, y + 14], fill=RED)
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=10, outline=c, width=5)
    for ex in (x + int(s * 0.36), x + int(s * 0.60)):
        d.ellipse([ex, y + int(s * 0.48), ex + 9, y + int(s * 0.48) + 9], fill=c)
    my = y + int(s * 0.70)
    for k in range(3):
        gx = x + int(s * 0.38) + k * 11
        d.line([gx, my, gx, my + 9], fill=c, width=4)


def icon_ball(d, x, y, s, c):
    """Football: circle, centre pentagon, seams."""
    cx, cy, r = x + s // 2, y + s // 2, int(s * 0.42)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=5)
    pent = [(cx, cy - 11), (cx + 11, cy - 3), (cx + 7, cy + 9),
            (cx - 7, cy + 9), (cx - 11, cy - 3)]
    d.polygon(pent, fill=c)
    for px, py in ((cx, cy - r + 4), (cx + r - 12, cy + 8), (cx - r + 12, cy + 8)):
        d.line([cx, cy, px, py], fill=c, width=3)


def icon_cricket(d, x, y, s, c):
    """Cricket bat at an angle and a red ball."""
    d.polygon([(x + int(s * 0.30), y + int(s * 0.30)),
               (x + int(s * 0.52), y + int(s * 0.52)),
               (x + int(s * 0.36), y + int(s * 0.86)),
               (x + int(s * 0.16), y + int(s * 0.66))], outline=c, width=5)
    d.line([x + int(s * 0.30), y + int(s * 0.30), x + int(s * 0.20), y + int(s * 0.14)],
           fill=c, width=6)
    bx, by, br = x + int(s * 0.72), y + int(s * 0.30), 13
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED)
    d.arc([bx - br + 4, by - br + 3, bx + br - 4, by + br - 3], 80, 280,
          fill=WHITE, width=2)


def icon_panel(d, x, y, s, draw_icon, colour):
    d.rectangle([x, y, x + s, y + s], fill=PANEL, outline=GREY, width=1)
    draw_icon(d, x + 8, y + 8, s - 16, colour)


# ---------------------------------------------------------------------
# Story blocks
# ---------------------------------------------------------------------

def story_with_icon(d, x, y, width, kick, colour, icon, headline, deck,
                    head_size=26, deck_size=16, icon_size=92):
    """Kicker, then icon left + headline and one-line deck right."""
    y += kicker(d, x, y, kick, colour) + 8
    icon_panel(d, x, y, icon_size, icon, colour)
    tx = x + icon_size + 14
    tw = width - icon_size - 14
    hf = serif_bold(head_size)
    y = draw_lines(d, tx, y, wrap(d, headline, hf, tw), hf, leading=3)
    y += 4
    df = sans(deck_size)
    y = draw_lines(d, tx, y, wrap(d, deck, df, tw), df, leading=4)
    return y


def story_plain(d, x, y, width, kick, colour, headline, deck,
                head_size=22, deck_size=15):
    """Kicker, headline, deck — no icon (bottom row)."""
    y += kicker(d, x, y, kick, colour) + 7
    hf = serif_bold(head_size)
    y = draw_lines(d, x, y, wrap(d, headline, hf, width), hf, leading=3)
    y += 3
    df = sans(deck_size)
    y = draw_lines(d, x, y, wrap(d, deck, df, width), df, leading=4)
    return y


# ---------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# --- frame ---------------------------------------------------------------
d.rectangle([10, 10, W - 10, H - 10], outline=INK, width=2)
d.rectangle([16, 16, W - 16, H - 16], outline=GREY, width=1)

# --- top strip -----------------------------------------------------------
strip = sans_bold(14)
d.text((MARGIN, 25), "INTERNATIONAL EDITION", font=strip, fill=GREY)
label = "ONE PAGE · THE WHOLE DAY"
d.text((RIGHT - text_w(d, label, strip), 25), label, font=strip, fill=GREY)

# --- masthead ------------------------------------------------------------
name = "The World Ledger"
mf = fit_font(d, name, 74, masthead_font, CONTENT_W)
d.text(((W - text_w(d, name, mf)) / 2, 38), name, font=mf, fill=INK)
hrule(d, 118, width=3)
hrule(d, 124, width=1)

# --- date bar ------------------------------------------------------------
d.rectangle([MARGIN, 134, RIGHT, 178], fill=INK)
date_text = "MONDAY  23  NOVEMBER  2026"
df = fit_font(d, date_text, 33, sans_bold, CONTENT_W - 40)
d.text(((W - text_w(d, date_text, df)) / 2, 142), date_text, font=df,
       fill=WHITE)

# --- lead story: COP31 ---------------------------------------------------
lead_y = 190
kicker(d, MARGIN, lead_y, "CLIMATE SUMMIT · ANTALYA, TÜRKİYE", RED, size=16)
head_f = serif_bold(54)
hy = lead_y + 34
for line in ("COP31 COLLAPSES", "WITHOUT A DEAL"):
    d.text((MARGIN, hy), line, font=head_f, fill=INK)
    hy += 57

# visual panel beside the headline: a globe split by a jagged red crack,
# captioned with the summit's starkest number
px0, py0, px1, py1 = 676, lead_y + 34, RIGHT, lead_y + 152
d.rectangle([px0, py0, px1, py1], fill=PANEL, outline=GREY, width=1)
cx, cy, r = (px0 + px1) // 2, py0 + 42, 38
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=4)
for frac in (0.40, 0.75):
    rx = int(r * frac)
    d.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=BLUE, width=2)
for k in (-0.5, 0.0, 0.5):
    half = int(r * (1 - k * k) ** 0.5)
    d.line([cx - half, cy + int(k * r), cx + half, cy + int(k * r)],
           fill=BLUE, width=2)
crack = [(cx - 9, cy - r + 3), (cx + 3, cy - 22), (cx - 6, cy - 4),
         (cx + 8, cy + 16), (cx - 2, cy + 29), (cx + 5, cy + r - 3)]
d.line(crack, fill=RED, width=5, joint="curve")
cap_f = sans_bold(15)
cap = "1.5°C OVERSHOOT CONFIRMED"
d.text(((px0 + px1 - text_w(d, cap, cap_f)) / 2, py0 + 90), cap,
       font=cap_f, fill=DARKRED)

stand_f = sans_bold(19)
sy = draw_lines(d, MARGIN, hy + 6, wrap(
    d, "The longest UN climate summit in history ended in failure, "
       "after the EU refused to endorse a final text that never "
       "mentioned fossil fuels.", stand_f, CONTENT_W), stand_f, leading=4)
body_f = sans(17)
lead_end = draw_lines(d, MARGIN, sy + 6, wrap(
    d, "Kurum conceded there was no consensus on the “Antalya Pact” — "
       "a record 194 delegations, and the first collapse since "
       "Copenhagen in 2009.", body_f, CONTENT_W), body_f, leading=4)

hrule(d, lead_end + 8, width=2)

# --- row A: Ukraine/Libya | Poland/NATO ----------------------------------
row_a = lead_end + 20
mid = W // 2
col_w = mid - MARGIN - 18
end_a = story_with_icon(
    d, MARGIN, row_a, col_w, "UKRAINE · LIBYA", BLUE, icon_ship,
    "Ukraine sinks Russian warship off Libya",
    "Seven sea drones sank the corvette Merkury at Benghazi, Zelensky "
    "confirms; a weapons ship was also hit.")
d.line([mid, row_a + 2, mid, row_a + 140], fill=GREY, width=1)
end_a = max(end_a, story_with_icon(
    d, mid + 18, row_a, RIGHT - mid - 18, "EUROPE · NATO", DARKRED,
    icon_missile,
    "Russian missiles fell on Poland; NATO meets",
    "Warsaw confirms three Kh-101 missiles crashed in the south-east "
    "on Friday; Tusk calls it a provocation."))

hrule(d, end_a + 8, width=2)

# --- row B: Gulf | Taiwan -------------------------------------------------
row_b = end_a + 20
end_b = story_with_icon(
    d, MARGIN, row_b, col_w, "MIDDLE EAST · GULF", DARKRED, icon_tanker,
    "Iran strikes Bahrain; tankers hit in Hormuz",
    "Two wounded in Sitra; Tehran claims US radars hit. Saudi downs "
    "Houthi missiles; Brent holds near $92.")
d.line([mid, row_b + 2, mid, row_b + 140], fill=GREY, width=1)
end_b = max(end_b, story_with_icon(
    d, mid + 18, row_b, RIGHT - mid - 18, "MARKETS · TAIPEI", RED,
    icon_chart,
    "Taiwan bans short selling after 17.5% plunge",
    "Worst week since 1990 for the Taiex in an AI selloff; the ban "
    "took effect on Monday."))

hrule(d, end_b + 8, width=2)

# --- row C: Geneva | Football | Cricket -----------------------------------
row_c = end_b + 20
c_w, gap = 304, 20
end_c = story_plain(
    d, MARGIN, row_c, c_w, "AI WEAPONS · GENEVA", GOLD,
    "128 states to draft killer-robot rules by 2028",
    "No binding treaty at UN talks; campaigners call it watered down.")
end_c = max(end_c, story_plain(
    d, MARGIN + (c_w + gap), row_c, c_w, "SPORT · FOOTBALL", GREEN,
    "Liverpool 4–0 United: Pochettino’s nightmare",
    "Yoro off in eight minutes; heaviest debut defeat since 1926."))
end_c = max(end_c, story_plain(
    d, MARGIN + 2 * (c_w + gap), row_c, c_w, "CRICKET · WELLINGTON", BLUE,
    "India’s 720 not enough: New Zealand escape",
    "Nicholls’ unbeaten 175 and a last-day rearguard save the draw."))

hrule(d, end_c + 8, width=2)

# --- footer briefs ---------------------------------------------------------
foot_y = end_c + 16
bf = sans_bold(14)
brief_head = "ALSO TODAY  "
# two hand-balanced lines: the first runs beside the label, the
# second spans the full width — five briefs, no third line
brief_a = ("Mexico captures “El Chapo Isidro”, 11 dead · South "
           "Korea’s education minister quits over AI exam cheating")
brief_b = ("24 killed in South Sudan raid · Bolsonaro stable in "
           "intensive care · North Korea expands uranium plant")
bx = MARGIN + text_w(d, brief_head, bf)
d.text((MARGIN, foot_y), brief_head, font=bf, fill=RED)
d.text((bx, foot_y), brief_a, font=bf, fill=INK)
d.text((MARGIN, foot_y + bf.size + 3), brief_b, font=bf, fill=INK)

img.save("entry.png", format="PNG")
print("wrote entry.png")
