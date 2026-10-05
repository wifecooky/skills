# script.json + assets -> index.html (HyperFrames, 1080x1920). Run in the project dir: python3 build.py
# All timing is derived from the real VO wav lengths: rerun after any re-voice, never hand-edit index.html.
import json, math, os, random, shutil, subprocess
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
S = json.load(open("script.json"))
# theme pack (themes/<name>/ is itself a mini project): its first "head" scenes open the video, the rest close it;
# its cast/bgm fill gaps, and asset() falls back to its assets/ -> intro, outro, jingles and their VO are made once.
TH = SKILL / "themes" / S["theme"] if S.get("theme") else None
T = json.load(open(TH / "script.json")) if TH else {"scenes": [], "head": 0}
S["cast"] = {**T.get("cast", {}), **S["cast"]}
S["bgm"] = {**T.get("bgm", {}), **S.get("bgm", {})}
S.setdefault("series", T.get("series", ""))
S.setdefault("watermark", T.get("watermark"))  # channel handle, on screen the whole video
SC = T["scenes"][:T["head"]] + S["scenes"] + T["scenes"][T["head"]:]

def dur(p):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))

def asset(kind, name):
    """Project file first, else copy it from the theme pack, else from the skill."""
    for ext in ("wav", "mp3", "ttf", "jpg"):
        p = Path(f"assets/{kind}/{name}.{ext}")
        if p.exists():
            return str(p)
        for root in (TH, SKILL):
            b = root / "assets" / kind / f"{name}.{ext}" if root else None
            if b and b.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(b, p)
                return str(p)
    raise SystemExit(f"missing assets/{kind}/{name}")

FONTS = {"HY": asset("fonts", "ZCOOLQingKeHuangYou-Regular"), "KL": asset("fonts", "ZCOOLKuaiLe-Regular"),
         "SC": asset("fonts", "NotoSansSC")}

# ---------- timing: lay lines end to end, scene length = last line + tail ----------
t = 0.0
for s in SC:
    s["t0"] = round(t, 3)
    c = 0.0
    for i, l in enumerate(s.get("lines", [])):
        l["vo"] = asset("vo", f"{s['id']}-{i}")
        c += l.get("lead", 0.25 if i == 0 else 0.3)
        l["at"] = round(c, 3)
        c += dur(l["vo"])
    s["d"] = round(max(s.get("min", 1.2 if s.get("lines") else 2.0), c + s.get("tail", 0.5)), 3)
    t += s["d"]
TOTAL = round(t, 3)
at = lambda s, off: round(s["t0"] + off, 3)

audio = []  # (id, src, start, duration, volume)
def add(aid, src, st, vol=1.0, d=None):
    d = min(d or dur(src), TOTAL - st)
    audio.append((aid, src, round(st, 3), round(d, 3), vol))

for s in SC:
    sid = s["id"]
    for i, l in enumerate(s.get("lines", [])):
        add(f"vo-{sid}-{i}", l["vo"], at(s, l["at"]))
    if s.get("entry") == "push":
        add(f"sx-whoosh-{sid}", asset("sfx", "whoosh-short"), at(s, 0), 0.45)
    if s.get("entry") == "flash":
        add(f"sx-impact-{sid}", asset("sfx", "impact-bass-1"), at(s, 0), 0.8)
    if s.get("sfx") and not s.get("cues"):
        add(f"sx-pop-{sid}", asset("sfx", "pop"), at(s, 0.15), 0.4)
    if s.get("title"):
        add(f"sx-title-{sid}", asset("sfx", "impact-bass-2"), at(s, 0.1), 0.9)
    if s.get("stamp"):
        s["stamp_at"] = round(s["t0"] + s["d"] - 1.4, 3)
        add(f"sx-stamp-{sid}", asset("sfx", "impact-bass-2"), s["stamp_at"] + 0.25, 0.8)
    for k, cue in enumerate(s.get("cues", [])):
        name, off, vol = cue[:3]
        d = s["d"] - off if cue[3:] == ["scene"] else (cue[3] if cue[3:] else None)
        add(f"sx-{name}-{sid}-{k}", asset("sfx", name), at(s, off), vol, d)

