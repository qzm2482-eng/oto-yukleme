"""ODDYzenTC renderer (locked STYLE.md look).
usage: python scripts/render/oddy.py spec.json out.mp4 [work]
spec: {"slides":[{"tag":"GUESS THE COUNTRY","text":"spoken text","items":[...]}, ...]}
item kinds (each may carry "at": a word from the slide's spoken text; appears when that word is spoken):
  {"k":"text","s":"line","size":54,"y":0.2,"color":"ink|terra|teal"}
  {"k":"big","s":"148.8","unit":"liters / year","y":0.5}
  {"k":"flag","cc":"cz","name":"Czechia","y":0.3,"w":300}
  {"k":"icon","name":"pig","y":0.45,"size":220,"x":0.5}
  {"k":"flags","ccs":["us","de"],"y":0.6}
  {"k":"bars","rows":[["de","Germany",10],["cz","Czechia",148.8]],"fmt":"{:.0f}","unit":"L"}
  {"k":"question","y":0.45}
"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from common import *

INK = (31, 36, 33); NAVY = (35, 48, 56); TERRA = (193, 88, 61); MUST = (220, 164, 66); TEAL = (63, 110, 120); SAGE = (138, 160, 120)
PAPER = (247, 243, 232)
COL = {"ink": NAVY, "terra": TERRA, "teal": TEAL, "mustard": MUST, "sage": SAGE}
CY0, CY1 = 300, 1010      # content area (keeps clear of bottom overlay)
VOICE = dict(voice="en-US-BrianNeural", rate="+4%", pitch="+0Hz")


def paper():
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for x in range(0, W, 36):
        d.line([(x, 0), (x, H)], fill=(228, 222, 206), width=1)
    for y in range(0, H, 36):
        d.line([(0, y), (W, y)], fill=(228, 222, 206), width=1)
    g = grain((W, H), 8, 5)
    return Image.blend(im, Image.merge("RGB", (g, g, g)), 0.04)


def header():
    L = Image.new("RGBA", (W * 2, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = font("caveat-latin-700.ttf", 170)
    d.text((W, 120), "Did you know?", font=f, fill=NAVY, anchor="mm")
    # mustard brush underline (curved, tapered)
    pts = []
    for i in range(61):
        x = W - 330 + i * 11; y = 205 + 10 * math.sin(i / 60 * math.pi) - 6 * (i / 60)
        pts.append((x, y))
    for i in range(len(pts) - 1):
        w = int(6 + 16 * math.sin(i / 60 * math.pi))
        d.line([pts[i], pts[i + 1]], fill=MUST, width=w)
    return L.resize((W, 130), Image.LANCZOS)


def tag_img(text):
    f = font("fredoka-latin-600.ttf", 64)
    s = f"[{text}]"
    tw = f.getlength(s)
    im = Image.new("RGBA", (int(tw + 80), 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, im.width - 5, 115], 18, fill=(255, 252, 244), outline=NAVY, width=6)
    d.text((im.width / 2, 60), s, font=f, fill=NAVY, anchor="mm")
    return im.resize((im.width // 2, 60), Image.LANCZOS)


def hand_flag(cc, w):
    fl = flag_img(cc, w)
    pad = 10
    im = Image.new("RGBA", (fl.width + pad * 2 + 8, fl.height + pad * 2 + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad + 6, pad + 8, pad + fl.width + 6, pad + fl.height + 8], 14, fill=(0, 0, 0, 40))
    m = rounded_mask(fl.size, 14)
    im.paste(fl, (pad, pad), m)
    d.rounded_rectangle([pad - 2, pad - 2, pad + fl.width + 1, pad + fl.height + 1], 15, outline=NAVY, width=5)
    return im


def text_img(s, size, color, fnt="patrick-hand-latin-400.ttf", maxw=540):
    f = font(fnt, size * 2)
    words = s.split(); lines = [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if f.getlength(t) > maxw * 2 and lines[-1]:
            lines.append(w)
        else:
            lines[-1] = t
    lh = int(size * 2 * 1.15)
    im = Image.new("RGBA", (maxw * 2, lh * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((maxw, lh * i + lh // 2 + 6), ln, font=f, fill=color, anchor="mm")
    return im.resize((maxw, im.height // 2), Image.LANCZOS)


def big_img(s, unit=None):
    f = font("caveat-latin-700.ttf", 300)
    tw = f.getlength(s)
    uw = font("patrick-hand-latin-400.ttf", 84).getlength(unit) if unit else 0
    im = Image.new("RGBA", (int(max(tw, uw, 600) + 60), 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((im.width / 2 + 6, 176), s, font=f, fill=(0, 0, 0, 40), anchor="mm")
    d.text((im.width / 2, 170), s, font=f, fill=TERRA, anchor="mm")
    if unit:
        fu = font("patrick-hand-latin-400.ttf", 84)
        d.text((im.width / 2, 360), unit, font=fu, fill=NAVY, anchor="mm")
    im = im.resize((int(im.width * 0.62), int(im.height * 0.62)), Image.LANCZOS)
    if im.width > 520:
        k = 520 / im.width; im = im.resize((520, int(im.height * k)), Image.LANCZOS)
    return im


def question_img():
    im = Image.new("RGBA", (520, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g = svg_icon("world", 360, color="#233038", stroke=1.6)
    d.ellipse([90, 90, 430, 430], fill=(210, 230, 228))
    im.alpha_composite(g, (80, 80))
    f = font("caveat-latin-700.ttf", 240)
    d.text((410, 120), "?", font=f, fill=TERRA, anchor="mm")
    d.text((120, 150), "?", font=font("caveat-latin-700.ttf", 150), fill=MUST, anchor="mm")
    return im.resize((400, 400), Image.LANCZOS)


def icon_img(name, size, accent=None):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if accent:
        c = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5))
        d.ellipse([size * 0.12, size * 0.16, size * 0.92, size * 0.96], fill=c + (255,))
    ic = svg_icon(name, int(size * 0.86), color="#233038", stroke=1.5)
    im.alpha_composite(ic, (int(size * 0.07), int(size * 0.07)))
    return im


class Bars:
    def __init__(self, it):
        self.rows = it["rows"]; self.fmt = it.get("fmt", "{:,.0f}"); self.unit = it.get("unit", "")
        self.vmax = max(r[2] for r in self.rows)
        self.flags = [icon_img(r[0][2:], 100 if len(self.rows) < 5 else 78, "#F2D9A0") if r[0].startswith("i:") else hand_flag(r[0], 92 if len(self.rows) < 5 else 68) for r in self.rows]
        self.f = font("patrick-hand-latin-400.ttf", 36); self.fv = font("caveat-latin-700.ttf", 56)

    def draw(self, canvas, top, t_rows, t):
        n = len(self.rows); gap = min(150, 560 / n)
        d = ImageDraw.Draw(canvas)
        x0, xmax = 170, 420
        for i, r in enumerate(self.rows):
            ts = t_rows[i]
            if t < ts:
                continue
            y = top + i * gap
            p = ease((t - ts) / 0.7)
            fl = self.flags[i]
            a = min(1, (t - ts) / 0.2)
            canvas.alpha_composite(fl, (28, int(y)))
            d.text((32, int(y + fl.height + 2)), r[1], font=self.f, fill=NAVY, anchor="lt")
            L = (xmax - x0) * (r[2] / self.vmax) * p
            winner = i == n - 1
            col = TERRA if winner else (TEAL if i % 2 == 0 else SAGE)
            yb = y + 14
            d.rounded_rectangle([x0, yb, x0 + max(L, 12), yb + 60], 14, fill=col, outline=NAVY, width=4)
            if p > 0.3:
                lab = r[3] if len(r) > 3 and p >= 0.9 else self.fmt.format(r[2] * min(1, p * 1.1)) + self.unit
                d.text((x0 + max(L, 12) + 12, yb + 30), lab, font=self.fv, fill=TERRA if winner else NAVY, anchor="lm")


def build_slide(sl, tw_slide):
    """returns list of (t_appear, kind, payload)"""
    els = []
    def word_time(w, default):
        if not w:
            return default
        for ww, s, e in tw_slide:
            if norm(ww).startswith(norm(w)) or norm(w) in norm(ww):
                return s
        return default
    t0 = tw_slide[0][1] if tw_slide else 0
    for it in sl.get("items", []):
        ta = word_time(it.get("at"), t0 + 0.1)
        k = it["k"]
        if k == "text":
            img = text_img(it["s"], it.get("size", 62), COL[it.get("color", "ink")], maxw=it.get("maxw", 540))
        elif k == "big":
            img = big_img(it["s"], it.get("unit"))
        elif k == "flag":
            img = hand_flag(it["cc"], it.get("w", 340))
            if it.get("name"):
                nm = text_img(it["name"], 60, NAVY, "fredoka-latin-600.ttf", maxw=600)
                c = Image.new("RGBA", (max(img.width, nm.width), img.height + nm.height), (0, 0, 0, 0))
                c.alpha_composite(img, ((c.width - img.width) // 2, 0)); c.alpha_composite(nm, ((c.width - nm.width) // 2, img.height))
                img = c
        elif k == "flags":
            fl = [hand_flag(cc, it.get("w", 130)) for cc in it["ccs"]]
            wtot = sum(f.width for f in fl) + 10 * (len(fl) - 1)
            img = Image.new("RGBA", (wtot, max(f.height for f in fl)), (0, 0, 0, 0)); x = 0
            for f in fl:
                img.alpha_composite(f, (x, 0)); x += f.width + 10
        elif k == "icon":
            img = icon_img(it["name"], it.get("size", 280), it.get("accent"))
        elif k == "question":
            img = question_img()
        elif k == "bars":
            b = Bars(it)
            ats = it.get("ats") or []
            rows_t = []
            for i in range(len(it["rows"])):
                rows_t.append(word_time(ats[i] if i < len(ats) else None, ta + i * it.get("step", 0.9)))
            rows_t[0] = min(rows_t[0], ta)
            els.append(dict(t=ta, kind="bars", obj=b, rows_t=rows_t, y=it.get("y", 0.02))); continue
        else:
            continue
        els.append(dict(t=ta, kind="img", img=img, x=it.get("x", 0.5), y=it.get("y", 0.5), pop=k in ("big", "flag", "icon", "question")))
    return els


def render(spec, out_mp4, work):
    os.makedirs(work, exist_ok=True)
    slides = spec["slides"]
    text = " ".join(s["text"] for s in slides)
    mp3 = os.path.join(work, "voice.mp3")
    v = dict(VOICE); v.update(spec.get("voice", {}))
    tw = tts(text, v["voice"], mp3, v["rate"], v["pitch"])
    voice = load_wav(mp3)
    lead = 0.1
    words = text.split()
    timing = align(words, tw)
    timing = [(a + lead, b + lead) for a, b in timing]
    total = len(voice) / SR + lead + 1.0
    n = int(total * FPS)
    # slide boundaries
    wi = 0; sl_t = []; sl_w = []
    for s in slides:
        k = len(s["text"].split())
        sl_t.append(0.0 if not sl_t else timing[wi][0] - 0.35)
        sl_w.append([(words[wi + j], timing[wi + j][0], timing[wi + j][1]) for j in range(k)])
        wi += k
    built = [build_slide(s, w) for s, w in zip(slides, sl_w)]
    # first slide: everything visible from frame 0 (cover/hook)
    for e in built[0]:
        if e["t"] < 2.5:
            e["t"] = 0.0
    tags = [tag_img(s["tag"]) for s in slides]
    bgp = paper().convert("RGBA"); hd = header()
    sfx = []
    for i in range(1, len(slides)):
        sfx.append((whoosh(i), sl_t[i] - 0.05, 0.9))
    for b in built:
        for e in b:
            if e["kind"] == "img" and e["pop"] and e["t"] > 0.2:
                sfx.append((pop(900 + 60 * (len(sfx) % 4)), e["t"], 0.7))
            if e["kind"] == "bars":
                for tr in e["rows_t"]:
                    sfx.append((pop(700 + 40 * (len(sfx) % 5)), tr, 0.6))

    def slide_canvas(i, t):
        c = Image.new("RGBA", (W, CY1 - 200), (0, 0, 0, 0))
        tg = tags[i]
        c.alpha_composite(tg, ((W - tg.width) // 2, 10))
        top = 100
        for e in built[i]:
            if t < e["t"]:
                continue
            if e["kind"] == "bars":
                e["obj"].draw(c, 120 + int(e["y"] * 600), e["rows_t"], t); continue
            img = e["img"]
            q = (t - e["t"]) / 0.35
            sc = ease_out_back(q) if e["pop"] else 1.0
            al = min(1, q * 1.5)
            if sc < 0.999:
                im2 = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
            else:
                im2 = img
            if al < 1:
                a = im2.split()[3].point(lambda v: int(v * al)); im2 = im2.copy(); im2.putalpha(a)
            cx = e["x"] * W; cy = 150 + e["y"] * 600
            if not e["pop"] and q < 1:
                cy += 18 * (1 - ease(q))
            cy = min(max(cy, 86 + img.height / 2), c.height - 6 - img.height / 2)
            c.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))
        return c

    def frames():
        for fi in range(n):
            t = fi / FPS
            i = max(k for k in range(len(slides)) if sl_t[k] <= t)
            fr = bgp.copy()
            fr.alpha_composite(hd, (0, 42))
            tr = 0.45
            if i > 0 and t - sl_t[i] < tr:
                q = ease((t - sl_t[i]) / tr)
                a = slide_canvas(i - 1, t); b = slide_canvas(i, t)
                fr.alpha_composite(a, (int(-W * q), 200)); fr.alpha_composite(b, (int(W * (1 - q)), 200))
            else:
                fr.alpha_composite(slide_canvas(i, t), (0, 200))
            yield np.asarray(fr.convert("RGB"))
    bed = lofi_bed(total + 1)
    mix_and_encode(frames(), n, voice, bed, spec.get("bed_db", 26), sfx, out_mp4, voice_delay=lead, tmpdir=work)
    return dict(duration=total, words=len(words))


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    work = sys.argv[3] if len(sys.argv) > 3 else "/tmp/oddy_work"
    print(render(spec, sys.argv[2], work))
