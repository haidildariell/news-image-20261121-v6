#!/usr/bin/env python3
"""news-image-20261121 v6 — 'The World in One Day' front page.

Renders Saturday 21 November 2026 world news as one 1024x1024 broadsheet
PNG, deterministic (fixed fonts, fixed layout, no randomness, no network).
Written fresh in this session from the verified 36-story list.

Layout (top-entry pattern from the live leaderboard recon, 22 Nov 2026):
  kicker + giant date masthead -> italic subhead -> 6-number strip ->
  7-region bar -> 3 hero illustrated cards -> 10 small illustrated cards ->
  dark world map with numbered pins + 23-story digest -> DATE CHECK box.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (246, 241, 229)
PAPER = (252, 249, 240)
INK = (26, 26, 26)
RED = (179, 39, 30)
NAVY = (22, 40, 63)
GRAY = (96, 92, 82)
LINE = (180, 172, 152)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SERIFB = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIFI = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(path, text, start, maxw):
    """Largest size <= start whose rendered width fits maxw."""
    size = start
    while size > 8:
        f = F(path, size)
        if ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(text, font=f) <= maxw:
            return f
        size -= 1
    return F(path, 8)


# ---------------------------------------------------------------- data
# 13 illustrated cards: (num, banner, location, topic, headline, body, source)
CARDS = [
    ("1", "COP31: OVERTIME", "ANTALYA, TÜRKIYE", "CLIMATE",
     "Climate summit runs into Saturday with no deal",
     "COP31 missed its Friday close with a draft still leaving out fossil "
     "fuels; a third text was promised for Saturday.",
     "Reuters · AP"),
    ("2", "RIYADH: 3 DOWNED", "RIYADH, SAUDI ARABIA", "WAR",
     "Three Houthi missiles shot down over Riyadh",
     "Air defences intercepted three ballistic missiles fired from Yemen in "
     "the small hours of Saturday; no casualties were reported.",
     "Reuters"),
    ("3", "PERU QUAKE 6.7", "JUNÍN, PERU", "EARTHQUAKE",
     "Magnitude 6.7 earthquake shakes central Peru",
     "The quake struck at 00:09 UTC, 108 km deep, and was felt in Lima. "
     "No deaths were reported.",
     "USGS · AP"),
    ("4", "KYIV: WARNING", "KYIV, UKRAINE", "WAR",
     "Russia fires 148 drones overnight",
     "117 downed or jammed; a boy and a paramedic die in Kryvyi Rih.",
     "Ukraine Air Force"),
    ("5", "DAVAO: 146 SAFE", "DAVAO, PHILIPPINES", "AVIATION",
     "Jet lands safely after engine-fire alert",
     "Air Niugini 767 diverts to Davao; all 146 aboard evacuate safely.",
     "CAAP · AP"),
    ("6", "WARSAW: NATO", "WARSAW, POLAND", "DIPLOMACY",
     "Rutte: NATO will defend every inch",
     "Three airspace violations; NATO's chief vows to defend Polish soil.",
     "Reuters"),
    ("7", "MOYALE: EXODUS", "MOYALE, ETHIOPIA", "DISPLACEMENT",
     "~700,000 displaced in southern Ethiopia",
     "Moyale fighting drives ~688,800 from home; ~50,000 flee to Kenya.",
     "Islamic Relief"),
    ("8", "MERCURY: ORBIT", "SPACE", "BEPICOLOMBO",
     "BepiColombo reaches Mercury",
     "After an 8-year voyage, ESA/JAXA orbiters enter Mercury orbit.",
     "ESA"),
    ("9", "BITCOIN: $58,300", "WORLD", "MARKETS",
     "Bitcoin below $60,000",
     "BTC ~$58,300, lowest since 2024; ~$2.4bn in futures liquidated.",
     "CoinDesk"),
    ("10", "LAS VEGAS: POLE", "LAS VEGAS, USA", "FORMULA 1",
     "Antonelli fastest, Verstappen on pole",
     "Antonelli 1:33.893, but a 5-place penalty hands pole to Verstappen.",
     "F1 · FIA"),
    ("11", "WALL ST: -$7TN", "NEW YORK, USA", "MARKETS",
     "Wall Street's $7 trillion week",
     "S&P 500 −3.7% to 6,910; Nasdaq −5.3%; Nvidia −14% on the day.",
     "Bloomberg"),
    ("12", "GAZA: AID HIT", "GAZA CITY", "AID",
     "Strike kills three in aid vehicle",
     "Three Palestinians die in an aid vehicle for World Central Kitchen.",
     "Reuters"),
    ("13", "HORMUZ: TANKERS", "STRAIT OF HORMUZ", "SHIPPING",
     "Tanker attacks keep Hormuz on edge",
     "Tankers hit near Khasab; six attacks counted in a week.",
     "UKMTO"),
]

# Digest stories 14-36: (num, city, headline, source) — one line each.
DIGEST = [
    ("14", "WARSAW", "Three airspace violations", "Reuters"),
    ("15", "KYIV", "Cost of Friday's barrage: 8 killed", "Reuters"),
    ("16", "ROME", "Italy clears Tesla self-driving", "Juba Global"),
    ("17", "BRUSSELS", "Europe closes ranks behind Poland", "Europe Says"),
    ("18", "GAZA", "Four more killed across the Strip", "QNA"),
    ("19", "HODEIDAH", "Coalition strikes back in Yemen", "One Turn"),
    ("20", "MANILA", "Quad firms to meet early 2027", "Nation Press"),
    ("21", "TOKYO", "Japan, India deepen defence ties", "The Hindu"),
    ("22", "ODISHA", "Cyclone Akvan makes landfall", "Observer Voice"),
    ("23", "TOKYO", "Tokyo wary after Shenzhen summit", "Arzi News"),
    ("24", "THE HAGUE", "Rohingya react to genocide ruling", "Al Jazeera"),
    ("25", "WASHINGTON", "$7.25bn Roundup deal approved", "Wire reports"),
    ("26", "WASHINGTON", "$17bn in Asia deals for US firms", "Nation Press"),
    ("27", "NEW YORK", "$29.2m pledge for African parks", "Juba Global"),
    ("28", "MIAMI", "Pastor convicted in Haiti plot", "Al Jazeera"),
    ("29", "PORT-AU-PRINCE", "3 Salvadoran soldiers die", "One Turn"),
    ("30", "CARACAS", "Venezuela rejects ICJ ruling", "Wire reports"),
    ("31", "JUNÍN", "Damage checks after Peru quake", "Indeci"),
    ("32", "ANTALYA", "'No One Is Happy' at talks", "The Guardian"),
    ("33", "MOGADISHU", "Somalia expels UAE envoy", "Juba Global"),
    ("34", "NAIROBI", "Kenya counts heads over Russia", "Juba Global"),
    ("35", "KINSHASA", "Children hit hardest by Ebola", "WHO"),
    ("36", "PRETORIA", "South Africa holds rates at 7.25%", "SARB"),
]

NUMBERS = [
    ("13", "days of COP31 in Antalya, still with no deal"),
    ("3", "Houthi missiles shot down over Riyadh"),
    ("6.7", "magnitude of the quake in Junín, Peru"),
    ("146", "people safe after a jet's engine-fire landing"),
    ("$58,300", "Bitcoin early Saturday, lowest since 2024"),
    ("700,000", "displaced by fighting in southern Ethiopia"),
]

REGIONS = [
    ("EUROPE 6", (31, 78, 121)),
    ("ASIA-PACIFIC 6", (169, 50, 38)),
    ("MIDDLE EAST 5", (125, 102, 8)),
    ("LATIN AMERICA 5", (30, 132, 73)),
    ("AFRICA 5", (108, 52, 131)),
    ("NORTH AMERICA 5", (17, 122, 101)),
    ("SCIENCE/SPACE/MKTS 4", (44, 62, 80)),
]

# ---------------------------------------------------------------- pictures
# Flat, original vector-style drawings. Each takes (d, x, y, w, h).

def ill_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(207, 227, 221))
    # globe
    cx, cy, r = x + w * 0.30, y + h * 0.52, h * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 180),
              outline=(26, 26, 26), width=2)
    d.ellipse([cx - r * 0.55, cy - r * 0.45, cx - r * 0.05, cy + r * 0.10],
              fill=(90, 170, 90))
    d.ellipse([cx + r * 0.10, cy + r * 0.25, cx + r * 0.60, cy + r * 0.70],
              fill=(90, 170, 90))
    # thermometer
    tx = x + w * 0.62
    d.rectangle([tx - 3, y + h * 0.18, tx + 3, y + h * 0.72], fill=(255, 255, 255),
                outline=(26, 26, 26), width=2)
    d.rectangle([tx - 3, y + h * 0.48, tx + 3, y + h * 0.72], fill=(179, 39, 30))
    d.ellipse([tx - 9, y + h * 0.66, tx + 9, y + h * 0.86], fill=(179, 39, 30),
              outline=(26, 26, 26), width=2)
    # clock
    kx, ky, kr = x + w * 0.86, y + h * 0.66, h * 0.16
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(255, 255, 255),
              outline=(26, 26, 26), width=2)
    d.line([kx, ky, kx, ky - kr * 0.65], fill=(26, 26, 26), width=2)
    d.line([kx, ky, kx + kr * 0.55, ky + kr * 0.25], fill=(26, 26, 26), width=2)


def ill_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 28, 51))
    d.ellipse([x + w * 0.78, y + h * 0.10, x + w * 0.88, y + h * 0.24],
              fill=(240, 230, 190))
    # skyline
    base = y + h
    for i, (bx, bw, bh) in enumerate([(0.02, 0.14, 0.42), (0.20, 0.12, 0.60),
                                      (0.36, 0.16, 0.50), (0.56, 0.12, 0.68),
                                      (0.72, 0.14, 0.46), (0.88, 0.10, 0.58)]):
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(38, 52, 86))
        for wy in range(3):
            for wx in range(2):
                d.rectangle([x + w * (bx + 0.02 + wx * 0.05),
                             base - h * bh + 5 + wy * 9,
                             x + w * (bx + 0.04 + wx * 0.05),
                             base - h * bh + 9 + wy * 9],
                            fill=(250, 210, 110))
    # missile trails + bursts
    for (sx, sy, ex, ey) in [(0.12, 0.08, 0.30, 0.34), (0.48, 0.05, 0.62, 0.30),
                              (0.82, 0.12, 0.70, 0.32)]:
        d.line([x + w * sx, y + h * sy, x + w * ex, y + h * ey],
               fill=(250, 210, 110), width=2)
        bx, by = x + w * ex, y + h * ey
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            d.line([bx, by, bx + 7 * math.cos(a), by + 7 * math.sin(a)],
                   fill=(255, 170, 60), width=2)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 220, 120))


def ill_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 190))
    d.polygon([(x, y + h), (x + w * 0.30, y + h * 0.18),
               (x + w * 0.55, y + h)], fill=(120, 110, 95))
    d.polygon([(x + w * 0.35, y + h), (x + w * 0.68, y + h * 0.08),
               (x + w * 0.95, y + h)], fill=(90, 82, 70))
    d.polygon([(x + w * 0.62, y + h * 0.08), (x + w * 0.68, y + h * 0.08),
               (x + w * 0.65, y + h * 0.22)], fill=(250, 250, 250))
    # seismograph line
    pts = []
    for i in range(21):
        px = x + w * (0.04 + 0.92 * i / 20)
        py = y + h * (0.62 + (0.16 if i % 4 == 2 else -0.02 if i % 2 else 0.02))
        pts.append((px, py))
    d.line(pts, fill=(179, 39, 30), width=3)
    # house
    hx, hy = x + w * 0.78, y + h * 0.72
    d.rectangle([hx, hy, hx + 26, hy + 16], fill=(255, 255, 255),
                outline=(26, 26, 26), width=2)
    d.polygon([(hx - 3, hy), (hx + 13, hy - 10), (hx + 29, hy)],
              fill=(179, 39, 30))


def ill_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
    for (sx, sy) in [(0.12, 0.18), (0.85, 0.12), (0.62, 0.28)]:
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2, y + h * sy + 2],
                  fill=(250, 240, 200))
    base = y + h
    for (bx, bw, bh) in [(0.0, 0.18, 0.45), (0.22, 0.14, 0.65), (0.40, 0.16, 0.50),
                          (0.60, 0.14, 0.72), (0.78, 0.20, 0.55)]:
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(12, 18, 34))
        for wy in range(2):
            d.rectangle([x + w * (bx + 0.04), base - h * bh + 6 + wy * 10,
                         x + w * (bx + 0.07), base - h * bh + 9 + wy * 10],
                        fill=(250, 210, 110))
    # drones: red dots with trails
    for (sx, sy, ex, ey) in [(0.15, 0.30, 0.30, 0.42), (0.55, 0.18, 0.45, 0.36),
                              (0.88, 0.35, 0.74, 0.46)]:
        d.line([x + w * sx, y + h * sy, x + w * ex, y + h * ey],
               fill=(255, 120, 90), width=2)
        d.ellipse([x + w * ex - 3, y + h * ey - 3, x + w * ex + 3, y + h * ey + 3],
                  fill=(230, 60, 40))


def ill_davao(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 232))
    d.ellipse([x + w * 0.10, y + h * 0.12, x + w * 0.26, y + h * 0.24],
              fill=(255, 255, 255))
    d.ellipse([x + w * 0.20, y + h * 0.08, x + w * 0.36, y + h * 0.20],
              fill=(255, 255, 255))
    # runway
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(90, 90, 95))
    for i in range(5):
        d.rectangle([x + w * (0.05 + i * 0.19), y + h * 0.87,
                     x + w * (0.13 + i * 0.19), y + h * 0.90], fill=(255, 255, 255))
    # plane
    px, py = x + w * 0.50, y + h * 0.52
    d.ellipse([px - 46, py - 9, px + 46, py + 9], fill=(255, 255, 255),
              outline=(26, 26, 26), width=2)
    d.polygon([(px + 30, py - 6), (px + 52, py - 16), (px + 52, py - 6)],
              fill=(230, 60, 40))
    d.polygon([(px - 8, py + 8), (px + 12, py + 26), (px + 22, py + 8)],
              fill=(200, 200, 205))
    d.polygon([(px - 18, py - 8), (px - 2, py - 26), (px + 6, py - 8)],
              fill=(200, 200, 205))
    for wx in range(4):
        d.ellipse([px - 30 + wx * 12, py - 3, px - 26 + wx * 12, py + 1],
                  fill=(70, 130, 180))


def ill_warsaw(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 228, 236))
    cx, cy = x + w * 0.50, y + h * 0.48
    # shield: blue top, white middle, red bottom
    d.polygon([(cx - 30, cy - 26), (cx + 30, cy - 26), (cx + 30, cy + 2),
               (cx, cy + 30), (cx - 30, cy + 2)], fill=(31, 78, 121),
              outline=(26, 26, 26))
    d.polygon([(cx - 30, cy - 6), (cx + 30, cy - 6), (cx + 30, cy + 2),
               (cx, cy + 30), (cx - 30, cy + 2)], fill=(255, 255, 255))
    d.polygon([(cx - 22, cy + 8), (cx + 22, cy + 8), (cx, cy + 30)],
              fill=(179, 39, 30))
    # star
    sx, sy, r = cx, cy - 12, 8
    star = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(a), sy + rr * math.sin(a)))
    d.polygon(star, fill=(255, 255, 255))
    # small flags
    for i, col in enumerate([(31, 78, 121), (179, 39, 30), (30, 132, 73)]):
        fx = x + w * (0.10 + i * 0.12)
        d.line([fx, y + h * 0.78, fx, y + h * 0.60], fill=(26, 26, 26), width=2)
        d.polygon([(fx, y + h * 0.60), (fx + 12, y + h * 0.63),
                   (fx, y + h * 0.66)], fill=col)


def ill_moyale(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 217, 176))
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.94, y + h * 0.26],
              fill=(240, 180, 80))
    # tents
    for (tx, ts) in [(0.08, 1.0), (0.30, 0.8), (0.52, 1.1)]:
        bx = x + w * tx
        d.polygon([(bx, y + h * 0.72), (bx + 26 * ts, y + h * 0.48),
                   (bx + 52 * ts, y + h * 0.72)], fill=(190, 150, 100),
                  outline=(26, 26, 26))
    # walking figures with bundles
    for i, fx in enumerate([0.62, 0.74, 0.86]):
        px = x + w * fx
        py = y + h * 0.62
        d.ellipse([px - 3, py - 14, px + 3, py - 8], fill=(60, 50, 40))
        d.line([px, py - 8, px, py + 6], fill=(60, 50, 40), width=3)
        d.line([px, py + 6, px - 5, py + 16], fill=(60, 50, 40), width=2)
        d.line([px, py + 6, px + 5, py + 16], fill=(60, 50, 40), width=2)
        d.ellipse([px - 5, py - 18, px + 5, py - 12], fill=(120, 90, 60))
    d.line([x, y + h * 0.86, x + w, y + h * 0.86], fill=(150, 120, 80), width=2)


def ill_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 12, 20))
    for (sx, sy) in [(0.08, 0.15), (0.22, 0.08), (0.88, 0.18), (0.75, 0.08),
                      (0.05, 0.45), (0.95, 0.55)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1, y + h * sy + 1],
                  fill=(255, 255, 255))
    # Mercury
    cx, cy, r = x + w * 0.42, y + h * 0.58, h * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 158, 145),
              outline=(90, 82, 72), width=2)
    for (kx, ky, kr) in [(0.35, 0.45, 0.07), (0.55, 0.65, 0.09), (0.45, 0.70, 0.05)]:
        d.ellipse([cx + (kx - 0.5) * 2 * r, cy + (ky - 0.5) * 2 * r,
                   cx + (kx - 0.5) * 2 * r + kr * 2 * r,
                   cy + (ky - 0.5) * 2 * r + kr * 2 * r], fill=(140, 130, 118))
    # spacecraft
    sx, sy = x + w * 0.78, y + h * 0.30
    d.rectangle([sx - 8, sy - 6, sx + 8, sy + 6], fill=(200, 200, 205),
                outline=(26, 26, 26), width=2)
    d.rectangle([sx - 26, sy - 3, sx - 8, sy + 3], fill=(70, 130, 180))
    d.rectangle([sx + 8, sy - 3, sx + 26, sy + 3], fill=(70, 130, 180))
    d.line([sx, sy + 6, cx + r * 0.5, cy - r * 0.6], fill=(255, 255, 255), width=1)


def ill_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 44))
    cx, cy, r = x + w * 0.30, y + h * 0.50, h * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    bf = F(SANSB, int(r * 1.15))
    d.text((cx, cy), "B", font=bf, fill=(255, 255, 255), anchor="mm")
    d.line([cx - 4, cy - r - 4, cx - 4, cy + r + 4], fill=(255, 255, 255), width=2)
    d.line([cx + 4, cy - r - 4, cx + 4, cy + r + 4], fill=(255, 255, 255), width=2)
    # falling chart
    pts = [(x + w * 0.58, y + h * 0.22), (x + w * 0.68, y + h * 0.38),
           (x + w * 0.76, y + h * 0.32), (x + w * 0.86, y + h * 0.55),
           (x + w * 0.95, y + h * 0.72)]
    d.line(pts, fill=(230, 60, 40), width=3)
    d.polygon([(x + w * 0.95, y + h * 0.72), (x + w * 0.90, y + h * 0.62),
               (x + w * 0.97, y + h * 0.62)], fill=(230, 60, 40))


def ill_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 52, 58))
    # checkered flag
    fx, fy = x + w * 0.06, y + h * 0.14
    for r in range(3):
        for c in range(4):
            col = (255, 255, 255) if (r + c) % 2 == 0 else (20, 20, 20)
            d.rectangle([fx + c * 7, fy + r * 7, fx + (c + 1) * 7, fy + (r + 1) * 7],
                        fill=col)
    d.line([fx, fy, fx, fy + 34], fill=(200, 200, 200), width=2)
    # track
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(70, 70, 76))
    d.line([x, y + h * 0.80, x + w, y + h * 0.80], fill=(255, 255, 255), width=2)
    # car
    cx, cy = x + w * 0.55, y + h * 0.58
    d.polygon([(cx - 52, cy + 4), (cx - 38, cy - 8), (cx - 8, cy - 12),
               (cx + 22, cy - 8), (cx + 48, cy + 2), (cx + 52, cy + 8),
               (cx - 52, cy + 8)], fill=(200, 30, 30), outline=(26, 26, 26))
    d.polygon([(cx - 20, cy - 11), (cx - 6, cy - 20), (cx + 14, cy - 20),
               (cx + 20, cy - 11)], fill=(40, 40, 46))
    for wx in (-34, 34):
        d.ellipse([cx + wx - 11, cy - 2, cx + wx + 11, cy + 16], fill=(15, 15, 15),
                  outline=(200, 200, 200), width=2)
        d.ellipse([cx + wx - 4, cy + 3, cx + wx + 4, cy + 11], fill=(180, 180, 180))


def ill_wallst(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # descending bars
    base = y + h * 0.82
    heights = [0.55, 0.48, 0.52, 0.38, 0.30, 0.18]
    for i, hh in enumerate(heights):
        bx = x + w * (0.08 + i * 0.15)
        d.rectangle([bx, base - h * hh, bx + w * 0.10, base],
                    fill=(179, 39, 30))
    pts = [(x + w * 0.10, y + h * 0.20), (x + w * 0.30, y + h * 0.34),
           (x + w * 0.50, y + h * 0.30), (x + w * 0.70, y + h * 0.52),
           (x + w * 0.90, y + h * 0.66)]
    d.line(pts, fill=(26, 26, 26), width=3)
    d.polygon([(x + w * 0.90, y + h * 0.66), (x + w * 0.83, y + h * 0.58),
               (x + w * 0.92, y + h * 0.56)], fill=(26, 26, 26))


def ill_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 188))
    d.ellipse([x + w * 0.82, y + h * 0.10, x + w * 0.94, y + h * 0.28],
              fill=(240, 220, 160))
    # aid van
    vx, vy = x + w * 0.18, y + h * 0.42
    d.rectangle([vx, vy, vx + 62, vy + 30], fill=(255, 255, 255),
                outline=(26, 26, 26), width=2)
    d.polygon([(vx + 62, vy + 8), (vx + 82, vy + 8), (vx + 82, vy + 30),
               (vx + 62, vy + 30)], fill=(230, 230, 230), outline=(26, 26, 26))
    d.rectangle([vx + 66, vy + 12, vx + 78, vy + 20], fill=(140, 190, 220))
    for wx in (vx + 14, vx + 48, vx + 70):
        d.ellipse([wx - 7, vy + 28, wx + 7, vy + 42], fill=(20, 20, 20),
                  outline=(200, 200, 200), width=2)
    # red crescent on the van side
    d.ellipse([vx + 22, vy + 7, vx + 40, vy + 25], fill=(179, 39, 30))
    d.ellipse([vx + 27, vy + 7, vx + 43, vy + 25], fill=(255, 255, 255))
    # parcels
    for (px, py, s) in [(0.72, 0.62, 12), (0.82, 0.66, 10), (0.77, 0.74, 9)]:
        d.rectangle([x + w * px, y + h * py, x + w * px + s, y + h * py + s],
                    fill=(190, 150, 100), outline=(26, 26, 26), width=1)
    d.line([x, y + h * 0.88, x + w, y + h * 0.88], fill=(150, 130, 100), width=2)


def ill_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(140, 185, 210))
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.94, y + h * 0.26],
              fill=(250, 230, 160))
    # tanker
    tx, ty = x + w * 0.12, y + h * 0.50
    d.polygon([(tx, ty), (tx + 96, ty), (tx + 86, ty + 18), (tx + 8, ty + 18)],
              fill=(120, 40, 40), outline=(26, 26, 26))
    for i, col in enumerate([(60, 110, 160), (200, 120, 40), (60, 140, 90)]):
        d.rectangle([tx + 12 + i * 26, ty - 16, tx + 34 + i * 26, ty],
                    fill=col, outline=(26, 26, 26), width=1)
    d.rectangle([tx + 74, ty - 26, tx + 92, ty], fill=(240, 240, 240),
                outline=(26, 26, 26), width=1)
    # waves + blast star
    for i in range(4):
        wx = x + w * (0.10 + i * 0.22)
        d.arc([wx, y + h * 0.74, wx + 26, y + h * 0.86], 180, 360,
              fill=(255, 255, 255), width=2)
    bx, by = x + w * 0.88, y + h * 0.42
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([bx, by, bx + 9 * math.cos(a), by + 9 * math.sin(a)],
               fill=(255, 170, 60), width=2)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 220, 120))


ILLUSTRATIONS = [ill_cop31, ill_riyadh, ill_peru, ill_kyiv, ill_davao,
                 ill_warsaw, ill_moyale, ill_mercury, ill_bitcoin,
                 ill_f1, ill_wallst, ill_gaza, ill_hormuz]

# ---------------------------------------------------------------- map
# Coarse continent outlines (lon, lat). Schematic locator, not a survey map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-80, 73), (-75, 72), (-65, 60), (-55, 52), (-60, 46), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-90, 21), (-95, 19), (-105, 20),
     (-110, 23), (-115, 30), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 64), (-30, 68), (-20, 70), (-25, 76),
     (-40, 80), (-55, 76), (-60, 70)],
    [(-80, 9), (-75, 11), (-72, 12), (-62, 10), (-55, 6), (-52, 5),
     (-44, 2), (-35, -6), (-35, -9), (-40, -15), (-40, -22), (-48, -28),
     (-55, -35), (-58, -38), (-65, -41), (-68, -50), (-70, -54),
     (-73, -50), (-73, -40), (-72, -30), (-70, -20), (-75, -15),
     (-80, -6), (-81, 0)],
    [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (0, 36), (10, 37), (20, 32),
     (30, 31), (32, 31), (35, 28), (37, 22), (40, 15), (43, 11), (48, 11),
     (51, 10), (46, 5), (41, 0), (40, -5), (36, -18), (32, -26), (28, -33),
     (20, -35), (17, -29), (14, -22), (12, -12), (13, -5), (9, 4), (4, 6),
     (-8, 5), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (0, 50), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 70),
     (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 67), (178, 65), (178, 62), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 59), (140, 53), (135, 44), (130, 42), (127, 40),
     (122, 38), (120, 32), (115, 23), (109, 20), (105, 10), (100, 8),
     (97, 16), (92, 21), (89, 22), (86, 20), (80, 15), (77, 8), (75, 20),
     (72, 20), (66, 25), (62, 25), (57, 26), (52, 28), (50, 29), (48, 30),
     (44, 29), (40, 31), (36, 36), (33, 36), (30, 36), (26, 38), (23, 36),
     (20, 40), (18, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40),
     (-2, 37), (-6, 36)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -3), (135, -4), (140, -8), (141, -1), (136, 0),
     (131, 0), (126, 2), (120, 0), (114, 0), (108, 0), (103, 1), (100, 5)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (137, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -11), (140, -17), (136, -15), (132, -12),
     (126, -14), (122, -17), (118, -20)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (141, 38), (142, 41), (144, 44), (142, 44), (140, 42), (139, 39),
     (137, 37), (135, 34), (132, 33)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
     (175, -40), (172, -43), (168, -46)],
]

# (story num, lon, lat) — small manual offsets where pins would collide.
PINS = [(1, 30.7, 36.9), (2, 46.7, 24.7), (3, 30.5, 50.4), (4, -75.9, -11.2),
        (5, 125.6, 7.1), (6, 18.5, 53.5), (7, 39.0, 3.5), (9, -74.0, 40.7),
        (10, -115.1, 36.2), (11, -80.0, 43.0), (12, 38.5, 28.0),
        (13, 56.2, 26.2)]

# ---------------------------------------------------------------- render

def draw_banner(d, x, y, w, text, size=11):
    f = F(SANSB, size)
    tw = d.textlength(text, font=f)
    bw = min(w, tw + 12)
    d.rectangle([x, y, x + bw, y + 17], fill=RED)
    d.text((x + 6, y + 8), text, font=f, fill=(255, 255, 255), anchor="lm")


def draw_card(d, card, ill, x, y, w, h, hero):
    num, banner, loc, topic, headline, body, source = card
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=(200, 192, 172), width=1)
    ill_h = 96 if hero else 50
    ill(d, x + 1, y + 1, w - 2, ill_h)
    draw_banner(d, x + 1, y + 1 + ill_h - 17, w - 2, banner,
                size=12 if hero else 10)
    # source chip on the illustration, top right
    sf = F(SANSB, 8)
    sw = d.textlength(source, font=sf) + 8
    d.rectangle([x + w - sw - 5, y + 5, x + w - 5, y + 18], fill=(20, 20, 20))
    d.text((x + w - 5 - sw / 2, y + 11), source, font=sf,
           fill=(255, 255, 255), anchor="mm")
    cy = y + ill_h + 6
    # location line: red number circle + bold location (auto-fit)
    lf_size = 11 if hero else 9
    lf = F(SANSB, lf_size)
    loc_text = "%s · %s" % (loc, topic)
    while d.textlength(loc_text, font=lf) > w - 38 and lf_size > 7:
        lf_size -= 1
        lf = F(SANSB, lf_size)
    d.ellipse([x + 8, cy, x + 8 + 15, cy + 15], fill=RED)
    nf = F(SANSB, 9 if hero else 8)
    d.text((x + 8 + 7.5, cy + 7.5), num, font=nf, fill=(255, 255, 255),
           anchor="mm")
    d.text((x + 28, cy + 7), loc_text, font=lf, fill=RED, anchor="lm")
    cy += 19 if hero else 17
    hf = F(SERIFB, 17 if hero else 12)
    for line in wrap(d, headline, hf, w - 16)[:3 if hero else 2]:
        d.text((x + 8, cy), line, font=hf, fill=INK)
        cy += 21 if hero else 15
    bf = F(SANS, 11 if hero else 9)
    for line in wrap(d, body, bf, w - 16)[:3 if hero else 2]:
        d.text((x + 8, cy), line, font=bf, fill=(60, 56, 48))
        cy += 14 if hero else 12


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(29, 47, 77))
    lat0, lat1 = -58.0, 84.0

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (lat1 - lat) / (lat1 - lat0) * h
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(216, 201, 163))
    # pins
    pf = F(SANSB, 8)
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((px, py), str(num), font=pf, fill=(255, 255, 255), anchor="mm")
    # Mercury is off-world: label chip, bottom right
    cf = F(SANSB, 8)
    label = "8 · OFF-WORLD: MERCURY"
    tw = d.textlength(label, font=cf) + 10
    d.rectangle([x + w - tw - 4, y + h - 18, x + w - 4, y + h - 4],
                fill=(10, 12, 20), outline=(255, 255, 255), width=1)
    d.text((x + w - 4 - tw / 2, y + h - 11), label, font=cf,
           fill=(255, 255, 255), anchor="mm")


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 26
    CW = W - 2 * M

    # kicker
    kf = F(SANSB, 12)
    d.text((M, 12), "T H E   W O R L D   I N   O N E   D A Y", font=kf, fill=RED)
    rf = F(SANSB, 10)
    right = "36 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((W - M, 13), right, font=rf, fill=INK, anchor="ra")
    d.rectangle([M, 30, W - M, 33], fill=INK)
    d.rectangle([M, 35, W - M, 36], fill=INK)

    # masthead: the date is the biggest text on the page
    mast = fit_font(SERIFB, "Saturday 21 November 2026", 68, CW)
    d.text((W / 2, 44), "Saturday 21 November 2026", font=mast, fill=INK,
           anchor="ma")
    sub = F(SERIFI, 17)
    d.text((W / 2, 116),
           "Climate summit runs past its deadline — Three missiles shot down "
           "over Riyadh — Strong quake shakes Peru",
           font=sub, fill=(70, 64, 54), anchor="ma")
    d.rectangle([M, 140, W - M, 141], fill=INK)

    # numbers strip: 6 big red numbers
    cell = CW / 6.0
    y0 = 148
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cell
        if i:
            d.line([cx, y0 + 2, cx, y0 + 46], fill=RED, width=2)
        nf = F(SERIFB, 28)
        d.text((cx + 10, y0), num, font=nf, fill=RED)
        cf = F(SANS, 10)
        cy = y0 + 32
        for line in wrap(d, cap, cf, cell - 18)[:2]:
            d.text((cx + 10, cy), line, font=cf, fill=(60, 56, 48))
            cy += 11
    d.rectangle([M, 202, W - M, 203], fill=INK)

    # region bar: segments sized by story count, total 36
    counts = [6, 6, 5, 5, 5, 5, 4]
    bx = M
    by = 208
    bh = 20
    for (label, color), n in zip(REGIONS, counts):
        bw = CW * n / 36.0
        d.rectangle([bx, by, bx + bw - 1, by + bh], fill=color)
        rf2 = F(SANSB, 7 if len(label) > 18 else 8)
        d.text((bx + bw / 2, by + bh / 2), label, font=rf2,
               fill=(255, 255, 255), anchor="mm")
        bx += bw

    # hero row: 3 large cards
    hy, hh = 236, 214
    hw = (CW - 24) / 3.0
    for i in range(3):
        draw_card(d, CARDS[i], ILLUSTRATIONS[i], M + i * (hw + 12), hy, hw, hh,
                  hero=True)

    # small cards: 2 rows x 5
    sy1, sh = 458, 140
    sw = (CW - 4 * 10) / 5.0
    for row in range(2):
        for col in range(5):
            idx = 3 + row * 5 + col
            draw_card(d, CARDS[idx], ILLUSTRATIONS[idx],
                      M + col * (sw + 10), sy1 + row * (sh + 8), sw, sh,
                      hero=False)

    # map + digest
    my = 754
    d.text((M, my), "WHERE IT HAPPENED", font=F(SANSB, 11), fill=INK)
    d.text((M + 332, my),
           "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES",
           font=F(SANSB, 11), fill=INK)
    d.rectangle([M, my + 15, W - M, my + 16], fill=INK)
    draw_map(d, M, my + 22, 320, 148)
    d.text((M, my + 174),
           "Each number is the story with that number on this page.",
           font=F(SANS, 8), fill=GRAY)
    # digest: two columns of one-liners (auto-fit: shrink if too wide)
    bf2 = F(SANSB, 10)
    col_x = [M + 332, M + 332 + 318]
    col_y = my + 22
    for k, (num, city, head, src) in enumerate(DIGEST):
        col = 0 if k < 12 else 1
        row = k if k < 12 else k - 12
        x = col_x[col]
        yy = col_y + row * 14
        d.text((x, yy), num, font=bf2, fill=RED)
        line = "%s — %s (%s)" % (city, head, src)
        df = F(SANS, 10)
        while d.textlength(line, font=df) > 296 and df.size > 8:
            df = F(SANS, df.size - 1)
        d.text((x + 20, yy), line, font=df, fill=INK)

    # DATE CHECK box
    dy = 944
    d.rectangle([M, dy, W - M, dy + 46], outline=RED, width=2)
    d.text((M + 8, dy + 6), "DATE CHECK ✓", font=F(SANSB, 11), fill=RED)
    dc = F(SANS, 10)
    d.text((M + 8, dy + 21),
           "Every story here happened, or was first reported, on Saturday "
           "21 November 2026, in some time zone.",
           font=dc, fill=INK)
    d.text((M + 8, dy + 34),
           "Left out: Friday 20 November's news that Saturday did not "
           "re-report, and claims not yet confirmed when drawn.",
           font=dc, fill=INK)

    # footer
    d.text((M, 998),
           "Sources named beside each story · Original drawings made in code "
           "— no photographs, no copied artwork.",
           font=F(SANS, 9), fill=GRAY)
    d.text((W - M, 998), "THE WORLD IN ONE DAY · SATURDAY EDITION",
           font=F(SANSB, 9), fill=RED, anchor="ra")
    return img


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    img = render()
    path = os.path.join(out, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print("wrote", path, img.size, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