# BGM: a scene inherits the previous scene's track unless it sets "bgm" (null = silence)
runs, cur = [], None
for s in SC:
    cur = s.get("bgm", cur)
    if runs and runs[-1][0] == cur:
        runs[-1][2] = s["t0"] + s["d"]
    else:
        runs.append([cur, s["t0"], s["t0"] + s["d"]])
for k, (name, a, b) in enumerate(runs):
    if not name:
        continue
    src = asset("bgm", name)
    if b - a > dur(src):  # loop with 3s crossfades until long enough
        n = int((b - a) // (dur(src) - 3)) + 1
        loop = f"assets/bgm/{name}-loop.wav"
        f = "[0][1]acrossfade=d=3" + "".join(f"[x{i}];[x{i}][{i + 1}]acrossfade=d=3" for i in range(n - 2))
        subprocess.run(["ffmpeg", "-v", "error", "-y", *sum([["-i", src] for _ in range(n)], []),
                        "-filter_complex", f, loop], check=True)
        src = loop
    add(f"bgm-{name}-{k}", src, a, S["bgm"][name].get("vol", 0.25), b - a)

# ---------- dream bubble (the spine): stages grow, swap content, shatter ----------
stages, pills = [], []
for s in SC:
    d = s.get("dream")
    if not d:
        continue
    os_l = next((l for l in s.get("lines", []) if l.get("os")), None)
    when = at(s, os_l["at"] - 0.25) if os_l else at(s, 0.1)
    if d.get("pill"):
        pills.append((when, d["pill"], round(s["t0"] + s["d"], 3)))
    else:
        stages.append((when, d))
shatter = next((s for s in SC if s.get("shatter")), None)
still = next((s for s in SC if s.get("still")), None)
n = len(stages)
for k, (_, d) in enumerate(stages):
    d.setdefault("scale", round(0.42 + 0.38 * k / max(n - 1, 1), 2))

# ---------- HTML ----------
def burst_svg(s):
    """Manga focus lines (集中线): black wedges from the panel edge toward s["burst"] = [x%, y%] (true = centre)."""
    if not s.get("burst"):
        return ""
    cx, cy = (s["burst"] if isinstance(s["burst"], list) else [50, 50])
    cx, cy, R = cx * 10, cy * 12.5, random.Random(s["id"])  # viewBox 1000x1250, seeded -> same lines every build
    tri = []
    for i in range(80):
        a, w = math.radians(i * 360 / 80 + R.uniform(-1.5, 1.5)), math.radians(R.uniform(0.4, 1.3))
        r0 = R.uniform(330, 480)
        p = [(cx + r0 * math.cos(a), cy + r0 * 1.25 * math.sin(a))] + \
            [(cx + 1700 * math.cos(a + d), cy + 1700 * math.sin(a + d)) for d in (-w, w)]
        tri.append("M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in p) + "Z")
    return (f'<svg class="burst" id="burst-{s["id"]}" viewBox="0 0 1000 1250" preserveAspectRatio="none" '
            f'style="transform-origin:{cx / 10}% {cy / 12.5}%"><path d="{"".join(tri)}"/></svg>')

CHIP = {k: ("" if c.get("chip", "red") == "red" else " m") for k, c in S["cast"].items()}
def scene_html(s):
    sid = s["id"]
    says = [l for l in s.get("lines", []) if not l.get("os")]
    h = (f'<div class="scene clip{" gray" if s.get("gray") else ""}" id="s{sid}" data-start="{s["t0"]}" '
         f'data-duration="{s["d"]}" data-track-index="1"><div class="pw" id="pw-{sid}"><div class="panel">'
         f'<img class="art" id="art-{sid}" src="{asset("panels", sid)}" alt="">{burst_svg(s)}</div></div>')
    if s.get("sfx"):
        h += f'<div class="sfx" id="sfx-{sid}">{s["sfx"]}</div>'
    if s.get("title"):  # true = the episode title; or the scene's own [line1, line2] (outro)
        t1, t2 = s["title"] if isinstance(s["title"], list) else S["title"]
        h += (f'<div class="title" id="title-{sid}"><span class="t1">{t1}</span>'
              f'<span class="t2">{t2}</span><span class="ep">{s.get("ep", S.get("episode", ""))}</span></div>')
    if s.get("stamp"):
        h += f'<div class="stamp" id="stamp-{sid}">{S.get("stamp", "完")}</div>'
    for i, l in enumerate(says):
        h += (f'<div class="say" id="say-{sid}-{i}"><span class="who{CHIP[l["who"]]}">{S["cast"][l["who"]]["name"]}</span>'
              f'<p>{l["text"]}</p>' + (f'<p class="sub">{l["sub"]}</p>' if l.get("sub") else "") + '</div>')
    if s.get("card"):  # language-point card: headline / pronunciation / translation / meaning
        c = s["card"]
        h += (f'<div class="card" id="card-{sid}"><b>{c["zh"]}</b><span class="py">{c.get("py", "")}</span>'
              f'<span class="en">{c.get("en", "")}</span><span class="note">{c.get("note", "").replace(" · ", "<br>")}</span></div>')
    if s.get("entry") == "flash":
        h += f'<div class="flash" id="flash-{sid}"></div>'
    return h + "</div>"

SHARDS = ["0 0,55 0,45 40,0 30", "55 0,100 0,100 35,45 40", "0 30,45 40,30 70,0 65", "45 40,100 35,100 70,60 65",
          "30 70,45 40,60 65,55 100,20 100", "0 65,30 70,20 100,0 100", "60 65,100 70,100 100,55 100"]
poly = lambda p: ",".join(" ".join(f"{v}%" for v in pt.split()) for pt in p.split(","))
def layer(k, d):
    if d.get("img"):
        inner = f'<img src="assets/panels/{d["img"]}.jpg" alt="">'
    else:
        inner = f'<div class="thought{" big" if d.get("big") else ""}">{d["text"]}</div>'
    return f'<div class="layer ly-{k}">{inner}</div>'
dream_html = ""
if stages:
    d0 = stages[0][0]
    d1 = round(shatter["t0"] + shatter["d"], 3) if shatter else TOTAL
    shards = "".join(f'<div class="shard" id="shard-{i}" style="clip-path:polygon({poly(p)})">'
                     + "".join(layer(k, d) for k, (_, d) in enumerate(stages)) + "</div>"
                     for i, p in enumerate(SHARDS))
    pill_html = "".join(f'<div class="doubt" id="pill-{k}">{p[1]}</div>' for k, p in enumerate(pills))
    dream_html = (f'<div class="dream clip" id="dream" data-start="{d0}" data-duration="{round(d1 - d0, 3)}" '
                  f'data-track-index="2"><div class="dream-in" id="dream-in"><div class="dots" id="dots">'
                  f'<i></i><i></i><i></i></div>{shards}{pill_html}</div></div>')

first = next((s for s in SC if not s.get("title")), SC[0])
header = (f'<div class="header clip" id="header" data-start="{first["t0"]}" data-duration="{round(TOTAL - first["t0"], 3)}" '
          f'data-track-index="3"><span class="series">{S["series"]}</span></div>')

wm = (f'<div class="wm clip" id="wm" data-start="0" data-duration="{TOTAL}" data-track-index="4">{S["watermark"]}</div>'
      if S.get("watermark") else "")

lanes, audio_html = [], []  # first free lane wins -> no overlapping audio on one track
for a, src, st, d, v in sorted(audio, key=lambda x: x[2]):
    k = next((i for i, e in enumerate(lanes) if e <= st), len(lanes))
    if k == len(lanes):
        lanes.append(0)
    lanes[k] = st + d
    audio_html.append(f'<audio id="{a}" src="{src}" data-start="{st}" data-duration="{d}" '
                      f'data-track-index="{10 + k}" data-volume="{v}"></audio>')

# ---------- motion ----------
def cam(f, z):
    """GSAP vars putting point f = [x%, y%] of the art at the panel centre at zoom z, clamped so no edge shows."""
    lim = (z - 1) * 50
    cl = lambda v: round(max(-lim, min(lim, v)), 1)
    return f'scale:{z},xPercent:{cl((50 - f[0]) * z)},yPercent:{cl((50 - f[1]) * z)}'

js = []
for s in SC:
    sid, s0, d, rot = s["id"], s["t0"], s["d"], s.get("rot", 0)
    pw = f"#pw-{sid}"
    if s.get("entry") == "push":
        js.append(f'tl.fromTo("{pw}",{{x:1150,rotation:{rot + 6}}},{{x:0,rotation:{rot},duration:0.38,ease:"power3.out"}},{s0});')
    elif s.get("entry") == "flash":
        js.append(f'tl.fromTo("{pw}",{{scale:1.12,rotation:{rot}}},{{scale:1,rotation:{rot},duration:0.3,ease:"power2.out"}},{s0});')
        js.append(f'tl.fromTo("#flash-{sid}",{{opacity:1}},{{opacity:0,duration:0.35,ease:"power1.in"}},{s0});')
    else:
        js.append(f'tl.fromTo("{pw}",{{scale:1.05,rotation:{rot}}},{{scale:1,rotation:{rot},duration:0.25,ease:"power2.out"}},{s0});')
    move = "none" if s.get("still") else s.get("move", "drift")
    cams = [(l["at"], l["focus"], l.get("zoom", 1.3)) for l in s.get("lines", []) if l.get("focus")]
    if cams and move == "drift":  # camera follows the speaker: snap-push onto each line's focus, then creep in
        ends = [c[0] - 0.15 for c in cams[1:]] + [d]
        js.append(f'tl.fromTo("#art-{sid}",{{{cam(cams[0][1], 1.1)}}},{{{cam(cams[0][1], 1.1)},duration:0.01}},{s0});')
        for (t_, f, z), e in zip(cams, ends):
            t1 = max(t_ - 0.15, 0.02)
            js.append(f'tl.to("#art-{sid}",{{{cam(f, z)},duration:0.45,ease:"power3.inOut"}},{round(s0 + t1, 3)});')
            js.append(f'tl.to("#art-{sid}",{{{cam(f, z + 0.05)},duration:{round(max(e - t1 - 0.45, 0.05), 3)},ease:"none"}},{round(s0 + t1 + 0.45, 3)});')
    elif move == "pulse":  # heartbeat: slow push-in + double-thump every 0.8s
        js.append(f'tl.fromTo("#art-{sid}",{{scale:1}},{{scale:1.22,duration:{d},ease:"none"}},{s0});')
        beat = 0.05
        while beat < d - 0.3:
            for off in (beat, beat + 0.23):
                js.append(f'tl.fromTo("{pw}",{{scale:1.035}},{{scale:1,duration:0.2,ease:"power2.out"}},{round(s0 + off, 3)});')
            beat += 0.8
    elif move == "lunge":
        js.append(f'tl.fromTo("#art-{sid}",{{scale:1}},{{scale:1.18,duration:{d},ease:"power1.in",transformOrigin:"60% 30%"}},{s0});')
    elif move == "drift":
        js.append(f'tl.fromTo("#art-{sid}",{{scale:1}},{{scale:1.06,duration:{d},ease:"none"}},{s0});')
    if s.get("burst"):  # slam in, then jitter like hand-drawn lines
        js.append(f'tl.fromTo("#burst-{sid}",{{scale:1.6,opacity:0}},{{scale:1,opacity:1,duration:0.25,ease:"power3.out"}},{round(s0 + 0.05, 3)});')
        js.append(f'tl.to("#burst-{sid}",{{rotation:1.2,duration:0.06,yoyo:true,repeat:{int((d - 0.35) / 0.06)},ease:"none"}},{round(s0 + 0.3, 3)});')
    if s.get("sfx"):
        js.append(f'tl.fromTo("#sfx-{sid}",{{scale:0,rotation:-25}},{{scale:1,rotation:-8,duration:0.35,ease:"back.out(2.5)"}},{round(s0 + 0.12, 3)});')
        if d > 2.4:  # an impact word is a beat, not a caption: gone before the next line plays
            js.append(f'tl.to("#sfx-{sid}",{{opacity:0,duration:0.25}},{round(s0 + 2.0, 3)});')
    says = [l for l in s.get("lines", []) if not l.get("os")]
    for i, l in enumerate(says):
        js.append(f'tl.fromTo("#say-{sid}-{i}",{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:0.22,ease:"back.out(2)"}},{round(s0 + l["at"] - 0.05, 3)});')
        if i + 1 < len(says):
            js.append(f'tl.to("#say-{sid}-{i}",{{opacity:0,duration:0.1}},{round(s0 + says[i + 1]["at"] - 0.12, 3)});')
    if s.get("shake"):
        for k, (x, y) in enumerate([(-16, 8), (14, -10), (-10, -6), (8, 10), (-5, 4), (0, 0)]):
            js.append(f'tl.to("{pw}",{{x:{x},y:{y},duration:0.05,ease:"none"}},{round(s0 + 0.15 + k * 0.05, 3)});')
    if s.get("title"):
        js.append(f'tl.fromTo("#title-{sid}",{{scale:2.4,opacity:0,rotation:-4}},{{scale:1,opacity:1,rotation:-4,duration:0.35,ease:"power4.in"}},{at(s, 0.1)});')
        js.append(f'tl.to("#title-{sid}",{{y:10,duration:0.06,yoyo:true,repeat:5,ease:"none"}},{at(s, 0.45)});')
    if s.get("card"):
        js.append(f'tl.fromTo("#card-{sid}",{{scale:0.6,opacity:0,rotation:-3}},{{scale:1,opacity:1,rotation:-1.5,duration:0.35,ease:"back.out(2)"}},{at(s, 0.2)});')
    if s.get("stamp"):
        js.append(f'tl.fromTo("#stamp-{sid}",{{scale:3.2,opacity:0,rotation:-30}},{{scale:1,opacity:1,rotation:-12,duration:0.28,ease:"power4.in"}},{s["stamp_at"]});')

if stages:
    js.append(f'tl.set("#dream-in",{{scale:0}},0);')
    for k, (when, d) in enumerate(stages):
        js.append(f'tl.to("#dream-in",{{scale:{d["scale"]},duration:0.4,ease:"back.out(1.8)"}},{when});')
        js.append(f'tl.fromTo(".ly-{k}",{{opacity:0}},{{opacity:1,duration:0.25,immediateRender:false}},{when});')
        if k + 1 < n:
            js.append(f'tl.to(".ly-{k}",{{opacity:0,duration:0.25}},{stages[k + 1][0]});')
    for k, (when, _, end) in enumerate(pills):
        js.append(f'tl.fromTo("#pill-{k}",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.3,ease:"back.out(3)"}},{when});')
        js.append(f'tl.to("#dream-in",{{rotation:-4,duration:0.08,yoyo:true,repeat:3,ease:"none"}},{when});')
        js.append(f'tl.to("#pill-{k}",{{opacity:0,duration:0.15}},{end});')
    if still and still["t0"] > stages[0][0]:
        js.append(f'tl.to("#dream-in",{{filter:"grayscale(1)",duration:0.1}},{still["t0"]});')
        back = next((w for w, _ in stages if w > still["t0"]), None)  # a later dream brings colour back
        if back is not None:
            js.append(f'tl.to("#dream-in",{{filter:"grayscale(0)",duration:0.2}},{back});')
    if shatter:
        t13 = at(shatter, 0.15)
        js.append(f'tl.to("#dots",{{opacity:0,duration:0.05}},{t13});')
        fly = [(-260, -120, -80), (240, -160, 70), (-320, 260, -120), (300, 200, 110), (-60, 420, -40), (-380, 520, 150), (260, 560, -90)]
        for i, (x, y, r) in enumerate(fly):
            js.append(f'tl.to("#shard-{i}",{{x:{x},y:{y},rotation:{r},duration:0.9,ease:"power2.in"}},{t13});')
            js.append(f'tl.to("#shard-{i}",{{opacity:0,duration:0.3}},{round(t13 + 0.7, 3)});')

css = (SKILL / "scripts" / "style.css").read_text()
html = f'''<!doctype html>
<html lang="zh">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "HY"; src: url("{FONTS["HY"]}"); }}
@font-face {{ font-family: "KL"; src: url("{FONTS["KL"]}"); }}
@font-face {{ font-family: "SC"; src: url("{FONTS["SC"]}"); font-weight: 100 900; }}
{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{"".join(scene_html(s) for s in SC)}
{header}
{wm}
{dream_html}
{chr(10).join(audio_html)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
open("index.html", "w").write(html)
for s in SC:
    print(f'{s["id"]:>4} {s["t0"]:6.2f}-{s["t0"] + s["d"]:6.2f}  ' + " / ".join(l["text"] for l in s.get("lines", [])))
print("total", TOTAL, "s, audio clips", len(audio))
