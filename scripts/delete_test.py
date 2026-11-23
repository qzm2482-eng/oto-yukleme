import os, requests
items = [("YT_TOKEN_1","IG_TOKEN_1","Vcl8cNojqWM","18110875337212796"),
         ("YT_TOKEN_2","IG_TOKEN_2","z24WtTb7AJ4","18133910405493512")]
for yk, ik, yt, ig in items:
    a = requests.post("https://oauth2.googleapis.com/token", data={"client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ[yk], "grant_type": "refresh_token"}).json()
    r = requests.delete("https://www.googleapis.com/youtube/v3/videos", params={"id": yt},
        headers={"Authorization": "Bearer " + a.get("access_token", "")})
    print("YT", yt, r.status_code, r.text[:150].replace("\n", " "))
    r = requests.delete(f"https://graph.facebook.com/v21.0/{ig}", params={"access_token": os.environ[ik]})
    print("IG", ig, r.status_code, r.text[:150])
