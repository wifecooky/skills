# Per-phrase loudness of VO clips: split on silence (< -40 dBFS), print each phrase's
# median RMS dBFS. "!" = a phrase more than 6 dB under the clip median, mid-clip.
# (A sentence-final word mid-clip can sit ~5 dB low; the voice-drop defect was 8–10 dB.)
# The clip's last phrase may fall off (sentence-end decay) and is only marked "~".
# usage: python3 vo_levels.py assets/vo/vo*.mp3   → exit 1 if any mid-clip "!"
import subprocess, sys
import numpy as np

bad = 0
for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    w = 1600
    n = len(x) // w
    db = 20 * np.log10(np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1) + 1e-12))
    segs, s = [], None
    for i, v in enumerate(list(db > -40) + [False]):
        if v and s is None:
            s = i
        elif not v and s is not None:
            if i - s >= 3:
                segs.append((s, i))
            s = None
    lv = [(a / 10, float(np.median(db[a:b]))) for a, b in segs]
    med = float(np.median([l for _, l in lv]))
    out = []
    for k, (t, l) in enumerate(lv):
        mark = ""
        if l < med - 6:
            mark = "~" if k == len(lv) - 1 else "!"
            bad += mark == "!"
        out.append(f"{t:.1f}s:{l:.1f}{mark}")
    print(f.split("/")[-1], "median", round(med, 1), " ".join(out))
sys.exit(1 if bad else 0)
