"""Scheduled uploader. Queue layout:
videos/<channel>/<YYYY-MM-DD_HHMM>.mp4   slot time in Europe/Istanbul
                 <same>.json  {"title","description","tags":[...]}
                 <same>.jpg   cover (used for Instagram Reel cover and YouTube thumbnail)
Uploads every item whose slot time has passed, then removes it from the repo.
"""
import json, os, sys, time, glob, requests
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
CFG = json.load(open("config.json"))
GRAPH = "https://graph.facebook.com/v21.0"
NOW = datetime.now(ZoneInfo("Europe/Istanbul"))
LOG = "logs/uploads.jsonl"


def raw(path):
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}"


def yt_access_token(refresh):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": refresh, "grant_type": "refresh_token"}, timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]


def upload_youtube(ch, path, meta, cover):
    token = yt_access_token(os.environ[ch["yt_token_secret"]])
    body = {"snippet": {"title": meta["title"][:100], "description": meta.get("description", ""),
                        "tags": meta.get("tags", []), "categoryId": ch.get("category", "27")},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json",
         "X-Upload-Content-Type": "video/mp4"}
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                      headers=h, data=json.dumps(body), timeout=60)
    r.raise_for_status()
    with open(path, "rb") as f:
        r2 = requests.put(r.headers["Location"], data=f, headers={"Content-Type": "video/mp4"}, timeout=1800)
    r2.raise_for_status()
    vid = r2.json()["id"]
    if cover:
        try:
            with open(cover, "rb") as f:
                t = requests.post(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}",
                                  headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
                                  data=f, timeout=120)
            print("  YT thumbnail:", t.status_code, "" if t.ok else t.text[:200])
        except Exception as e:
            print("  YT thumbnail skipped:", e)
    return vid


def upload_instagram(ch, path, meta, cover):
    token = os.environ[ch["ig_token_secret"]]
    caption = meta.get("caption") or f"{meta['title']}\n\n{meta.get('description', '')}".strip()
    data = {"media_type": "REELS", "video_url": raw(path), "caption": caption,
            "share_to_feed": "true", "access_token": token}
    if cover:
        data["cover_url"] = raw(cover)
    r = requests.post(f"{GRAPH}/{ch['ig_id']}/media", data=data, timeout=120)
    if not r.ok:
        raise RuntimeError(f"IG container: {r.text[:300]}")
    cid = r.json()["id"]
    for _ in range(90):
        s = requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code", "access_token": token}, timeout=60).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"IG processing failed: {s}")
        time.sleep(10)
    else:
        raise RuntimeError("IG processing timed out")
    p = requests.post(f"{GRAPH}/{ch['ig_id']}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=120)
    if not p.ok:
        raise RuntimeError(f"IG publish: {p.text[:300]}")
    return p.json()["id"]


def due(path):
    stem = os.path.basename(path)[:-4]
    try:
        slot = datetime.strptime(stem[:15], "%Y-%m-%d_%H%M").replace(tzinfo=ZoneInfo("Europe/Istanbul"))
    except ValueError:
        return True
    return slot <= NOW


def main():
    os.makedirs("logs", exist_ok=True)
    failed = False
    for key, ch in CFG.items():
        for path in sorted(glob.glob(f"videos/{key}/*.mp4")):
            if not due(path):
                continue
            base = path[:-4]
            meta = json.load(open(base + ".json")) if os.path.exists(base + ".json") else {}
            meta.setdefault("title", os.path.basename(base))
            cover = base + ".jpg" if os.path.exists(base + ".jpg") else None
            print(f"[{ch['name']}] {path}")
            rec = {"time": NOW.isoformat(), "channel": key, "file": path, "title": meta["title"]}
            try:
                if not meta.get("_yt_done"):
                    rec["youtube"] = upload_youtube(ch, path, meta, cover)
                    meta["_yt_done"] = rec["youtube"]
                    json.dump(meta, open(base + ".json", "w"))
                    print("  YouTube OK:", rec["youtube"])
                rec["instagram"] = upload_instagram(ch, path, meta, cover)
                print("  Instagram OK:", rec["instagram"])
                for ext in (".mp4", ".json", ".jpg"):
                    if os.path.exists(base + ext):
                        os.remove(base + ext)
            except Exception as e:
                failed = True
                rec["error"] = str(e)[:300]
                print("  FAILED:", e)
            open(LOG, "a").write(json.dumps(rec, ensure_ascii=False) + "\n")
    sys.exit(1 if failed else 0)


main()
