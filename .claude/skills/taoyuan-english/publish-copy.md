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
- Tags pick who the platform shows the video to first, so they target learners, not the news crowd (LEARNINGS H9, 2026-10-15). Put at least 3 learning tags first (`#英语口语` `#学英语` `#每日英语` `#地道英语` `#英语表达`), then at most 1 trend tag, and only when the people following that news overlap with English learners: `#雅思` `#出国` `#留学` `#抢票` `#演唱会` yes; `#双11` (shoppers) or `#中网` (sports results) no. The trend itself goes in the title and the first line.
- YouTube upload defaults (set 2026-10-21): every new upload is prefilled with a channel footer description (series pitch, subscribe line, `📚 全部课程和例句 → https://taoyuan.thewang.net/`, `#学英语 #英语口语 #桃园英语角`) and generic tags, language Chinese (中国語), category Education. Paste the episode description **above** the footer (cursor at the start, don't select-all), keep only the hashtags the footer lacks (e.g. `#Shorts`), and add only episode-specific tags.
- YouTube 繁體 title/description (from 2026-10-21; Taiwan 46.5% + Hong Kong 5.9% of views over the 28 days to 10-19): after uploading, take the video's final title and description from the Studio Details page (footer included), run each through `python3 $SK/zht.py` (OpenCC s2twp, Taiwan wording; hashtags stay simplified so both versions feed the same tag pages), then fill it in on `https://studio.youtube.com/video/<id>/translations` (verified 2026-10-21 on all 16 published videos, English Studio UI). Viewers whose YouTube is set to Traditional then see this version.
  1. If the page shows "Set language" + "Confirm" (videos uploaded before 10-21 have no video language): pick Chinese, untick "Make this the default for my channel" (`[role=checkbox]`, check `aria-checked="false"`), Confirm. Wait for "Video language: Chinese".
  2. Add language → Chinese (Traditional). A dialog titled "Chinese (Traditional)" opens with `#textbox[aria-label="Title"]` and `#textbox[aria-label="Description"]` (contenteditable; fill with focus + `execCommand('selectAll')` + `execCommand('insertText')`).
  3. Update. Check the toast "Chinese (Traditional) title and description published" and that the row's Title & description column says Published. To re-check later, click the row's language name: the same dialog opens with the saved text; close it with its Cancel (X) icon.
  - Right after page load, dropdown and checkbox clicks are often ignored, and the page can briefly show a stale state: retry the click until the value changes, and reload if the page looks half-loaded.
- YouTube captions (from 2026-10-21): after uploading, upload `renders/<project>.srt` (from `srt.py`). Studio → 字幕 → the 中国語 row's pencil → 続行 (this overwrites the auto track) → ⋮ → ファイルをアップロード → タイムコードあり. Before clicking 続行 in that dialog, `file_upload` into its `#captions-file-loader` (inside `ytve-captions-editor-upload-dialog`). Check the cues loaded, then 公開. Auto captions garble the English phrase the episode teaches. The button names above come from the Japanese Studio UI (sengoku/GLC); taoyuan's Studio is in English (verified 2026-10-21 on ep17): do it inside the upload dialog at Video elements → Subtitles "Add" → "Upload file" → (a "With timing" prompt appears; don't click Continue) `file_upload` into `#captions-file-loader` → check cues → "Done". That Done only saves a draft: after publishing the video, go to `studio.youtube.com/video/<id>/translations` → "Edit subtitles" → "Publish", and check the toast "Chinese subtitles published".
- YouTube thumbnail (from 2026-10-21): on the Studio edit page, `file_upload` the 3:4 `renders/cover-epN-<slug>.jpg` into `ytcp-thumbnail-uploader input#file-loader`, then 保存. Check 「変更を保存しました」 and the reloaded sidebar thumbnail. If nothing changes, the channel may still need phone verification (the user does it; a `yt-trust-tiers-wizard` asks for 電話番号).
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
