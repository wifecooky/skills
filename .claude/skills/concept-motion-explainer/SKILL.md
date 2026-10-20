---
name: concept-motion-explainer
description: Use when the user wants a portfolio-grade motion-graphics explainer video for an abstract concept or technical principle (e.g. "how LLMs work", "how TCP works", "what is a hash table"), optionally with voiceover, BGM, longer/detailed cuts, or other-language versions. Built on HyperFrames. Triggers - "动效视频", "作品集级别", "讲清楚 X 的原理", "explainer animation", "加配音/BGM", "做个日文版/英文版".
---

# Concept Motion Explainer

Proven recipe from the "预测下一个词 (LLM next-token)" piece: 15s silent cut → 58.5s narrated → 122.8s detailed → Japanese version.
The quality comes from **decisions**, not from a magic prompt. This skill encodes those decisions.

Load `/hyperframes` + `/hyperframes-core` before writing composition HTML. This skill decides WHAT to build; those skills own HOW HyperFrames works.

## 1. Concept — do this before touching code

1. **One-sentence message.** Reduce the concept to its essence. LLM → "一次只预测下一个词，然后重复". If you can't say it in one line, you don't understand it yet.
   - **When explaining someone's project, the message is their novel idea, not the familiar background it rests on.** Cause: the Handwired episode was framed as "GPU 快因为它笨" (well-known GPU lockstep) while the author's own tagline is "turn regular JS into a neural net; no training, exact" — the user caught it after the full build. Fix: read the project's top-level README/tagline first and put that idea in the message; mechanisms and payoffs (GPU speed) become supporting scenes. Verify: the one-sentence message contains the author's headline claim, and a viewer could not have learned the message from a generic textbook.
   - **Read the whole source before any draft, not just its first screen.** Cause: the re-pitch was written from the README's first paragraphs and repeated the tagline's "代码直接变成网络", while the docs say no tool converts existing JS (you write builder code; the auto compiler is a lab experiment), and the other demos (Mini OS, learned gallery) were never read — the user had to ask again. Fix: before pitching, read the landing page, docs index, every demo's README and the author's status / known-limits page; list what the author says is NOT delivered. Verify: the draft names every demo the author ships, and each claim in it is checked against the docs, not the tagline.
