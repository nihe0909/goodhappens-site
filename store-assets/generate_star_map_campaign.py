from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "store-assets"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Hiragino Sans GB.ttc"
FONT_MEDIUM = "/System/Library/Fonts/STHeiti Medium.ttc"
LOGO_PATH = ROOT / "GoodThing/Assets.xcassets/星图素材.imageset/app_icon_white_outline_120.png"


CATEGORIES = [
    ("收到花", (245, 193, 112), ["看日出", "好成绩", "看星星", "学游泳", "看话剧", "堆雪人"]),
    ("练书法", (83, 226, 171), ["穿搭", "看萤火虫", "放风筝", "骑行", "散步", "提拉米苏"]),
    ("完成目标", (160, 128, 255), ["旅行照", "泡温泉", "买礼物", "逛书店", "番茄牛腩"]),
    ("做手工", (72, 168, 255), ["攀岩", "读好书", "拿 offer", "喝咖啡", "做瑜伽", "听音乐"]),
    ("写日记", (237, 94, 153), ["做陶艺", "拍晚霞", "摸猫咪", "红烧肉", "放烟花"]),
    ("做早餐", (78, 216, 236), ["看日落", "跳绳", "引体向上", "学钢琴", "看极光", "看书喝茶"]),
    ("钓鱼", (255, 143, 70), ["跑步", "看电影", "搬新家", "冥想", "打羽毛球", "做志愿者"]),
    ("做蛋糕", (235, 186, 73), ["宝藏小店", "追剧", "写总结", "遛狗狗", "被表扬", "收快递"]),
]


def font(size: int, medium: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_MEDIUM if medium else FONT_REGULAR, size)


def add_glow(base: Image.Image, xy: tuple[float, float], color: tuple[int, int, int], radius: int, strength: float) -> None:
    x, y = xy
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    for i in range(6, 0, -1):
        r = radius * i / 6
        alpha = int(255 * strength * (i / 6) ** 2 / 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.25))
    base.alpha_composite(layer)


def draw_background(img: Image.Image, rng: random.Random, focus: tuple[float, float]) -> None:
    w, h = img.size
    px = img.load()
    fx, fy = focus
    for y in range(h):
        for x in range(w):
            nx = x / w
            ny = y / h
            dist = math.sqrt((nx - fx) ** 2 * 1.2 + (ny - fy) ** 2)
            v = max(0, 1 - dist * 1.5)
            r = int(3 + 16 * v + 4 * ny)
            g = int(3 + 13 * v)
            b = int(8 + 28 * v + 8 * (1 - ny))
            px[x, y] = (r, g, b, 255)

    dust = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(dust, "RGBA")
    for _ in range(int(w * h / 3600)):
        x = rng.randrange(w)
        y = rng.randrange(h)
        r = rng.uniform(0.7, 2.0)
        a = rng.randrange(22, 88)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(205, 210, 240, a))
    for _ in range(int(w * h / 18000)):
        x = rng.randrange(w)
        y = rng.randrange(h)
        r = rng.uniform(1.8, 4.8)
        a = rng.randrange(16, 48)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(180, 190, 225, a))
    img.alpha_composite(dust)


def constellation_points(center: tuple[float, float], count: int, scale: float, rng: random.Random) -> list[tuple[float, float]]:
    points = []
    for i in range(count):
        angle = (math.pi * 2 * i / count) + rng.uniform(-0.42, 0.42)
        radius = scale * rng.uniform(0.28, 1.0)
        points.append((center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius * 0.7))
    return points


def draw_firework(d: ImageDraw.ImageDraw, x: float, y: float, color: tuple[int, int, int], radius: float, alpha: int) -> None:
    for i in range(16):
        a = math.pi * 2 * i / 16
        d.line(
            (x + math.cos(a) * radius * 0.25, y + math.sin(a) * radius * 0.25,
             x + math.cos(a) * radius, y + math.sin(a) * radius),
            fill=(*color, alpha),
            width=1,
        )
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*color, max(20, alpha)))


