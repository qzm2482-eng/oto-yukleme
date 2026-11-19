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
