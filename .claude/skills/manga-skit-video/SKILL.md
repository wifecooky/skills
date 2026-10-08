---
name: manga-skit-video
description: Use when the user wants a joke, skit, funny short, YouTube Short/TikTok, or anecdote re-enacted as a vertical comic/manga-style video with AI-drawn panels, AI voice-over and speech bubbles — 漫画重演, 搞笑短剧, 做成爆笑视频, 日漫风段子, manga gag remake.
---

# Manga Skit Video

## Overview
One `script.json` drives everything: OpenAI gpt-image-2 draws the panels, ListenHub voices the lines, MusicGen makes the BGM, and `build.py` writes a HyperFrames `index.html` (1080x1920). **Timing comes from the real VO lengths**, so you never hand-time anything. Re-voice a line, rerun build, done.

Reference implementation: `example/script.json`, a 14-scene, 51s skit (rooftop "confession" twist).

## Workflow
Scripts live in `~/.claude/skills/manga-skit-video/scripts/`. Run them all **from the project dir** (`SK=~/.claude/skills/manga-skit-video/scripts`).

1. **Get the source.** If there's a URL, watch/transcribe it. Confirm the format with the user: a re-enactment of the joke, NOT a game or quiz wrapped around it.
2. **Storyboard.** Write `script.json` (copy the example) plus a short `STORYBOARD.md` with three tables, and get user approval before spending money:
   - scene → art → line → gag
   - **cast card**: character → personality / `persona` → voice → default tone
   - **every line → its `emo`**, or "plain TTS" for calm, deadpan or teaching lines

   Before showing it, run **`logic-check.md`** with a fresh subagent (setup/payoff, reveal-once, causality …) and fix every BLOCKER. Rerun it after any scene change.

   Voice only after the user confirms the cast card and emotions.
3. `npx hyperframes init` (or reuse a project) → put `script.json` in the project root.
4. `python3 $SK/panels.py`. The first run only makes `assets/panels/00-charsheet.png`. **Show it to the user.** Rerun to draw all panels (parallel, skips existing). Redo one: delete the png/jpg, then `panels.py 07`.
5. `python3 $SK/voice.py`. Prints each line's duration. Redo: `voice.py --force` or `voice.py 11-1`. Changed only `speed`? Run `voice.py --local`. It re-trims and re-tempos the cached raw mp3s with no API cost.
6. `python3 $SK/bgm.py` (slow; run in background). Needs torch and transformers.
7. `python3 $SK/build.py`. Prints the timing table. Copies fonts and sfx into `assets/` if missing.
8. `npx hyperframes check`, then `npx hyperframes snapshot --at <one time per scene> --no-end`, then **Read the contact sheet**.
9. `npx hyperframes preview --background`, then give the user the URL. Render MP4 **only after the user approves**, with `npx hyperframes render --crf 23`. Projects pin the CLI version in `package.json`. Upgrade with `npx hyperframes@latest upgrade --project . --check`, then without `--check`, then `check` and compare a snapshot against the old one. If the latest version won't install, keep the pin: `npx --yes hyperframes@<pin> …`. The default `looks` quality is CRF 16, which comes out around 16 Mbps / 140 MB for 73 s; CRF 23 is about 40 MB with no visible loss.
10. **Always** write `publish.md` (抖音 / 视频号 / 小红书 / YouTube / X copy) per `publish-copy.md`, check title lengths with Python, and give it to the user along with the MP4.
11. **Publish (only when the user says so).** Drive the user's **own logged-in Chrome** with Claude in Chrome (`mcp__claude-in-chrome__*`; load them all in one ToolSearch). This overrides the global "use gstack-browse" rule: gstack's Chromium is an empty profile with no logins, and cookie import is blocked by the sandbox.
   - One platform per tab, one at a time. Order: YouTube first (X needs the Shorts link) → 抖音 → 视频号 → 小红书 → X.
   - X: post the `publish.md` X text with the real Shorts link (no `?si=`). Don't use YouTube's Share → X button: it only sends the title + link, so the hashtags and the expression line are lost.
   - Upload the MP4 + 3:4 cover with `file_upload` on the page's `<input type=file>` (never click the upload button: it opens a native picker). **Read `publish-platforms.md` first**: the 10 MB upload cap, the 抖音 cover input, the 视频号 shadow DOM (`scripts/cors_serve.py`), and 小红书 topic picking.
   - Fill title / copy / tags from `publish.md`, then **show the user the exact title and copy and wait for a yes before clicking 发布** on each platform.

