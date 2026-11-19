"""Uploads every new video in videos/<channel>/ to YouTube (Shorts) and Instagram (Reels).

For each video X.mp4 an optional X.json may hold {"title": ..., "description": ...}.
A video is deleted from the repo after both uploads succeed.
"""
import json, os, sys, time, glob, requests

REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
CFG = json.load(open("config.json"))
GRAPH = "https://graph.facebook.com/v21.0"


def yt_access_token(refresh):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": refresh, "grant_type": "refresh_token"}, timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]


def upload_youtube(ch, path, title, desc):
    token = yt_access_token(os.environ[ch["yt_token_secret"]])
    meta = {"snippet": {"title": title[:100], "description": desc, "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json",
         "X-Upload-Content-Type": "video/mp4"}
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos"
                      "?uploadType=resumable&part=snippet,status",
                      headers=h, data=json.dumps(meta), timeout=60)
    r.raise_for_status()
    with open(path, "rb") as f:
        r2 = requests.put(r.headers["Location"], data=f,
                          headers={"Content-Type": "video/mp4"}, timeout=1800)
    r2.raise_for_status()
    return r2.json()["id"]


def upload_instagram(ch, path, caption):
    token = os.environ[ch["ig_token_secret"]]
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}"
    r = requests.post(f"{GRAPH}/{ch['ig_id']}/media", data={
        "media_type": "REELS", "video_url": url, "caption": caption,
        "access_token": token}, timeout=120)
    r.raise_for_status()
    cid = r.json()["id"]
    for _ in range(60):
        s = requests.get(f"{GRAPH}/{cid}", params={
            "fields": "status_code", "access_token": token}, timeout=60).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram processing failed: {s}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram processing timed out")
    p = requests.post(f"{GRAPH}/{ch['ig_id']}/media_publish", data={
        "creation_id": cid, "access_token": token}, timeout=120)
    p.raise_for_status()
    return p.json()["id"]


def main():
    failed = False
    for key, ch in CFG.items():
        for path in sorted(glob.glob(f"videos/{key}/*.mp4")):
            meta_path = path[:-4] + ".json"
            meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
            title = meta.get("title") or os.path.basename(path)[:-4]
            desc = meta.get("description", "")
            print(f"[{ch['name']}] {path}")
            try:
                yt = upload_youtube(ch, path, title, desc)
                print("  YouTube OK:", yt)
                ig = upload_instagram(ch, path, f"{title}\n\n{desc}".strip())
                print("  Instagram OK:", ig)
                os.remove(path)
                if os.path.exists(meta_path):
                    os.remove(meta_path)
            except Exception as e:
                failed = True
                print("  FAILED:", e)
    sys.exit(1 if failed else 0)


main()
