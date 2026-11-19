"""Verifies that each secret belongs to the right account. Prints only OK/MISMATCH, never secrets."""
import os, requests

EXPECT_PAGE = {"IG_TOKEN_1": "1363471316857861", "IG_TOKEN_2": "1523380257506778"}
EXPECT_IG = {"IG_TOKEN_1": "17841480760907210", "IG_TOKEN_2": "17841473699787179"}
EXPECT_YT = {"YT_TOKEN_1": "Empire in Minutes History", "YT_TOKEN_2": "ODDYzenTC"}

for k, page in EXPECT_PAGE.items():
    t = os.environ.get(k, "")
    r = requests.get("https://graph.facebook.com/v21.0/me",
                     params={"fields": "id,name,instagram_business_account", "access_token": t}, timeout=60).json()
    ig = (r.get("instagram_business_account") or {}).get("id")
    ok = r.get("id") == page and ig == EXPECT_IG[k]
    d = requests.get("https://graph.facebook.com/v21.0/debug_token", params={"input_token": t, "access_token": t}, timeout=60).json().get("data", {})
    print(k, "expires_at:", d.get("expires_at"), "fb_post:", "pages_manage_posts" in d.get("scopes", []))
    print(k, "OK" if ok else f"MISMATCH (page={r.get('id')} name={r.get('name')} ig={ig} err={r.get('error', {}).get('message')})")

for k, name in EXPECT_YT.items():
    a = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ.get(k, ""), "grant_type": "refresh_token"}, timeout=60).json()
    if "access_token" not in a:
        print(k, "FAILED:", a.get("error")); continue
    c = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"},
                     headers={"Authorization": f"Bearer {a['access_token']}"}, timeout=60).json()
    t = (c.get("items") or [{}])[0].get("snippet", {}).get("title")
    print(k, "OK" if t == name else f"MISMATCH (channel={t})")
