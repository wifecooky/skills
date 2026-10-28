#!/usr/bin/env python3
"""Hard checks for the rules in pipeline.md, publish-copy*.md and SKILL.md that a script can see.
usage: check_episode.py [project-dir ...]   (default: the current dir). Exit 1 on any problem.
The same file lives in taoyuan-english, sengoku-chinese and gods-learn-chinese; the series comes
from the skill dir it sits in. A rule that a script can check goes here, not only into prose."""
import json, pathlib, re, sys, time

SKILL = pathlib.Path(__file__).resolve().parent.parent
SERIES = {
    "taoyuan-english": {"tag": "#桃园英语角"},
    "sengoku-chinese": {"tag": "#戦国武将中国語を学ぶ", "example_in": "card", "stamp_in_card": True},
    "gods-learn-chinese": {"tag": "#GodsLearnChinese", "example_in": "card or publish.md", "no_han_for_en": True},
}[SKILL.name]
SRT_SINCE = time.mktime((2026, 10, 21, 0, 0, 0, 0, 0, -1))  # .srt next to the mp4 is required from 2026-10-21
HAN = re.compile(r"[㐀-鿿\U00020000-\U0003134f]")
# platform section → (title label, max chars) per publish-copy-common.md; X is checked as a weighted post
TITLES = {"YouTube": 100, "抖音": 30}
# platforms whose post carries the series tag; YouTube gets it from the channel footer (since 2026-10-21)
TAGGED = ("抖音", "视频号", "小红书", "TikTok", "X")
SKIPPED = re.compile(r"跳过|先不发|暂停|skip", re.I)


def x_weight(s):
    s = re.sub(r"https?://\S+", "x" * 23, s)
    return sum(2 if ord(c) > 0x10FF else 1 for c in s)


def sections(md):
    out, cur = {}, None
    for line in md.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return out


def labelled(lines, labels):
    """the first non-empty line after a **label** line"""
    for i, l in enumerate(lines):
        if l.strip().strip("*") in labels and l.strip().startswith("**"):
            return next((x.strip() for x in lines[i + 1:] if x.strip()), "")
    return None


def check(proj):
    bad = []
    fail = lambda m: bad.append(f"{proj.name}: {m}")
    try:
        d = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{proj.name}: no script.json"]
    theme = d.get("theme")
    pack = SKILL / "themes" / theme / "script.json" if theme else None
    cast = {**(json.loads(pack.read_text(encoding="utf-8")).get("cast", {}) if pack and pack.exists() else {}), **d.get("cast", {})}
    scenes = d.get("scenes", [])

    # script.json (pipeline.md § script.json quick reference)
    if "NO TEXT" not in d.get("style", "").upper():
        fail('style must contain "NO TEXT" (text in generated panels comes out garbled)')
    if theme and d.get("intro", True) and scenes and "title" in scenes[0]:
        fail("scene 01 has `title`, but the theme intro already carries the title")
    emo = {}
    for s in scenes:
        for ln in s.get("lines", []):
            who = ln.get("who")
            emo.setdefault(who, set()).add("emo" in ln)
            c = cast.get(who, {})
            drawn = (proj / "assets" / "panels" / f"{s.get('id')}.jpg").exists()  # focus is set from the drawn panel
            if drawn and c.get("look") and not ln.get("os") and "focus" not in ln:
                fail(f"scene {s.get('id')}: on-screen speaker {c.get('name', who)} has no `focus`: {ln.get('text', '')[:30]}")
            if SERIES.get("no_han_for_en") and "zh_" not in c.get("voice", "") and HAN.search(ln.get("say", ln.get("text", ""))):
                fail(f"scene {s.get('id')}: 汉字 fed to the English voice of {c.get('name', who)}; spell it in `say`: {ln.get('text', '')[:30]}")
    for who, kinds in emo.items():
        if len(kinds) > 1:
            fail(f"{cast.get(who, {}).get('name', who)} mixes `emo` and plain TTS lines (they sound like two people)")
    card = next((s["card"] for s in scenes if s.get("card")), None)
    ex = (d.get("lesson") or {}).get("examples") or []
    pub = proj / "publish.md"
    md = pub.read_text(encoding="utf-8") if pub.exists() else ""
    where = SERIES.get("example_in")
    if where and card and ex and (where == "card" or md):
        zh = ex[0].get("zh", "")
        if zh not in card.get("note", "") and (where == "card" or zh not in md):
            fail(f"lesson.examples[0] 「{zh}」 is not on the card{' or in publish.md' if where != 'card' else ''}: {card.get('note')}")
    if SERIES.get("stamp_in_card") and card and d.get("stamp") and d["stamp"] not in card.get("zh", ""):
        fail(f"stamp 「{d['stamp']}」 is not a character of the card word 「{card.get('zh')}」")
    if SKILL.name == "taoyuan-english" and card and not card.get("zh", "").isascii():
        fail(f"card.zh holds the English phrase, got 「{card.get('zh')}」")

    # after render (pipeline.md steps 9 and 11)
    mp4s = sorted((proj / "renders").glob("*.mp4")) if (proj / "renders").is_dir() else []
    if not mp4s:
        return bad
    if not (proj / "renders" / f"{proj.name}.srt").exists() and mp4s[-1].stat().st_mtime >= SRT_SINCE:
        fail(f"renders/{proj.name}.srt missing: run srt.py after the render")
    if not list((proj / "renders").glob("cover-ep*.jpg")):
        fail("no renders/cover-ep*.jpg (3:4 cover)")
    if not md:
        fail("rendered but no publish.md (pipeline.md step 11)")
        return bad
    for name, lines in sections(md).items():
        if name.startswith(TAGGED) and not SKIPPED.search(name + "\n".join(lines)) and SERIES["tag"] not in "\n".join(lines):
            fail(f"publish.md {name}: no series tag {SERIES['tag']}")
        plat = next((p for p in TITLES if name.startswith(p)), None)
        title = labelled(lines, {"タイトル", "Title", "标题"}) if plat else None
        if title and len(title) > TITLES[plat]:
            fail(f"publish.md {plat} title is {len(title)} chars, max {TITLES[plat]}: {title}")
        if name.startswith("视频号"):
            t = labelled(lines, {"短标题", "标题"})
            if t and not 6 <= len(t) <= 16:
                fail(f"publish.md 视频号 短标题 is {len(t)} chars, want 6–16: {t}")
        if name.startswith("X") and not SKIPPED.search(name + "\n".join(lines)):
            body = "\n".join(l for l in lines if l.strip() and not l.startswith("**")).strip()
            if body and x_weight(body) > 280:
                fail(f"publish.md X post weighs {x_weight(body)}, max 280")
    return bad


if __name__ == "__main__":
    dirs = [pathlib.Path(p).resolve() for p in sys.argv[1:]] or [pathlib.Path.cwd()]
    problems = [m for p in dirs for m in check(p)]
    for m in problems:
        print("✗", m, file=sys.stderr)
    print(f"check_episode: {len(problems)} problems in {len(dirs)} project(s)")
    sys.exit(1 if problems else 0)
