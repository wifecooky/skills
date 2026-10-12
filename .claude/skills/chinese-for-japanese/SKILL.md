---
name: chinese-for-japanese
description: Use when making, voicing, publishing or exporting an episode of 「戦国武将、中国語を学ぶ」 (sengoku theme), or any short video teaching Chinese to Japanese viewers — kanji false friends, 同形異義語, Japanese TTS, Japanese-language copy.
---

# 戦国武将、中国語を学ぶ (Chinese for Japanese viewers)

**REQUIRED SUB-SKILL:** manga-skit-video (pipeline, script.json fields, render). This skill only adds what is specific to this series.

## Series
- Audience: Japanese adults learning Chinese. Dialogue is Japanese; only the taught Chinese is Chinese.
- Theme pack `sengoku` (head=1). Recurring cast: N 信長 (impatient boss), H 秀吉 (overconfident flatterer, makes the mistake), I 家康 (deadpan, explains the misunderstanding in one line), T 老師 (teaches the word). Guests (明の商人 etc.) go in the episode's own `cast`.
- Default acting (keep per character, never mix emo and plain for one person): N `emo`; H plain; I plain, `speed` 0.95, `lead` 0.5; T plain, `speed` 0.9 on Chinese words.
- 秀吉's voice is `minimax-official-japanese-generousizakayaowner-98b84089f8` from ep2 on (ep1, rendered and scheduled 2026-10-11, used the Chinese-accented `multi_male_jingqiangkanye`; leave it). Pick voices for Japanese-speaking characters among native `japanese-*` ones: audition on a real line in `samples/`.
- Glyphs: title line 1 = the Japanese word as the hook (手紙); `episode`, card and `stamp` = simplified Chinese (手纸; stamp = the char that differs, 纸).
- `panels.py`/`voice.py` read only the project `script.json` (only `build.py` merges the pack): copy the pack's full `cast` and `style` into the project, edit only the SETTING, add guests to `cast`.
- Project dir: `~/git/sengoku-chinese/videos/sengoku-NN-<slug>` (slug = romanized word, e.g. `sengoku-02-shouzhi`).
- Topic backlog with gag hooks: `topics.md`.

Before any money is spent: STORYBOARD.md + logic-check + user approval of storyboard and cast (manga-skit-video step 2). Ask the user before locking a topic.

## Episode formula (~35s body, ~50s with intro/outro)
1. Setup: 信長 orders 秀吉 to use Chinese.
2. 秀吉 uses the **Japanese meaning** of a shared kanji word → the Chinese side hears something absurd.
3. 家康 dry one-liner names what went wrong.
4. Card scene: `{zh, py, en: "＝<日本語の意味>", note: "<correct word> · <例文>（訳）"}`, `min` ≈ 6. 老師 says the word slowly.
5. Callback: 信長 "learns" it and over-applies or reverses it → final gag + stamp.

Put one reusable example sentence in `"lesson": {"examples": [{"zh","py","tr"}]}`; it must equal the card's example.

## Voice rules (each one cost a re-take)
| Situation | Do |
|---|---|
| Japanese where nativeness matters (CTA, explanations) — give these lines to 家康; 老師 (multi voice) only gets one short Japanese prompt like 「では、「むすめ」は？」 | Native Japanese voice: minimax `japanese-*` or doubao `ja_female_bv52x`. doubao `multi_*` voices speak Japanese with a Chinese accent (ASR heard フォロー as ポロー). |
| A line mixing Japanese and Chinese | Split into two lines, one language each. |
| Kanji with ambiguous readings | Pin with kana in `say` (`ははうえ`, `むっつ`, `ミン`). Kana only the ambiguous word: keep the kanji before a particle (`皇帝への`), since all-kana `こうていへの` read the particle へ as *he* instead of *e*. |
| Short isolated Chinese word **being taught** (card word: 娘, 手纸) | `say` it twice with 。 (teaching repetition), `speed` 0.9. Never end it with ！ — 「再见！」 squeaked to ~570 Hz. |
| Short Chinese word that is **not taught** (outro 再见) | Say it **once**, ending with 。: `say` must match `text`. A doubled `say` under a single bubble plays two 再见 against one caption. |
| Japanese line naming a Chinese word (家康's explanation) | Refer to the written form: 「中国語で「手紙」と書けば、ちり紙。」, not 「中国語の「手紙」は…」 — the latter reads the Chinese word in Japanese (てがみ) and sounds wrong. |
| Outro | The spoken line must say what the on-screen title says (title フォローしてね → 家康「……フォロー、してくだされ。」). |
| Pure-Chinese teacher | `doubao-official-zh_female_shuangkuaisisi_moon_bigtts` exists if the multi voice sounds off. |

## QA gate (before showing any preview)
After `build.py`: `python3 $SK/vo_check.py`. It ASRs every line in its own language and flags pitch outliers per speaker+language. Re-voice or ear-check every CHECK line; a shouted line may be a false positive, a squeaky short word is not. Only then send the preview URL.

## Feedback (manga-skit-video `feedback-loop.md`)
- Store `<S>`: `~/git/sengoku-chinese/videos/_metrics/sengoku`
- Public sources for `fetch`: every `published.youtube` link in `~/git/sengoku-chinese/content/sengoku/episodes/*.json`, plus `https://www.tiktok.com/@sengoku_chugokugo`
- No dashboards.

## Publish
Japanese copy, rules in `publish-copy.md`. Never publish without an explicit go per platform (manga-skit-video step 11).

## Content export (the site owns the content)
After render, and again after publishing (fill `published` links): `python3 $SK/export_lesson.py` → `~/git/sengoku-chinese/content/sengoku/episodes/NN-<slug>.json` (cover copied to `covers/`; also fill `published.date`; deploy per that repo's README). Re-export keeps the `published` links.
