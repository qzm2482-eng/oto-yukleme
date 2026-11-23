"""Daily stats snapshot of every uploaded video -> logs/stats.jsonl (read by the production run)."""
import json, os, requests
from datetime import datetime, timezone

CFG = json.load(open("config.json"))
NOW = datetime.now(timezone.utc).isoformat()
G = "https://graph.facebook.com/v21.0"
rows = [json.loads(l) for l in open("logs/uploads.jsonl")] if os.path.exists("logs/uploads.jsonl") else []
out = []
for key, ch in CFG.items():
    tok = requests.post("https://oauth2.googleapis.com/token", data={"client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ[ch["yt_token_secret"]],
        "grant_type": "refresh_token"}).json().get("access_token")
    ids = [r["youtube"] for r in rows if r.get("channel") == key and r.get("youtube")]
    for i in range(0, len(ids), 50):
        d = requests.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "statistics,snippet",
            "id": ",".join(ids[i:i+50])}, headers={"Authorization": f"Bearer {tok}"}).json()
        for v in d.get("items", []):
            out.append({"time": NOW, "channel": key, "platform": "youtube", "id": v["id"],
                        "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"], **v["statistics"]})
    try:
        from datetime import date
        ra = requests.get("https://youtubeanalytics.googleapis.com/v2/reports", params={
            "ids": "channel==MINE", "startDate": "2026-11-01", "endDate": date.today().isoformat(),
            "metrics": "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,shares,subscribersGained",
            "dimensions": "video", "sort": "-views", "maxResults": 200}, headers={"Authorization": f"Bearer {tok}"}).json()
        if "error" in ra:
            out.append({"time": NOW, "channel": key, "platform": "youtube_analytics", "error": str(ra["error"])[:300]})
        heads = [h["name"] for h in ra.get("columnHeaders", [])]
        for row in ra.get("rows", []):
            out.append({"time": NOW, "channel": key, "platform": "youtube_analytics", **dict(zip(heads, row))})
    except Exception as e:
        print("yt analytics skipped:", e)
    m = requests.get(f"{G}/{ch['ig_id']}/media", params={"fields": "id,caption,timestamp,like_count,comments_count,media_product_type",
        "limit": 50, "access_token": os.environ[ch["ig_token_secret"]]}).json()
    if "error" in m:
        out.append({"time": NOW, "channel": key, "platform": "instagram", "error": str(m["error"])[:300]})
    for p in m.get("data", []):
        out.append({"time": NOW, "channel": key, "platform": "instagram", "id": p["id"],
                    "title": (p.get("caption") or "")[:80], "published": p.get("timestamp"),
                    "likes": p.get("like_count"), "comments": p.get("comments_count"),
                    **{i["name"]: (i.get("values") or [{}])[0].get("value") for i in requests.get(f"{G}/{p['id']}/insights",
                       params={"metric": "views,reach,saved,shares,total_interactions",
                               "access_token": os.environ[ch["ig_token_secret"]]}).json().get("data", [])}})
    tokp = os.environ[ch["ig_token_secret"]]
    for r in rows:
        if r.get("channel") != key or not r.get("facebook"):
            continue
        vid = r["facebook"]
        ins = requests.get(f"{G}/{vid}/video_insights", params={"access_token": tokp}).json()
        mets = {i["name"]: (i.get("values") or [{}])[0].get("value") for i in ins.get("data", [])}
        info = requests.get(f"{G}/{vid}", params={"fields": "created_time,description", "access_token": tokp}).json()
        out.append({"time": NOW, "channel": key, "platform": "facebook", "id": vid, "title": r.get("title"),
                    "published": info.get("created_time"), **{k: v for k, v in mets.items() if not isinstance(v, dict)}})
os.makedirs("logs", exist_ok=True)
with open("logs/stats.jsonl", "a") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print(len(out), "rows")
