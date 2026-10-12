# Publish copy for English-speaking viewers (publish.md)

Series rules on top of manga-skit-video `publish-copy.md` (platform limits, shared rules): all copy in **English**, platforms YouTube / TikTok / X. The 汉字, pinyin (tone marks) and example appear exactly as on the card.

| platform | title / first line | body | tags |
|---|---|---|---|
| YouTube | ≤ 100 chars incl. ` #Shorts`; hook = the literal translation ("Why do Chinese fans shout 'ADD OIL'?") | plot 2–3 lines → 📖 Word of the day: 汉字 pinyin = meaning → 💬 example + translation → 💡 fun fact (verified) → comment prompt | `#learnchinese #mandarin #GodsLearnChinese` |
| TikTok | first line = hook with emoji | 📖 word → 💬 example → question answerable in one line | 4–5 incl. `#greekmythology` + series tag |
| X | ≤ 280 weighted (CJK = 2, URL = 23) | hook → 📖 word → Shorts link | 2 incl. series tag |

Rules:
- Platforms and order: YouTube → TikTok → X (no 抖音/视频号/小红书). In publish.md the X link is the placeholder `https://youtube.com/shorts/<id>`.
- Take plot and lines from `script.json`; never invent plot.
- Series tag on every platform: `#GodsLearnChinese`.
- Site link `https://gods.thewang.net/ep/<NN-slug>/`: YouTube description last line `📚 Examples + full script → <link>`; TikTok last line, domain only (`gods.thewang.net`, not clickable there); X: not needed (Shorts link only).
- History claims: only what is verifiable, stated narrowly (ep1: Panathenaic Games in Athens awarded olive oil — not "the Olympics").
- Check lengths with Python; post X after YouTube is live (real Shorts link, no `?si=`).
