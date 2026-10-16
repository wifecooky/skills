# Pipeline reference

## Voiceover (ListenHub)

Credential: never print or write the key. Load inline per command:
`export LISTENHUB_API_KEY=$(grep -ohE "lh_sk_[A-Za-z0-9_-]{8,}" ~/.claude/projects/*/*.jsonl | head -1)`
(or rely on `listenhub auth login` OAuth).

```bash
# one clip per scene
listenhub openapi tts --text "<line>" --voice zh-male-guchuan-9d6a4666 --format mp3 --output assets/vo/vo0.mp3
# Japanese: --voice minimax-official-japanese-optimisticyouth-b70b8e2a53 --speed 1.2 ; pass hard readings as kana
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/vo/vo0.mp3
```
- Voices used: 谷川 `zh-male-guchuan-9d6a4666` (fun, lively — preferred over plain narrators).
- English: Host Sam `hostsam-dab52696` at `--speed 1.08` (user picked it from a 4-voice audition: `listenhub speakers list --lang en`, one 20 s clip each, concatenated into one file to compare).
- `--speed` validation bug: 1.1 / 1.10 / 1.12 / 1.15 are rejected ("at most two decimals", float rounding). 1.08, 1.2, 1.25 work.
- ListenHub English clips come out ~2 dB quieter than the Chinese ones. Match them (`-af volume=2dB`) before mixing, or the BGM level from the other version drowns the VO.
- Script tone: conversational, a little cheeky ("其实这家伙只会一件事"), short sentences, one idea per clip.

## Script check: logic and expression (before showing the script, before TTS)

Cause: the unit-test video said 「这本书最警惕的是误报」 and 「书的答案是」, but no book was ever introduced (the source only appears in the end-card credit). The user caught it after the render. The same pass found three more: 漏报/误报 → 四根柱子 had no bridge, 柱子 → 设计 had no bridge, and 「起火」 and 「坏了」 were mixed for the same idea. Every one of these cost a re-TTS, a retime, and a re-render.

