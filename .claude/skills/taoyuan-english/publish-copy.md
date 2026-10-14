# Publish copy for Chinese viewers (publish.md)

Series rules on top of `publish-copy-common.md` (platform limits, shared rules). All copy is in Chinese, and the English phrase appears verbatim. Platforms: 抖音 / 视频号 / 小红书 / YouTube / X.

| platform | title | body |
|---|---|---|
| 抖音 | hook + phrase | 3–6 lines: plot setup → 📖 phrase = 中文 → 💬 example → comment question |
| 视频号 | 短标题 | plot in 1–2 sentences → 📖 phrase + meaning → 💬 example + translation → 💡 one tip |
| 小红书 | | emoji section heads (📖 今日俗语 / 💬 例句直接抄 / 💡 小贴士), IPA, short lines, ends with 收藏 + comment prompt |
| YouTube | see `~/git/taoyuan-english/videos/_brand/youtube-copy.md` | description with phrase, IPA, example, tips, hashtags |
| X | | hook line → English phrase → Shorts link |

Rules:
- Fixed series tag on every platform: `#桃园英语角`.
- Comment question: tag a friend, or make a sentence with the phrase.
- Site link `https://taoyuan.thewang.net/ep/<NN-slug>/`: YouTube description last line `📚 例句和全文 → <link>`; 抖音 and 视频号 last line, domain only (`🌐 taoyuan.thewang.net`, no https, not clickable there); 小红书: none (outside links get notes throttled; put the domain in the profile instead); X: not needed.

## Template

```markdown
# 发布文案 · 第N课 <中文俗语> / <English phrase>

视频：`renders/<latest>.mp4`
封面：`renders/cover-epN-<slug>.jpg`（3:4）

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
