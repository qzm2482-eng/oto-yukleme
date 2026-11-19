"""Empire in Minutes History renderer (locked STYLE.md look).
usage: python scripts/render/empire.py spec.json out.mp4 [--work DIR]
"""
import sys, os, json, math, re, hashlib
import numpy as np, requests
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, os.path.dirname(__file__))
from common import *

INK = (16, 18, 34)
SCR = (46, 118, 674, 742)          # inner screen box
SW, SH = SCR[2] - SCR[0], SCR[3] - SCR[1]
CAP_Y = 818                        # caption block centre
VOICE = dict(voice="en-US-ChristopherNeural", rate="+8%", pitch="-6Hz")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) EmpireInMinutes/1.0", "AIC-User-Agent": "EmpireInMinutes (github qzm2482-eng)"}


# ------------------------------------------------------------------ assets
def get_image(src, work):
    work = os.environ.get("IMG_CACHE", work)
    os.makedirs(os.path.join(work, "img"), exist_ok=True)
    if src.startswith("aic:"):
        iid = src[4:]
        p = os.path.join(work, "img", iid + ".jpg")
        if not os.path.exists(p):
            for size in ("1686,", "843,"):
                r = requests.get(f"https://www.artic.edu/iiif/2/{iid}/full/{size}/0/default.jpg", headers=UA, timeout=90)
                if r.ok and len(r.content) > 5000:
                    open(p, "wb").write(r.content); break
            else:
                raise RuntimeError("image download failed " + iid)
        return Image.open(p).convert("RGB")
    if src.startswith("commons:"):
        import hashlib
        from commons import download, thumb_url
        p = os.path.join(work, "img", hashlib.md5(src.encode()).hexdigest() + ".jpg")
        if not os.path.exists(p):
            download(thumb_url(src[8:]), p)
        return Image.open(p).convert("RGB")
    if src.startswith("http"):
        import hashlib
        from commons import download
        p = os.path.join(work, "img", hashlib.md5(src.encode()).hexdigest() + ".jpg")
        if not os.path.exists(p):
            download(src, p)
        return Image.open(p).convert("RGB")
    return Image.open(src).convert("RGB")


def background():
    im = Image.new("RGB", (W, H))
    a = np.zeros((H, W, 3), np.float32)
    top, bot = np.array([18, 22, 54]), np.array([30, 28, 72])
    for y in range(H):
        a[y] = top + (bot - top) * (y / H)
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 48):
        d.line([(x, 0), (x, H)], fill=(36, 42, 86), width=1)
    for y in range(0, H, 48):
        d.line([(0, y), (W, y)], fill=(36, 42, 86), width=1)
    # desk (lower third)
    d.rectangle([0, 1092, W, H], fill=(122, 76, 42))
    d.rectangle([0, 1092, W, 1112], fill=(150, 98, 56))
    d.line([(0, 1092), (W, 1092)], fill=INK, width=6)
    for y in (1150, 1210):
        d.line([(30, y), (W - 30, y)], fill=(104, 64, 36), width=3)
    g = grain((W, H), 9, 3)
    im = Image.blend(im, Image.merge("RGB", (g, g, g)), 0.06)
    return im


def monitor_layer():
    L = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = (SCR[0] - 20) * 2, (SCR[1] - 20) * 2, (SCR[2] + 20) * 2, (SCR[3] + 26) * 2
    d.rounded_rectangle([x0 + 10, y0 + 16, x1 + 10, y1 + 16], 52, fill=(8, 10, 24, 140))
    d.rounded_rectangle([x0, y0, x1, y1], 52, fill=(47, 143, 139), outline=INK, width=12)
    d.rounded_rectangle([x0 + 14, y0 + 14, x1 - 14, y0 + 40], 20, fill=(78, 176, 170))
    d.ellipse([x1 - 70, y1 - 38, x1 - 50, y1 - 18], fill=(150, 255, 160), outline=INK, width=4)
    sx0, sy0, sx1, sy1 = [v * 2 for v in SCR]
    d.rounded_rectangle([sx0 - 6, sy0 - 6, sx1 + 6, sy1 + 6], 30, fill=INK)
    d.rounded_rectangle([sx0, sy0, sx1, sy1], 26, fill=(0, 0, 0, 0))
    return L.resize((W, H), Image.LANCZOS)


