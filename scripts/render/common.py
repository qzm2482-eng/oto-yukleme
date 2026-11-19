"""Shared helpers for the Empire / ODDY renderers (free tools only: edge-tts, numpy, PIL, ffmpeg)."""
import asyncio, os, ssl, subprocess, json, math, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, "assets")
W, H, FPS = 720, 1280, 30
SR = 44100


def font(name, size):
    return ImageFont.truetype(os.path.join(ASSETS, "fonts", name), size)


# ---------------------------------------------------------------- TTS
def tts(text, voice, out_mp3, rate="+0%", pitch="+0Hz"):
    """edge-tts with word boundaries -> returns list of (word, start_s, end_s)."""
    import edge_tts, edge_tts.communicate as c
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):
        c._SSL_CTX = ssl.create_default_context(cafile=ca)
    words = []

    async def run():
        com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
        with open(out_mp3, "wb") as f:
            async for ch in com.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    s = ch["offset"] / 1e7
                    words.append((ch["text"], s, s + ch["duration"] / 1e7))
    for attempt in range(4):
        try:
            words.clear()
            asyncio.run(run())
            break
        except Exception as e:
            if attempt == 3:
                raise
    return words


def load_wav(path):
    """decode any audio to mono float32 at SR via ffmpeg"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def save_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    pcm = (x * 32767).astype("<i2")
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def envelope(voice, fps=FPS):
    """per-frame RMS 0..1 for lip sync"""
    hop = SR // fps
    n = len(voice) // hop + 1
    out = np.zeros(n)
    for i in range(n):
        seg = voice[i * hop:(i + 1) * hop]
        if len(seg):
            out[i] = np.sqrt(np.mean(seg ** 2))
    if out.max() > 0:
        out = out / np.percentile(out[out > 0], 95)
    return np.clip(out, 0, 1)


def db(x):
    return 10 ** (x / 20)


def _reverb(x, mix=0.25):
    y = x.copy()
    for d, g in ((0.031, 0.5), (0.047, 0.4), (0.071, 0.33), (0.113, 0.25), (0.173, 0.18)):
        k = int(d * SR)
        z = np.zeros_like(x); z[k:] = x[:-k] * g
        y += z
    return x * (1 - mix) + y * mix


def music_box(dur, seed=0):
    """soft, sweet music-box bed; bright, no bass."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR) + SR
    out = np.zeros(n)
    # gentle I-vi-IV-V in C, played high (C5..C7)
    prog = [[72, 76, 79, 84], [69, 72, 76, 81], [65, 69, 72, 77], [67, 71, 74, 79]]
    step = 60 / 76 / 2  # eighth notes at 76 bpm
    t = 0.0; bar = 0
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    while t < dur + 1:
        chord = prog[bar % 4]
        for k, p in enumerate(pattern):
            midi = chord[p] + (12 if (k == 3 and bar % 2) else 0)
            f = 440 * 2 ** ((midi - 69) / 12)
            L = int(1.6 * SR); tt = np.arange(L) / SR
            note = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt))
            note *= np.exp(-tt * 3.2) * (1 - np.exp(-tt * 400)) * (0.55 + 0.1 * rng.random())
            i0 = int((t + k * step) * SR)
            seg = out[i0:i0 + L]; seg += note[:len(seg)]
        t += step * len(pattern); bar += 1
    out = _reverb(out, 0.35)
    out = out[:int(dur * SR)]
    return out / (np.abs(out).max() + 1e-9) * 0.5


def lofi_bed(dur, seed=1):
    """very quiet lo-fi bed: soft electric-piano chords + light vinyl noise"""
    rng = np.random.default_rng(seed)
    n = int(dur * SR) + SR
    out = np.zeros(n)
    prog = [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 65]]
    bar = 60 / 72 * 4
    t = 0.0; b = 0
    while t < dur + 1:
        for midi in prog[b % 4]:
            f = 440 * 2 ** ((midi - 69) / 12)
            L = int(bar * SR); tt = np.arange(L) / SR
            note = np.sin(2 * np.pi * f * tt) * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * tt)) + 0.2 * np.sin(2 * np.pi * 2 * f * tt)
            note *= np.exp(-tt * 0.9) * (1 - np.exp(-tt * 60)) * 0.25
            i0 = int(t * SR); seg = out[i0:i0 + L]; seg += note[:len(seg)]
        t += bar; b += 1
    out = out[:int(dur * SR)]
    # one-pole lowpass for warmth
    a = 0.12; y = np.zeros_like(out); acc = 0.0
    for i in range(0, len(out)):
        acc += a * (out[i] - acc); y[i] = acc
    noise = rng.normal(0, 1, len(y)) * 0.004
    crack = (rng.random(len(y)) > 0.9997) * rng.normal(0, 0.2, len(y))
    y = y / (np.abs(y).max() + 1e-9) * 0.5 + noise + crack * 0.3
    return y


