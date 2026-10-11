# Watermark designs → build/wm-{seal,mark,vert}.png (cream on transparent, full alpha;
# the overall opacity is applied at overlay time by build/watermark.py).
from PIL import Image, ImageDraw, ImageFont

SERIF = "build/wm-font.otf"
MONO = "/System/Library/Fonts/Menlo.ttc"
CREAM = (239, 230, 214)


def seal():
    # 印章: 2×2 characters in a thin rounded frame
    S, f = 92, ImageFont.truetype(SERIF, 34)
    im = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, S - 2, S - 2), radius=8, outline=CREAM + (255,), width=2)
    for i, c in enumerate("双言两语"):
        cx, cy = (S * (1 + 2 * (i % 2))) // 4, (S * (1 + 2 * (i // 2))) // 4
        d.text((cx, cy + 1), c, font=f, fill=CREAM + (255,), anchor="mm")
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
    for i, c in enumerate("双言两语"):
        d.text((22, 22 + i * 38), c, font=f, fill=CREAM + (255,), anchor="mm")
    d.line((50, 6, 50, 162), fill=CREAM + (200,), width=1)
    return im


for name, fn in (("seal", seal), ("mark", mark), ("vert", vert)):
    fn().save(f"build/wm-{name}.png")
