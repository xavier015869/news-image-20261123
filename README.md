# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/xavier015869/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/xavier015869/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

"The World Ledger" — a one-page newspaper front page that sums up the world news of Monday 23 November 2026 in a single 1024×1024 image: the COP31 climate summit's collapse in Antalya, Russian cruise missiles confirmed on Polish soil, the Iran–Houthi escalation in the Gulf, Taiwan's short-selling ban after a record market plunge, Ukrainian sea drones at Benghazi, the UN's killer-robot rules, Liverpool's rout of ten-man Manchester United, and the day's briefs. `render.py` draws the page deterministically with Pillow; `main.py` (standard library only) writes the rendered `entry.png` to the output directory, byte for byte.

## Run it

```sh
python3 render.py   # redraws entry.png (deterministic, byte-identical)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=9d3wsaqp&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