def whoosh(seed=2, dur=0.4):
    rng = np.random.default_rng(seed)
    L = int(dur * SR); tt = np.arange(L) / SR
    nz = rng.normal(0, 1, L)
    # sweep band via moving-average differences
    env = np.sin(np.pi * tt / dur) ** 2
    y = np.zeros(L); acc = 0.0
    for i in range(L):
        a = 0.02 + 0.25 * (i / L)
        acc += a * (nz[i] - acc); y[i] = acc
    y = y * env
    return y / (np.abs(y).max() + 1e-9) * 0.5


def pop(f0=880, dur=0.09):
    L = int(dur * SR); tt = np.arange(L) / SR
    f = f0 * (1 - 0.35 * tt / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 45) * 0.6


def place(bus, clip, t, gain=1.0):
    i = int(t * SR)
    if i >= len(bus) or i < 0:
        return
    seg = bus[i:i + len(clip)]
    seg += clip[:len(seg)] * gain


def mix_and_encode(frames_iter, n_frames, voice, bed, bed_db, sfx, out_mp4, voice_delay=0.0, tmpdir="/tmp"):
    """voice: float array, bed: float array (already length >= total), bed_db: dB under voice peak level"""
    total = n_frames / FPS
    N = int(total * SR)
    v = np.zeros(N); place(v, voice, voice_delay)
    m = np.zeros(N); m[:min(N, len(bed))] = bed[:N]
    # fade bed in/out
    fi = int(0.4 * SR); fo = int(1.2 * SR)
    m[:fi] *= np.linspace(0, 1, fi); m[-fo:] *= np.linspace(1, 0, fo)
    vr = np.sqrt(np.mean(v[np.abs(v) > 0.01] ** 2)) if np.any(np.abs(v) > 0.01) else 0.1
    mr = np.sqrt(np.mean(m ** 2)) + 1e-9
    m *= vr / mr * db(-bed_db)
    s = np.zeros(N)
    for clip, t, g in sfx:
        place(s, clip, t, g)
    sr_ = np.sqrt(np.mean(s[np.abs(s) > 0.001] ** 2)) if np.any(np.abs(s) > 0.001) else 1
    s *= (vr / sr_) * db(-14) if np.any(s) else 1
    audio = v + m + s
    wav = os.path.join(tmpdir, "mix.wav"); save_wav(wav, audio / (np.abs(audio).max() + 1e-9) * 0.9)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium",
           "-crf", "26", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-movflags", "+faststart",
           "-shortest", out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames_iter:
        p.stdin.write(fr.tobytes() if isinstance(fr, Image.Image) else fr)
    p.stdin.close(); p.wait()
    if p.returncode:
        raise RuntimeError("ffmpeg failed")


# ---------------------------------------------------------------- word timing helpers
def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def align(script_words, tts_words):
    """map every script word index -> (start,end) using tts boundaries (greedy, tolerant)."""
    out = []; j = 0
    tw = [(norm(w), s, e) for w, s, e in tts_words]
    for w in script_words:
        nw = norm(w)
        if not nw:
            out.append(out[-1] if out else (0, 0)); continue
        found = None
        for k in range(j, min(j + 6, len(tw))):
            if tw[k][0] == nw or (nw and tw[k][0] and (tw[k][0].startswith(nw) or nw.startswith(tw[k][0]))):
                found = k; break
        if found is None:
            # numbers etc. may be split/merged: reuse current position
            k = min(j, len(tw) - 1)
            out.append((tw[k][1], tw[k][2])); continue
        out.append((tw[found][1], tw[found][2])); j = found + 1
    return out


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.7):
    x = max(0.0, min(1.0, x)) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def svg_icon(name, size, color="#1F2421", stroke=2.0, fill=None):
    path = os.path.join(ASSETS, "icons", name + ".svg")
    svg = open(path).read().replace('stroke="currentColor"', f'stroke="{color}"').replace('stroke-width="2"', f'stroke-width="{stroke}"')
    if fill:
        svg = svg.replace('fill="none"\n  stroke', f'fill="{fill}"\n  stroke', 1)
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size)], input=svg.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def flag_img(cc, w):
    path = os.path.join(ASSETS, "flags", cc.lower() + ".svg")
    h = int(w * 3 / 4)
    png = subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), path], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255)
    return m


def grain(size, amount=10, seed=0):
    rng = np.random.default_rng(seed)
    a = rng.normal(0, amount, (size[1], size[0])).clip(-40, 40) + 128
    return Image.fromarray(a.astype(np.uint8), "L")
