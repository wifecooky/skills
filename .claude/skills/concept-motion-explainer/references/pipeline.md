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
