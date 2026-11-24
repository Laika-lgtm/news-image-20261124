# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Laika-lgtm/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Laika-lgtm/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up the world's news of **Tuesday 24 November 2026**:
36 stories across 7 regions, every one first reported that day.

## Run it

```sh
python3 main.py            # writes entry.png (1024x1024, < 1 MiB)
python3 main.py --out out/entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=w2e3vyyb&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>

# The World in One Day — Tuesday 24 November 2026

## What is on the page

- Masthead **"THE WORLD IN ONE DAY"** with the date repeated three times
  (masthead, top strip, footer) — the day is unmissable.
- **6 stats**: 15 killed in Kyiv region strikes · 3 Russian oil sites hit ·
  24 killed in the Indonesia factory fire · 4-way talks urged · 2 states
  sue SpaceX · 1 Pacific island evacuated.
- **Colour-coded region bar** — Europe 9 · Middle East 6 · Americas 6 ·
  Asia-Pacific 7 · Africa 1 · Oceania 3 · World 4 = **36 stories**.
- **3 hero stories** with code-drawn flat illustrations: Kyiv strikes,
  Zelenskyy's four-way talks call, Tehran's war-crimes lawsuits.
- **12 illustrated cards** (#4–15) and **21 more stories** (#16–36).
- **THE DAY IN UTC** timeline (00:31–06:22), a **world map with numbered
  pins** matching story numbers, a red **DATE CHECK** box naming the big
  22–23 Nov stories deliberately left out, and a **certainty key**
  (REPORTED / CLAIM / FORECAST) with tags on the three heroes.

## How it is made

`main.py` (Python 3, standard library + Pillow) reads `stories.json` and
draws the whole 1024×1024 front page with PIL shapes — flat vector-style
illustrations, no photos, no AI-generated images, no external files.
It runs offline and deterministically: two runs write identical bytes.

```sh
python3 main.py            # writes entry.png (1024x1024, < 1 MiB)
python3 main.py --out out/entry.png
```

## Files

- `main.py` — the renderer (entrypoint)
- `stories.json` — all 36 stories, stats, UTC timeline, map pins
- `SOURCES.md` — every fact, with its source and date
- `entry.png` — the rendered front page

## Licence

MIT — see `LICENSE`.
