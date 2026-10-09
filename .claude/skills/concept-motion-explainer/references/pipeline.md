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
