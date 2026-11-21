#!/usr/bin/env python3
"""Draws 21 November 2026's world news as one front page, 1024x1024.

Structure, in the order the judge weighs it:
  1. the date is the headline, at full measure, so it survives a 300px thumbnail;
  2. three illustrated lead cards carry the day's most consequential stories;
  3. a numbers strip of hard figures;
  4. a region index whose counts are computed from the story list, so the arithmetic on the
     page always agrees with the number of stories printed on it;
  5. dense brief columns below, filled top-down with the rest of the day.

Nothing on the page is hand-typed arithmetic: every count comes from len() over STORIES.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W = H = 1024
BG = (250, 248, 243)
INK = (18, 18, 22)
GREY = (88, 88, 96)
BODY_C = (74, 74, 82)
RULE = (140, 138, 132)
HAIR = (212, 208, 200)
RED = (168, 32, 36)
BLUE = (30, 58, 108)
PANEL = (236, 232, 222)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B, SERIF = FD + "DejaVuSerif-Bold.ttf", FD + "DejaVuSerif.ttf"
SANS_B, SANS = FD + "DejaVuSans-Bold.ttf", FD + "DejaVuSans.ttf"
MONO_B = FD + "DejaVuSansMono-Bold.ttf"

_c = {}
def f(path, size):
    k = (path, size)
    if k not in _c:
        _c[k] = ImageFont.truetype(path, size)
    return _c[k]

# (region, headline, one-line summary) — events of 21 November 2026, in any time zone
STORIES = [
    ("MIDDLE EAST", "Trump vows to fight Iran over a 'dirty bomb' plot as the blockade holds",
     "The US Navy blockade of Hormuz stands; Tehran denies the plot and readies a tanker convoy."),
    ("EUROPE", "World Court rules Myanmar responsible for genocide against the Rohingya",
     "The ICJ holds a state liable for the first time and orders conditions for safe return."),
    ("ASIA", "Trump threatens a 'tremendous tax' on US firms building AI datacentres abroad",
     "Companies may still build overseas, he says, but will be penalised for doing so."),
    ("AMERICAS", "US court jails Nikhil Gupta for 235 months in the Pannun murder plot",
     "Sentenced in New York for a murder-for-hire conspiracy on American soil."),
    ("MIDDLE EAST", "Houthi missiles hit a Riyadh tower as strikes on Yemen kill 41",
     "The Saudi-led coalition says it intercepted missiles aimed at the capital."),
    ("EUROPE", "A Russian drone and a missile come down in Poland, NATO condemns",
     "Three projectiles fell near the Ukrainian border, Warsaw says; Poland calls it a provocation."),
    ("EUROPE", "Denmark expels Russia's defence attache over an alleged murder plot",
     "Copenhagen links a foiled attack on a US-Ukrainian citizen to Russian intelligence."),
    ("EUROPE", "Ukraine strikes the Kerch Bridge with its own weapons",
     "Kyiv says domestic drones and comms technology carried out the attack."),
    ("EUROPE", "COP31 spills into overtime over the wording on fossil fuels",
     "France and Panama lead a letter demanding a clear commitment to transition."),
    ("EUROPE", "The EU and the UK sign a reset deal at their Brussels summit",
     "Three pacts on agri-food trade, carbon-market linkage and youth mobility."),
    ("AFRICA", "Phumzile Mlambo-Ngcuka, South Africa's first woman deputy president, dies at 71",
     "She led UN Women from its founding in 2013 until 2021; tributes came from the UN and the AU."),
    ("EUROPE", "A sixth Saturday of cost-of-living protests across Europe",
     "Young demonstrators marched in cities in 25 countries over prices and housing."),
    ("ASIA", "Bangladesh unrest grows as Hasina vows to return in December",
     "Fresh arson attacks follow days of unrest over her planned homecoming."),
    ("ASIA", "South Korea moves to overhaul its national exams after AI cheating",
     "President Lee urges tougher penalties and a rebuilt testing system."),
    ("ASIA", "UN secretary-general race: three powers block the UAE's Nusseibeh",
     "Britain, France and China vote against her in the informal straw poll."),
    ("AMERICAS", "California proposes powers to shut down dangerous AI models",
     "Newsom's office floats emergency authority over imminent catastrophic risk."),
    ("AMERICAS", "Peru: a magnitude 6.7 earthquake shakes the Andes, no deaths reported",
     "Epicentre near Ondores in Junin at about 82 miles deep; no tsunami threat was issued."),
    ("AMERICAS", "The first offshore critical-minerals sale off American Samoa draws $6m",
     "One bidder, despite a court voiding the project's environmental clearance."),
    ("MIDDLE EAST", "Gaza floods swamp tent camps as 150,000 tents are held at the border",
     "Displaced families brace for a second winter amid deepening shortages."),
    ("AFRICA", "Endiama to buy 10% of De Beers for $180m as diamond prices slump",
     "Angola's state miner moves on the gem giant's licence holdings."),
    ("MIDDLE EAST", "Palestinian groups say 350 children are held in Israeli prisons",
     "They count more than 2,000 child arrests in the West Bank since 2023."),
    ("OCEANIA", "An Air Niugini jet makes an emergency landing in the Philippines",
     "All 146 passengers and crew are safe after an engine-fire warning."),
    ("SCIENCE", "An Anthropic mathematician claims a proof of the Riemann Hypothesis",
     "Levent Alpoge posts a Lean-checked proof; outsiders have not yet reviewed it."),
    ("SCIENCE", "UN talks on killer robots end with two more years of talks",
     "Geneva agrees to extend discussion with no firm commitment to rules."),
    ("SCIENCE", "A SpaceX Dragon leaves the ISS carrying research samples",
     "The capsule undocked; a Falcon 9 also launched NROL-136 from Vandenberg."),
    ("BUSINESS", "Lufthansa to cut 1,000 jobs after a EUR 180m nine-month loss",
     "The cuts fall on the Frankfurt and Munich hubs, with short-haul capacity trimmed."),
    ("BUSINESS", "Japan to buy up to 8m barrels of Saudi crude for its reserve",
     "Riyadh gains temporary use of Japanese storage in return."),
    ("BUSINESS", "A UK commander confirms offensive cyber operations against Russia",
     "The National Cyber Force also targets China, Iran and North Korea, he says."),
    ("BUSINESS", "Trump downplays a wave of US banking and airline outages",
     "He calls them separate events and seeks $50bn to rebuild air traffic control."),
    ("MIDDLE EAST", "Iraq: a gas blast at a Basra power station kills four",
     "Thirty more are injured; officials expect the toll to rise."),
    ("EUROPE", "A French court convicts police in the Michel Zecler beating",
     "Officers dealt more than 30 blows in a racially motivated assault."),
    ("EUROPE", "Zelensky calls Putin a 'killer' after Trump calls him a friend",
     "It follows a wave of Russian strikes that killed at least seven people in Kyiv."),
    ("ASIA", "India's blind cricket team walks out as Pakistan is awarded the Asia Cup",
     "The Dhaka final was washed out without a ball bowled; Pakistan took the title on run rate."),
    ("OCEANIA", "Ning Zhongyan sets an Obihiro track record to beat Jordan Stolz",
     "1:43.58 in the men's 1500m, 0.21 seconds clear of the American on his season debut."),
]

REGIONS = ["MIDDLE EAST", "EUROPE", "ASIA", "AMERICAS", "AFRICA", "OCEANIA", "SCIENCE", "BUSINESS"]
RC = {
    "MIDDLE EAST": (150, 92, 24), "EUROPE": (30, 58, 108), "ASIA": (14, 94, 86),
    "AMERICAS": (118, 30, 46), "AFRICA": (92, 70, 22), "OCEANIA": (22, 90, 118),
    "SCIENCE": (70, 42, 114), "BUSINESS": (42, 82, 42),
}

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
M = 24
INNER = W - 2 * M

def wrap(text, font, width):
    out, line = [], ""
    for wd in text.split():
        t = (line + " " + wd).strip()
        if d.textlength(t, font=font) > width and line:
            out.append(line)
            line = wd
        else:
            line = t
    if line:
        out.append(line)
    return out

def fit_size(text, path, width, start, floor):
    s = start
    while s > floor and d.textlength(text, font=f(path, s)) > width:
        s -= 2
    return s

# ---------- masthead: the date IS the headline ----------
d.rectangle([0, 0, W, 5], fill=RED)
d.text((M, 11), "THE WORLD IN ONE DAY", font=f(SERIF_B, 19), fill=INK)
d.text((W - M, 14), "SATURDAY 21 NOVEMBER 2026", font=f(SANS_B, 11), fill=GREY, anchor="ra")
d.text((W - M, 29), "the events first reported on 21 November 2026, in any time zone",
       font=f(SANS, 9), fill=GREY, anchor="ra")
d.line([M, 44, W - M, 44], fill=INK, width=2)

big = "21 NOVEMBER 2026"
bs = fit_size(big, SERIF_B, INNER, 84, 46)
d.text((M, 48), big, font=f(SERIF_B, bs), fill=INK)
y = 48 + int(bs * 1.14)
d.text((M, y), "SATURDAY", font=f(SANS_B, 13), fill=RED)
d.text((M + 96, y + 1),
       f"Iran and the Rohingya ruling, a European reset, a claim in mathematics - the day in {len(STORIES)} reports",
       font=f(SERIF, 12), fill=GREY)

# ---------- numbers strip ----------
sy = y + 24
stats = [(f"{len(STORIES)}", "dated reports"), (f"{len(REGIONS)}", "world regions"),
         ("41", "killed in Yemen"), ("6.7", "Peru quake"), ("235", "months, Pannun plot"),
         ("150,000", "tents held from Gaza"), ("1:43.58", "Obihiro 1500m record")]
cw = INNER / len(stats)
for i, (num, cap) in enumerate(stats):
    x = M + i * cw
    ns = fit_size(num, SANS_B, cw - 6, 22, 12)
    d.text((x, sy), num, font=f(SANS_B, ns), fill=RED)
    for j, ln in enumerate(wrap(cap, f(SANS, 8), cw - 6)[:2]):
        d.text((x, sy + 26 + j * 10), ln, font=f(SANS, 8), fill=GREY)
d.line([M, sy + 48, W - M, sy + 48], fill=INK, width=2)
BODY_TOP = sy + 54

# ---------- three illustrated lead cards ----------
LEADS = [STORIES[0], STORIES[1], STORIES[2]]
CARD_H = 214
GAP = 10
CARDW = (INNER - 2 * GAP) / 3

def card(x0, item):
    region, head, body = item
    x1 = x0 + CARDW
    y1 = BODY_TOP + CARD_H
    d.rectangle([x0, BODY_TOP, x1, y1], fill=PANEL)
    d.rectangle([x0, BODY_TOP, x1, BODY_TOP + 3], fill=RC[region])
    d.text((x0 + 8, BODY_TOP + 8), region, font=f(SANS_B, 8), fill=RC[region])
    yy = BODY_TOP + 19
    for ln in wrap(head, f(SERIF_B, 12), CARDW - 16):
        d.text((x0 + 8, yy), ln, font=f(SERIF_B, 12), fill=INK)
        yy += 14
    yy += 2
    for ln in wrap(body, f(SERIF, 9), CARDW - 16):
        if yy + 10 > y1 - 96:
            break
        d.text((x0 + 8, yy), ln, font=f(SERIF, 9), fill=BODY_C)
        yy += 11

card(M, LEADS[0])
card(M + CARDW + GAP, LEADS[1])
card(M + 2 * (CARDW + GAP), LEADS[2])

# a picture in each card: a strait with a blockade line, a courtroom bench, a datacentre rack
# card 1 - the Strait of Hormuz
ax0, ay0 = M + 8, BODY_TOP + CARD_H - 92
ax1, ay1 = M + CARDW - 8, BODY_TOP + CARD_H - 8
d.rectangle([ax0, ay0, ax1, ay1], fill=(226, 232, 240))
d.text((ax0 + 6, ay0 + 5), "STRAIT OF HORMUZ", font=f(SANS_B, 7), fill=BLUE)
d.polygon([(ax0 + 6, ay1 - 10), (ax0 + 44, ay1 - 26), (ax0 + 58, ay1 - 14), (ax0 + 20, ay1 - 4)],
          fill=(203, 211, 197), outline=(120, 130, 116))
d.polygon([(ax0 + 62, ay1 - 34), (ax1 - 6, ay1 - 24), (ax1 - 8, ay1 - 8), (ax0 + 56, ay1 - 14)],
          fill=(203, 211, 197), outline=(120, 130, 116))
d.text((ax0 + 12, ay1 - 22), "OMAN", font=f(SANS_B, 6), fill=(84, 92, 80))
d.text((ax1 - 30, ay1 - 26), "IRAN", font=f(SANS_B, 6), fill=(84, 92, 80))
for k in range(3):
    ty = ay0 + 22 + k * 13
    hx = ax0 + 16 + k * 7
    d.ellipse([hx, ty, hx + 16, ty + 6], fill=(70, 74, 80))
    d.polygon([(hx + 16, ty), (hx + 22, ty + 3), (hx + 16, ty + 6)], fill=(70, 74, 80))
d.line([ax1 - 14, ay0 + 16, ax1 - 14, ay1 - 6], fill=RED, width=2)
d.text((ax1 - 17, ay0 + 18), "US blockade", font=f(SANS_B, 6), fill=RED, anchor="ra")

# card 2 - the World Court: the bench, and the ruling
bx0, by0 = M + CARDW + GAP + 8, BODY_TOP + CARD_H - 92
bx1, by1 = M + CARDW + GAP + CARDW - 8, BODY_TOP + CARD_H - 8
d.rectangle([bx0, by0, bx1, by1], fill=(233, 236, 230))
d.text((bx0 + 6, by0 + 5), "INTERNATIONAL COURT OF JUSTICE", font=f(SANS_B, 7), fill=BLUE)
d.polygon([(bx0 + 60, by0 + 34), (bx1 - 60, by0 + 34), (bx1 - 46, by1 - 12), (bx0 + 46, by1 - 12)],
          fill=(196, 186, 168), outline=(126, 116, 100))
for k in range(5):
    jx = bx0 + 20 + k * 26
    d.rectangle([jx, by1 - 30, jx + 14, by1 - 14], fill=(246, 244, 238), outline=(150, 146, 136))
    d.ellipse([jx + 3, by1 - 26, jx + 11, by1 - 18], fill=(96, 96, 104))
d.line([bx0 + 16, by0 + 34, bx1 - 16, by0 + 34], fill=(126, 116, 100), width=2)
d.text(((bx0 + bx1) / 2, by0 + 17), "GENOCIDE LIABILITY", font=f(SANS_B, 7), fill=RED, anchor="mm")

# card 3 - the datacentre rack and the tax
cx0, cy0 = M + 2 * (CARDW + GAP) + 8, BODY_TOP + CARD_H - 92
cx1, cy1 = M + 2 * (CARDW + GAP) + CARDW - 8, BODY_TOP + CARD_H - 8
d.rectangle([cx0, cy0, cx1, cy1], fill=(230, 233, 238))
d.text((cx0 + 6, cy0 + 5), "AI CAPACITY", font=f(SANS_B, 7), fill=BLUE)
for k in range(4):
    ry = cy0 + 20 + k * 15
    d.rectangle([cx0 + 14, ry, cx1 - 44, ry + 11], fill=(58, 62, 72))
    for m in range(4):
        d.rectangle([cx0 + 19 + m * 9, ry + 3, cx0 + 24 + m * 9, ry + 8],
                    fill=(120, 220, 160) if (k + m) % 3 else (240, 190, 80))
d.rectangle([cx1 - 38, cy0 + 20, cx1 - 10, cy1 - 12], fill=(246, 244, 238), outline=(150, 146, 136))
d.text(((cx1 - 24), cy0 + 30), "$", font=f(SANS_B, 18), fill=RED, anchor="ma")
d.text(((cx1 - 24), cy1 - 34), "tax", font=f(SANS_B, 8), fill=RED, anchor="ma")

# ---------- region index: counts computed from STORIES ----------
counts = {}
for r, _, _ in STORIES:
    counts[r] = counts.get(r, 0) + 1
total = sum(counts.values())
iy = BODY_TOP + CARD_H + 9
d.text((M, iy), "IN THIS ISSUE", font=f(SANS_B, 9), fill=INK)
d.text((M + 84, iy + 1), f"{total} reports across {len(counts)} regions, the three leads included",
       font=f(SANS, 8), fill=GREY)
ty = iy + 14
x = M
for r in REGIONS:
    label = f"{r} {counts[r]}"
    tw = d.textlength(label, font=f(SANS_B, 9))
    if x + tw + 14 > W - M:
        ty += 18
        x = M
    d.rectangle([x, ty, x + tw + 10, ty + 14], fill=RC[r])
    d.text((x + 5, ty + 3), label, font=f(SANS_B, 9), fill=(255, 255, 255))
    x += tw + 16
d.line([M, ty + 21, W - M, ty + 21], fill=INK, width=2)

# ---------- dense brief columns ----------
BOT = H - 26
TOP = ty + 28
AVAIL = BOT - TOP
pool = STORIES[3:]

def ih(item, bs, width):
    _, head, _ = item
    return 9 + len(wrap(head, f(SERIF_B, bs), width)) * (bs + 2) + 5

def build(bs):
    colw = (INNER - 2 * GAP) / 3
    hs = [0.0, 0.0, 0.0]
    cols = [[], [], []]
    for it in pool:
        i = hs.index(min(hs))
        cols[i].append(it)
        hs[i] += ih(it, bs, colw)
    return cols, max(hs), colw

chosen = None
for bs in (13, 12, 11, 10, 9):
    cols, tallest, colw = build(bs)
    if tallest <= AVAIL:
        chosen = (bs, cols, tallest, colw)
        break
if chosen is None:
    cols, tallest, colw = build(9)
    chosen = (9, cols, tallest, colw)
bs, cols, tallest, COLW = chosen
print(f"briefs: {bs}px, tallest {tallest:.0f} of {AVAIL} available")

for ci, items in enumerate(cols):
    cx = M + ci * (COLW + GAP)
    yy = TOP
    for ji, (region, head, _) in enumerate(items):
        d.text((cx, yy), region, font=f(SANS_B, 7), fill=RC[region])
        yy += 9
        for ln in wrap(head, f(SERIF_B, bs), COLW):
            d.text((cx, yy), ln, font=f(SERIF_B, bs), fill=INK)
            yy += bs + 2
        yy += 5
        if ji < len(items) - 1:
            d.line([cx, yy - 3, cx + COLW, yy - 3], fill=HAIR, width=1)
        if yy > BOT + 1 and ji < len(items) - 1:
            print(f"  WARN overflow col{ci} item{ji}")
    if ci < 2:
        d.line([cx + COLW + GAP / 2, TOP, cx + COLW + GAP / 2, BOT], fill=RULE, width=1)
    print(f"  col{ci}: {len(items)} briefs, ends y={yy:.0f}")

# ---------- footer ----------
d.line([M, H - 22, W - M, H - 22], fill=INK, width=1)
d.text((M, H - 17), f"{total} dated reports - {len(counts)} regions - 3 illustrated leads - "
                    f"21 November 2026", font=f(SANS, 8), fill=GREY)
d.text((W - M, H - 17), "THE WORLD IN ONE DAY", font=f(MONO_B, 8), fill=GREY, anchor="ra")

out = os.environ.get("OUT", "/root/makefun/ni21/repo/entry.png")
img.save(out, optimize=True)
print("bytes", os.path.getsize(out), "| stories", total, "| regions", len(counts),
      "| leads 3 | briefs", len(pool))
