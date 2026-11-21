# Saturday 21 November 2026 — The World in One Day

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/haidildariell/news-image-20261121-v6/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard)
[![reward](https://make.fun/badge/news-image-20261121/haidildariell/news-image-20261121-v6/reward.svg)](https://make.fun/bounty/news-image-20261121)

One image that sums up the world's news of **Saturday 21 November 2026**:
36 dated stories across 7 regions — 13 illustrated cards, a world map with
numbered pins, and a 23-story digest — laid out as a broadsheet front page,
"The World in One Day".

Lead stories: COP31 runs into overtime in Antalya with no deal · three
Houthi missiles shot down over Riyadh · a magnitude 6.7 quake shakes
central Peru · 146 safe after a jet's engine-fire landing in Davao ·
BepiColombo reaches Mercury · Bitcoin below $60,000.

## How it is built

- `build_image.py` draws the 1024×1024 front page with Pillow
  (deterministic: fixed fonts, fixed layout, no network, no randomness).
- `main.py` (stdlib only) copies the rendered `entry.png` to
  `MAKEFUN_OUTPUT_DIR`.
- `stories_20261121.json` holds all 36 verified stories; `SOURCES.md`
  names the outlet behind each one.

## Run

```sh
python3 build_image.py          # renders entry.png here
MAKEFUN_OUTPUT_DIR=out python3 main.py   # copies entry.png to out/
```

Entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261121)
`news-image-20261121` (deadline 23 November 2026 07:00 WIB, top 50 share
$100). License: MIT.
