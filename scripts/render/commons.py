"""Wikimedia Commons search limited to public-domain files (checks LicenseShortName)."""
import sys, time, requests, re, os, json
UA = {"User-Agent": "EmpireHistoryPipeline/2.0 (+https://github.com/qzm2482-eng/oto-yukleme) python-requests"}
API = "https://commons.wikimedia.org/w/api.php"


def _get(params):
    for i in range(6):
        r = requests.get(API, params=params, headers=UA, timeout=60)
        if r.status_code == 429:
            time.sleep(4 + 4 * i); continue
        r.raise_for_status(); return r.json()
    raise RuntimeError("commons rate limited")


def search(q, n=12, minw=1000):
    d = _get({"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n,
              "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1600, "format": "json"})
    out = []
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = p.get("imageinfo", [{}])[0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "")
        if not re.search(r"public domain|PD|CC0", lic, re.I):
            continue
        if ii.get("width", 0) < minw:
            continue
        artist = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", ""))[:40]
        out.append(dict(title=p["title"], lic=lic, w=ii["width"], h=ii["height"], url=ii.get("thumburl") or ii["url"], artist=artist,
                        date=re.sub("<[^>]+>", "", md.get("DateTimeOriginal", {}).get("value", ""))[:30]))
    return out


def thumbify(url, width=1280):
    url = url.split("?")[0]
    m = re.match(r"https://upload.wikimedia.org/wikipedia/commons/([0-9a-f])/([0-9a-f]{2})/(.+)$", url)
    if m:
        name = m.group(3)
        return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m.group(1)}/{m.group(2)}/{name}/{width}px-{name}" + (".jpg" if name.lower().endswith((".tif", ".tiff")) else "")
    return url


def thumb_url(name, width=1280):
    import hashlib
    name = name.replace("File:", "").replace(" ", "_")
    h = hashlib.md5(name.encode()).hexdigest()
    from urllib.parse import quote
    q = quote(name)
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"


def resolve(title, width=1280):
    """File title -> thumbnail URL (checks public-domain licence)."""
    if not title.startswith("File:"):
        title = "File:" + title
    d = _get({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": width, "format": "json"})
    p = list(d["query"]["pages"].values())[0]
    ii = p["imageinfo"][0]
    lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
    if not re.search(r"public domain|PD|CC0", lic, re.I):
        raise RuntimeError(f"not public domain: {title} ({lic})")
    return ii.get("thumburl") or ii["url"]


def _curl(url, path):
    import subprocess
    r = subprocess.run(["curl", "-s", "-L", "--http2", "-A", UA["User-Agent"], "-o", path, "-w", "%{http_code}", url],
                       capture_output=True, text=True, timeout=120)
    ok = r.stdout.strip() == "200" and os.path.exists(path) and os.path.getsize(path) > 5000
    if not ok and os.path.exists(path):
        os.remove(path)
    return ok


def download(url, path):
    url = url.split("?")[0]
    cands = [url] if "/thumb/" in url else [thumbify(url, 1280), thumbify(url, 960), url]
    for i in range(14):
        for u in cands:
            if _curl(u, path):
                time.sleep(1.5)
                return path
        time.sleep(4 + 3 * i)
    raise RuntimeError("download failed " + url)
