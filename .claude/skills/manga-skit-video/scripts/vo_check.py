# VO QA: ASR every voiced line in its own language + flag pitch outliers per speaker.
# Run in the project dir after build.py:  python3 vo_check.py [line ids like 05-0 outro-1 ...]
# Report only: "CHECK" lines need an ear check, nothing is changed. Needs mlx_whisper + librosa.
import json, re, sys, difflib, warnings, numpy as np, librosa, mlx_whisper
from pathlib import Path
warnings.filterwarnings("ignore")
SKILL = Path(__file__).resolve().parent.parent
S = json.load(open("script.json"))
T = json.load(open(SKILL / "themes" / S["theme"] / "script.json")) if S.get("theme") else {"scenes": [], "head": 0}
CAST = {**T.get("cast", {}), **S["cast"]}
SC = T["scenes"][:T["head"]] + S["scenes"] + T["scenes"][T["head"]:]
ASR = "mlx-community/whisper-small-mlx"

def spoken(l):
    return l.get("say") or re.sub(r"<[^>]+>", "", l["text"])

def lang(t):  # kana -> ja, any CJK -> zh, else en; Latin + CJK in one line -> mixed
    if re.search(r"[぀-ヿ]", t): return "ja"
    cjk, lat = re.search(r"[一-鿿]", t), re.search(r"[A-Za-z]{2,}", t)
    return "mixed" if cjk and lat else "zh" if cjk else "en"

def norm(t):
    return re.sub(r"[\s\W_]+", "", t.lower())

def pitch(f):  # median F0 over the loud frames (pyin's voicing drops acted takes) and the loud share of the clip
    y, sr = librosa.load(f, sr=16000)
    f0 = librosa.yin(y, fmin=70, fmax=800, sr=sr, frame_length=1024, hop_length=160)
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=160)[0]
    n = min(len(f0), len(rms)); loud = rms[:n] > rms.max() * 10 ** (-25 / 20)
    return float(np.median(f0[:n][loud])), loud.mean()

rows = []
for sc in SC:
    for i, l in enumerate(sc.get("lines", [])):
        lid, f = f'{sc["id"]}-{i}', Path(f'assets/vo/{sc["id"]}-{i}.wav')
        if (sys.argv[1:] and lid not in sys.argv[1:]) or not f.exists(): continue
        t, lg = spoken(l), lang(spoken(l))
        heard = mlx_whisper.transcribe(str(f), path_or_hf_repo=ASR, language="en" if lg == "mixed" else lg)["text"].strip()
        hz, vs = pitch(f)
        rows.append(dict(id=lid, who=l["who"], lang=lg, text=t, heard=heard, hz=hz, voiced=vs,
                         sim=difflib.SequenceMatcher(None, norm(t), norm(heard)).ratio()))

# a multi-language voice sits ~1.5x higher in one language than the other: compare within (speaker, language)
med = {k: np.median([r["hz"] for r in rows if (r["who"], r["lang"]) == k]) for k in {(r["who"], r["lang"]) for r in rows}}
bad = 0
for r in rows:
    why = []
    if r["lang"] == "mixed": why.append("mixed-language line: unless the voice is bilingual, the CJK gets read with the wrong accent; listen, split if so")
    if r["sim"] < 0.5: why.append(f"ASR mismatch {r['sim']:.2f}")
    m = med[r["who"], r["lang"]]
    if not 0.6 < r["hz"] / m < 1.5: why.append(f"pitch {r['hz']:.0f}Hz vs {CAST[r['who']]['name']} [{r['lang']}] median {m:.0f}Hz")
    if r["voiced"] < 0.35: why.append(f"only {r['voiced']:.0%} voiced (rushed/clipped?)")
    bad += bool(why)
    print(f"{'CHECK' if why else 'ok   '} {r['id']:9s} [{r['lang']}] {r['text'][:28]:28s} -> {r['heard'][:28]:28s} {r['hz']:4.0f}Hz", *(["  ! " + "; ".join(why)] if why else []))
print(f"{len(rows)} lines, {bad} to check by ear")
