# -*- coding: utf-8 -*-
"""Generates the SY World modpack logo.

Output: docs/curseforge/logo.png (512x512; CurseForge wants at least 400x400).
Run: python tools/gen_logo.py

Drawn from primitives, like every SY logo: a dark field, one hero object, warm and magic light.
The hero is a floating island - the world - and each mod in the pack lives somewhere on it:

  - SY Village : a house on the grass, its window lit
  - SY Works   : a furnace-like machine beside it, glowing at the slot
  - SY Magic   : a violet orb hanging over the island
  - SY Dungeon : a barred archway in the rock underneath, lit from inside

When the family grows, the new mod gets a place on the island; the picture does not have to be
redrawn around a count. Composition rule: it must survive the 64px gallery thumbnail, so the
island (green top, earth-and-stone wedge) is the one big mass and the two lights are the accents.
"""
import os

from PIL import Image, ImageDraw, ImageFilter

SS = 4
S = 512 * SS

BG_CENTER = (36, 42, 76)
BG_EDGE = (9, 10, 20)
STAR = (220, 226, 255)

GRASS_DARK = (62, 118, 48)
GRASS = (98, 168, 72)
GRASS_LIGHT = (130, 196, 90)
DIRT_TOP = (124, 88, 56)
DIRT_BOTTOM = (92, 64, 42)
STONE_TOP = (112, 112, 120)
STONE_BOTTOM = (48, 48, 58)

WOOD = (168, 120, 72)
WOOD_DARK = (104, 72, 42)
ROOF = (180, 66, 52)
ROOF_DARK = (122, 40, 34)
WINDOW = (255, 204, 110)

FURNACE_FRONT = (126, 126, 134)
FURNACE_TOP = (166, 166, 174)
FURNACE_SIDE = (86, 86, 96)
FURNACE_EDGE = (52, 52, 60)
FIRE = (255, 150, 56)

ARCH_STONE = (150, 150, 158)
ARCH_EDGE = (70, 70, 80)
ARCH_GLOW = (255, 150, 60)
BARS = (40, 42, 48)

ORB_CORE = (255, 253, 250)
ORB_RIM = (150, 86, 214)
ORB_HALO = (150, 92, 226)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = [os.path.join(ROOT, 'docs', 'curseforge', 'logo.png')]


def px(v):
    return round(v * SS)


def pts(points):
    return [(px(x), px(y)) for x, y in points]


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def radial(img, centre, radius, inner, outer, steps=160):
    d = ImageDraw.Draw(img)
    cx, cy = px(centre[0]), px(centre[1])
    r_max = px(radius)
    for i in range(steps, -1, -1):
        t = i / steps
        r = round(r_max * t)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=lerp(inner, outer, t))


def glow(img, centre, radius, colour, strength, blur):
    """A soft light: a filled disc blurred into the picture."""
    mask = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(mask)
    cx, cy, r = px(centre[0]), px(centre[1]), px(radius)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=strength)
    mask = mask.filter(ImageFilter.GaussianBlur(px(blur)))
    img.paste(Image.new('RGB', (S, S), colour), (0, 0), mask)


