#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_brand.py — собирает бренд-пакет «Хурмыч» из сгенерированного арта:
  brand/banner_2560x1440.png   шапка YouTube (с учётом безопасной зоны)
  brand/vk_cover_1590x400.png  обложка VK-сообщества
  brand/og_1200x630.png        превью для сайта / соцсетей (Open Graph)
  brand/avatar_800.png         аватар YouTube / VK / Дзен / Rutube
  brand/tg_avatar_512.png      аватар Telegram

Запуск:  python3 scripts/build_brand.py
Зависимости: Pillow. Шрифт Liberation Sans (идёт со многими дистрибутивами;
путь ниже можно заменить на свой, например Arial/DejaVu).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(BASE, "brand")
BG = os.path.join(BRAND, "banner_bg.png")
EMBLEM = os.path.join(BRAND, "emblem_hurmych.png")

FONT_BOLD = "/app/node_modules/pdfjs-dist/standard_fonts/LiberationSans-Bold.ttf"
FONT_REG = "/app/node_modules/pdfjs-dist/standard_fonts/LiberationSans-Regular.ttf"
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = FONT_REG = None  # PIL подставит дефолтный

GOLD = (242, 232, 213)        # кремовый — основной текст заголовка
GOLD_DIM = (235, 122, 52)     # персиковый — линии и акценты
PERSIMMON = (235, 122, 52)    # акцент «хурма»
TEAL = (185, 175, 163)        # приглушённый тёплый серый
INK = (20, 22, 28)

TITLE = "ХУРМЫЧ"
SUB1 = "L2 ESSENCE  •  MAIN"
SUB2 = "ГАЙДЫ  •  ПАТЧИ  •  ЭКОНОМИКА"


def font(path, size):
    if path is None:
        return ImageFont.load_default(size=size)
    return ImageFont.truetype(path, size)


def cover(img, w, h):
    """Масштабирует и кропит изображение под точный размер w×h."""
    iw, ih = img.size
    s = max(w / iw, h / ih)
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def tracked(draw, xy, text, fnt, fill, tracking=0, anchor_center=True, cx=None):
    """Текст с межбуквенным интервалом. anchor_center + cx — центровать по cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (cx - total / 2) if anchor_center else xy[0]
    y = xy[1]
    for ch, wd in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wd + tracking
    return total


def compose(width, height, out_name, title_size, sub1_size, sub2_size, pad_box=True):
    bg = cover(Image.open(BG).convert("RGB"), width, height)
    # лёгкое затемнение центра для читаемости текста
    veil = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(veil)
    cy = height // 2
    box_h = int(title_size * 3.4)
    if pad_box:
        d.rounded_rectangle(
            [width * 0.06, cy - box_h // 2, width * 0.94, cy + box_h // 2],
            radius=28, fill=(8, 11, 18, 150),
        )
    veil = veil.filter(ImageFilter.GaussianBlur(2))
    bg = Image.alpha_composite(bg.convert("RGBA"), veil).convert("RGB")
    draw = ImageDraw.Draw(bg)

    f_title = font(FONT_BOLD, title_size)
    f_sub1 = font(FONT_BOLD, sub1_size)
    f_sub2 = font(FONT_REG, sub2_size)

    tw = tracked(draw, (0, cy - int(title_size * 1.05)), TITLE, f_title, GOLD,
                 tracking=int(title_size * 0.06), cx=width // 2)
    # тонкая золотая линия под заголовком
    ly = cy + int(title_size * 0.15)
    draw.line([width // 2 - tw / 2 - 40, ly, width // 2 + tw / 2 + 40, ly],
              fill=GOLD_DIM, width=max(2, title_size // 60))
    s1y = cy + int(title_size * 0.35)
    tracked(draw, (0, s1y), SUB1, f_sub1, PERSIMMON,
            tracking=int(sub1_size * 0.30), cx=width // 2)
    tracked(draw, (0, s1y + int(sub1_size * 1.7)), SUB2, f_sub2, TEAL,
            tracking=int(sub2_size * 0.22), cx=width // 2)

    out = os.path.join(BRAND, out_name)
    bg.save(out, quality=92)
    print("сохранено:", out)


def avatars():
    emb = Image.open(EMBLEM).convert("RGB")
    a800 = cover(emb, 800, 800)
    a800.save(os.path.join(BRAND, "avatar_800.png"))
    print("сохранено:", os.path.join(BRAND, "avatar_800.png"))
    a512 = cover(emb, 512, 512)
    a512.save(os.path.join(BRAND, "tg_avatar_512.png"))
    print("сохранено:", os.path.join(BRAND, "tg_avatar_512.png"))


if __name__ == "__main__":
    compose(2560, 1440, "banner_2560x1440.png", 250, 58, 46)
    compose(1590, 400, "vk_cover_1590x400.png", 110, 30, 26, pad_box=False)
    compose(1200, 630, "og_1200x630.png", 130, 32, 28)
    avatars()
    print("Бренд-пакет готов.")