## script.json quick reference
Top level:
- `series` (header text) and `title` [line1, line2-red]
- `episode`, `stamp` (end stamp char), `speed` (global TTS speed; 1.2 sounds natural)
- `cast.{F,M}`: `{name, chip:"red"|"ink", voice, look, persona?}`. `look` is the English appearance prompt (leave it empty for a narrator who is never drawn). `persona` is a Chinese identity anchor (e.g. "关羽，高冷威严的中年男人，低沉男声"). It is prepended to every `emo` line's acting note to keep the speaker consistent (meant to curb mid-line drift; not proven yet).
- `style`: the art prompt. Must include "NO TEXT" and the SETTING.
- `watermark`: channel handle shown top-right for the whole video (a theme can set it).
- `bgm.{name}`: `{vol, prompt, sec?}` (`sec` = length to generate, default 28; use 3–6 for stings and jingles)
- `theme`: a reusable theme pack at `themes/<name>/` that adds an intro, an outro, jingles and a recurring cast. The pack dir is itself a mini project:
  - Its `script.json` has `head` (how many of its scenes open the video; the rest close it), plus `style`, `cast`, `bgm` and `scenes`.
  - Make its assets once by running `panels.py`, `voice.py` and `bgm.py` inside the pack dir.
  - `build.py` splices its scenes around the episode. Its cast and bgm fill gaps; the project wins on clashes.
  - Missing `assets/*` files are copied from the pack.
  - The intro carries `title: true`, so **don't put `title` on scene 01**. The outro's `title` is its own `[line1, line2]` plus `ep`.
  - Available packs: `sanguo` (刘关张曹 + Owen老师, war-drum intro, jingle outro, watermark `@桃园英语角`).
  - New series: copy a pack, edit its `script.json` (`style`, `cast`, `bgm`, `scenes`), and rerun the three scripts in the pack dir.

Scene fields:
| field | meaning |
|---|---|
| `id`, `art` | panel `assets/panels/{id}.jpg` + its prompt |
| `entry` | `cut` / `push` (whoosh) / `flash` (white flash + impact) |
| `rot` | panel tilt in degrees |
| `lines` | `[{who, text, emo?, os?, lead?, speed?, say?}]`. `emo`: Chinese acting note (e.g. "嚎啕大哭，夸张到滑稽地喊"). It routes the line to the generative listenhub-voice model; the note is acted, not read aloud. `os`: inner voice, no bubble (shown in the dream bubble). `lead`: gap before the line (default .25/.3). `say`: different TTS text. `sub`: small second-language subtitle under the bubble text. `focus: [x%, y%]`: the speaker's face in the panel. The camera snap-pushes there when the line starts (`zoom`, default 1.3), replacing the default drift. **Give every on-screen speaker a focus.** Edge faces get clamped, so use `zoom` 1.6 for them. |
| `min`, `tail` | min scene length; hold after the last line (default .5) |
| `sfx` | big katakana SFX text (ドキッ, ガーン …); fades out after 2 s |
| `burst` | manga focus lines (集中线) aimed at `[x%, y%]` (or `true` = centre), slammed in and jittering. Use on shouts and entrances. |
| `move` | `pulse` (heartbeat zoom) / `lunge`; default slow drift |
| `shake`, `gray`, `still` | jitter / gray paper / freeze (also grays the dream) |
| `title`, `stamp` | title card / end stamp in this scene |
| `bgm` | switch track (inherits until changed; `null` = silence) |
| `cues` | `[[sfx, at, vol, dur or "scene"]]` from `assets/sfx/` (heartbeat, gong, glass, wind, scratch, caw, sparkle, chime, riser …) |
| `dream` | escalating thought bubble: `{text, big?}` or `{img, art}` (drawn 1024²) or `{pill}` (doubt tag). Grows each stage. |
| `shatter` | dream bubble shatters at this scene |
| `card` | language-point card over the panel: `{zh, py, en, note}` = headline / pronunciation / translation / example (`note` splits into two lines at " · "). Put the **target language** in the headline: for English learners `zh` = the English phrase, `py` = IPA, `en` = the Chinese idiom. Give the scene `min` ≈ 6 so it can be read. |

## Keys and voices
- OpenAI: `OPENAI_API_KEY` env or `~/.baoyu-skills/.env`.
- ListenHub: `LISTENHUB_API_KEY` env or `~/.listenhub.env` (chmod 600).
- **Never print a key or write one into project files.**
- Voice list: `GET https://api.marswave.ai/openapi/v1/speakers/list?language=zh`.

