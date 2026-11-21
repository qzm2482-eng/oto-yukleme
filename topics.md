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
- Powder monkey at Trafalgar, 1805 — 2026-11-21_1700
- Greek fire, Arab siege of Constantinople (670s) — 2026-11-21_2000
- Medusa's island / Perseus (myth) — 2026-11-21_2300
- Hannibal's elephants over the Alps, 218 BC — 2026-11-22_0200
- Great Fire of London, Sept 1666 — 2026-11-22_1700
- Trojan Horse: would you open the gates? (myth) — 2026-11-22_2000
- Tenochtitlan when Cortés arrives, 1519-1521 — 2026-11-22_2300
- Kublai Khan's fleet vs Japan 1281 (kamikaze) — 2026-11-23_0200
### remakes (IG + FB only, 13:00)
- Theodosian walls ("Why No Army Could Break Constantinople's Walls", YT original ~1.3K views) — 2026-11-20_1300
- Ötzi the Iceman ("Hikers Found Him in the Ice. He'd Been Dead 5,300 Years", YT original 1,150 views; kept the proven title) — 2026-11-21_1300
- Constantinople founded between Europe and Asia, 324-330 ("Why This City Ruled Two Worlds for 1000 Years", YT original 1,346 views = Empire #1; kept the title) — 2026-11-22_1300

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
- Australia: biggest wild camel herd (~1M 2008, ~300k 2013) — 2026-11-21_1700
- Costa Rica: no army since 1 Dec 1948 (vs Panama, Iceland, Liechtenstein) — 2026-11-21_2000
- Iceland: first mosquitoes ever, Oct 2025 (myth-bust #2) — 2026-11-21_2300
- Israel: most poultry per person, 58.5 kg (OECD-FAO 2018) — 2026-11-22_0200
- Colombia rainiest country, 3,240 mm/yr (World Bank via Wikipedia list) — 2026-11-22_1700
- Lesotho: highest lowest point, 1,400 m (> Ben Nevis 1,345) — 2026-11-22_2000
- Australia wider than the Moon (~4,000 vs 3,475 km; myth-bust/space test #3, same 23:00 slot as Pluto) — 2026-11-22_2300
- Pasta: Tunisia #2 after Italy (17 vs 23.5 kg, Euronews 2023 / EU pasta makers) — 2026-11-23_0200
### remakes (IG + FB only, 13:00)
- USA toilet paper 141 rolls/person (YT original 1,284 views, channel #1) — 2026-11-20_1300
- Most time online per day: South Africa 9h37 (Digital 2025) — remake of "Philippines internet capital" (YT 679). Hot dogs (#2) skipped: no reliable per-country table for the bar chart; chocolate/rice/Germany-zombie also lack clean data -> next remakes: sheep, languages (PNG), donuts only if a clean table is found. — 2026-11-21_1300
- Papua New Guinea 840 languages (SIL 2024) — remake of "Why 7% of the World's Languages Are in One Country" (YT 498, best retention 58%); title corrected to "1 in 10" (840 of ~7,100). — 2026-11-22_1300

## Skipped / parked (and why)
- Beer per capita (Czechia 148.8 L, Kirin 2024): could not verify the other countries' litres for the bar chart -> parked until a full table is found.
- Coca-Cola per person (Mexico), cheese per person: sources disagree -> parked.
- Plague doctor London 1665: beak mask is not documented for London 1665 (it is Italian/French) -> needs re-angle (e.g. Rome 1656) before making.
- Hot dogs per country, chocolate per person: no reliable per-country table -> skipped as remakes.
- Oldest population (Japan 65+ share): source pages blocked this run, not verified -> parked.
- Japan vending machines: only the drink-machine count (1.95M, 2025) is solid; total count unclear -> parked.

## Learning log
- 2026-11-19 (first pipeline run): no logs/stats.jsonl yet (Daily stats Action has not produced data) and only 2 test uploads in uploads.jsonl, no errors. So no per-platform data to learn from yet.
  Plan: test 3 Empire themes in the first 48 h (Survive the Moment / Worst Jobs / Mythology) and 2 ODDY formats (per-person "more X than people" vs myth-bust "Pluto > Russia"), then compare views, avg view %, IG reach/shares after ~3 days.
  Reason: YouTube audit says Empire's winners are the Byzantine/Constantinople series (~1.3K views each) -> 2 Constantinople pieces in this batch (1453 new + walls remake on IG/FB). ODDY winners are food/consumption + "why country X is the most Y" -> toilet paper remake + "more X than Y" topics.
- Hypothesis to test: myth-bust hooks ("You've heard X. It's wrong.") vs. classic "Can you guess which country?" on ODDY (Pluto video is the first test).
- Tooling notes for next runs: renderers are now in scripts/render (empire.py, oddy.py, cover.py, commons.py). Wikimedia API/uploads rate-limit hard: download thumbnails (1280px) via curl (commons.download), pace requests, cache images. Art Institute of Chicago API needs a browser-like User-Agent.
- 2026-11-19 first stats snapshot (IG empire): old-style "Pompeii's Victims Are Still Frozen in Ash" 1,176 views / 4 shares vs. new locked-style Pompeii 138 views after ~9 h. Too early (1 data point, different age) — watch: if new-style IG reach stays far below old style after 3 days, test stronger cover hooks / first-frame images before anything else.
- 2026-11-20 run: Stats Action has run only once (19 Nov); audit.json (YT views, 19 Nov 23:16 UTC) shows new locked-style uploads at 0-5 views (Empire) and 6-30 (ODDY) after 3-9 h, BUT the last old-style Empire uploads (Venice series, 19 Nov) also sit at 8-10 views -> looks like a channel-wide YouTube slump, not the style. Not enough data to judge yet (need 3-day numbers).
  Tests in this batch: (a) remake keeps the proven old YT title verbatim ("Hikers Found Him in the Ice...") to see if the title drives IG/FB reach; (b) ODDY myth-bust #2 (Iceland mosquitoes, news hook from Oct 2025) vs Pluto myth-bust; (c) Empire 'Byzantine' winner topic again (Greek fire; old YT 897/883 views) in the new style.
  Changed: Empire scripts trimmed to ~91-100 words (renders were 48-51 s, STYLE wants 30-45 s); now ~44 s. Added Tabler (MIT) icons: wifi, device-mobile, meat, egg, clock, shield-off, school, cactus, snowflake, bomb, eye-off, axe, barrel, flask, bug-off, etc. Big Empire renders (map/engraving detail, ~10 MB) re-encoded at CRF 29 to stay ~5-6 MB.
  QC (separate agent, 2 rounds): fixed framed-image whole-pixel stepping in empire.py (now subpixel affine), ODDY final chart now held >=1.5 s (extra line after the winner), replaced a Turner diptych + half-empty coin shot. All 10 passed.
  Next run: if 3-day stats show new-style Empire far below old style on IG too, test (1) first frame = the strongest real image with the hook text bigger, (2) shorter 30-35 s cut.
- 2026-11-20 stats snapshot (08:25 UTC): YT Empire new videos 3-7 views, except Embalmer (02:00 slot) 61 -> early hint that the 02:00 Istanbul slot (US evening) beats 17:00/20:00; IG ODDY: Pluto myth-bust 881 views (posted manually by owner at 23:00) vs bot-posted sauna/pigs/horses 119-172; old-style noodles 1,714. Watch: myth-bust format and late slots. Slots stay fixed until ~10-12 days of data (rule).
  Stats gaps found: Empire Instagram rows and all YouTube Analytics rows are missing (API returned an error silently). stats.py now logs those errors into stats.jsonl so the next run can see the cause (likely token scope/expiry).
- 2026-11-20 YouTube Studio data from owner (screenshots, lifetime, OLD-style Shorts; first real retention numbers, Analytics API still missing):
  ODDY (47-55 s videos): channel avg view duration 0:21, avg viewed 42.7% -> viewers leave at ~20 s, before most reveals/charts. Best %: "7% of languages in one country" 58% (0:27), Philippines internet 51.6%, turkey 49.8%. Views 80-1,281 (toilet paper #1, hot dogs 1,209, zombie Germany 922).
  Empire (mostly 22-31 s videos): avg viewed 64.7%. Winners: Ataturk "How One Man Built a Nation From Ashes in 5 Years" 100.2% at 0:51 (1,345 views, 3 subs = best sub converter), "They Rebuilt These Walls in 60 Days to Stop Attila" 115.6% (loops), Ötzi 71.4%. Long-form (15 min) 62 and 5 views -> long-form is dead for this channel, do not make any.
  Pattern: almost every Short stops at ~1,000-1,350 views = the feed's first test batch; none broke past it. To break out we need clearly higher retention + loops, not more topics.
  Actions: (1) Empire: aim 30-35 s (inside STYLE 30-45 s; old winners were 22-31 s, current renders ~44 s). Answer/payoff by ~15 s, last line loops back to the hook. (2) Titles: concrete human story + number ("in 60 Days", "5,300 Years", "in 5 Years") beat generic "Why X..." — use that title pattern. (3) ODDY: shorter cut (~30-35 s, reveal by ~12 s) proposed to owner because STYLE says 40-50 s — Owner approved 20 Nov -> ODDY now ~30-35 s (STYLE.md updated).
- 2026-11-21 run (stats snapshot 21 Nov 07:xx UTC, 2nd day of data):
  Saw: ODDY myth-bust "Pluto vs Russia" keeps growing (YT 439, IG 1,487 = best new video on both). Embalmer (02:00 slot, gross detail in title) YT 316, every other new Empire YT 1-21. Facebook: 0 plays on almost every reel on both pages (0-2) -> FB distribution is ~zero, nothing in code to fix (posts are published, copyright check clean).
  IG Empire, same topic test: walls remake in new locked style 204 views vs old-style walls posts 1,484-1,689; all 10 new-style Empire IG posts 112-207 vs old-style median ~560 (many old ones 1,000-1,700). Hypothesis: on IG the new cartoon-narrator look itself underperforms (YT can't tell yet). Per rule, not switching; case written here for the 5 Dec review and flagged to owner.
  YouTube Analytics API is DISABLED in the Google Cloud project (403 'has not been used in project 575710555122') -> no retention data. Owner must enable it (one click in console).
  Tried: (1) ODDY myth-bust/space pattern again in Pluto's 23:00 slot (Australia wider than the Moon); hooks framed as "not X, not Y" (rain: not India/UK; pasta: #2 isn't in Europe). (2) Shorter cuts: ODDY 66-83 words -> 33-39 s (was 47-50 s), Empire 84-87 words -> 37-45 s (was 44-47). (3) Remakes: Empire #1 YT topic (Constantinople two worlds) with proven title; ODDY languages with retention-winner topic.
  Fixed: common.norm() now strips accents (São Tomé cue matched 'Solomon' and the bar popped 6 s early); Empire cover band now opaque (caption text bled through).
  Next: compare Australia-Moon vs Pluto at 23:00; if myth-bust/space keeps winning, make 1 per day. Watch whether 33-39 s ODDY raises YT views.
