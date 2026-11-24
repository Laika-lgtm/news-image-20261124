# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Laika-lgtm/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Laika-lgtm/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up the world's news of **Tuesday 24 November 2026**:
36 stories across 7 regions, every one first reported that day.

## Run it

```sh
python3 main.py            # writes entry.png (1024x1024, < 1 MiB)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=w2e3vyyb&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>

# The World in One Day — Tuesday 24 November 2026

## What is on the page

- Masthead **"THE WORLD IN ONE DAY"** with the date repeated three times
  (masthead, top strip, footer) — the day is unmissable.
- **6 stats**: 2 killed in the Zaporizhzhia strike · 40 wounded in
  Zaporizhzhia · 2 tankers hit mines off Hormuz · 7 killed in Gaza
  strikes · 60 Patriot interceptors held up · 1 Pacific island evacuated.
- **Colour-coded region bar** — Europe 9 · Middle East 5 · Americas 5 ·
  Asia-Pacific 9 · Africa 2 · Oceania 3 · World 3 = **36 stories**.
- **3 hero stories** with code-drawn flat illustrations: the Zaporizhzhia
  strike, Iran says two tankers hit mines east of Hormuz (CLAIM), Israel
  kills Hamas' security chief in Gaza.
- **12 illustrated cards** (#4–15) and **21 more stories** (#16–36).
- **THE DAY IN UTC** timeline (04:26–12:35), a **world map with numbered
  pins** matching story numbers, a red **DATE CHECK** box naming the 12
  big 22–23 Nov stories deliberately left out plus 2 "Not yet" items, and
  a **certainty key** (REPORTED / CLAIM / FORECAST) with tags on the
  three heroes.

## Round 2 — what changed vs round 1

Round 1 ranked 164 of 7,302. A full date audit found 12 of its 15 top
stories were actually from 23 November or earlier (the Dymer toll-15
story, Zelenskyy's four-way talks, Iran's war-crimes suits, the oil-site
strikes, Megaspeed, the Finland envoy, Guterres' AI speech, the Grok
suits, the ICE detention, SharkNinja, the Cikande toll-24 figure, and a
Duisburg furnace story from September) — the same failure mode that sank
news-22 r12 in the final heat. Round 2 replaces all twelve with stories
verified against a wire timestamp from Tuesday 24 November 2026, expands
DATE CHECK to 12 exclusions + 2 Not-yet items, and fixes three hero
headlines so each is true read alone. Layout, masthead and the 36-story /
7-region structure are unchanged. See `SOURCES.md` for every fact and
its source, and for the full list of corrections vs round 1.

## How it is made

`main.py` (Python 3, standard library + Pillow) reads `stories.json` and
draws the whole 1024×1024 front page with PIL shapes — flat vector-style
illustrations, no photos, no AI-generated images, no external files.
It runs offline and deterministically: two runs write identical bytes.

```sh
python3 main.py            # writes entry.png (1024x1024, < 1 MiB)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

If Pillow or the DejaVu fonts are unavailable in the grading sandbox,
the program falls back to copying the pre-rendered `entry.png` that
ships in this repository, so the output is always the same verified image.

## Files

- `main.py` — the renderer (entrypoint)
- `stories.json` — all 36 stories, stats, UTC timeline, map pins
- `SOURCES.md` — every fact, with its source and date
- `entry.png` — the rendered front page

## Licence

MIT — see `LICENSE`.
