"""Inventory: all YouTube videos (status, scheduled time) vs Instagram/Facebook posts. Writes logs/audit.json."""
import json, os, requests
CFG = json.load(open("config.json")); G = "https://graph.facebook.com/v21.0"; res = {}
for key, ch in CFG.items():
    tok = requests.post("https://oauth2.googleapis.com/token", data={"client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ[ch["yt_token_secret"]],
        "grant_type": "refresh_token"}).json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}
    up = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "contentDetails", "mine": "true"}, headers=H).json()
    pl = up["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        r = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params={"part": "contentDetails", "playlistId": pl,
            "maxResults": 50, **({"pageToken": page} if page else {})}, headers=H).json()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        page = r.get("nextPageToken")
        if not page: break
    vids = []
    for i in range(0, len(ids), 50):
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "snippet,status,statistics,contentDetails",
            "id": ",".join(ids[i:i+50])}, headers=H).json()
        for v in r.get("items", []):
            vids.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                         "privacy": v["status"]["privacyStatus"], "publishAt": v["status"].get("publishAt"),
                         "duration": v["contentDetails"]["duration"], "views": v["statistics"].get("viewCount")})
    t = os.environ[ch["ig_token_secret"]]
    ig = requests.get(f"{G}/{ch['ig_id']}/media", params={"fields": "id,caption,timestamp,media_product_type", "limit": 100, "access_token": t}).json().get("data", [])
    fb = requests.get(f"{G}/{ch['fb_page_id']}/video_reels", params={"fields": "id,description,created_time", "limit": 100, "access_token": t}).json().get("data", [])
    pt = requests.get(f"{G}/{ch['fb_page_id']}", params={"fields": "access_token,name", "access_token": t}).json()
    print(key, "page token:", "ok" if pt.get("access_token") else pt)
    me = requests.get(f"{G}/me", params={"fields": "id,name", "access_token": t}).json()
    print(key, "me:", me)
    t2 = pt.get("access_token", t)
    fb2 = requests.get(f"{G}/{ch['fb_page_id']}/video_reels", params={"fields": "id,description,created_time,status", "limit": 20, "access_token": t2}).json()
    print(key, "reels via page token:", json.dumps(fb2)[:600])
    fbst = []
    for line in open("logs/uploads.jsonl"):
        r = json.loads(line)
        if r.get("channel") == key and r.get("facebook"):
            d = requests.get(f"{G}/{r['facebook']}", params={"fields": "status,published,permalink_url,created_time", "access_token": t2}).json()
            fbst.append({"id": r["facebook"], "file": r.get("file"), "info": d})
    res[key] = {"facebook_status": fbst, "youtube": vids, "instagram": [{"id": m["id"], "caption": (m.get("caption") or "")[:100], "time": m.get("timestamp"), "type": m.get("media_product_type")} for m in ig],
                "facebook": [{"id": m["id"], "desc": (m.get("description") or "")[:100], "time": m.get("created_time")} for m in fb]}
    print(key, "yt", len(vids), "scheduled", sum(1 for v in vids if v["publishAt"]), "ig", len(ig), "fb", len(fb))
json.dump(res, open("logs/audit.json", "w"), ensure_ascii=False, indent=1)