Fix: run these checks on the whole script and fix what fails *before* the user sees it:
1. **Every reference is defined.** Each 这本书 / 它 / 这个 / 书里 / 作者 points to something the viewer has already heard in the VO. The on-screen credit does not count. If it is undefined, introduce it once or cut the reference.
2. **Clip-to-clip bridge.** Read only the first sentence of each clip in order. Together they should form one argument. Each clip opens by saying how it relates to the last one: cause, contrast (反过来), question (怎么做到？), or mapping (不漏报，叫防止回归). When a new concept (四根柱子) arrives, tie it to one already explained.
3. **One metaphor, one vocabulary.** State the mapping the first time it comes up (测试 = 报警器, 代码坏了 = 该响). Then use the same words every time, and make the on-screen captions match the VO.
4. **Every claim has its reason.** 「它就响了」 needs the why (调用次数变了). 「测试却不响」 needs the mechanism (照抄实现，跟着一起错).
5. **Pay off the hook.** If the hook promises something (「只做一件事」), deliver the answer within about 20 s and close it again at the end. Don't hold it open for the whole video.
6. **Expression.** One idea per sentence. No 书面语 inside spoken lines. Read each line aloud: if it needs a second read to parse, rewrite it.
7. **Dropped subjects (Chinese).** Write out the omitted subject of every sentence. Where the topic changes (AI 写测试 → 「一千块一件」), the dropped subject can't be recovered by ear. Name it (「比如一段算订单的代码：…」). The same goes for the head noun behind a measure word: 「一千块一件」 is stall talk, where the item is in front of you, and in a video the ear fills in the default noun for 件 (衣服). Write 「一件商品一千块」. The same applies when the referent silently switches: 「这个测试」 in a later scene must be the same test the viewer already met, or say 「有的测试」.
8. **Cold listener (the author can't do 1–7 on their own script).** The author always knows the missing subject, so the gap stays invisible to them (user caught 「一千块一件」 after checks 1–6 passed). Spawn a fresh `general-purpose` agent, not a fork. Give it the VO lines in order, the audience profile (e.g. "Chinese developers who know 单元测试/重构/覆盖率"), and a one-line on-screen summary per clip. Don't give it the source article. Ask it, sentence by sentence: explicit subject, link to the previous sentence, and a flag wherever it had to guess. Without the audience profile it flags every term (22 flags, about half of them noise). Triage its table yourself: keep the flags that would hold for the real audience, and drop the rest with a reason.

Verify: show the user a table of each failing line → its fix, with the check number, next to the script. They approve both before any TTS.

## Word timestamps (sync visual hits to words)

```bash
HF_HUB_OFFLINE=1 mlx_whisper assets/vo/vo3.mp3 --model mlx-community/whisper-small-mlx \
  --language zh --word-timestamps True --output-format json --output-dir /tmp/vot
```
large-v3-turbo download can hang at 0% CPU — use cached small model offline.
Never pass the script as `--initial-prompt`: whisper loops/hallucinates (unit-test-alarm v2: 4 of 8 clips garbage). For simplified output use a short neutral prompt + `--condition-on-previous-text False`: `--initial-prompt "以下是普通话的句子。"`. Homophones (响→想) don't matter for timing; check char count vs the txt.

## Re-voice an existing cut (new VO, same visuals) — time warp, not hand retiming

Cause (unit-test-alarm v2): script fixes changed every clip length; hand-shifting ~200 tween times is error-prone. Fix:
- Keep all authored times in the v1 timebase. `build/warp.py` builds a piecewise-linear map W(v1→v2) from anchors = scene boundaries (same lead/tail around each VO as v1) + characters both VO transcripts share (difflib on per-char whisper times). Don't anchor VO starts if v2 prepends words to a clip. Hand-pin hits on reworded words (`MANUAL`).
- In index.html: real timeline `TL`; `tl = {to,set,fromTo}` wrappers map position `p → W(p)` (durations unchanged); render reads `Wi(clock.t)`; clock/end card/shiftChildren/registration on `TL` with `END = W(S.end)`. Rail fills: `duration: W(out) - W(STEP_AT[i])`. sfx.py maps cues through the same warp.json.
- Verify: print where key beats land vs the new whisper word times (each within ~0.2 s), and `grep -n 'data-duration="<old total>"' index.html` → nothing left (v2 missed `#scene` → everything black after 100 s). Captions authored back-to-back can collide when W compresses the gap — check `content_overlap` info lines.
- Prepended words stretch: when a new clip starts with words v1 never had (v3 「比如一段算订单金额的代码：」), v1 events 0.02 s apart can end up 0.26 s apart. One element shows before the other hides, and they overlap (test card over the chip grid). Fix: pin each event of such a swap to the same word (`(9.84, first(1, "代")), (9.86, first(1, "代") + 0.03)`). Also pin anything that must sit on a sentence that is now new (vo6 card on 「真实的代码里」, not on the later 「测试」).
- A pin drops char anchors within 0.3 s, never scene boundaries. Keep them in a separate `struct` list (v3 lost `(9.6, 9.6)`, so scene 1 started 1.7 s late). The chain step must be 0.01, not 0.02: `9.86 - 9.84` is `0.0199…` in floats, so a 0.02 test silently drops the second pin. Verify: print W at every scene start (it must equal `S`) and at every pin.

## Other-language variant (English cut of the 7-min LLM lecture)

- **Carrier**: pick a line whose tokenization keeps the same number of tokens as the original, so every N-column layout survives. "To be or not to be, that is the ___" is exactly 10 real cl100k tokens (no "for this demo" caveat). Look up real IDs and neighbours with `tiktoken` instead of inventing them.
- **Ribbon pitch**: English words are wider than one CJK glyph. The 80 px pitch / 60 px font became 128 px / 52 px (x = 256 + 128·i), with the slot widening to 256 when the long answer lands. Measure widths with PIL on the subset font first.
- **Subtitles**: one sentence per line if ≤ 72 chars, else pack clauses split at `, ; :` up to 64 chars, and as a last resort split at the space nearest the middle. Sentence split must also handle `."` (period inside a closing quote).
- **BGM** is length-bound: a longer VO needs the bed extended (`acrossfade=d=6` with a mid-track section of itself), then check the mean dB around the seam.
- Agents: give each one the whole seamless chain (ch01–ch04 to one agent), so no boundary spans two agents. Hand over the old-language cue sheet as well, so they map beats instead of guessing.

## BGM (ListenHub music)

```bash
listenhub music instrumental --prompt "<mood: warm minimal ambient electronic, soft pulse, no vocals>" --json
# "unreachable / failover" error → just retry
ffmpeg -i full.mp3 -t <duration+1> -c copy assets/bgm/bgm.mp3
```

## Audio tracks

| track | content | volume | notes |
|---|---|---|---|
| 1 | VO clips | 1 | data-duration ≤ real media length (`clip_media_fit` lint) |
| 2 | BGM | 0.2–0.22 | data-fade-in 1.5, data-fade-out 2.5–3 |
| 3–4 | SFX | 0.15–0.55 | alternate tracks so no same-track overlap |

SFX vocabulary (Pixabay, keep CREDITS.md): whoosh-cinematic (opening), whoosh-short (scene transitions), key-press/typing (text typing), glitch (scramble/ID flicker), pop (element appears), click/click-soft (selection), sparkle (reveal), chime (insight), impact-bass (big statement), riser (build-up).
Generate SFX `<audio>` tags from a list `[time, file, vol]` with a script that assigns track 3/4 greedily to avoid overlap.
Verify mix: `ffmpeg -i renders/video.mp4 -af volumedetect -f null -` → max_volume between -1.5 and -5 dB.

**Loudness-normalize SFX before mixing** (user heard "开头好多噪音"): the library files differ by >15 dB in mean loudness, so the same `vol` is inaudible for one and louder than the VO for another (impact-bass was +8 dB over VO; glitch-2 is a 3.5 s noise bed that sits under speech). Fix:
- `gain = min(1, 10**((-35 - mean_dB)/20) * vol/0.3)` with `mean_dB` from `volumedetect` per file, cap `vol` at 0.5.
- Never put long glitch/noise files under VO — swap glitch-* for `click`.
- Target result: VO ≥ 6 dB over BGM (BGM ~0.13 for a −23 dB VO), integrated ≈ −18 LUFS, peak ≈ −4 dBFS.

## Fonts (CJK subset — full fonts are huge)

```bash
# collect every non-ASCII char in index.html + base set
python3 - <<'PY' > /tmp/chars.txt
import re;s=open('index.html',encoding='utf-8').read()
print(''.join(sorted(set(c for c in s if ord(c)>127)))+'0123456789')
PY
for w in Regular SemiBold Black; do
  pyftsubset NotoSerifSC-$w.otf --text-file=/tmp/chars.txt --flavor=woff2 --output-file=assets/fonts/NotoSerifSC-$w.woff2
done
```
Re-run after any text change, or new glyphs fall back to system fonts.

## HyperFrames gotchas hit in practice

- One paused root timeline `window.__timelines["main"]`; one clock-driver tween for per-frame counters/timecode.
- Same-track `<audio>` overlap = lint error.
- Intentional overflow (scrolling corpus, glyph overhang) → `data-layout-allow-overflow`.
- `content_overlap` warnings are real — move the element, don't ignore.
- Panels over the background need opaque backgrounds or the grid/moon bleeds through.
- `check` "Navigation timeout" under load is transient → retry.
- Vendor GSAP locally (`assets/vendor/gsap.min.js`); a CDN fetch can fail mid-render on a long piece.
- Two `fromTo` on the same element + property: the later one's from-state wins at seek 0 (immediateRender). Any fromTo that is not the first on that property needs `immediateRender: false`, or the opening frame shows the wrong state.
- A layer built for a later scene but drawn at the same spot as an earlier one (e.g. the font 木 that takes over from the morphing glyph at the family chapter) must be hidden at t=0 and shown only at its handover. If it isn't, it sits on top of the earlier scene the whole time, and the viewer sees the "answer" before it is revealed. Verify by snapshotting the early scenes and checking that only that scene's element is visible. Snapshotting only the scene you just built won't catch it.
- Progress rails/timelines: give each stop three distinct states. Future: a faint skeleton (hollow dot, labels at about 0.22 alpha, no content). Current: bright labels, an accent dot at 1.5×, full content. Past: content at 0.4, labels at 0.45. Add an accent fill line that grows with the transition. Never show future content up front.
- Morph sequences (A→B→C): keep the state you just left as a ghost behind the new one, at about 0.16 opacity. Keep only one ghost at a time and fade out the older one, so viewers can compare before and after without clutter. This was user feedback on the hanzi evolution.
- An exiting scene must be gone before the next one fades in. For example, the ring zoom-out ending 0.15s before 沐 starts. If the two overlap at half opacity the frame turns to mud. Check by snapshotting the 0.3s around every hand-off.

## Long form: chapter sub-compositions and seamless boundaries

For anything over ~2 min, split into one sub-composition per chapter (`compositions/chNN-*.html`, ids prefixed `chNN-`, hosts alternate tracks 2/3). Shared bg/HUD/subtitles/audio stay in root. Hand each chapter to an agent with a written contract (geometry of shared elements, local cue times, safe area, verification steps).

**Boundary rule** (user saw "同一帧闪了一下" at 1:48 and 2:13):
- *Scene change* (different content on both sides): each chapter fades its content out over its last 0.5 s and in over its first 0.5 s. That is fine.
- *Continuous element across the cut* (the carrier ribbon, vector columns): **no exit fade in chapter N and no enter fade in chapter N+1.** Chapter N+1's frame 0 must equal chapter N's last frame. Fading both makes the same picture dip to black and come back, which reads as a flash.
  - **Same data**: one constant for IDs/values across all chapters. ch03 used different token IDs from ch02, so the numbers visibly jumped.
  - **Same geometry**: same box model, font, letter-spacing, line-height, color.
  - If chapter N+1's style differs, start it in chapter N's style and tween to its own over ~0.5 s (e.g. border 0.55→0.22, accent "?" crossfades to a dashed slot).
  - Remove only chapter-N-only labels with a short local fade before the cut.
  - No yoyo or breathe tweens on the shared elements in the last ~1.5 s: a residual offset of a few px shows as a jump.
  - Verify with a pixel diff, not by eye: snapshot `boundary−0.04` and `boundary+0.04`, crop out the HUD (y 130–860), then run `ImageChops.difference`. Max ≲ 20/255 = seamless.

```bash
npx hyperframes snapshot . --at "108.9,108.97" --describe false
python3 -c "from PIL import Image,ImageChops as C;import glob;f=sorted(glob.glob('snapshots/frame-*.png'));print(C.difference(*(Image.open(x).convert('L').crop((80,130,1840,860)) for x in f[:2])).getextrema())"
```

## Intro & end card

Scene times `S` stay VO-derived (0 = first scene). Intro and outro are pure offsets on top:

```js
const INTRO = 1.5, OUTRO = 4.0;
const clock = { t: -INTRO };                       // render() sees negative t during intro
// ... build all scene tweens at S times ...
tl.shiftChildren(INTRO, false, 0);                 // push every scene tween back by INTRO
tl.fromTo("#fade", { opacity: 1 }, { opacity: 0, duration: 1.4, ease: "power2.inOut" }, 0);
tl.fromTo("#hud-brand", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.8, ease: "power3.out", immediateRender: false }, 0.5);
tl.fromTo(clock, { t: -INTRO }, { t: S.end, duration: S.end + INTRO, ease: "none", onUpdate: render }, 0);

const EC = S.end + INTRO;                          // end card starts after the final fade
tl.set(["#cam", "#title", "#hud" /* ...everything on screen */], { opacity: 0 }, EC);
tl.to("#endcard", { opacity: 1, duration: 0.7, ease: "power2.out" }, EC);
tl.to("#ec-k", { opacity: 1, duration: 0.6 }, EC + 0.3);
tl.to("#ec-name span", { opacity: 1, y: 0, duration: 0.7, ease: "expo.out", stagger: 0.09 }, EC + 0.45);
tl.to("#ec-rule", { scaleX: 1, duration: 0.6, ease: "power3.inOut" }, EC + 1.0);
tl.to("#ec-sub", { opacity: 1, duration: 0.6 }, EC + 1.25);
tl.to("#endcard", { opacity: 0, duration: 0.8, ease: "power2.in" }, EC + OUTRO - 0.9);
```

```html
<div id="endcard">  <!-- inset:0, flex column centered, radial ink→black bg, last child of the scene -->
  <div id="ec-k">关注视频号</div>                <!-- serif 30px, letter-spacing .5em, dim -->
  <div id="ec-name"><span>双</span><span>言</span><span>两</span><span>语</span></div>  <!-- Noto Serif SC 900, 168px -->
  <div id="ec-rule"></div>                       <!-- 300×3 accent -->
  <div id="ec-sub">WECHAT CHANNELS</div>         <!-- mono, dim -->
</div>
```

- Every `<audio>` `data-start` += INTRO (vo0 at 0.6 → 2.1); root, scene and BGM `data-duration` = `S.end + INTRO + OUTRO`.
- Timecode must count from the real frame: `f = round((t + INTRO) * FPS)`.

## Check, snapshot, render

```bash
npx hyperframes check .
npx hyperframes snapshot . --at 3,12,25,40 --describe false   # read the contact sheets yourself
npx hyperframes render . -q high -o ./renders/video.mp4
# web copy — use bitrate cap; crf barely compresses because of the grain layer
ffmpeg -i renders/video.mp4 -c:v libx264 -preset slow -b:v 7M -maxrate 9M -bufsize 14M \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/video-web.mp4
```
≈ 0.9 MB per second at 7M (58s → 49MB, 123s → 108MB).
For long pieces (> 3 min) use `-crf 20 -maxrate 6M -bufsize 12M` instead of `-b:v 7M`: 7-min LLM lecture went 272 MB → 76 MB with no visible loss.

## Anti-piracy watermark (post-process, never in the composition)

The user wanted a faint moving mark that "不影响阅读". The first try used fixed spots at 12% plain text. They said it was too strong, and the fixed spots sat next to content. What shipped:
- **Design**: the 印章 seal (双言/两语 2×2 in a thin rounded frame, 92 px, cream). Make it with `scripts/wm_designs.py`, which needs `build/wm-font.otf`.
  - To get the font: `fontTools` → load the woff2 → `flavor=None` → save as .otf. ffmpeg can't read woff2.
- **Opacity 7%**. It hops every 20 s with a 1 s fade in and out, and is off from the end card on.
- **Auto-placement**: for each 20 s window, sample frames at 1 fps and build an edge map, taking the max over the window. Pick the box with the fewest edges inside the safe area (below the HUD, above the captions), with a 48 px margin and at least 500 px from the previous spot. So it never covers text, and it can't be cropped away in one place.
- The end-card start comes from `build/timing.json` `endcard_at` (no hard-coded END). Run `python3 scripts/watermark.py seal renders/video.mp4 snapshots/wm 50,130` to get previews, then `... seal renders/video.mp4 renders/video-web-wm.mp4` for the full encode. On a 7-minute video that takes about 1.5 min, and it does the web encode in the same pass.
- Feed the **web copy** (`renders/video-web.mp4`), not the `-q high` master, to both preview and full encode. The ~540 MB master's decode made a 100 s preview run past 10 min; the web copy did a 115 s preview in 7 s. The placement only reads 1 fps edge maps, and the full encode re-encodes to web bitrate anyway, so the result is the same.
- ffmpeg notes:
  - The fade is `geq` on a looped PNG: `a='alpha(X,Y)*A*fade(T)'`.
  - Preview frames use `-ss T -copyts`, plus `setpts=PTS+T/TB` on the PNG stream so `T` stays absolute.
- Verify:
  - Diff the frame against the unwatermarked web copy at a spot. Expect a max of about 17/255 mid-window, about 5 at 0.3 s into a window, and 0 on the end card.
  - Always keep the unwatermarked `video-web.mp4` too.