def title_layer(text):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font("montserrat-latin-900.ttf", 40)
    while f.getlength(text) > 600 and f.size > 24:
        f = font("montserrat-latin-900.ttf", f.size - 2)
    tw = f.getlength(text)
    big = Image.new("RGBA", (W * 2, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    bw = tw * 2 + 80
    x0 = (W * 2 - bw) / 2
    d.rounded_rectangle([x0 + 6, 18, x0 + bw + 6, 138], 30, fill=(8, 10, 24, 150))
    d.rounded_rectangle([x0, 10, x0 + bw, 130], 30, fill=(245, 230, 196), outline=INK, width=8)
    f2 = font("montserrat-latin-900.ttf", f.size * 2)
    d.text((W, 72), text, font=f2, fill=(26, 32, 70), anchor="mm")
    L.alpha_composite(big.resize((W, 100), Image.LANCZOS), (0, 8))
    return L


# ------------------------------------------------------------------ narrator (bottom, lip-synced)
def narrator_parts():
    S = 2
    def canvas():
        return Image.new("RGBA", (360 * S, 300 * S), (0, 0, 0, 0))
    cx, cy, r = 180 * S, 120 * S, 78 * S
    body = canvas(); d = ImageDraw.Draw(body)
    # shoulders / jacket
    d.rounded_rectangle([cx - 120 * S, cy + 70 * S, cx + 120 * S, cy + 260 * S], 70 * S, fill=(38, 54, 96), outline=INK, width=6 * S)
    d.polygon([(cx - 34 * S, cy + 72 * S), (cx, cy + 140 * S), (cx + 34 * S, cy + 72 * S)], fill=(236, 230, 214), outline=INK)
    d.polygon([(cx - 10 * S, cy + 96 * S), (cx + 10 * S, cy + 96 * S), (cx, cy + 150 * S)], fill=(200, 60, 52))
    d.ellipse([cx + 52 * S, cy + 110 * S, cx + 70 * S, cy + 128 * S], fill=(229, 193, 88), outline=INK, width=3 * S)
    # neck + head
    d.rectangle([cx - 22 * S, cy + 50 * S, cx + 22 * S, cy + 84 * S], fill=(232, 186, 146), outline=INK, width=5 * S)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(242, 201, 160), outline=INK, width=6 * S)
    # ears
    for sx in (-1, 1):
        d.ellipse([cx + sx * r - 14 * S, cy - 4 * S, cx + sx * r + 14 * S, cy + 26 * S], fill=(236, 190, 150), outline=INK, width=5 * S)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=6 * S)
    # hair cap
    d.chord([cx - r - 2 * S, cy - r - 8 * S, cx + r + 2 * S, cy + r * 0.35], 180, 360, fill=(58, 40, 30), outline=INK, width=6 * S)
    # brows
    for sx in (-1, 1):
        d.line([(cx + sx * 22 * S, cy - 14 * S), (cx + sx * 46 * S, cy - 20 * S)], fill=INK, width=6 * S)
    # cheeks
    for sx in (-1, 1):
        d.ellipse([cx + sx * 44 * S - 12 * S, cy + 22 * S, cx + sx * 44 * S + 12 * S, cy + 36 * S], fill=(240, 160, 140))
    eyes_open = canvas(); d = ImageDraw.Draw(eyes_open)
    for sx in (-1, 1):
        d.ellipse([cx + sx * 32 * S - 9 * S, cy + 0 * S, cx + sx * 32 * S + 9 * S, cy + 20 * S], fill=INK)
        d.ellipse([cx + sx * 32 * S - 3 * S, cy + 4 * S, cx + sx * 32 * S + 2 * S, cy + 9 * S], fill=(255, 255, 255))
    eyes_closed = canvas(); d = ImageDraw.Draw(eyes_closed)
    for sx in (-1, 1):
        d.arc([cx + sx * 32 * S - 11 * S, cy + 2 * S, cx + sx * 32 * S + 11 * S, cy + 18 * S], 20, 160, fill=INK, width=5 * S)
    mouths = []
    for k in range(6):
        m = canvas(); d = ImageDraw.Draw(m)
        o = k / 5
        mw, mh = (24 + 6 * o) * S, (3 + 22 * o) * S
        my = cy + 46 * S
        if k == 0:
            d.arc([cx - 20 * S, my - 14 * S, cx + 20 * S, my + 8 * S], 20, 160, fill=INK, width=5 * S)
        else:
            d.ellipse([cx - mw, my - mh / 2 - 3 * S, cx + mw, my + mh / 2 + 3 * S], fill=(120, 30, 40), outline=INK, width=5 * S)
            if k >= 2:
                d.chord([cx - mw * 0.6, my + mh * 0.05, cx + mw * 0.6, my + mh / 2 + 3 * S], 0, 180, fill=(230, 110, 120))
        mouths.append(m)
    sm = lambda im: im.resize((360, 300), Image.LANCZOS)
    return sm(body), sm(eyes_open), sm(eyes_closed), [sm(m) for m in mouths]


