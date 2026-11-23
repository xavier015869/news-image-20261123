#!/usr/bin/env python3
"""Render the front page for Monday 23 November 2026.

Draws a one-page newspaper, "The World Ledger", that sums up the day's
world news in a single 1024x1024 image:

  * COP31 in Antalya collapses without a deal over fossil fuels
  * Warsaw confirms three Russian cruise missiles fell on Poland
  * Iran strike wounds two in Bahrain; Houthis claim Saudi refinery hit
  * Taiwan bans short selling after the Taiex loses 17.5% in a week
  * Suspected Ukrainian sea drones hit a Russian warship at Benghazi
  * 128 states back international rules on killer robots by 2028
  * Liverpool rout ten-man Manchester United in Pochettino's debut
  * Briefs: Mexico cartel capture, South Sudan, Bolsonaro, North Korea

Everything is drawn with Pillow primitives and system fonts, with no
randomness and no timestamps, so two runs write byte-identical PNGs.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
RIGHT = W - MARGIN

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


def kicker(draw, x, y, label, colour):
    """A small coloured tag with white bold caps text; returns its height."""
    fnt = sans_bold(15)
    w = text_w(draw, label, fnt) + 18
    draw.rectangle([x, y, x + w, y + 24], fill=colour)
    draw.text((x + 9, y + 4), label, font=fnt, fill=WHITE)
    return 24


def story(draw, x, y, width, kick, colour, headline, body,
          head_size=26, body_size=15, head_leading=3, body_leading=4):
    """One news block: kicker, serif headline, sans body. Returns end y."""
    y += kicker(draw, x, y, kick, colour) + 8
    hf = serif_bold(head_size)
    y = draw_lines(draw, x, y, wrap(draw, headline, hf, width), hf,
                   leading=head_leading)
    y += 3
    bf = sans(body_size)
    y = draw_lines(draw, x, y, wrap(draw, body, bf, width), bf,
                   leading=body_leading)
    return y


def hrule(draw, y, x0=MARGIN, x1=RIGHT, fill=INK, width=2):
    draw.line([x0, y, x1, y], fill=fill, width=width)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# --- frame ---------------------------------------------------------------
d.rectangle([10, 10, W - 10, H - 10], outline=INK, width=2)
d.rectangle([16, 16, W - 16, H - 16], outline=GREY, width=1)

# --- top strip -----------------------------------------------------------
strip = sans_bold(13)
d.text((MARGIN, 27), "INTERNATIONAL EDITION", font=strip, fill=GREY)
label = "ONE PAGE · THE WHOLE DAY"
d.text((RIGHT - text_w(d, label, strip), 27), label, font=strip, fill=GREY)

# --- masthead ------------------------------------------------------------
name = "The World Ledger"
mf = fit_font(d, name, 96, masthead_font, RIGHT - MARGIN)
d.text(((W - text_w(d, name, mf)) / 2, 44), name, font=mf, fill=INK)
hrule(d, 158, width=3)
hrule(d, 164, width=1)

# --- date bar ------------------------------------------------------------
d.rectangle([MARGIN, 174, RIGHT, 220], fill=INK)
date_text = "MONDAY  23  NOVEMBER  2026"
df = fit_font(d, date_text, 31, sans_bold, RIGHT - MARGIN - 40)
d.text(((W - text_w(d, date_text, df)) / 2, 182), date_text, font=df,
       fill=WHITE)

# --- lead story: COP31 ---------------------------------------------------
lead_y = 236
kicker(d, MARGIN, lead_y, "CLIMATE SUMMIT · ANTALYA, TÜRKİYE", RED)
head_f = serif_bold(58)
hy = lead_y + 32
for line in ("COP31 COLLAPSES", "WITHOUT A DEAL"):
    d.text((MARGIN, hy), line, font=head_f, fill=INK)
    hy += 64

# standfirst and body, left column
stand_f = sans_bold(19)
sy = draw_lines(d, MARGIN, 398, wrap(
    d, "The longest UN climate summit in history ended in failure, as "
       "the EU refused to sign a final text that never mentioned "
       "fossil fuels.", stand_f, 640), stand_f, leading=5)
body_f = sans(15)
draw_lines(d, MARGIN, sy + 8, wrap(
    d, "After two weeks and two days of overtime in Antalya, 194 "
       "delegations could not agree the “Antalya Pact”. Ireland’s "
       "Darragh O’Brien, speaking for the EU, said the bloc would not "
       "endorse a deal “that does not even mention fossil fuels”. Saudi "
       "Arabia led opposition to any phase-out language. Australia’s "
       "Anthony Albanese called the failure a sign of “difficult "
       "geopolitical times”.", body_f, 640), body_f, leading=4)

# visual panel: a globe split by a jagged red crack, right of the text
px0, py0, px1, py1 = 692, 398, RIGHT, 554
d.rectangle([px0, py0, px1, py1], fill=PANEL, outline=GREY, width=1)
cx, cy, r = (px0 + px1) // 2, py0 + 58, 50
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=3)
for frac in (0.38, 0.72):
    rx = int(r * frac)
    d.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=BLUE, width=1)
for k in (-0.5, 0.0, 0.5):
    half = int(r * (1 - k * k) ** 0.5)
    d.line([cx - half, cy + int(k * r), cx + half, cy + int(k * r)],
           fill=BLUE, width=1)
crack = [(cx - 10, cy - r + 3), (cx + 3, cy - 26), (cx - 7, cy - 4),
         (cx + 9, cy + 20), (cx - 2, cy + 38), (cx + 6, cy + r - 4)]
d.line(crack, fill=RED, width=4, joint="curve")
cap_f = sans_bold(16)
cap = "1.5°C OVERSHOOT"
d.text(((px0 + px1 - text_w(d, cap, cap_f)) / 2, py0 + 116), cap,
       font=cap_f, fill=DARKRED)
cap2_f = sans(13)
cap2 = "FORMALLY ACKNOWLEDGED"
d.text(((px0 + px1 - text_w(d, cap2, cap2_f)) / 2, py0 + 136), cap2,
       font=cap2_f, fill=DARKRED)

hrule(d, 578, width=2)

# --- row 2: Poland | Gulf --------------------------------------------------
row2_y = 594
mid = W // 2
story(d, MARGIN, row2_y, mid - MARGIN - 18,
      "EUROPE · WARSAW", BLUE,
      "Russian cruise missiles fell on Poland, Warsaw confirms",
      "Poland confirmed on Monday that three objects that fell in the "
      "country’s south-east on Friday were Russian cruise missiles. "
      "NATO allies will meet over the incursion, the latest sign of the "
      "Kremlin’s escalating “shadow war” against Europe.")
d.line([mid, row2_y + 2, mid, 758], fill=GREY, width=1)
story(d, mid + 18, row2_y, RIGHT - mid - 18,
      "MIDDLE EAST · GULF", DARKRED,
      "Iran strike wounds two in Bahrain",
      "Yemen’s Houthis claimed strikes on a Saudi oil refinery and "
      "radar, with at least six injured; the US embassy warned its "
      "citizens, and UAE tankers now run the Strait of Hormuz under "
      "US escort.")

hrule(d, 784, width=2)

# --- row 3: Markets | Benghazi | Killer robots | Sport ---------------------
row3_y = 800
col_w, gap = 226, 16
cols = [
    ("MARKETS · TAIPEI", RED, "Taiwan bans short selling",
     "After a record plunge — the Taiex lost 17.5% in a week, 7,642 "
     "points, to 36,033 — a ban on short sales at or below the flat "
     "price took effect on Monday."),
    ("WAR · LIBYA", BLUE, "Sea drones hit Russian warship",
     "Libyan officials said suspected Ukrainian sea drones struck a "
     "Russian warship at the Benghazi naval base, Kyiv’s drone war "
     "reaching the Mediterranean."),
    ("TECH · UNITED NATIONS", GOLD, "128 states back killer-robot rules",
     "At the United Nations, 128 states agreed to pursue international "
     "rules on lethal autonomous weapons by 2028, as diplomacy races "
     "the AI arms race."),
    ("SPORT · FOOTBALL", GREEN, "Liverpool rout ten-man United",
     "Pochettino’s Manchester United reign began in nightmare: Leny "
     "Yoro sent off, Liverpool rampant. India pushed for victory over "
     "New Zealand in the first Test."),
]
for i, (kick, colour, head, body) in enumerate(cols):
    x = MARGIN + i * (col_w + gap)
    if i:
        d.line([x - gap // 2, row3_y + 2, x - gap // 2, 950],
               fill=GREY, width=1)
    story(d, x, row3_y, col_w, kick, colour, head, body,
          head_size=21, body_size=13, head_leading=3, body_leading=4)

# --- footer briefs ---------------------------------------------------------
foot_f = sans(12)
briefs = [
    "ALSO TODAY — Mexico captures cartel boss “El Chapo Isidro”, 11 dead "
    "in Sinaloa · 24 civilians killed in South Sudan",
    "Bolsonaro “stable” in intensive care · North Korea expands its "
    "uranium plant · South Korea’s education minister quits over an AI "
    "exam-cheating scandal",
]
fy = 968
for line in briefs:
    d.text(((W - text_w(d, line, foot_f)) / 2, fy), line, font=foot_f,
           fill=GREY)
    fy += 16

img.save("entry.png", format="PNG")
print("wrote entry.png")
