---
name: chinese-for-english-speakers
description: Use when making, voicing, publishing or exporting an episode of "Gods Learn Chinese" (olympus theme), or any short video teaching Chinese to English-speaking viewers — literal-translation gags, English TTS saying Chinese words, English-language copy.
---

# Gods Learn Chinese (Chinese for English speakers)

**REQUIRED SUB-SKILL:** manga-skit-video (pipeline, script.json fields, render). This skill only adds what is specific to this series.

## Series
- Audience: English speakers learning Mandarin. Dialogue is English; only the taught expression is Chinese.
- Theme pack `olympus` (head=1). Recurring cast: Z Zeus (boss who volunteers others), E Hermes (god of translation — deadpan, gives only the literal translation), H Hercules (takes everything literally, makes the mistake), A Athena (narrator/teacher, never drawn).
- Default acting (one engine per character): Z plain; E plain, `speed` 0.9–0.95, pause between words; H `emo` on every line; A plain, `speed` 1.0.
- A god outside the cast (Poseidon…) either stays off-screen (show only his horses/waves) or joins the episode `cast` with a voice audition.
- `panels.py`/`voice.py` read only the project `script.json` (only `build.py` merges the pack): copy the pack's full `cast` and `style` into the project, edit only the SETTING, add guests to `cast`.
- Project dir: `~/git/manga-chinese-sites/videos/olympus-NN-<slug>` (slug = pinyin without tones, e.g. `olympus-02-mashang`).
- Topic backlog with gag hooks: `topics.md`.

Before any money is spent: STORYBOARD.md + logic-check + user approval of storyboard and cast (manga-skit-video step 2). Ask the user before locking a topic.

## Episode formula (~40s body, ~55s with intro/outro)
1. Setup: Zeus drops a task on Hercules; the Chinese expression appears in context.
2. Hermes: the word-for-word translation, deadpan ("Add. Oil.").
3. Hercules acts out the literal meaning → disaster. `gray` = what he imagines; anything a later scene pays off must happen in a normal panel.
4. Card scene, Athena explains: `{zh: "<汉字>", py: "<tone-marked pinyin>", en: "<real meaning>", note: "<tone tip> · <when to use>"}`, `min` ≈ 6, plus a "Say it with me" line.
5. Payoff: Hercules uses it right, then a twist that seems to "prove" the literal meaning; Hermes repeats his line → stamp.

Put one reusable example in `"lesson": {"examples": [{"zh","py","tr"}]}` (tr = English); it must match the card/description.
Ancient-Greece facts used as gags must be true and go in the description narrowed to what is verifiable.

## Voice rules
| Situation | Do |
|---|---|
| An English voice says the Chinese word | Bubble `text` shows 汉字; `say` spells it phonetically ("Jyah-yoh", "Mah-shahng") — not bare pinyin ("Jiayou" in ep1 06-1 is the exception to avoid). Never feed 汉字 to an English voice. |
| Teaching the tones | Only Athena (`zh_female_yingyujiaoxue`, bilingual teacher voice) says real Chinese. A lone 汉字 inside an English sentence loses its tone (ep1 「油」 came out flat); end each Chinese word with 。 (`加。 means add. 油。 means oil.`), `speed` 1.0. Ear-check every syllable. |
| Hercules shouting (emo) | High-energy emo can swap speaker mid-line; ep1 06-1 hit 513 Hz. Re-roll 3–4 takes, keep the one whose pitch stays in his range (vo_check), let the user pick by ear; plain TTS only if every take swaps. |
| Outro | Spoken line must match the on-screen title: pack says "Got it? Follow for more Chinese!" + 「下次见。」 under title "Follow for more Chinese!". Change both together or neither. |

## QA gate (before showing any preview)
After `build.py`: `python3 $SK/vo_check.py`. Athena's mixed lines are always flagged "mixed" — expected for her bilingual voice, but listen to the Chinese part. Ear-check or re-voice every other CHECK line, then send the preview URL.

## Publish
English copy, rules in `publish-copy.md`. Never publish without an explicit go per platform (manga-skit-video step 11).

## Content export (the site owns the content)
After render, and again after publishing (fill `published` links): `python3 $SK/export_lesson.py` → `~/git/manga-chinese-sites/content/olympus/episodes/NN-<slug>.json` (cover copied to `covers/`; also fill `published.date`; deploy per that repo's README). Re-export keeps the `published` links.
