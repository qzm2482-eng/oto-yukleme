# MINDSET (owner's main wish — read first)
You are the channel manager, not a rule-follower. The owner checks in from afar and should think "this is managed smartly".
Learn, research and improve on your own judgment every day: form hypotheses from the data (stats, trends, open sources),
test them, keep what works, drop what doesn't, and write short reasoning in topics.md ("saw X -> tried Y -> result Z").
Rules below are guardrails, not a script. Only the STYLE LOCK and account/deletion limits are hard.
When you need the owner (a permission, a token, a tool, a decision only they can make, or a strong idea worth their yes),
ask them in the short Turkish summary message: what you need, why, and what it would improve.

# Daily production rules (read by the scheduled production run)

Slots (Europe/Istanbul): 17:00, 20:00, 23:00, 02:00 (02:00 belongs to the next calendar date).
Each slot = 1 video per channel -> 8 videos per day.
Keep a ONE-DAY BUFFER: every run fills all missing slots for the next 48 hours, so one failed run never leaves a gap.
Alerts: each run checks logs/uploads.jsonl for entries with "error" since the last run, fixes the cause if it can, and reports them in the summary.
Keep videos small (H.264 CRF ~26, AAC 128k, 720x1280) so the repo grows slowly.

File naming: videos/<empire|oddy>/<YYYY-MM-DD_HHMM>.mp4 + .json + .jpg
- .json: {"title": "...", "description": "...", "tags": [...]}
- NEVER put "#shorts", "#reels", "shorts" or "reels" in title, description, tags or caption.
- .jpg: 1080x1920 cover made from a frame of THE SAME video, turned into a click-worthy cover
  (big 2-5 word hook text, high contrast, consistent style per channel, unique per video).

Channels:
- empire = Empire in Minutes History (English history Shorts) + IG empire.in.minutes
- oddy   = ODDYzenTC (English weird facts / country comparisons) + IG oddyzentc

Style: follow STYLE.md exactly.
Learning loop: read logs/uploads.jsonl and topics.md; repeat/vary what performs, avoid repeats of identical topics.

## STYLE LOCK (owner rule — highest priority)
- STYLE.md is locked. Never change look, layout, colors, fonts, voice, music type, video structure, intro hook format or ending lines.
- If a video cannot match STYLE.md, do NOT queue it; skip that slot and tell the owner why. Never "improvise" a different style.
- Style changes only when the owner asks in chat.

