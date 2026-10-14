# Publish copy (publish.md)

After every render, write `publish.md` in the project root. One file holds the copy for all platforms. The series skill's `publish-copy.md` sets the language, platforms, series tag and template; this file holds what every series shares.

## Limits (check with Python `len()`; an emoji counts as 1)

| platform | title | tags | other |
|---|---|---|---|
| 抖音 | ≤ 30 chars | ≤ 5, end with series tag | |
| 视频号 | 短标题 6–16 chars, plain (no emoji, no punctuation tricks) | 3–5 | |
| 小红书 | ≤ 20 chars incl. emoji | 5–10 | body ≤ 1000 chars; cover is 3:4 (1080×1440) |
| YouTube | ≤ 100 chars incl. ` #Shorts` | 3–5 in description | publish as Public |
| X | — | 2–3 | one post ≤ 280 weighted (CJK = 2, URL = 23); post after YouTube is live; link `https://youtube.com/shorts/<id>` |

## Rules
- Take the plot, the lines, and the card from `script.json`. Never invent plot points that are not in the video.
- The taught phrase, its pronunciation, and the example must match the card in the video word for word.
- Topical episodes (news, sports scores): use the real facts as stated in the script (score, opponent, home/away).
- Fixed series tag on every platform (named in the series skill).
- Header lines: video path in `renders/`, cover path (3:4).
- Comment question: something viewers can answer in one line.
- Site link (traffic to the series site): the episode page `https://<domain>/ep/<NN-slug>/` (NN-slug = the exported episode file name). The series skill names the domain and which platforms get it. It is live only after the episode is exported with its `published` link and pushed (step 12).
