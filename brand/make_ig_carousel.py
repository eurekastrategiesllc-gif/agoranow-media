"""AgoraNow Instagram carousel renderer.

Usage: python3 make_ig_carousel.py carousel.json OUT_PREFIX
Writes OUT_PREFIX_01.jpg ... (1080x1350 JPEG).

carousel.json = {"slides": [
  {"type": "cover", "category": "Congress", "hook": "..."},
  {"type": "point", "headline": "...", "body": ["sentence", "• bullet", ...]},
  {"type": "cta", "cta": "one-line takeaway"}
]}

Uses the real brand header (laurel logo + AGORANOW wordmark) and background
from brand/reference_cover.png, which sits next to this script.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REF = Image.open(os.path.join(HERE, "reference_cover.png")).convert("RGB")
W, H = REF.size  # 1080 x 1350
WHITE, SOFT, GOLD, RED = (255, 255, 255), (205, 214, 228), (212, 175, 85), (200, 16, 46)
FONTS = "/usr/share/fonts/truetype/dejavu/"
SERIF, SANS_B, SANS = FONTS + "DejaVuSerif-Bold.ttf", FONTS + "DejaVuSans-Bold.ttf", FONTS + "DejaVuSans.ttf"
font = lambda p, s: ImageFont.truetype(p, s)


def base():
    strip = REF.crop((0, 0, 20, H)).resize((W, H))  # background gradient + red bottom bar
    return strip, ImageDraw.Draw(strip)


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) > max_w and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur: lines.append(cur)
    return lines


def header(im):
    im.paste(REF.crop((0, 0, W, 320)), (0, 0))  # logo + wordmark (above the category pill)


def pill(d, text, y=338):
    f = font(SANS_B, 28); tw = d.textlength(text.upper(), font=f)
    d.rounded_rectangle([W / 2 - tw / 2 - 26, y, W / 2 + tw / 2 + 26, y + 52], 16, fill=RED)
    d.text((W / 2, y + 26), text.upper(), font=f, fill=WHITE, anchor="mm")


def centered(d, text, f, cy, max_w, lh, color=WHITE):
    lines = wrap(d, text, f, max_w); y = cy - lh * len(lines) / 2
    for ln in lines:
        d.text((W / 2, y), ln, font=f, fill=color, anchor="ma"); y += lh


def cover(s):
    im, d = base(); header(im); pill(d, s["category"])
    centered(d, s["hook"], font(SERIF, 72), 700, 920, 88)
    d.text((W / 2, 1200), "Swipe to see the receipts  →", font=font(SANS_B, 32), fill=GOLD, anchor="mm")
    return im


def point(s, n, total):
    im, d = base()
    d.text((80, 72), "AGORANOW", font=font(SANS_B, 32), fill=WHITE)
    d.rectangle([80, 122, 180, 128], fill=GOLD)
    d.text((W - 80, 72), f"{n} / {total}", font=font(SANS_B, 32), fill=GOLD, anchor="ra")
    y = 190; fh = font(SERIF, 64)
    for ln in wrap(d, s["headline"], fh, 920):
        d.text((80, y), ln, font=fh, fill=WHITE); y += 82
    y += 24; fb = font(SANS, 40)
    for para in s["body"]:
        bullet = para.startswith("•")
        txt = para.lstrip("•").strip()
        for i, ln in enumerate(wrap(d, txt, fb, 860 if bullet else 920)):
            if bullet and i == 0:
                d.text((80, y), "•", font=fb, fill=GOLD)
            d.text((118 if bullet else 80, y), ln, font=fb, fill=SOFT); y += 56
        y += 22
    if y > H - 60:
        raise SystemExit(f"Slide {n}: text too long ({y}px) — shorten it")
    return im


def cta(s):
    im, d = base(); header(im)
    centered(d, s["cta"], font(SERIF, 64), 700, 900, 82)
    d.text((W / 2, 1060), "Your democracy. Your data.", font=font(SANS_B, 38), fill=GOLD, anchor="mm")
    d.text((W / 2, 1125), "agoranow.org  ·  link in bio", font=font(SANS, 32), fill=SOFT, anchor="mm")
    return im


if __name__ == "__main__":
    slides = json.load(open(sys.argv[1]))["slides"]; out = sys.argv[2]
    total = sum(1 for s in slides if s["type"] == "point"); k = 0
    for i, s in enumerate(slides, 1):
        if s["type"] == "cover": im = cover(s)
        elif s["type"] == "cta": im = cta(s)
        else: k += 1; im = point(s, k, total)
        path = f"{out}_{i:02d}.jpg"; im.save(path, quality=92); print(path)
