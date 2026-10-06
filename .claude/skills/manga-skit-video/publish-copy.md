# Publish copy (publish.md)

After every render, write `publish.md` in the project root. One file holds the copy for all platforms. Audience: Chinese speakers learning English. All copy is in Chinese, and the English phrase appears verbatim.

## Limits (check with Python `len()`; an emoji counts as 1)

| platform | title | body | tags | other |
|---|---|---|---|---|
| 抖音 | ≤ 30 chars, hook + phrase | 3–6 lines: plot setup → 📖 phrase = 中文 → 💬 example → comment question | ≤ 5, end with series tag | |
| 视频号 | 短标题 6–16 chars, plain (no emoji, no punctuation tricks) | plot in 1–2 sentences → 📖 phrase + meaning → 💬 example + translation → 💡 one tip | 3–5 | |
| 小红书 | ≤ 20 chars incl. emoji | ≤ 1000 chars, emoji section heads (📖 今日俗语 / 💬 例句直接抄 / 💡 小贴士), IPA, short lines, ends with 收藏 + comment prompt | 5–10 | cover is 3:4 (1080×1440) |
| YouTube | see `brand/youtube-copy.md` format: title ≤ 100 with `#Shorts` | description with phrase, IPA, example, tips, hashtags | 3–5 in description | publish as Public |
| X | — | one post ≤ 280 weighted (CJK = 2, URL = 23): hook line → English phrase → Shorts link | 2–3 | post after YouTube is live; link `https://youtube.com/shorts/<id>` |

## Rules
- Take the plot, the lines, and the phrase card from `script.json`. Never invent plot points that are not in the video.
- The phrase, IPA, and example must match the card in the video word for word.
- Topical episodes (news, sports scores): use the real facts as stated in the script (score, opponent, home/away).
- Fixed series tag on every platform: `#桃园英语角`.
- Header lines: video path in `renders/`, cover path (3:4 for 小红书 / 视频号).
- Comment question: something viewers can answer in one line (tag a friend, make a sentence with the phrase).

## Template

```markdown
# 发布文案 · 第N课 <中文俗语> / <English phrase>

视频：`renders/<latest>.mp4`
封面：`../brand/cover-epN-<slug>.jpg`（3:4）

## 抖音
**标题**（≤30 字）
**简介**
#… ×≤5

## 视频号
**短标题**（6–16 字）
**描述**
#… ×3–5

## 小红书
**标题**（≤20 字）
**正文**
#… ×5–10

## YouTube
（title / description / tags, or a pointer to brand/youtube-copy.md）

## X
**推文**（≤280 加权字符，链接发布后填）
```

Reference: `~/Downloads/funny-short/videos/caocao/publish.md`, `guozu/publish.md`.
