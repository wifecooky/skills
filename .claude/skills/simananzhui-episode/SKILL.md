---
name: simananzhui-episode
description: Per-episode procedure for the 驷码难追 engineering/AI explainer channel (B站 main, 视频号 sync) - topic → BRIEF/STORYBOARD/SCRIPT → 解说小明 2.0 voice → build → two builds (<dir> 视频号, <dir>-bili B站) → seal/watermark → publish kit. Triggers - "驷码难追", "新一期", "simananzhui", "B站工程科普", "做下一期".
---

# 驷码难追 episode

Procedure only. Decisions live in the repo: `~/Documents/git/simananzhui/README.md` (positioning, batch table, copy rule) and each episode's `BRIEF.md`. Generic craft lives in `concept-motion-explainer` (SKILL.md + `references/pipeline.md`, `references/publish-channels.md`). This skill links to those rules and does not copy them.

## 0. Channel

- **Positioning:** two-minute animations that explain one engineering or AI principle. Engineering is the main line and AI the secondary one, about 2:1. Audience: engineers 0–3 years in, plus people coding with AI who lack the fundamentals. One episode every two weeks, with a 9:16 short per episode from ep 3.
- **Accents:** engineering line amber `#ffb23a`. The AI line gets a different accent. It isn't fixed yet; the first batch kept its own colours (LLM 朱砂 `#ff5b3a`, unit test red `#ff4a32`). Fix the AI accent in README on the first new AI episode (ep 6 KV cache) and add it here.
- Visual system, HUD, intro breath (1.5 s) and end card (5 s): concept-motion-explainer §1–2.

## 1. Topic → BRIEF / STORYBOARD / SCRIPT → gate

1. Pick the topic from the README batch table: a classic concept, angled from a Japanese first-hand source, with an example from the user's own work.
2. **Explaining someone's project → the message is their headline idea.** Read the whole source first. Rules: concept-motion-explainer §1.1, both sub-bullets.
3. BRIEF.md frontmatter, same fields as `unit-test-alarm-v4-bili/BRIEF.md`: `workflow: general-video`, `flow: automation`, `storyboard: yes`, `message`, `aspect: 1920x1080`, `language: zh`, `length`, `angle`, `source`. STORYBOARD.md has one frame per scene with the morph to the next.
4. SCRIPT.md: run pipeline.md § Writing pass (ljg-plain → human-writing → dbs-hook) and § Script check 1–13, including the cold listener and the engineer-viewer loop. Every revision re-runs the whole pass.
5. **Channel bans, for VO and captions alike:**
   - no 「：」 leading a line (prompt-style colons), except before a quoted line
   - no `—` / `——`
   - no 不是…而是 turnaround, and no 其实 / 恰恰 / 说到底 moves
   - no 说白了
   - no triple parallelism (三连排比)
   Code and machine fields on screen are exempt.

Done when: the user has approved message, length, STORYBOARD and SCRIPT, plus the fix table from Script check. No TTS before that.

## 2. New episode dir

- `rsync -a --exclude renders --exclude snapshots --exclude node_modules <prev>/ <new>/`, then set the new `id` in `meta.json` (`{id,name,createdAt}`).
- **Never overwrite a finished version.** A new angle or redo means a new dir (`handwired-search` → `handwired-v2`; the old dir stays untouched).
- Keep the CLI version pinned in the copied package.json (`hyperframes@0.8.140` as of Handwired).

Done when: `npx hyperframes check .` runs in the new dir.

## 3. Voice: 解说小明 2.0

Credential: never print or write the key. Load inline per command:
`export LISTENHUB_API_KEY=$(grep -ohE "lh_sk_[A-Za-z0-9_-]{8,}" ~/.claude/projects/*/*.jsonl | head -1)`
When grepping transcripts for anything else, pipe through `sed 's/lh_sk_[A-Za-z0-9_-]*/<KEY>/g'`.

1. Write the TTS text with `## voN` sections (`SCRATCH/vo-xm/tts.md`) and split it into `voN.txt`. Use spoken punctuation: short clauses, `！` on the surprising fact, `？` on the question. Numbers are spelled as they should be read (Script check 10). Bracket directions such as 「[用惊讶的语气]」 are read aloud, so never use them.
2. Audition the hook first (pipeline.md § Voiceover). The channel voice is fixed, so the audition is about the vo0 text variant.
3. Run the clips in parallel:
   ```bash
   listenhub openapi tts --text "$(cat vo$i.txt)" --voice doubao-official-zh_male_jieshuoxiaoming_uranus_bigtts --output vo$i.mp3
   ```
