#!/bin/sh
# Voice one line of an onemin episode with ListenHub 晓曼, keep the shortest of N takes.
# usage: vo.sh <episode-dir> <key> [takes=1]   (text comes from assets/vo/xiaoman/lines.tsv)
# writes assets/vo/xiaoman/<key>.{mp3,wav}, assets/vo/<key>.wav, updates both durations.json;
# a previous <key>.wav is kept as xiaoman/old/<key>-<epoch>.wav
set -e
EP=$1; K=$2; N=${3:-1}
VO="$EP/assets/vo"; X="$VO/xiaoman"; T=$(awk -F'\t' -v k="$K" '$1==k{print $2}' "$X/lines.tsv")
[ -n "$T" ] || { echo "no line $K in $X/lines.tsv" >&2; exit 1; }
TMP=$(mktemp -d); best=""; bestd=999
for i in $(seq 1 "$N"); do
  u=$(listenhub tts create --text "$T" --mode direct --speaker 晓曼 --lang zh --json 2>/dev/null | grep -o '"audioUrl": *"[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)"/\1/')
  [ -n "$u" ] || { echo "take $i: no audioUrl" >&2; continue; }
  curl -sS -o "$TMP/$i.mp3" "$u"
  ffmpeg -hide_banner -loglevel error -y -i "$TMP/$i.mp3" -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse" -ar 44100 -ac 1 "$TMP/$i.wav"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/$i.wav")
  echo "take $i: ${d}s"
  if [ "$(echo "$d < $bestd" | bc)" = 1 ]; then best=$i; bestd=$d; fi
done
[ -n "$best" ] || exit 1
if [ -f "$VO/$K.wav" ]; then mkdir -p "$X/old"; cp "$VO/$K.wav" "$X/old/$K-$(date +%s).wav"; fi
cp "$TMP/$best.mp3" "$X/$K.mp3"; cp "$TMP/$best.wav" "$X/$K.wav"
ffmpeg -hide_banner -loglevel error -y -i "$X/$K.wav" -af "volume=7dB,alimiter=limit=0.84:attack=3:release=50:level=false" "$VO/$K.wav"
python3 - "$VO" "$K" "$bestd" <<'PY'
import json, sys, pathlib
vo, k, d = pathlib.Path(sys.argv[1]), sys.argv[2], round(float(sys.argv[3]), 2)
for f in (vo / "durations.json", vo / "xiaoman" / "durations.json"):
    j = json.loads(f.read_text()) if f.exists() else {}
    j[k] = d; f.write_text(json.dumps(dict(sorted(j.items())), indent=1, ensure_ascii=False) + "\n")
print(f"{k}: kept take {sys.argv[3]}s; VO sum {sum(json.loads((vo/'durations.json').read_text()).values()):.2f}s")
PY
rm -rf "$TMP"
