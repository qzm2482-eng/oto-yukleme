"""Cover (1080x1920 jpg) from a frame of the same video + big hook text in the channel's cover style.
usage: python cover.py video.mp4 time_s "HOOK TEXT" empire|oddy out.jpg
"""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from common import font


def frame(video, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return Image.frombytes("RGB", (720, 1280), raw)


def fit(text, fname, size, maxw):
    f = font(fname, size)
    while f.getlength(text) > maxw and size > 40:
        size -= 4; f = font(fname, size)
    return f


def wrap(text, n=2):
    w = text.split()
    if len(w) <= 2:
        return [text]
    k = (len(w) + 1) // 2
    return [" ".join(w[:k]), " ".join(w[k:])]


def empire(im, hook):
    im = im.resize((1080, 1920), Image.LANCZOS).convert("RGBA")
    # hide small caption under the screen: navy band, then hook text
    d = ImageDraw.Draw(im)
    band = Image.new("RGBA", (1080, 330), (14, 18, 46, 255))
    im.alpha_composite(band, (0, 1135))
    lines = wrap(hook.upper())
    y = 1300 - (len(lines) - 1) * 70
    for ln in lines:
        f = fit(ln, "montserrat-latin-900.ttf", 128, 1000)
        sh = Image.new("RGBA", (1080, 200), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        ds.text((546, 108), ln, font=f, fill=(0, 0, 0, 220), anchor="mm")
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (0, y - 100))
        d = ImageDraw.Draw(im)
        d.text((540, y), ln, font=f, fill=(255, 212, 59), anchor="mm", stroke_width=7, stroke_fill=(16, 18, 34))
        y += 140
    return im.convert("RGB")


def oddy(im, hook):
    im = im.resize((1080, 1920), Image.LANCZOS).convert("RGBA")
    lines = wrap(hook)
    card = Image.new("RGBA", (980, 120 + 150 * len(lines)), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([14, 18, card.width - 1, card.height - 1], 34, fill=(0, 0, 0, 60))
    d.rounded_rectangle([0, 0, card.width - 14, card.height - 18], 34, fill=(255, 250, 238), outline=(35, 48, 56), width=8)
    y = 60 + 75
    for ln in lines:
        f = fit(ln, "caveat-latin-700.ttf", 170, 880)
        d.text(((card.width - 14) / 2, y), ln, font=f, fill=(193, 88, 61), anchor="mm")
        y += 150
    d.line([(160, card.height - 50), (card.width - 174, card.height - 56)], fill=(220, 164, 66), width=12)
    card = card.rotate(-2.5, Image.BICUBIC, expand=True)
    im.alpha_composite(card, ((1080 - card.width) // 2, 1440))
    return im.convert("RGB")


if __name__ == "__main__":
    v, t, hook, ch, out = sys.argv[1:6]
    im = frame(v, float(t))
    (empire if ch == "empire" else oddy)(im, hook).save(out, quality=88)
