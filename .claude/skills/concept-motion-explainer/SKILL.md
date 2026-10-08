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
2. **One carrier example for the whole video.** Pick something the audience already knows whose "answer" they can guess. LLM → 《静夜思》"床前明月光，疑是地上__" (everyone guesses 霜). The same example flows through every stage; never switch examples mid-video.
3. **Stage list = the real pipeline.** Map the mechanism to 5–7 stages (LLM: 输入 → 切分 → 嵌入 → 注意力 → 预测 → 重复 [+ 训练 in detailed cut]). Each stage = one scene.
4. **One-take, no hard cuts.** Each scene's output element *morphs* into the next scene's input (text → token chips → column labels → vector columns → attention → probability bars → char flies back into the sentence). Camera = transforms on `#cam`/`#world`.
5. **Hook + landing.**
   - Open with a misconception struck through: 「AI 在~~思考~~？」→「其实它只会一件事」→ big accent statement.
   - End with a pull-back, title mask-rise, then fade. Never start or end on a hard frame: ~0.6s lead-in before VO, BGM fade-in 1.5s / fade-out 2.5–3s.
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
2. Script (if narrated), one line per scene → verify: user approves script BEFORE TTS
3. TTS per scene clip → ffprobe durations   → verify: no clip longer than its scene
4. Scene timing table S = derived from VO   → voice drives timing, not the reverse
5. Word timestamps (whisper) → key visual hits land on the spoken word
6. Build composition (single index.html, one paused root timeline)
7. BGM + SFX                                → verify: VO 6–8 dB above BGM, peak < -1 dB
8. npx hyperframes check .                  → 0 errors
9. snapshot contact sheets at scene midpoints → look at them yourself, fix overlaps
10. render -q high, then web encode         → ffprobe duration matches
```

Commands, mix levels, and gotchas: `references/pipeline.md`.

## 4. Variants

- **Never overwrite a finished version.** New version = new dir: `rsync -a --exclude renders --exclude snapshots src/ dst/`, change `meta.json` id.
- **Longer / detailed cut**: add explanation, not padding. Each new beat needs a new visual (LLM detailed: tokenizer vocab lookup, semantic-space neighbors, shallow vs deep layers, temperature sampling, streaming chat bubble, training scene with loss curve). Re-derive S from new VO.
- **Other language**: translate UI text + VO. Keep the carrier example if the audience can read it (Chinese poem kept for Japanese viewers); re-subset fonts for the new script (e.g. Noto Serif JP with SC fallback); re-fit timing to new VO durations; set `<html lang>`. A subagent can run this in parallel.

## 5. Quality bar checklist

- [ ] Can a non-expert state the one-sentence message after watching?
- [ ] Same carrier example from first frame to last?
- [ ] Zero hard cuts between scenes?
- [ ] Accent color only on the current focal element?
- [ ] No text overlapping (check snapshots, not just lint)?
- [ ] Soft open, soft close, no audio clipping?
