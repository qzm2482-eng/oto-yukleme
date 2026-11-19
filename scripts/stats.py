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
    m = requests.get(f"{G}/{ch['ig_id']}/media", params={"fields": "id,caption,timestamp,like_count,comments_count,media_product_type",
        "limit": 50, "access_token": os.environ[ch["ig_token_secret"]]}).json()
    for p in m.get("data", []):
        out.append({"time": NOW, "channel": key, "platform": "instagram", "id": p["id"],
                    "title": (p.get("caption") or "")[:80], "published": p.get("timestamp"),
                    "likes": p.get("like_count"), "comments": p.get("comments_count")})
os.makedirs("logs", exist_ok=True)
with open("logs/stats.jsonl", "a") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print(len(out), "rows")
