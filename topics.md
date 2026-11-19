# Topics already made (never repeat) + performance notes
Format: topic — slot (Istanbul) — note. Specs (script + images) live in specs/<channel>/<slot>.json.

## empire
- Pompeii 79 AD ("You Have 18 Hours Before Vesuvius Erupts") — manual, before pipeline
- A night in ancient Rome (sample)
- Thermopylae 480 BC, one of the 300 — 2026-11-19_1700
- Roman fuller / urine laundry + Vespasian urine tax — 2026-11-19_2000
- Minotaur's Labyrinth (myth) — 2026-11-19_2300
- Egyptian embalmer / mummification — 2026-11-20_0200
- Inside Constantinople, 29 May 1453 — 2026-11-20_1700
- Sphinx's riddle (myth) — 2026-11-20_2000
- Odysseus in the Cyclops' cave (myth) — 2026-11-20_2300
- Tosher in London's sewers, 1850 — 2026-11-21_0200
### remakes (IG + FB only, 13:00)
- Theodosian walls ("Why No Army Could Break Constantinople's Walls", YT original ~1.3K views) — 2026-11-20_1300

## oddy
- Instant noodles per person (Vietnam 81)
- Tea per person (sample)
- Finland: more saunas than cars (3.3M vs 2.7M in traffic) — 2026-11-19_1700
- Denmark: ~2 pigs per person (11.9M pigs, Jun 2025) — 2026-11-19_2000
- Pluto vs Russia, myth busted (Pluto 17.7M km² > Russia 17.1M) — 2026-11-19_2300
- Mongolia: more horses than people (4.7M vs 3.5M, 2024) — 2026-11-20_0200
- Canada: ~62% of the world's big lakes — 2026-11-20_1700
- Sweden: 267,570 islands — 2026-11-20_2000
- 5 countries with no airport of their own — 2026-11-20_2300
- South Africa: three capitals — 2026-11-21_0200
### remakes (IG + FB only, 13:00)
- USA toilet paper 141 rolls/person (YT original 1,284 views, channel #1) — 2026-11-20_1300

## Skipped / parked (and why)
- Beer per capita (Czechia 148.8 L, Kirin 2024): could not verify the other countries' litres for the bar chart -> parked until a full table is found.
- Coca-Cola per person (Mexico), cheese per person: sources disagree -> parked.
- Plague doctor London 1665: beak mask is not documented for London 1665 (it is Italian/French) -> needs re-angle (e.g. Rome 1656) before making.
- Japan vending machines: only the drink-machine count (1.95M, 2025) is solid; total count unclear -> parked.

## Learning log
- 2026-11-19 (first pipeline run): no logs/stats.jsonl yet (Daily stats Action has not produced data) and only 2 test uploads in uploads.jsonl, no errors. So no per-platform data to learn from yet.
  Plan: test 3 Empire themes in the first 48 h (Survive the Moment / Worst Jobs / Mythology) and 2 ODDY formats (per-person "more X than people" vs myth-bust "Pluto > Russia"), then compare views, avg view %, IG reach/shares after ~3 days.
  Reason: YouTube audit says Empire's winners are the Byzantine/Constantinople series (~1.3K views each) -> 2 Constantinople pieces in this batch (1453 new + walls remake on IG/FB). ODDY winners are food/consumption + "why country X is the most Y" -> toilet paper remake + "more X than Y" topics.
- Hypothesis to test: myth-bust hooks ("You've heard X. It's wrong.") vs. classic "Can you guess which country?" on ODDY (Pluto video is the first test).
- Tooling notes for next runs: renderers are now in scripts/render (empire.py, oddy.py, cover.py, commons.py). Wikimedia API/uploads rate-limit hard: download thumbnails (1280px) via curl (commons.download), pace requests, cache images. Art Institute of Chicago API needs a browser-like User-Agent.
- 2026-11-19 first stats snapshot (IG empire): old-style "Pompeii's Victims Are Still Frozen in Ash" 1,176 views / 4 shares vs. new locked-style Pompeii 138 views after ~9 h. Too early (1 data point, different age) — watch: if new-style IG reach stays far below old style after 3 days, test stronger cover hooks / first-frame images before anything else.
