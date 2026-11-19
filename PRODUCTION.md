# Daily production rules (read by the scheduled production run)

Slots (Europe/Istanbul): 17:00, 20:00, 23:00, 02:00 (02:00 belongs to the next calendar date).
Each slot = 1 video per channel -> 8 videos per day.

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

## What it may NOT change without the owner
- Style (above), upload times (17:00, 20:00, 23:00, 02:00), number of videos, which channels/accounts get posts, deleting anything already published, account/token settings.
