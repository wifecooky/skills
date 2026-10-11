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
- Script tone: conversational, a little cheeky ("其实这家伙只会一件事"), short sentences, one idea per clip.

## Word timestamps (sync visual hits to words)

```bash
HF_HUB_OFFLINE=1 mlx_whisper assets/vo/vo3.mp3 --model mlx-community/whisper-small-mlx \
  --language zh --word-timestamps True --output-format json --output-dir /tmp/vot
```
large-v3-turbo download can hang at 0% CPU — use cached small model offline.

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
- Run `python3 scripts/watermark.py seal renders/video.mp4 snapshots/wm 50,130` to get previews, then `... seal renders/video.mp4 renders/video-web-wm.mp4` for the full encode. On a 7-minute video that takes about 1.5 min, and it does the web encode in the same pass.
- ffmpeg notes:
  - The fade is `geq` on a looped PNG: `a='alpha(X,Y)*A*fade(T)'`.
  - Preview frames use `-ss T -copyts`, plus `setpts=PTS+T/TB` on the PNG stream so `T` stays absolute.
- Verify:
  - Diff the frame against the unwatermarked web copy at a spot. Expect a max of about 17/255 mid-window, about 5 at 0.3 s into a window, and 0 on the end card.
  - Always keep the unwatermarked `video-web.mp4` too.
