# Watermark designs → build/wm-{seal,mark,vert}.png (cream on transparent, full alpha;
# the overall opacity is applied at overlay time by build/watermark.py).
# usage: python3 wm_designs.py [NAME [FONT]]   (default 双言两语, build/wm-font.otf)
import sys
from PIL import Image, ImageDraw, ImageFont

NAME = sys.argv[1] if len(sys.argv) > 1 else "双言两语"
SERIF = sys.argv[2] if len(sys.argv) > 2 else "build/wm-font.otf"
MONO = "/System/Library/Fonts/Menlo.ttc"
CREAM = (239, 230, 214)


def seal(S=92):
    # 印章: 2×2 characters in a thin rounded frame (S=92 for the watermark; larger for an avatar)
    k = S / 92
    f = ImageFont.truetype(SERIF, round(34 * k))
    im = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((k, k, S - 2 * k, S - 2 * k), radius=round(8 * k), outline=CREAM + (255,), width=max(2, round(2 * k)))
    for i, c in enumerate(NAME):
        cx, cy = (S * (1 + 2 * (i % 2))) // 4, (S * (1 + 2 * (i // 2))) // 4
        d.text((cx, cy + round(k)), c, font=f, fill=CREAM + (255,), anchor="mm")
    return im


def mark():
    # 字标: serif name over a hairline and a letter-spaced mono line
    f, m = ImageFont.truetype(SERIF, 32), ImageFont.truetype(MONO, 11)
    im = Image.new("RGBA", (200, 70))
    d = ImageDraw.Draw(im)
    d.text((100, 20), "双 言 两 语", font=f, fill=CREAM + (255,), anchor="mm")
    d.line((40, 44, 160, 44), fill=CREAM + (200,), width=1)
    d.text((100, 58), "S H U A N G Y A N", font=m, fill=CREAM + (220,), anchor="mm")
    return im


def vert():
    # 竖排题签: vertical name beside a hairline
    f = ImageFont.truetype(SERIF, 30)
    im = Image.new("RGBA", (54, 168))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(NAME):
        d.text((22, 22 + i * 38), c, font=f, fill=CREAM + (255,), anchor="mm")
    d.line((50, 6, 50, 162), fill=CREAM + (200,), width=1)
    return im


for name, fn in (("seal", seal), ("mark", mark), ("vert", vert)):
    fn().save(f"build/wm-{name}.png")