| role | voice id |
|---|---|
| cute young woman | `doubao-official-zh_female_sajiaoxuemei_uranus_bigtts` (撒娇学妹) |
| pure girl | `doubao-official-ICL_uranus_zh_female_qingxinshaonv_tob` (倾心少女) |
| sleazy/pompous man | `doubao-official-ICL_uranus_zh_male_younidashu_tob` (油腻大叔) |
| funny uncle | `doubao-official-ICL_uranus_zh_male_youmoshushu_tob` (幽默叔叔) |
| hammy young man | `doubao-official-ICL_uranus_zh_male_zhongerqingnian_tob` (中二青年) |
| flirty big sister | `doubao-official-zh_female_chanmeinv_uranus_bigtts` (谄媚女声) |
| comic old man | `doubao-official-ICL_uranus_zh_male_youmodaye_tob` (幽默大爷) |
| cold aloof man | `doubao-official-zh_male_lengkugege_emo_v2_mars_bigtts` (冷酷哥哥) |
| sly schemer | `doubao-official-ICL_uranus_zh_male_shenmifashi_tob` (神秘法师) |
| female English teacher | `doubao-official-zh_female_yingyujiaoxue_uranus_bigtts` (英语教学) |

Choosing a cast voice: render 3–4 candidate voices on the **same real line** into `samples/`, and let the user pick by ear.

## Common mistakes
- **Text inside generated images.** It comes out garbled. Keep "ABSOLUTELY NO TEXT" in `style`. All words go in bubbles and SFX.
- **Every cast member shows up in every panel** (the charsheet reference pulls everyone in). Put "Only X is drawn; Y and Z are NOT in this panel." in that scene's `art`. A global "only named characters" rule in the prompt backfires: the model redraws the character lineup. Flashback/montage panels are the worst case: everyone gets drawn twice. Always exclude there, and say "indoors, no crowd" if the setting is a street.
- **Period costume drift.** A vague `look` ("pink robe") lets the model pick any era. For historical settings, name the garment in `look` (e.g. Ming: "cross-collar ao-qun with bijia vest, NOT a qipao"). Changing `look` later means redrawing the charsheet and every panel of that character.
- **Flat emotion.** Plain `/tts` can't act, and a bracketed note gets read out loud. Use `emo`. Acted lines run 20–40% longer, so `speed` (applied as atempo) pulls the length back. Submits are limited to 5/min; `voice.py` retries on its own. The acted model can **switch speaker mid-line** (a male voice jumps to a ~300 Hz female voice for a second). Calm or deadpan lines don't need `emo`; plain TTS never drifts. **Pitch analysis can't detect drift reliably.** A pitch-ratio guard (yin/pyin) flagged a clean plain-TTS gravelly male line at x2.8, and rerolling the same `emo` 8 times never fixed it. Excited or high-energy notes ("八卦兴奋") trigger it the most. Fix: when the user hears a swap, switch that line to plain TTS (drop `emo`) at once, instead of rerolling. **Don't mix engines for one character**: acted and plain takes of the same voice id sound like two people. If one of a character's lines goes plain, make all of them plain.
- **One line much quieter than the rest.** Acted takes come back anywhere from −41 to −18 dB. `voice.py` ends every line with `loudnorm=I=-20`, so a rerun of `voice.py --local` levels old projects with no API cost. A theme pack's VO needs the same rerun inside the pack dir.
- **BGM inaudible.** MusicGen output is quiet (about −30 dB mean). `vol` 0.3 disappears under the VO. Start at 0.45–0.55 and compare with `ffmpeg -af volumedetect`.
- **Katakana or ♥ rendering as boxes.** The ZCOOL fonts lack them. SFX and `big` dream text already use Noto Sans SC 900. Keep it that way.
- **Dream bubble covering faces.** It sits top-right and is capped at scale 0.8. If it still covers a face, set `dream.scale` lower or shift the subject left in the `art` prompt.
- **OpenAI TTS sounds flat and slow.** Use ListenHub voices at speed about 1.2. Slow only the punchline (`speed: 1.0`).
- **Bubbles hidden under the Douyin/YouTube Shorts UI.** The status bar covers y<190, the caption and account bar cover y>1490, and the action icons cover the right ~140px from y≈900 down. `style.css` keeps the header, bubble, stamp and card out of those zones; don't move them back. Check with a snapshot that has those zones drawn over it.
- **Hand-editing `index.html`.** Edit `script.json` and rerun `build.py`.
- **Baoyu image skill / bun socket errors.** `panels.py` calls the API directly with curl. Use it.
- **Preview "connection refused" days later.** Rerun `npx hyperframes preview --background`.
- **Lint warnings that are fine:**
  - `nested_structure_needs_subcomposition`
  - `timeline_track_too_dense`
  - `overlapping_gsap_tweens` / `fromto_without_baseline` on `#pw-*`
  - `duplicate_media_discovery_risk` (the dream shards)
- **Lint errors:** fix them.

For HyperFrames rules beyond this, load `/hyperframes` → `/hyperframes-core`.
