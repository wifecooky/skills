---
name: sengoku-chinese
description: Use when making, voicing, publishing or exporting an episode of 「戦国武将、中国語を学ぶ」 (sengoku theme), or any short video teaching Chinese to Japanese viewers — kanji false friends, 同形異義語, Japanese TTS, Japanese-language copy.
---

# 戦国武将、中国語を学ぶ (Chinese for Japanese viewers)

**Pipeline:** `pipeline.md` in this skill (workflow, script.json fields, render). Scripts: `SK=~/.claude/skills/sengoku-chinese/scripts`; theme pack in `themes/`. This skill is self-contained.

## Series
- Audience: Japanese adults learning Chinese. Dialogue is Japanese; only the taught Chinese is Chinese.
- Theme pack `sengoku` (head=1). Recurring cast: N 信長 (impatient boss), H 秀吉 (overconfident flatterer, makes the mistake), I 家康 (deadpan, explains the misunderstanding in one line), T 老師 (teaches the word). Guests (明の商人 etc.) go in the episode's own `cast`.
- Default acting (keep per character, never mix emo and plain for one person): N `emo`; H plain; I plain, `speed` 0.95, `lead` 0.5; T plain, `speed` 0.9 on Chinese words.
- 秀吉's voice is `minimax-official-japanese-generousizakayaowner-98b84089f8` from ep2 on (ep1, rendered and scheduled 2026-10-11, used the Chinese-accented `multi_male_jingqiangkanye`; leave it). Pick voices for Japanese-speaking characters among native `japanese-*` ones: audition on a real line in `samples/`.
- Glyphs: title line 1 = the Japanese word as the hook (手紙); `episode`, card and `stamp` = simplified Chinese (手纸; stamp = the char that differs, 纸).
- `panels.py`/`voice.py` read only the project `script.json` (only `build.py` merges the pack): copy the pack's full `cast` and `style` into the project, edit only the SETTING, add guests to `cast`.
- Project dir: `~/git/sengoku-chinese/videos/sengoku-NN-<slug>` (slug = romanized word, e.g. `sengoku-02-shouzhi`).
- Topic backlog with gag hooks: `topics.md`.
- Famous beauties (user, 2026-10-12: adult audience, add when the plot calls for it, not every episode): a historical beauty as a guest in the episode `cast` — Japanese side お市の方, 濃姫, 茶々; Chinese side 楊貴妃, 西施, 貂蝉 (as a 明 guest, a dream-bubble image or a 信長 fantasy). Level: alluring, not revealing — glamorous makeup, sultry eyes, flirty acting, at most a bare shoulder; no cleavage or body focus, no underwear (YouTube age-restriction kills Shorts reach, TikTok drops suggestive posts from For You). `look`: name the period garment (Sengoku: layered kosode + uchikake; Tang: ruqun with pibo shawl; NOT a qipao) and "bare neck and collarbone, alluring, elegant, fully clothed, no cleavage" (2026-10-12: an off-shoulder uchikake without "no cleavage" drew cleavage; a closed neckline was too prim — the user preferred bare neck and collarbone). Japanese-speaking beauty: audition native `japanese-*` female voices in `samples/`. Put her in the storyboard's cast card so the user approves her.

Before any money is spent: STORYBOARD.md + logic-check + user approval of storyboard and cast (`pipeline.md` step 2). Ask the user before locking a topic.

