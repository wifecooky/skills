# index.html + script.json -> renders/<project>.srt (captions for YouTube). Run in the project dir after build.py.
# Timing comes from the built <audio id="vo-<scene>-<i>"> tags (what the render plays); text is the bubble text.
import json, re, html
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
S = json.load(open("script.json"))
T = json.load(open(SKILL / "themes" / S["theme"] / "script.json")) if S.get("theme") else {"scenes": []}
TEXT = {f"{s['id']}-{i}": l["text"] for s in T["scenes"] + S["scenes"] for i, l in enumerate(s.get("lines", []))}

def plain(t):
    return html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", "\n", t)))

def ts(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

vo = re.findall(r'<audio[^>]*id="vo-([^"]+)"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', open("index.html").read())
cues = sorted((float(st), float(st) + float(d), TEXT[lid]) for lid, st, d in vo)
out = Path("renders") / f"{Path.cwd().name}.srt"
out.parent.mkdir(exist_ok=True)
out.write_text("".join(
    f"{n}\n{ts(a)} --> {ts(b)}\n{plain(t)}\n\n"
    for n, (a, b, t) in enumerate(cues, 1)), encoding="utf-8")
print(f"{out}  cues={len(cues)}  end={ts(cues[-1][1])}")
