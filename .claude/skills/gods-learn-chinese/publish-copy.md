# Publish copy for English-speaking viewers (publish.md)

Series rules on top of `publish-copy-common.md` (platform limits, shared rules): all copy in **English**, platforms YouTube / TikTok / X. The 汉字, pinyin (tone marks) and example appear exactly as on the card.

| platform | title / first line | body | tags |
|---|---|---|---|
| YouTube | ≤ 100 chars incl. ` #Shorts`; hook = the literal translation ("Why do Chinese fans shout 'ADD OIL'?") | plot 2–3 lines → 📖 Word of the day: 汉字 pinyin = meaning → 💬 example + translation → 💡 fun fact (verified) → comment prompt | none: the channel default description ends with them |
| TikTok | first line = hook with emoji | 📖 word → 💬 example → question answerable in one line | 4–5 incl. `#greekmythology` + series tag |
| X | ≤ 280 weighted (CJK = 2, URL = 23) | hook → 📖 word → Shorts link | 2 incl. series tag |

Rules:
- **For now: YouTube only** (user, 2026-10-12: no Gods TikTok account; X paused). Write only the YouTube section in publish.md and publish only there; the TikTok/X rows apply again when the user says so.
- X account: **@MeowMotto** (https://x.com/MeowMotto). Before posting, check the logged-in X handle is @MeowMotto; if not, stop and ask the user to switch.
- Platforms and order: YouTube → TikTok → X (no 抖音/视频号/小红书). In publish.md the X link is the placeholder `https://youtube.com/shorts/<id>`.
- Take plot and lines from `script.json`; never invent plot.
- Series tag on every platform: `#GodsLearnChinese`.
- Site link `https://gods.thewang.net/ep/<NN-slug>/`: YouTube description last line `📚 Examples + full script → <link>`; TikTok last line, domain only (`gods.thewang.net`, not clickable there); X: not needed (Shorts link only).
- YouTube upload defaults (set 2026-10-21): every new upload is prefilled with a channel footer description (series pitch, subscribe line, site link, `#learnchinese #mandarin #chineselesson #GodsLearnChinese`) and generic tags, language English, category Education. Paste the episode description **above** the footer (cursor at the start, don't select-all) and add only episode-specific tags. Drafts uploaded before 10-21 (ep14) have no footer: keep their own hashtag line.
- YouTube captions (from ep14): after publishing, upload `renders/<project>.srt` (from `srt.py`). Studio → 字幕 → the 英語 row's pencil → 続行 (this overwrites the auto track) → ⋮ → ファイルをアップロード → タイムコードあり. Before clicking 続行 in that dialog, `file_upload` into its `#captions-file-loader` (inside `ytve-captions-editor-upload-dialog`). Check the cues loaded, then 公開. Auto captions miss the Chinese and misspell names (ep14: "Odysius", 好久不见 dropped).
- YouTube thumbnail (from ep14; channel phone-verified 2026-10-21): on the Studio edit page, `file_upload` `renders/cover-*-916.jpg` into `ytcp-thumbnail-uploader input#file-loader`, then 保存. Check 「変更を保存しました」 and the reloaded sidebar thumbnail.
- History claims: only what is verifiable, stated narrowly (ep1: Panathenaic Games in Athens awarded olive oil — not "the Olympics").
- Check lengths with Python; post X after YouTube is live (real Shorts link, no `?si=`).
