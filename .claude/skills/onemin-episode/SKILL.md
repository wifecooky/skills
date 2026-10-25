---
name: onemin-episode
description: Make one episode of 「一分钟看懂日本」 (onemin, repo ~/Documents/git/onemin-japan): script, 晓曼 voiceover, HyperFrames build, onemin.net page. Use when starting, revising, re-voicing or shipping an onemin episode (episodes/epNN-*).
---

# onemin-episode

Procedure only. Decisions live in the repo: `BRIEF.md` (series: tone, template, sound, site, review gates), `TOPICS.md` (schedule), `episodes/<ep>/BRIEF.md` (this episode). When a decision changes, edit those files, not this skill.

Script and video craft come from `concept-motion-explainer`. Read its `references/pipeline.md` § Writing pass and § Script check when you reach step 1; this skill adds only what is onemin-specific. The newest episode is the template: copy from it, never from memory.

Paths below are relative to the repo root; `EP=episodes/epNN-slug`. CLI pin: `npx --yes hyperframes@0.8.169`.

## 1. Script → gate: user approves

1. Facts first: the topic row in `TOPICS.md`, its research file in `research/`, the primary source (maker, standard, regulator). Write `$EP/SCRIPT.md`: 配音稿 table (段 / # / 配音 / 画面) plus a sources section with URLs.
2. Shape: the 5 segments from the series BRIEF, 10–12 lines, VO ≤ ~46 s so intro + end card fit in 60 s.
3. Run § Writing pass and § Script check 1–13 on every draft, revisions included. Check 8 (cold listener) is a fresh general-purpose agent every time: it is the check that catches line-to-line contradictions.
4. onemin additions:
   - The 语气铁律 in the series BRIEF: mechanism and source, no praise, no comparison.
   - The last line closes the hook: 所以/这 pointing at the line before, ending on the hook's concrete claim (the episode BRIEF `message`).
   - Progress-bar labels are content words that agree with the script (ep02 「只改形状」 contradicted 「提示语也改了」).
   - TTS text: years as 「一九九五年」, numbers as words (「零点二秒」); on-screen titles use digits.

Done when `node scripts/check-rules.mjs $EP` passes (it runs `check_prose.py` on the 配音 column and fails on digits, URLs and 语气铁律 words), every check passed, the cold listener's one-line summary contains the BRIEF message, and the user said yes. TTS waits for that yes.

## 2. New episode project (skip when revising)

```sh
rsync -a --exclude node_modules --exclude renders --exclude snapshots --exclude .thumbnails --exclude 'assets/vo' \
  --exclude '.hyperframes/artifacts' --exclude '.hyperframes/preview' --exclude '.hyperframes/video-state*' \
  --exclude '.hyperframes/history-id' --exclude '.hyperframes/hf-ids-stamped.json' \
  episodes/<prev>/ $EP/ && (cd $EP && npm install)
```

Then rewrite: `meta.json` and `package.json` (id/name), `BRIEF.md` (frontmatter `message`, Assets, Customizations), `STORYBOARD.md`, and in `.hyperframes/gen_comps.py` the HUD issue line (`No.NN` + title), `SEGS` labels, scenes, `SFX`. Website data starts as `page.draft.json` (step 5 says why). Done when `grep -rn "<prev slug>\|<prev title>" $EP --exclude-dir=node_modules` finds nothing.

## 3. Voice

- `$EP/assets/vo/xiaoman/lines.tsv` (create the folder on a new episode): `key<TAB>text`, one line per VO line, text exactly as approved.
- `sh ~/.claude/skills/onemin-episode/scripts/vo.sh $EP <key> [takes]` voices one line (ListenHub 晓曼, trim, +7 dB limiter), keeps the shortest take, backs up the previous take, updates both `durations.json` and prints the VO sum.
- Takes vary in internal pauses by up to ~0.8 s. When a line must fit an existing slot, ask for 3 takes.
- `python3 ~/.claude/skills/onemin-episode/scripts/words.py $EP <key>...` prints word timings (whisper small) for hit points.

Done when every line is voiced and no line runs past the next line's `VO_AT`.

## 4. Build → gate: user approves the preview

1. In `gen_comps.py`: `VO_AT` from durations, every title / line-draw / colour change on its spoken word (from words.py), `SEGS` boundaries, `TOTAL` ≤ 60.
   - Illustrations: a hand or other body part, or any object the viewer must recognise, starts from an open-licensed outline that you restyle to `design.md`. Use pipeline.md § Body parts. Write the source and licence into the episode BRIEF under Assets. (ep02: a freehand hand read as 「离谱」; it was replaced with noto `palm-down-hand`, Apache 2.0.)
2. `cd $EP && python3 .hyperframes/gen_comps.py && sh assets/fonts/subset.sh && npx --yes hyperframes@0.8.169 check`. The generator also re-carves the BGM; subset again after any text change.
3. Snapshot every changed beat at its hit time: `npx --yes hyperframes@0.8.169 snapshot --at <t,t,…> --no-end --describe false -o .hyperframes/artifacts/snapN`, and look at each frame.
4. Update `SCRIPT.md` (add a 「vN → vN+1 修改」 table on revisions), `STORYBOARD.md`, the episode BRIEF's VO total.
5. Preview: `npx --yes hyperframes@0.8.169 preview --kill-all && npx --yes hyperframes@0.8.169 preview --background` (one preview server at a time), then hand over the `Studio` URL it prints (`http://localhost:<port>/#project/<ep>`) as is. Do not write a port from memory: this step used to say 3009 while the server actually ran on 3002.

Done when check says passed with 0 errors, the snapshots are looked at, and the user approved the preview. Render only after that (concept-motion-explainer pipeline step 10 onward). After the render, `node scripts/check-rules.mjs $EP` must pass again (it checks `renders/video.mp4` is 1080×1920 and ≤ 60 s, and that no URL is on screen). Once the user approves or the render is done, stop the server with `npx --yes hyperframes@0.8.169 preview --stop`. A server left running keeps its headless Chrome; 33 of them had piled up by 2026-10-21.

## 5. Website page

1. `$EP/figure.svg`: the object as a line drawing with one vermilion leader line, same classes as `episodes/ep01-shampoo/figure.svg`.
2. Add `"figure": "figure.svg", "og": "og.png"` to `page.draft.json`, then rename it to `page.json`. `site/build.mjs` reads every `page.json` and crashes on one without these keys; that is why drafts carry the other name.
3. `python3 brand/make.py` (writes `$EP/og.png`), drop the topic from `site/upcoming.json`, `node site/build.mjs`, then `node scripts/verify.mjs` (site-verify skill: `FEATURES.md` is the feature map; episode counts and titles are read from `site/dist`, so a new episode needs no test change). Look at the new episode's screenshots in `.verify/index.html` at 390 and 1440.
   - QA covers the whole page down to the footer, at 390 px too: scroll to the bottom and take a viewport screenshot. The bottom is where a full-page shot shrinks things out of view. (Pager, 2026-10-20: the 「上一期」 link had no arrow, and the 「下一期 · 制作中」 item, which is not a link, kept the 20px bold link style in grey, so it read as a broken link. There was also a 110px dead gap above the footer.) Done when every link carries an arrow pointing where it goes, and everything that is not a link is visibly quieter than the links.
   - Timeline line breaks (2026-10-24). Cause: `glued()` in `site/build.mjs` kept the source refs on one line with a fixed last 4 characters. That cut words (周|围, 山|中俊治), numbers (1|%) and quoted terms (実用|新案). Fix: the cut snaps to an `Intl.Segmenter` word boundary, and never lands inside a standard number, a number, a short 「」 term or a kana run (`ATOM`). When a new episode adds a new kind of term that must stay whole, add it to `ATOM`. Verify: the `fact-wrap` test in `node scripts/verify.mjs` fails on the old glue.

Deploy (`scripts/deploy.sh`: check-rules → build → ui-check → verify → `wrangler pages deploy site/dist --project-name onemin --branch main`) and the onemin.net domain only when the user asks. A rule that a script can check goes into `scripts/check-rules.mjs`, not only into prose here.

## 6. Publish kit

Cover, title, copy, tags for 小红书 / 抖音 / 视频号 / YouTube Shorts; the user posts by hand. Copy leads with what the viewer gets; no URLs anywhere in video or copy.

- Every platform gets the local render `$EP/renders/video.mp4`. Never a copy downloaded back from another platform: it carries that platform's logo and account ID, YouTube lists Shorts with other platforms' watermarks as not eligible for monetization, and Instagram ranks them lower.
- The episode BRIEF records the BGM like any other licensed asset: the provider it came through, the generation record (task id and date, or the file it lives in), and the terms it was used under. (ep02 reused ep01's `mureka-full.mp3`; its record is `episodes/ep01-shampoo/assets/bgm/result.json`. It was generated through ListenHub, so ListenHub's terms apply, not mureka.ai's.)
Done when the kit names the file to upload and the BGM line is in the episode BRIEF.

## Lessons

Every problem the user finds in an onemin episode becomes a rule in the same session, written as cause → fix → verify. Write it into this skill first, at the step where it bites. If the rule would hold for any explainer video, also put the general form in concept-motion-explainer's `pipeline.md`; this skill then keeps a one-line onemin version that points there. Series decisions go in the repo BRIEF.