def vertical_fill(img, polygon, stops):
    """Fill `polygon` with a vertical gradient through `stops` [(y, colour), ...]."""
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts(polygon), fill=255)
    grad = Image.new('RGB', (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        ly = y / SS
        if ly <= stops[0][0]:
            c = stops[0][1]
        elif ly >= stops[-1][0]:
            c = stops[-1][1]
        else:
            for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
                if y0 <= ly <= y1:
                    c = lerp(c0, c1, (ly - y0) / (y1 - y0))
                    break
        gd.line([(0, y), (S, y)], fill=c)
    img.paste(grad, (0, 0), mask)


def background():
    img = Image.new('RGB', (S, S), BG_EDGE)
    radial(img, (256, 236), 560, BG_CENTER, BG_EDGE)
    d = ImageDraw.Draw(img)
    for x, y, r in ((70, 70, 3), (140, 40, 2), (430, 64, 3), (470, 160, 2), (40, 190, 2),
                    (200, 96, 2), (96, 420, 2), (440, 400, 3), (470, 290, 2), (60, 300, 2),
                    (380, 470, 2), (150, 480, 2)):
        d.ellipse([px(x - r), px(y - r), px(x + r), px(y + r)], fill=STAR)
    return img


UNDERSIDE = [(84, 262), (104, 296), (132, 332), (164, 364), (196, 398), (226, 436),
             (256, 474), (284, 440), (314, 404), (346, 368), (378, 332), (406, 296), (428, 262)]


def island(img):
    # Earth, then stone, running down to the point of the island.
    vertical_fill(img, UNDERSIDE, [(262, DIRT_TOP), (300, DIRT_BOTTOM), (304, STONE_TOP), (474, STONE_BOTTOM)])
    d = ImageDraw.Draw(img)
    # A few strata so the rock reads as rock.
    for y, x0, x1 in ((330, 136, 376), (432, 232, 280)):
        d.line([(px(x0), px(y)), (px(x1), px(y))], fill=STONE_BOTTOM, width=px(3))
    # Grass: a darker rim, the lit top above it.
    d.ellipse([px(84), px(222), px(428), px(304)], fill=GRASS_DARK)
    d.ellipse([px(92), px(216), px(420), px(292)], fill=GRASS)
    d.ellipse([px(120), px(222), px(350), px(262)], fill=GRASS_LIGHT)


def dungeon_arch(img):
    """SY Dungeon: a barred archway in the rock, lit from within."""
    cx, top, bottom, half = 256, 350, 410, 28
    d = ImageDraw.Draw(img)
    # Stone frame.
    d.rectangle([px(cx - half - 8), px(top), px(cx + half + 8), px(bottom)], fill=ARCH_EDGE)
    d.ellipse([px(cx - half - 8), px(top - half - 8), px(cx + half + 8), px(top + half + 8)], fill=ARCH_EDGE)
    d.rectangle([px(cx - half - 4), px(top), px(cx + half + 4), px(bottom)], fill=ARCH_STONE)
    d.ellipse([px(cx - half - 4), px(top - half - 4), px(cx + half + 4), px(top + half + 4)], fill=ARCH_STONE)
    # The opening, dark above and warm at the floor.
    opening = Image.new('L', (S, S), 0)
    od = ImageDraw.Draw(opening)
    od.rectangle([px(cx - half), px(top), px(cx + half), px(bottom)], fill=255)
    od.ellipse([px(cx - half), px(top - half), px(cx + half), px(top + half)], fill=255)
    grad = Image.new('RGB', (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(px(top - half), px(bottom) + 1):
        t = (y / SS - (top - half)) / (bottom - (top - half))
        gd.line([(0, y), (S, y)], fill=lerp((14, 12, 18), ARCH_GLOW, max(0.0, t - 0.25) / 0.75))
    img.paste(grad, (0, 0), opening)
    for x in (cx - 16, cx, cx + 16):
        d.line([(px(x), px(top - half + 6)), (px(x), px(bottom))], fill=BARS, width=px(4))


def house(img):
    """SY Village: a house on the grass with a lit window."""
    d = ImageDraw.Draw(img)
    x0, x1, base, wall_top = 150, 210, 262, 222
    glow(img, (180, 236), 34, WINDOW, 120, 14)
    d.rectangle([px(x0 - 3), px(wall_top), px(x1 + 3), px(base + 3)], fill=WOOD_DARK)
    d.rectangle([px(x0), px(wall_top), px(x1), px(base)], fill=WOOD)
    d.polygon(pts([(x0 - 14, wall_top + 2), ((x0 + x1) / 2, 180), (x1 + 14, wall_top + 2)]), fill=ROOF_DARK)
    d.polygon(pts([(x0 - 8, wall_top), ((x0 + x1) / 2, 186), (x1 + 8, wall_top)]), fill=ROOF)
    d.rectangle([px(x0 + 10), px(wall_top + 10), px(x0 + 26), px(wall_top + 26)], fill=WINDOW)
    d.rectangle([px(x1 - 22), px(base - 26), px(x1 - 8), px(base)], fill=WOOD_DARK)


def furnace(img):
    """SY Works: a stone machine block, fire at the slot."""
    d = ImageDraw.Draw(img)
    fx0, fx1, fy0, fy1, depth = 262, 312, 214, 264, 14
    d.polygon(pts([(fx0, fy0), (fx0 + depth, fy0 - depth * 0.7), (fx1 + depth, fy0 - depth * 0.7), (fx1, fy0)]), fill=FURNACE_TOP)
    d.polygon(pts([(fx1, fy0), (fx1 + depth, fy0 - depth * 0.7), (fx1 + depth, fy1 - depth * 0.7), (fx1, fy1)]), fill=FURNACE_SIDE)
    d.rectangle([px(fx0), px(fy0), px(fx1), px(fy1)], fill=FURNACE_EDGE)
    d.rectangle([px(fx0 + 3), px(fy0 + 3), px(fx1 - 3), px(fy1 - 3)], fill=FURNACE_FRONT)
    glow(img, ((fx0 + fx1) / 2, fy1 - 14), 18, FIRE, 150, 8)
    d = ImageDraw.Draw(img)
    d.rectangle([px(fx0 + 10), px(fy1 - 20), px(fx1 - 10), px(fy1 - 9)], fill=FIRE)
    d.rectangle([px(fx0 + 10), px(fy0 + 10), px(fx1 - 10), px(fy0 + 18)], fill=FURNACE_EDGE)


def orb(img):
    """SY Magic: a violet orb over the island."""
    cx, cy, r = 352, 136, 26
    glow(img, (cx, cy), 70, ORB_HALO, 200, 34)
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hx, hy = cx - 8, cy - 8
    for i in range(120, -1, -1):
        t = i / 120.0
        rr = round(px(r) * t)
        x = round(px(cx + (hx - cx) * (1 - t)))
        y = round(px(cy + (hy - cy) * (1 - t)))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=lerp(ORB_CORE, ORB_RIM, t) + (255,))
    img.paste(layer, (0, 0), layer)
    sd = ImageDraw.Draw(img)
    for sx, sy, sr in ((300, 110, 4), (398, 176, 3), (384, 96, 3), (318, 180, 3)):
        sd.ellipse([px(sx - sr), px(sy - sr), px(sx + sr), px(sy + sr)], fill=(230, 208, 255))


def main():
    img = background()
    # A faint cool light under the island, so it floats rather than sits.
    glow(img, (256, 380), 150, (60, 70, 130), 90, 60)
    island(img)
    dungeon_arch(img)
    house(img)
    furnace(img)
    orb(img)
    img = img.resize((512, 512), Image.LANCZOS)
    for path in OUT:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print('wrote', path)


if __name__ == '__main__':
    main()
