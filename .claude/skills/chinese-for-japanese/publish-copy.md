# Publish copy for Japanese viewers (publish.md)

Overrides manga-skit-video `publish-copy.md` for this series: all copy in **Japanese**, platforms YouTube (JP) / TikTok (JP) / X. The Chinese word, pinyin and example appear exactly as on the card.

| platform | title / first line | body | tags |
|---|---|---|---|
| YouTube | ≤ 100 chars incl. ` #Shorts`; hook = the false friend as a question (「中国語の「娘」は“お母さん”！？」) | plot 2–3 lines → 📖 今日の単語 → 💬 例文（訳）→ 💡 one tip → comment prompt | `#中国語 #中国語勉強 #戦国武将中国語を学ぶ` |
| TikTok | first line = hook with emoji | 📖 word → 💬 例文 → question viewers can answer in one line | 4–5 incl. `#戦国武将 #日本史` + series tag |
| X | ≤ 280 weighted (CJK = 2, URL = 23) | hook → plot one line → 📖 word → Shorts link | 2 incl. series tag |

Rules:
- Platforms and order: YouTube → TikTok → X. In publish.md the X link is the placeholder `https://youtube.com/shorts/<id>`.
- Take plot and lines from `script.json`; never invent plot.
- Series tag on every platform: `#戦国武将中国語を学ぶ`.
- Use 「信長様」 respectful forms in copy, matching the in-video tone.
- Check lengths with Python; post X after YouTube is live (real Shorts link, no `?si=`).
- Reference: `~/git/manga-chinese-sites/videos/sengoku-01-niang/publish.md`.
