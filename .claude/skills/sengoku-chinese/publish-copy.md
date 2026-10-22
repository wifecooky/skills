# Publish copy for Japanese viewers (publish.md)

Series rules on top of `publish-copy-common.md` (platform limits, shared rules): all copy in **Japanese**, platforms YouTube (JP) / TikTok (JP) / X. The Chinese word, pinyin and example appear exactly as on the card.

| platform | title / first line | body | tags |
|---|---|---|---|
| YouTube | ≤ 100 chars incl. ` #Shorts`; hook = the false friend as a question (「中国語の「娘」は“お母さん”！？」) | plot 2–3 lines → 📖 今日の単語 → 💬 例文（訳）→ 💡 one tip → comment prompt | `#中国語 #中国語勉強 #戦国武将中国語を学ぶ` |
| TikTok | first line = hook with emoji | 📖 word → 💬 例文 → question viewers can answer in one line | 4–5 incl. `#戦国武将 #日本史` + series tag |
| X | ≤ 280 weighted (CJK = 2, URL = 23) | hook → plot one line → 📖 word → Shorts link | 2 incl. series tag |

Rules:
- Platforms and order: YouTube → TikTok → X. In publish.md the X link is the placeholder `https://youtube.com/shorts/<id>`.
- Take plot and lines from `script.json`; never invent plot.
- Series tag on every platform: `#戦国武将中国語を学ぶ`.
- Site link `https://sengoku.thewang.net/ep/<NN-slug>/`: YouTube description last line `📚 例文と全セリフ → <link>`; TikTok last line, domain only (`sengoku.thewang.net`, not clickable there); X: not needed (Shorts link only, saves 23 chars).
- YouTube upload defaults (set 2026-10-21): every new upload is prefilled with a channel footer description (series pitch, subscribe line, `📚 全エピソードと例文 → https://sengoku.thewang.net/`, `#中国語 #中国語勉強 #戦国武将中国語を学ぶ`) and generic tags, language 日本語, category 教育. Paste the episode description **above** the footer (cursor at the start, don't select-all), drop the episode's own hashtag line (the footer has it), and add only episode-specific tags. The tag box ignores typed commas and Enter: dispatch a `paste` ClipboardEvent with `text/plain` `tag1,tag2,` on the tag input.
- YouTube captions (from ep14, 2026-10-21): after uploading, upload `renders/<project>.srt` (from `srt.py`). Studio → 字幕 → the 日本語 row's pencil → 続行 (this overwrites the auto track) → ⋮ → ファイルをアップロード → タイムコードあり. Before clicking 続行 in that dialog, `file_upload` into its `#captions-file-loader` (inside `ytve-captions-editor-upload-dialog`). The page may hold two file inputs; use the one `find` lists next to the dialog's 続行 (ep14: the other one did nothing). Check the cues loaded, then 公開. Auto captions miss the Chinese word the episode teaches.
- YouTube thumbnail (from ep14): on the Studio edit page, `file_upload` `renders/cover-*-916.jpg` into `ytcp-thumbnail-uploader input#file-loader`, then 保存. Check 「変更を保存しました」 and the reloaded sidebar thumbnail. If nothing changes, the channel may still need phone verification (the user does it; a `yt-trust-tiers-wizard` asks for 電話番号).
- Use 「信長様」 respectful forms in copy, matching the in-video tone.
- Check lengths with Python; post X after YouTube is live (real Shorts link, no `?si=`).
- Reference: `~/git/sengoku-chinese/videos/sengoku-01-niang/publish.md`.