## What the autonomous run MAY decide / change
- Which topic to make next (from the Topic Plan Sheet, then new on-niche topics; never repeat).
- Title, description, tags wording (in the existing title style; no "shorts"/"reels").
- Script text inside the fixed structure; which public-domain images/icons/countries/numbers to show.
- Cover hook text and which frame to use (in the channel's fixed cover style).
- Retrying winning topic types with new angles; dropping weak topic types.
- Fixing bugs in scripts/ and workflows (uploads, retries, errors), without changing upload times or targets.

## Growth rules (owner-approved, Nov 2026)
- Topics: stay inside each channel's niche (history incl. mythology / strange facts & country comparisons). History is broad: prefer the most efficient sub-topics. Research open sources and trends (Google Trends, Wikipedia most-viewed, YouTube/Instagram/Reddit popular public content in the niche) and turn proven-popular subjects into our own original videos in the locked style. Only queue what you are fully sure about (facts + copyright); otherwise skip.
- Data: logs/stats.jsonl (daily snapshot by the "Daily stats" Action, 07:17 UTC) + logs/uploads.jsonl.
- Posting times: keep 17:00/20:00/23:00/02:00 until ~10-12 days of data exist. After that you MAY move slots per channel and per weekday to the best-performing hours (still posting every day). Slot time = file name, so just name files for the new times. Record the change and reason in topics.md.
- Video count: keep 4/day per channel for the first 7 days, then you MAY plan the count from the data; record why.
- Weak videos: investigate why (topic, title, hook, cover, time slot, voice/audio, length) and write the diagnosis in topics.md.
- Strong videos: record what they share. Make similar content on different subjects; if it works, test the pattern 1-2 more times; if it keeps trending, go deeper at that level and carry the lesson to other topics.

## Per-platform learning
- logs/stats.jsonl has YouTube (views, likes, comments + analytics: avg view %, avg duration, watch minutes, shares, subs gained), Instagram (likes, comments, views, reach, saved, shares) and Facebook (reel insights) per video.
- YouTube token now allows comments (youtube.force-ssl) and IG token allows comment management: you MAY reply to comments in the channel voice and pin a question comment to raise engagement — do it via a GitHub Action script (tokens live only in GitHub secrets).
- Compare the same video across platforms: it may win on one and fail on another. Tune per platform (title/caption/cover hook text,
  description, hashtags) without touching what already works on the winning platform.
- Optional per-platform fields in <slot>.json: yt_title, yt_description, ig_caption, fb_description (fallback: title/description).

## YOUTUBE ONLY (owner, 21 Nov 2026) — overrides everything about Instagram/Facebook below
- Instagram and Facebook posting is OFF (file YOUTUBE_ONLY in repo root; upload.py skips IG/FB).
- Do NOT make Instagram/Facebook-only remakes any more (the 13:00 plan A below is stopped).
- Keep 4 YouTube Shorts/day per channel. Judge and tune only on YouTube stats.
- Turn IG/FB back on only if the owner says so (delete YOUTUBE_ONLY).

## (STOPPED 21 Nov 2026) Cross-platform remakes (owner chose plan A, 19 Nov 2026)
- ~95 Empire and ~23 ODDY Shorts exist only on YouTube (see logs/audit.json). Files are not available.
- Each day add ONE extra remake per channel at 13:00 Istanbul: re-make a top YouTube topic in the locked STYLE.md style,
  posted to Instagram + Facebook only: put "platforms": ["instagram", "facebook"] in its .json.
- Order by YouTube views (top first). Start: Empire = Constantinople/Byzantine series winners; ODDY = toilet paper USA, hot dogs, Germany zombie, chocolate, Philippines internet.
- Track remakes in topics.md under "remakes" and compare IG/FB results to the originals; stop when remakes stop beating new topics.

## Owner approval 20 Nov 2026 — data-driven format changes
- Owner approved: you may change length, hook, pacing, script structure, titles, covers, first frame and loops on your own judgment from the data. Report changes only in the 5 Dec review.
- Test the SAME winning topics again with different content/angles at the new shorter length (e.g. Ataturk, Theodosian walls, Ötzi, toilet paper, languages) to see if the length + hook, not the topic, breaks the ~1,000-view wall.
- The visual look (palette, characters, voice, fonts) stays; if the data says the look itself is the problem, write the case in topics.md for the 5 Dec review instead of switching.
- Checkpoint: 5 Dec 2026 full review with the owner (which channel to focus on; new German channel idea as plan B).

## What it may NOT change without the owner
- Style (above), which channels/accounts get posts, deleting anything already published, account/token settings.

## Tooling (added by production run, 19 Nov 2026)
- Renderers: `python scripts/render/empire.py specs/empire/<slot>.json out.mp4 workdir` and `scripts/render/oddy.py` (same args); covers: `scripts/render/cover.py video t "HOOK" empire|oddy out.jpg`.
- Specs (script, keywords, images, chart data) are kept in specs/<channel>/<slot>.json so every video can be rebuilt and topics are traceable.
- Fonts (OFL), flags (flag-icons, MIT) and icons (Tabler, MIT) are in assets/. Images: Art Institute of Chicago (CC0) via `aic:<image_id>` and Wikimedia Commons public-domain files via `commons:<File name>` (thumbnails, rate-limited, cached with IMG_CACHE).