## Trend episodes (user, 2026-10-12: more reach)
- About one episode a week rides a **Japan-local** trend; the rest stay evergreen. A Chinese-only event (双十一) is not a trend for this audience.
- Find it before storyboarding: WebSearch Japanese trend sources (X/Yahoo realtime via trend-calendar, 渋谷トレンドリサーチ teen words, Nikkei Trendy, TV/drama buzz) plus calendar events (ハロウィン, 紅葉, 七五三, 忘年会, 流行語大賞 in early Dec, 年末年始). Add picks to `topics.md` "Trend candidates" and let the user choose.
- Map the trend to a word: a 同形異義語, or "how do you say <trending Japanese word> in Chinese" (推し活 → 追星). No word that fits the formula → skip the trend.
- Celebrity trends (user, 2026-10-14): a famous person's words, deeds or news (大谷翔平, マスク…) count as a trend when they link naturally to a word in the formula (大谷 → 野球: Chinese says 棒球, 野球 is a pickup game). Any natural link works; skip a forced one. Count it as a trend episode and mark it `[trend·名人]` in LEARNINGS. The celebrity is named only in dialogue and copy, as news the warlords hear (a 瓦版, a 書状); never drawn.
- Site series: a 同形異義語 stays in `sengoku` (/series/onaji-kanji/, 漢字は同じ。意味は、別モノ。). A "how do you say it in Chinese" episode goes to the 流行語 series: add `"series_id": "ryukogo"` after `"theme"` in the project `script.json` so `export_lesson.py` writes `content/ryukogo/` (page `/videos/ryukogo-NN-<slug>/`, not `/ep/`; use that URL in `publish.md`). Episode numbers stay one channel-wide sequence (ep5 追星 is ryukogo 第5話).
- Timing: a trend episode jumps the queue; schedule it within days, not behind the 2-day backlog.
- Never: politics or diplomacy (including Japan–China), disasters, crime, deaths, drawing living real people (no likeness, no name in art; naming a celebrity in dialogue and copy is fine). Don't draw characters from a TV drama or anime (copyright); naming the trend in copy and hashtags is fine.

## Episode formula (≤40 s, no intro; from ep18, LEARNINGS H14)
Set `"intro": false` after `"theme"`. The first scene carries `"title": true`: the title slams in at 0.1 s, stays alone about 1 s, and clears before the first bubble (build.py). Give that first line `lead` ≈ 1.8.
1. Cold open (0 s): 秀吉 uses the **Japanese meaning** of a shared kanji word → the Chinese side hears something absurd. The title states the absurd result (H7). Put the motive in the `sub` (例: 「必死で恋しておられる」), since there is no setup scene.
2. Card scene **by 10 s**: `{zh, py, en: "＝<日本語の意味>", note: "<correct word> · <例文>（訳）"}`, `min` ≈ 4.4. 老師 says the word slowly; the example stays on the card, not in the voice.
3. Irony: the viewer now knows; the characters act on the wrong meaning.
4. 家康 dry one-liner names what went wrong. Keep it: the card talks to the viewer, so a character needs an in-story trigger to learn the word.
5. Callback: 信長 "learns" it and over-applies or reverses it → final gag + stamp.
Outro (theme pack): title フォローしてね！ + badge 「毎回ひとつ、漢字のワナ」 (the subscribe reason). 
6. Next-episode teaser (ep19–20, H14 variant; user 2026-10-28): one last scene before the outro. 家康 says 「次回、「<next word>」は中国語で……？」 over the stamp panel (copy its image to the teaser id, so `panels.py` skips it: no image cost). Lock the next topic first; no locked topic → skip the teaser. It counts toward the 40 s. 家康 is not in that panel, so give the line `"focus": [50,45], "zoom": 1.0` (full frame, no push); without it `check_episode.py` fails "on-screen speaker has no focus", and `"os": true` is wrong (it renders a thought bubble). Budget: ep19 hit 44.9 s with the teaser; keep 家康's one-liner ≤ ~4 s and tail the teaser at 0.1 (ep19: 39.93 s).
Check the total in build.py output: ≤ 40 s, card start ≤ ~10 s.

Put one reusable example sentence in `"lesson": {"examples": [{"zh","py","tr"}]}`; it must equal the card's example.

