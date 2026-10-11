# Export one episode as lesson JSON for the series website (the site owns the content, platforms only get copies).
# Run in the project dir (named <theme>-<NN>-<slug>):  python3 export_lesson.py [content_root]
# Other dir names (e.g. 20261010-durian): EP=07-too-good-to-be-true python3 export_lesson.py
# Writes <site>/episodes/<NN>-<slug>.json and copies the latest cover to <site>/covers/<NN>-<slug>.jpg, where <site> is the
# theme's own website (SITES below; other themes: ~/git/manga-chinese-sites/content/<theme>), or <content_root>/<theme> if given.
# Re-export keeps the "published" links already in the file; fill them in (and published.date) by hand after each upload.
import json, os, re, sys, shutil, subprocess, datetime
from pathlib import Path
SKILL = Path(__file__).resolve().parent.parent
S = json.load(open("script.json"))
T = json.load(open(SKILL / "themes" / S["theme"] / "script.json")) if S.get("theme") else {"scenes": [], "head": 0}
CAST = {**T.get("cast", {}), **S["cast"]}
S.setdefault("series", T.get("series", ""))
SC = T["scenes"][:T["head"]] + S["scenes"] + T["scenes"][T["head"]:]
SID = S.get("theme") or "misc"
NN, SLUG = re.match(r"(\d+)-(.+)" if os.environ.get("EP") else r".*?-(\d+)-(.+)", os.environ.get("EP") or Path.cwd().name).groups()
SITES = {"sanguo": "~/git/taoyuan-english/content", "olympus": "~/git/gods-learn-chinese/content/olympus"}
ROOT = Path(f"{sys.argv[1]}/{SID}" if sys.argv[1:] else SITES.get(SID, f"~/git/manga-chinese-sites/content/{SID}")).expanduser()
OUT = ROOT / "episodes" / f"{NN}-{SLUG}.json"

def plain(t):
    return re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", "\n", t))

def lang(t):
    return "ja" if re.search(r"[぀-ヿ]", t) else "zh" if re.search(r"[一-鿿]", t) else "en"

def latest(pat):
    f = sorted(Path("renders").glob(pat), key=lambda p: p.stat().st_mtime)
    return f[-1] if f else None

card = next(sc["card"] for sc in S["scenes"] if "card" in sc)
mp4, cover = latest("*.mp4"), latest("cover*.jpg")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                           capture_output=True, text=True).stdout) if mp4 else None
old = json.load(open(OUT)) if OUT.exists() else {}
if cover:
    (ROOT / "covers").mkdir(parents=True, exist_ok=True)
    shutil.copy2(cover, ROOT / "covers" / f"{NN}-{SLUG}.jpg")

ep = {
    "series": S["series"], "series_id": SID, "episode": int(NN), "slug": SLUG,
    "title": [plain(t) for t in S["title"]], "label": S.get("episode", ""),
    "word": {"zh": card["zh"], "py": card["py"], "meaning": card["en"], "note": card.get("note", "")},
    "examples": S.get("lesson", {}).get("examples", []),
    "transcript": [{"scene": sc["id"], "who": CAST[l["who"]]["name"], "text": plain(l["text"]), "sub": l.get("sub", ""),
                    "lang": lang(plain(l["text"])), **({"inner": True} if l.get("os") else {})}
                   for sc in SC for l in sc.get("lines", [])],
    "video": {"file": str(Path.cwd() / mp4), "duration": round(dur, 1)} if mp4 else old.get("video"),
    "cover": f"../covers/{NN}-{SLUG}.jpg" if (ROOT / "covers" / f"{NN}-{SLUG}.jpg").exists() else None,
    "published": {"youtube": "", "tiktok": "", "x": "", "date": "", **old.get("published", {})},
    "updated": datetime.date.today().isoformat(),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(ep, open(OUT, "w"), indent=2, ensure_ascii=False)
print(f"{OUT}  word={card['zh']}  lines={len(ep['transcript'])}  examples={len(ep['examples'])}  video={'yes' if mp4 else 'NOT RENDERED'}  cover={'yes' if cover else 'none'}")