4. Trim: `silencedetect=n=-40dB:d=0.15`. Keep from the first `silence_end` − 0.08 s to the last `silence_start` + 0.15 s, using `atrim,asetpts=PTS-STARTPTS`, `libmp3lame -b:a 192k`, written to `assets/vo/voN.mp3`.
5. Word times:
   ```bash
   whisper assets/vo/vo$i.mp3 --model small --language zh --word_timestamps True --initial_prompt "$(cat vo$i.txt)" --output_format json --output_dir build/vot-xm
   ```
   Drop `--initial_prompt` on any clip where whisper hallucinates (Handwired vo2, vo4, vo8).
6. `python3 build/align.py <textdir> > build/align.txt` maps the script phrases to scene time and prints the S table. Lead 0.6 s on vo0, 0.3 s on the others, gap 0.6 s.

Open: ep 2–4 were voiced with 谷川 `zh-male-guchuan-9d6a4666`, which drops 8–10 dB mid-clip (pipeline.md § Voiceover). Run `concept-motion-explainer/scripts/vo_levels.py` on their `assets/vo/vo*.mp3` before publishing; re-voicing them is the user's call.

Verify every batch: `python3 ~/.claude/skills/concept-motion-explainer/scripts/vo_levels.py assets/vo/vo*.mp3` exits 0.

Done when: every clip is shorter than its scene, the hook claim lands ≤ 5 s (pipeline.md § Writing pass 5), and the S table is in `build/align.txt`.

## 4. Build → gate preview

- Composition, BGM/SFX, fonts, story beats, intro/end card, seams: pipeline.md, by section.
- Run `npx hyperframes check .` (0 errors), take snapshot contact sheets and look at them yourself, then `npx hyperframes preview --background` for the user.

Done when: the user approves the preview. Render only after that (`render -q high`, web encode, `scripts/seams.py`).

## 5. Two builds, end cards, seal

| build | dir | end card | CTA row |
|---|---|---|---|
| 视频号 | `<dir>` | `关注视频号` / 驷码难追 / `WECHAT CHANNELS` | 点赞 · 收藏 · 转给…… |
| B站 | `<dir>-bili` | `关注B站` / 驷码难追 / `BILIBILI` | 一键三连 · 转给…… |

- Make `-bili` by rsync from the finished 视频号 dir. Only the end card differs. Write `关注B站` with no spaces (the 0.5em letter-spacing spaces it).
- The 转给 target comes from the hook (转给写测试的同事). 视频号 has no 三连.
- Brand assets, in `simananzhui-brand/`: `avatar-ink.png`, `avatar-red.png`; `build/wm-seal.png` (92 px), `build/wm-font.otf` (Noto Serif SC Black subset of 驷码难追), `build/wm-vert.png`, `build/wm-seal-on-ink.png`. To regenerate: `concept-motion-explainer/scripts/wm_designs.py 驷码难追 <font.otf>`.
- Watermark each build: `scripts/watermark.py seal renders/video.mp4 snapshots/wm 50,130` for preview frames, then `... seal renders/video.mp4 renders/video-web-wm.mp4`. Check with `scripts/wm_check.py` (pipeline.md § Anti-piracy watermark).

Done when: both dirs have `renders/video-web-wm.mp4`, and an EC+3.5 snapshot of each shows the right platform strings.

## 6. Publish kit (only on the user's go)

- Copy rules: publish-channels.md § 驷码难追. The first sentence says what the viewer gets. Drafts go in `simananzhui-brand/bili-copy.md`.
- B站: 分区 科技 › 计算机技术, 类型 自制. **The user ticks 原创 themselves.** Upload `<dir>-bili/renders/video-web-wm.mp4`. Cover 1920×1080 with the main text inside the central 4:3. Title, 简介 with chapters (scene `S` + INTRO, mm:ss), tags.
- 视频号: upload `<dir>/renders/video-web-wm.mp4`, 话题 `#驷码难追 #程序员 #编程` plus topic tags.
- **Never cross-upload** a build to the other platform.
- Show the user the filled copy and cover. Publish nothing until they say go.

## 7. Repo / push

- `~/Documents/git/simananzhui` → private `git@github.com.wen:wifecooky/simananzhui.git`. For gh: `GH_TOKEN=$(gh auth token --user wifecooky)`.
- .gitignore drops renders/, snapshots/, node_modules/, .gstack/, *.log, *.bak. Commit at the end of each stage, and push only when the user asks.
- Update the README batch table (dir, status) when an episode changes state.

## Lessons

Every problem the user finds becomes cause → fix → verify, in the same session, right after the fix is verified:
- **Channel-only** (voice, end-card strings, brand, platform copy, bans): write it into this skill.
- **Generic** (writing, timing, layout, render): write it into concept-motion-explainer, plus a one-line pointer here if the channel trips on it often.
- **Other affected skills** (onemin-episode, human-writing, …): sync by judgement when they share the failure.
Report which skill line was added.