## Voice rules (each one cost a re-take)
| Situation | Do |
|---|---|
| Japanese where nativeness matters (CTA, explanations) — give these lines to 家康; 老師 (multi voice) only gets one short Japanese prompt like 「では、「むすめ」は？」 | Native Japanese voice: minimax `japanese-*` or doubao `ja_female_bv52x`. doubao `multi_*` voices speak Japanese with a Chinese accent (ASR heard フォロー as ポロー). |
| A line mixing Japanese and Chinese | Split into two lines, one language each. |
| Kanji with ambiguous readings | Pin with kana in `say` (`ははうえ`, `むっつ`, `ミン`). Kana only the ambiguous word: keep the kanji before a particle (`皇帝への`), since all-kana `こうていへの` read the particle へ as *he* instead of *e*. |
| 信長 (doubao `multi` emo voice) ending on an old-style particle (じゃのう, じゃな) | Use the common word (大胆, not 豪胆), put a comma before the particle in `say` (`だいたん、じゃのう`), and write 「咬字清楚」 in `emo`, not 「嘀咕」. ep7: the user flagged 「豪胆じゃのう」 twice; 6 re-takes. |
| Short isolated Chinese word **being taught** (card word: 娘, 手纸) | `say` it twice with 。 (teaching repetition), `speed` 0.9. Never end it with ！ — 「再见！」 squeaked to ~570 Hz. |
| Short Chinese word that is **not taught** (outro 再见) | Say it **once**, ending with 。: `say` must match `text`. A doubled `say` under a single bubble plays two 再见 against one caption. |
| Chinese polyphone (多音字) | The TTS picks a reading per 汉字 chunk (cut by 。): a lone 「扫。」 came out sǎo though the card taught sào (olympus ep7). `vo_check.py --text` checks Chinese lines against the card `py` and the bubble pinyin (「信 xìn」), and lists each misread as POLY with single-reading homophones. Put one in `say` only; the bubble keeps the real 汉字. Pick a char with no second reading. Japanese lines are skipped (their kanji go through the kana rule above). |
| Japanese line naming a Chinese word (家康's explanation) | Refer to the written form: 「中国語で「手紙」と書けば、ちり紙。」, not 「中国語の「手紙」は…」 — the latter reads the Chinese word in Japanese (てがみ) and sounds wrong. |
| Outro | The spoken line must say what the on-screen title says (title フォローしてね → 家康「……フォロー、してくだされ。」). |
| Pure-Chinese teacher | The `multi_` teacher voice can read the card word in the wrong tones; ASR does not catch it (it prints the right 汉字). ep20 (2026-10-29, user flagged): 「结束。」 came out like jiě shū — 结 dipped low, 束 stayed high and flat instead of falling. Fix: set the project's T `voice` to `doubao-official-zh_female_shuangkuaisisi_moon_bigtts` (same speaker, pure Chinese) and re-voice the card lines. Check: trace F0 (librosa.pyin) of the card line; each syllable's contour must match its tone (4th = clear fall, 2nd = rise or level, not a dip). |

## QA gate (before showing any preview)
Before `voice.py`: `python3 $SK/vo_check.py --text` (no audio, free); fix every POLY line first. After `build.py`: `python3 $SK/vo_check.py`. It ASRs every line in its own language and flags pitch outliers per speaker+language. Re-voice or ear-check every CHECK line; a shouted line may be a false positive, a squeaky short word is not. Only then send the preview URL.

## Feedback (`feedback-loop.md`)
- Store `<S>`: `~/git/sengoku-chinese/videos/_metrics/sengoku`
- Public sources for `fetch`: every `published.youtube` link in `~/git/sengoku-chinese/content/*/episodes/*.json`, plus `https://www.tiktok.com/@sengoku_chugokugo`
- No dashboards.
- Weekly scout (Mondays, or the first run of the week): YouTube search 「中国語 ショート」「中国語 勉強」「同じ漢字 中国語」, filter Shorts, this month. Look for small channels (≤ ~5K subscribers) whose video has views ≥ 10× their subscriber count. Copy title, hook (first line) and format into topics.md 「Scout」 with the URL and date. Ideas only: never copy art, script or a word list. Big channels don't count (their views come from the subscribers).

## Publish
Japanese copy, rules in `publish-copy.md`. Never publish without an explicit go per platform (`pipeline.md` step 11).

## Content export (the site owns the content)
After render, and again after publishing (fill `published` links): `python3 $SK/export_lesson.py` → `~/git/sengoku-chinese/content/sengoku/episodes/NN-<slug>.json` (or `content/ryukogo/` with `series_id`) (cover copied to `covers/`; also fill `published.date`; deploy per that repo's README). Re-export keeps the `published` links.