def draw_star_map(img: Image.Image, orientation: str) -> None:
    w, h = img.size
    rng = random.Random(20260428 if orientation == "portrait" else 20260429)
    draw_background(img, rng, (0.55, 0.42) if orientation == "portrait" else (0.62, 0.45))

    if orientation == "portrait":
        centers = [
            (250, 345), (760, 350), (295, 660), (430, 835),
            (820, 735), (250, 1085), (735, 1170), (765, 1390),
        ]
        cluster_scale = 128
        star_area_bottom = 1500
        small_text = 27
        hero_text = 38
    else:
        centers = [
            (400, 220), (890, 220), (1370, 235), (560, 525),
            (1040, 520), (1510, 550), (720, 815), (1310, 805),
        ]
        cluster_scale = 132
        star_area_bottom = 930
        small_text = 23
        hero_text = 34

    line_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    label_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(line_layer, "RGBA")
    dg = ImageDraw.Draw(glow_layer, "RGBA")
    dt = ImageDraw.Draw(label_layer, "RGBA")

    for idx, (hero, color, labels) in enumerate(CATEGORIES):
        center = centers[idx]
        pts = constellation_points(center, len(labels) + 1, cluster_scale * rng.uniform(0.78, 1.12), rng)
        pts[0] = center
        ordered = sorted(pts, key=lambda p: math.atan2(p[1] - center[1], p[0] - center[0]))

        for a, b in zip(ordered, ordered[1:] + ordered[:1]):
            if rng.random() > 0.18:
                dl.line((*a, *b), fill=(*color, 54), width=2)
        for p in pts:
            add_glow(glow_layer, p, color, 40 if p == center else 28, 0.42 if p == center else 0.25)
            r = 6 if p == center else rng.uniform(3.2, 4.6)
            dg.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(255, 255, 255, 205))
            dg.ellipse((p[0] - r * 1.6, p[1] - r * 1.6, p[0] + r * 1.6, p[1] + r * 1.6), outline=(*color, 110), width=1)

        shown = 0
        for p, label in zip(pts[1:], labels):
            if shown >= 3:
                break
            if 40 < p[1] < star_area_bottom - 20 and abs(p[0] - center[0]) + abs(p[1] - center[1]) > cluster_scale * 0.42:
                dt.text((p[0] + 14, p[1] - small_text * 0.55), label, font=font(small_text), fill=(*color, 112))
                shown += 1

        text_font = font(hero_text, True)
        hero_w = dt.textlength(hero, font=text_font)
        hero_box = (center[0] + 13, center[1] - hero_text * 0.58, center[0] + hero_w + 28, center[1] + hero_text * 0.62)
        dt.rounded_rectangle(hero_box, radius=12, fill=(2, 2, 8, 42))
        dt.text((center[0] + 18, center[1] - hero_text * 0.55), hero, font=text_font, fill=(*color, 232))

    df = ImageDraw.Draw(line_layer, "RGBA")
    for _ in range(10 if orientation == "portrait" else 8):
        draw_firework(df, rng.randrange(100, w - 100), rng.randrange(160, star_area_bottom - 90), (178, 171, 215), rng.randrange(22, 42), rng.randrange(18, 38))

    img.alpha_composite(line_layer.filter(ImageFilter.GaussianBlur(0.2)))
    img.alpha_composite(glow_layer)
    img.alpha_composite(label_layer)


def add_poster_finish(img: Image.Image, orientation: str) -> None:
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")

    # Soft vignette.
    for i in range(90):
        a = int(i * 1.25)
        d.rounded_rectangle((i, i, w - i, h - i), radius=70, outline=(0, 0, 0, a), width=2)

    if orientation == "portrait":
        d.rounded_rectangle((86, 1520, 994, 1768), radius=34, fill=(4, 4, 8, 116), outline=(255, 220, 150, 24), width=1)
        d.text((128, 1570), "200 件好事  ·  8 星座", font=font(38, True), fill=(218, 186, 114, 218))
        d.text((128, 1638), "Good things quietly become constellations", font=font(25), fill=(198, 190, 220, 108))
        logo_size = 48
        logo_xy = (878, 1604)
    else:
        d.rounded_rectangle((104, 804, 590, 948), radius=28, fill=(4, 4, 8, 88), outline=(255, 220, 150, 18), width=1)
        d.text((144, 840), "200 件好事  ·  8 星座", font=font(30, True), fill=(218, 186, 114, 200))
        d.text((144, 892), "A private sky of daily good things", font=font(21), fill=(198, 190, 220, 92))
        logo_size = 42
        logo_xy = (510, 848)

    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
        logo.putalpha(90)
        overlay.alpha_composite(logo, logo_xy)

    img.alpha_composite(overlay)


def make_asset(name: str, size: tuple[int, int], orientation: str) -> None:
    img = Image.new("RGBA", size, (0, 0, 0, 255))
    draw_star_map(img, orientation)
    add_poster_finish(img, orientation)
    out = OUT_DIR / name
    img.convert("RGB").save(out, quality=96, optimize=True)
    print(out)


if __name__ == "__main__":
    make_asset("good-map-campaign-landscape-1920x1080.png", (1920, 1080), "landscape")
    make_asset("good-map-campaign-portrait-1080x1920.png", (1080, 1920), "portrait")