2. **One carrier example for the whole video.** Pick something the audience already knows whose "answer" they can guess. LLM → 《静夜思》"床前明月光，疑是地上__" (everyone guesses 霜). The same example flows through every stage; never switch examples mid-video.
3. **Stage list = the real pipeline.** Map the mechanism to 5–7 stages (LLM: 输入 → 切分 → 嵌入 → 注意力 → 预测 → 重复 [+ 训练 in detailed cut]). Each stage = one scene.
4. **One-take, no hard cuts.** Each scene's output element *morphs* into the next scene's input (text → token chips → column labels → vector columns → attention → probability bars → char flies back into the sentence). Camera = transforms on `#cam`/`#world`.
5. **Hook + landing.**
   - Open with a misconception struck through: 「AI 在~~思考~~？」→「其实它只会一件事」→ big accent statement.
   - End with a pull-back, title mask-rise, then fade. Never start or end on a hard frame: ~0.6s lead-in before VO, BGM fade-in 1.5s / fade-out 2.5–3s.
   - **Intro breath (1.5s)**: fade from black + HUD brand slides in before the first VO. Without it the video starts mid-sentence and feels cut off.
   - **End card (5s)**: after the final fade, a channel sign-off: 「关注视频号」/ big serif channel name (per-char stagger) / accent rule / `WECHAT CHANNELS` / one CTA row. Every published video gets one.
     - **Which channel.** Kids/general science → **双言两语** (视频号 only). Engineering and AI principles → **驷码难追**, in two builds: `<dir>` for 视频号 (`关注视频号` / `WECHAT CHANNELS` / 点赞 · 收藏 · 转给…) and `<dir>-bili` for B站 (`关注B站` / `BILIBILI` / 一键三连 · 转给…). Write `关注B站` with no spaces; the 0.5em letter-spacing already spaces it out. Seal and watermark: `scripts/wm_designs.py 驷码难追 <font.otf>` (font = Noto Serif SC Black subset with the name's glyphs). Built assets are in `~/Documents/git/simananzhui/simananzhui-brand/`.
     - **CTA row**: three line-icon items, staggered in at EC+1.7 (e.g. 👍 点赞 · ☆ 收藏 · ↗ 转给写测试的同事).
     - **Platform verbs only.** 视频号 has 赞/收藏/转发/评论, not 「三连」. On B站, 「一键三连」 is the native verb and replaces 点赞 + 收藏.
     - **Tie the last item to the episode.** Name who to forward it to, from the hook. A generic 「点赞关注」 gets ignored.
     - **Layout.** Leave a 76px gap above the row so brand and actions read as two groups. Use 34px text, or it's unreadable when a 16:9 video plays in a portrait phone feed. Make the row about as wide as 双言两语.
     - **New glyphs → re-subset the fonts** (pipeline.md § Fonts).
     - **Verify.** Snapshot EC+3.5 at full size. Check the row is centered and every glyph is in the serif font (no fallback).
   - Build both as offsets, not by retiming scenes: `INTRO`/`OUTRO` constants, `tl.shiftChildren(INTRO)`, audio `data-start += INTRO`, root/BGM duration = `S.end + INTRO + OUTRO`. Code: `references/pipeline.md` § Intro & end card.
6. **Real numbers for credibility.** Vocab 100,277, layer 01/96, 4096 dims, top-1 0.72. Fake-precise numbers read as cheap; real ones read as expert.

Write this as BRIEF.md + STORYBOARD.md (frame per scene with time range and the morph that links it to the next).

## 2. Visual system (default — change palette per topic, keep the discipline)

See `references/design-system.md` for CSS. Rules:
- **3 colors only**: ink background, paper/cream foreground, ONE accent (used only for "the important thing right now").
- **Serif vs mono = human vs machine.** Human text (poem, sentences) in serif; IDs, numbers, labels in mono.
- **Background layers**: dot grid, one recurring motif (the moon — an anchor that persists across scenes and dims when it would compete), vignette, film grain.
- **HUD**: top-left series title, top-right `NN / NN 步骤名 ENGLISH`, bottom progress rail (width from `STEPS.length`), bottom-right timecode `mm:ss:ff · NNNF`. Makes it feel like an instrument, not a slideshow.
- Every scene has a one-line caption + a small mono sub-caption (bottom-left).
- Deterministic pseudo-random only: `hash(a,b,c)` (sin-hash). No `Math.random()`.

## 3. Pipeline (verify every step)

```
1. BRIEF + STORYBOARD                     → verify: user confirms message/example/length
2. Script (if narrated), one line per scene → draft against /ljg-plain 红线, gate with /human-writing, hook line through /dbs-hook (pipeline.md § Writing pass) → verify: check_prose.py clean + logic/expression check 1–13 passes (pipeline.md § Script check), then user approves script BEFORE TTS
3. TTS per scene clip → ffprobe durations   → verify: no clip longer than its scene
4. Scene timing table S = derived from VO   → voice drives timing, not the reverse
5. Word timestamps (whisper) → key visual hits land on the spoken word
6. Build composition (single index.html, one paused root timeline)
7. BGM + SFX                                → verify: VO 6–8 dB above BGM, peak < -1 dB
8. npx hyperframes check .                  → 0 errors
9. snapshot contact sheets at scene midpoints → look at them yourself, fix overlaps
10. render -q high, then web encode         → ffprobe duration matches
10a. seam check (scripts/seams.py)            → open breath, end-card join, music under the end card (pipeline.md § Seam check)
10b. watermarked copy (scripts/watermark.py) → preview frames approved first; scripts/wm_check.py: seal box ≫ noise mid-window, ≈0 on end card
11. publish to 视频号 (only on user's go)    → verify: list page shows the right 发表 time
```

Commands, mix levels, and gotchas: `references/pipeline.md`. Publishing (copy template + browser gotchas): `references/publish-channels.md`.

## 4. Variants

- **Never overwrite a finished version.** New version = new dir: `rsync -a --exclude renders --exclude snapshots src/ dst/`, change `meta.json` id.
- **Longer / detailed cut**: add explanation, not padding. Each new beat needs a new visual (LLM detailed: tokenizer vocab lookup, semantic-space neighbors, shallow vs deep layers, temperature sampling, streaming chat bubble, training scene with loss curve). Re-derive S from new VO.
- **Other language** (English cut notes: `references/pipeline.md` § Other-language variant): translate UI text + VO; for a non-CJK audience swap the carrier for a native line with the same token count. Keep the carrier example if the audience can read it (Chinese poem kept for Japanese viewers); re-subset fonts for the new script (e.g. Noto Serif JP with SC fallback); re-fit timing to new VO durations; set `<html lang>`. A subagent can run this in parallel.

## 5. Quality bar checklist

- [ ] Can a non-expert state the one-sentence message after watching?
- [ ] Same carrier example from first frame to last?
- [ ] Zero hard cuts between scenes?
- [ ] Accent color only on the current focal element?
- [ ] No text overlapping (check snapshots, not just lint)?
- [ ] Soft open, soft close, no audio clipping?
- [ ] Every chapter boundary where an element continues: pixel-diff of the frames either side ≈ 0 (no fade-out/fade-in dip, same IDs/values)?
- [ ] SFX loudness-normalized; nothing noisy under the VO?
- [ ] Machine cutaways: every joint and moving part checked at 4× in each state; pipes hollow, links fixed length, water levels physical (`references/pipeline.md` § Machine cutaways)?

## 6. Feedback loop

Every problem the user finds in a rendered video becomes a rule here or in `references/pipeline.md`, written as cause → fix → how to verify. Do it in the same session, right after the fix is verified, so the next video doesn't repeat it.