# ------------------------------------------------------------------ cartoon scenes inside the screen
def character(expr="scared", S=2, hood=(232, 118, 44)):
    im = Image.new("RGBA", (300 * S, 340 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy, r = 150 * S, 120 * S, 82 * S
    d.rounded_rectangle([cx - 110 * S, cy + 70 * S, cx + 110 * S, cy + 330 * S], 80 * S, fill=hood, outline=INK, width=7 * S)
    d.rounded_rectangle([cx - 40 * S, cy + 150 * S, cx + 40 * S, cy + 176 * S], 8 * S, fill=(250, 245, 230), outline=INK, width=4 * S)
    d.text((cx, cy + 163 * S), "YOU", font=font("montserrat-latin-900.ttf", 20 * S), fill=INK, anchor="mm")
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(246, 210, 172), outline=INK, width=7 * S)
    ey = cy + 4 * S
    if expr == "shock":
        for sx in (-1, 1):
            d.ellipse([cx + sx * 30 * S - 14 * S, ey - 14 * S, cx + sx * 30 * S + 14 * S, ey + 14 * S], fill=(255, 255, 255), outline=INK, width=5 * S)
            d.ellipse([cx + sx * 30 * S - 5 * S, ey - 5 * S, cx + sx * 30 * S + 5 * S, ey + 5 * S], fill=INK)
        d.ellipse([cx - 16 * S, cy + 34 * S, cx + 16 * S, cy + 66 * S], fill=(120, 30, 40), outline=INK, width=5 * S)
    elif expr == "determined":
        for sx in (-1, 1):
            d.ellipse([cx + sx * 30 * S - 8 * S, ey - 8 * S, cx + sx * 30 * S + 8 * S, ey + 8 * S], fill=INK)
            d.line([(cx + sx * 16 * S, ey - 22 * S), (cx + sx * 46 * S, ey - 30 * S)], fill=INK, width=6 * S)
        d.line([(cx - 22 * S, cy + 48 * S), (cx + 22 * S, cy + 44 * S)], fill=INK, width=6 * S)
    elif expr == "happy":
        for sx in (-1, 1):
            d.arc([cx + sx * 30 * S - 12 * S, ey - 8 * S, cx + sx * 30 * S + 12 * S, ey + 10 * S], 200, 340, fill=INK, width=6 * S)
        d.chord([cx - 26 * S, cy + 26 * S, cx + 26 * S, cy + 62 * S], 0, 180, fill=(120, 30, 40), outline=INK, width=5 * S)
    else:  # scared
        for sx in (-1, 1):
            d.ellipse([cx + sx * 30 * S - 8 * S, ey - 8 * S, cx + sx * 30 * S + 8 * S, ey + 8 * S], fill=INK)
            d.line([(cx + sx * 14 * S, ey - 20 * S), (cx + sx * 44 * S, ey - 14 * S)], fill=INK, width=6 * S)
        pts = [(cx - 24 * S + i * 8 * S, cy + 50 * S + (6 * S if i % 2 else 0)) for i in range(7)]
        d.line(pts, fill=INK, width=5 * S)
        d.polygon([(cx + 70 * S, cy - 40 * S), (cx + 82 * S, cy - 14 * S), (cx + 58 * S, cy - 14 * S)], fill=(120, 200, 255), outline=INK)
        d.ellipse([cx + 58 * S, cy - 26 * S, cx + 82 * S, cy - 2 * S], fill=(120, 200, 255), outline=INK, width=4 * S)
    return im.resize((300, 340), Image.LANCZOS)


def label_card(text, size=44, fill=(245, 230, 196), fg=(26, 32, 70), rot=0):
    f = font("montserrat-latin-900.ttf", size * 2)
    tw = f.getlength(text)
    im = Image.new("RGBA", (int(tw + 120), size * 2 + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 12, im.width - 2, im.height - 2], 26, fill=(8, 10, 24, 140))
    d.rounded_rectangle([0, 0, im.width - 10, im.height - 14], 26, fill=fill, outline=INK, width=8)
    d.text(((im.width - 10) / 2, (im.height - 14) / 2), text, font=f, fill=fg, anchor="mm")
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    return im.rotate(rot, Image.BICUBIC, expand=True) if rot else im


def badge(icon, color=(229, 193, 88), size=150):
    S = 2
    im = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([10, 16, size * S - 2, size * S - 2], fill=(8, 10, 24, 140))
    d.ellipse([0, 0, size * S - 12, size * S - 16], fill=color, outline=INK, width=9)
    ic = svg_icon(icon, int(size * S * 0.56), color="#101222", stroke=2.2)
    im.alpha_composite(ic, ((size * S - 12 - ic.width) // 2, (size * S - 16 - ic.height) // 2))
    return im.resize((size, size), Image.LANCZOS)


def cartoon_scene(sc):
    """static layer (oversized for gentle push-in)"""
    PW, PH = int(SW * 1.08), int(SH * 1.08)
    bg = tuple(int(sc.get("bg", "#2b3a6b")[i:i + 2], 16) for i in (1, 3, 5))
    im = Image.new("RGB", (PW, PH), bg)
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW]
    v = 1 - 0.45 * (((xx - PW / 2) / PW) ** 2 + ((yy - PH * 0.45) / PH) ** 2) * 2.2
    a *= v[..., None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    rays = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
    # floor + soft rays
    for k in range(10):
        ang = k / 10 * math.pi * 2
        d.polygon([(PW / 2, PH * 0.45), (PW / 2 + math.cos(ang) * 900, PH * 0.45 + math.sin(ang) * 900),
                   (PW / 2 + math.cos(ang + 0.2) * 900, PH * 0.45 + math.sin(ang + 0.2) * 900)], fill=(255, 255, 255, 16))
    im.alpha_composite(rays); d = ImageDraw.Draw(im)
    d.rectangle([0, PH * 0.78, PW, PH], fill=tuple(int(c * 0.6) for c in bg) + (255,))
    d.line([(0, PH * 0.78), (PW, PH * 0.78)], fill=INK, width=5)
    ch = character(sc.get("expr", "scared"))
    ch = ch.resize((int(ch.width * 1.15), int(ch.height * 1.15)), Image.LANCZOS)
    im.alpha_composite(ch, (int(PW * 0.5 - ch.width / 2 + sc.get("cx", 0)), int(PH - ch.height + 40)))
    icons = sc.get("icons", [])
    spots = [(0.15, 0.36), (0.85, 0.36), (0.14, 0.66), (0.86, 0.66)]
    for (ic, (px, py)) in zip(icons, spots):
        b = badge(ic, size=140)
        im.alpha_composite(b, (int(PW * px - 70), int(PH * py - 70)))
    if sc.get("label"):
        lc = label_card(sc["label"], 40, rot=sc.get("rot", -3))
        im.alpha_composite(lc, (int(PW / 2 - lc.width / 2), int(PH * 0.06)))
    g = grain((PW, PH), 10, 7)
    rgb = Image.blend(im.convert("RGB"), Image.merge("RGB", (g, g, g)), 0.05)
    return rgb


def end_scene():
    PW, PH = int(SW * 1.08), int(SH * 1.08)
    im = Image.new("RGB", (PW, PH)); a = np.zeros((PH, PW, 3), np.float32)
    a[:, :PW // 2] = (28, 92, 58); a[:, PW // 2:] = (120, 28, 34)
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.line([(PW // 2, 0), (PW // 2, PH)], fill=INK, width=8)
    ch = character("shock"); im.alpha_composite(ch, (PW // 2 - ch.width // 2, PH - ch.height + 30))
    s = label_card("SURVIVE", 50, fill=(70, 214, 120), fg=(10, 40, 20), rot=4)
    im.alpha_composite(s, (int(PW * 0.27 - s.width / 2), int(PH * 0.10)))
    t = label_card("DEAD", 56, fill=(255, 84, 84), fg=(50, 6, 8), rot=-4)
    im.alpha_composite(t, (int(PW * 0.75 - t.width / 2), int(PH * 0.10)))
    o = label_card("or", 30); im.alpha_composite(o, (PW // 2 - o.width // 2, int(PH * 0.30)))
    return im.convert("RGB")


# ------------------------------------------------------------------ image scenes
def prep_image(img, sc):
    z1 = max(sc.get("zoom", [1.0, 1.12]))
    k = max(SW * 1.25 / img.width, SH * 1.25 / img.height) * z1
    k = min(k, 1.0) if img.width * k > 4000 else k
    return img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)


class Scene:
    def __init__(self, sc, work, t0, t1):
        self.sc, self.t0, self.t1 = sc, t0, t1
        self.type = sc["type"]
        if self.type == "img":
            raw = get_image(sc["src"], work)
            if sc.get("crop"):
                x0, y0, x1, y1 = sc["crop"]; raw = raw.crop((int(x0 * raw.width), int(y0 * raw.height), int(x1 * raw.width), int(y1 * raw.height)))
            self.frame_mode = sc.get("reveal") == "frame"
            if self.frame_mode:
                fw, fh = int(SW * 0.80), int(SH * 0.80)
                kk = min(fw / raw.width, fh / raw.height)
                pic = raw.resize((int(raw.width * kk), int(raw.height * kk)), Image.LANCZOS)
                card = Image.new("RGBA", (pic.width + 36, pic.height + 36), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
                d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], 10, fill=(232, 212, 168), outline=INK, width=5)
                card.paste(pic, (18, 18)); ImageDraw.Draw(card).rectangle([18, 18, 18 + pic.width, 18 + pic.height], outline=INK, width=3)
                self.card = card
                blur = raw.resize((SW // 4, SH // 4)).filter(ImageFilter.GaussianBlur(6)).resize((int(SW * 1.1), int(SH * 1.1)), Image.BICUBIC)
                self.back = Image.blend(blur, Image.new("RGB", blur.size, (14, 16, 40)), 0.55)
            else:
                self.img = prep_image(raw, sc)
        elif self.type == "cartoon":
            self.img = cartoon_scene(sc)
        elif self.type == "end":
            self.img = end_scene()

    def render(self, t):
        dur = max(0.5, self.t1 - self.t0)
        p = (t - self.t0) / dur
        sc = self.sc
        if self.type == "img" and self.frame_mode:
            z = 1.0 + 0.04 * p
            bx = self.back.crop(((self.back.width - SW) // 2, (self.back.height - SH) // 2, (self.back.width - SW) // 2 + SW, (self.back.height - SH) // 2 + SH))
            out = bx.convert("RGBA")
            drop = ease((t - self.t0) / 0.7)
            cz = 0.94 + 0.06 * drop + 0.03 * p
            card = self.card.resize((int(self.card.width * cz), int(self.card.height * cz)), Image.BICUBIC)
            sh = Image.new("RGBA", card.size, (0, 0, 0, 120))
            x = (SW - card.width) // 2; y = int((SH - card.height) / 2 - 70 * (1 - drop))
            out.alpha_composite(sh, (x + 10, y + 14)); out.alpha_composite(card, (x, y))
            return out.convert("RGB")
        if self.type == "img":
            z0, z1 = sc.get("zoom", [1.0, 1.12])
            f0 = sc.get("focus", [0.5, 0.5]); f1 = sc.get("focus2", f0)
            e = ease(p) * 0.6 + p * 0.4
            z = z0 + (z1 - z0) * e
            fx = f0[0] + (f1[0] - f0[0]) * e; fy = f0[1] + (f1[1] - f0[1]) * e
            iw, ih = self.img.size
            base = max(SW / iw, SH / ih)  # scale that covers at zoom 1 (in source px)
            s = 1 / (base * z)          # source px per output px
            vw, vh = SW * s, SH * s
            cx = min(max(fx * iw, vw / 2), iw - vw / 2); cy = min(max(fy * ih, vh / 2), ih - vh / 2)
            return self.img.transform((SW, SH), Image.AFFINE, (s, 0, cx - vw / 2, 0, s, cy - vh / 2), Image.BICUBIC)
        # cartoon / end: gentle push-in
        iw, ih = self.img.size
        z = 1.0 + 0.06 * ease(p)
        if self.type == "end":
            z = 1.0 + 0.03 * math.sin(p * math.pi)
        s = (iw / 1.08) / SW / z
        vw, vh = SW * s, SH * s
        return self.img.transform((SW, SH), Image.AFFINE, (s, 0, (iw - vw) / 2, 0, s, (ih - vh) / 2), Image.BICUBIC)


def reveal_mask(kind, q, seed=0):
    q = ease(q)
    m = Image.new("L", (SW, SH), 0); d = ImageDraw.Draw(m)
    if kind == "iris":
        r = q * math.hypot(SW, SH) / 2 * 1.05
        d.ellipse([SW / 2 - r, SH / 2 - r, SW / 2 + r, SH / 2 + r], fill=255)
        return m.filter(ImageFilter.GaussianBlur(6))
    if kind == "wipe":
        x = -80 + q * (SW + 160)
        d.polygon([(0, 0), (x + 60, 0), (x - 60, SH), (0, SH)], fill=255)
        return m.filter(ImageFilter.GaussianBlur(14))
    return Image.new("L", (SW, SH), int(255 * q))


# ------------------------------------------------------------------ captions
def build_chunks(beats, timing):
    chunks = []
    wi = 0
    for b in beats:
        words = b["text"].split()
        keys = set(norm(k) for k in b.get("keys", []))
        cur = []
        for k, w in enumerate(words):
            cur.append((w, wi + k, norm(w) in keys))
            end_punct = w[-1] in ".?!,;:—" if w else False
            if len(cur) >= 4 or (end_punct and len(cur) >= 2) or (w[-1] in ".?!" and len(cur) >= 1):
                chunks.append(cur); cur = []
        if cur:
            if chunks and len(cur) <= 1 and len(chunks[-1]) < 6 and chunks[-1][-1][0][-1] not in ".?!":
                chunks[-1].extend(cur)
            else:
                chunks.append(cur)
        wi += len(words)
    out = []
    for i, c in enumerate(chunks):
        st = timing[c[0][1]][0]
        en = timing[chunks[i + 1][0][1]][0] if i + 1 < len(chunks) else timing[c[-1][1]][1] + 0.6
        out.append(dict(words=c, t0=st - 0.05, t1=en))
    return out


CF = None
def caption_layout(chunk):
    global CF
    CF = CF or font("montserrat-latin-900.ttf", 46)
    words = [w.upper() for w, _, _ in chunk["words"]]
    space = CF.getlength(" ")
    lines = [[]]; lw = 0
    for i, w in enumerate(words):
        wl = CF.getlength(w)
        if lines[-1] and lw + space + wl > 650:
            lines.append([]); lw = 0
        lines[-1].append(i); lw += (space if lw else 0) + wl
    pos = {}
    lh = 56
    y0 = CAP_Y - (len(lines) - 1) * lh / 2
    for li, ln in enumerate(lines):
        tot = sum(CF.getlength(words[i]) for i in ln) + space * (len(ln) - 1)
        x = W / 2 - tot / 2
        for i in ln:
            pos[i] = (x, y0 + li * lh); x += CF.getlength(words[i]) + space
    return pos


def draw_caption(frame, chunk, t, timing, cache):
    key = id(chunk)
    if key not in cache:
        cache[key] = caption_layout(chunk)
    pos = cache[key]
    L = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    sh = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    oy = CAP_Y - 100
    for i, (w, wi, hot) in enumerate(chunk["words"]):
        ws = timing[wi][0]
        if t < ws - 0.04:
            continue
        x, y = pos[i]
        col = (255, 212, 59) if hot else (255, 255, 255)
        ds.text((x + 3, y - oy + 5), w.upper(), font=CF, fill=(0, 0, 0, 200), anchor="lm")
        d.text((x, y - oy), w.upper(), font=CF, fill=col, anchor="lm", stroke_width=3, stroke_fill=(20, 20, 30))
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    frame.alpha_composite(sh, (0, oy)); frame.alpha_composite(L, (0, oy))


# ------------------------------------------------------------------ main
def render(spec, out_mp4, work):
    os.makedirs(work, exist_ok=True)
    beats = spec["beats"]
    text = " ".join(b["text"] for b in beats)
    mp3 = os.path.join(work, "voice.mp3")
    v = dict(VOICE); v.update(spec.get("voice", {}))
    tw = tts(text, v["voice"], mp3, v["rate"], v["pitch"])
    voice = load_wav(mp3)
    words = text.split()
    timing = align(words, tw)
    lead = 0.15
    timing = [(a + lead, b + lead) for a, b in timing]
    total = len(voice) / SR + lead + 1.2
    n = int(total * FPS)
    # scene times
    starts = []; wi = 0
    for b in beats:
        starts.append(0.0 if not starts else timing[wi][0] - 0.25); wi += len(b["text"].split())
    scenes = []
    for i, b in enumerate(beats):
        t1 = starts[i + 1] if i + 1 < len(beats) else total
        scenes.append(Scene(b["scene"], work, starts[i], t1 + 0.6))
    chunks = build_chunks(beats, timing)
    env = envelope(np.concatenate([np.zeros(int(lead * SR)), voice]))
    bg = background(); mon = monitor_layer(); tl = title_layer(spec["title_card"])
    body, eo, ec, mouths = narrator_parts()
    base = bg.convert("RGBA")
    NX, NY = W // 2 - 180, 852
    cache = {}
    def frames():
        sm = 0.0
        for fi in range(n):
            t = fi / FPS
            si = max(i for i in range(len(scenes)) if scenes[i].t0 <= t)
            cur = scenes[si].render(t)
            tr = 0.55
            if si > 0 and t - scenes[si].t0 < tr:
                prev = scenes[si - 1].render(t)
                q = (t - scenes[si].t0) / tr
                kind = beats[si]["scene"].get("reveal", "fade")
                if kind == "frame":
                    kind = "fade"
                cur = Image.composite(cur, prev, reveal_mask(kind, q))
            fr = base.copy()
            fr.paste(cur, (SCR[0], SCR[1]), rounded_mask((SW, SH), 26))
            fr.alpha_composite(mon); fr.alpha_composite(tl)
            # narrator
            e = env[min(fi, len(env) - 1)]
            sm = sm * 0.35 + e * 0.65
            lvl = int(round(min(1, sm * 1.1) * 5))
            blink = (fi % 104) in (0, 1, 2) and fi > 5
            fr.alpha_composite(body, (NX, NY))
            fr.alpha_composite(ec if blink else eo, (NX, NY))
            fr.alpha_composite(mouths[lvl], (NX, NY))
            # desk front edge in front of narrator
            fr.alpha_composite(desk_front, (0, 1092))
            for c in chunks:
                if c["t0"] <= t < c["t1"]:
                    draw_caption(fr, c, t, timing, cache); break
            yield np.asarray(fr.convert("RGB"))
    desk_front = bg.crop((0, 1092, W, H)).convert("RGBA")
    bed = music_box(total + 1, seed=hash(spec["title_card"]) % 1000)
    mix_and_encode(frames(), n, voice, bed, spec.get("bed_db", 19), [], out_mp4, voice_delay=lead, tmpdir=work)
    return dict(duration=total, words=len(words))


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    work = sys.argv[3] if len(sys.argv) > 3 else "/tmp/empire_work"
    print(render(spec, sys.argv[2], work))
