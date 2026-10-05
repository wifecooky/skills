# ListenHub TTS for every line in script.json -> assets/vo/<scene>-<i>.wav (silence-trimmed, 48k stereo).
# Run in the project dir:  python3 voice.py [--force] [--local] [line ids like 12-0 ...]   (--local = redo trim/speed from cached raw mp3, no API)
# A line with "emo" (acting note, e.g. "嚎啕大哭地喊") uses the generative listenhub-voice model instead of plain TTS.
# Existing wavs are skipped unless --force or named explicitly. Prints each line's duration.
import json, os, sys, time, subprocess, concurrent.futures as cf

def key():
    if os.environ.get("LISTENHUB_API_KEY"):
        return os.environ["LISTENHUB_API_KEY"]
    return open(os.path.expanduser("~/.listenhub.env")).read().split("=", 1)[1].strip()

KEY = key()
S = json.load(open("script.json"))
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.08,"
        "loudnorm=I=-20:TP=-1.5")  # acted takes come back anywhere from -41 to -18 dB: level every line

def lines():
    for s in S["scenes"]:
        for i, l in enumerate(s.get("lines", [])):
            yield f"{s['id']}-{i}", l

API = "https://api.marswave.ai/openapi/v1"

def curl(*args):
    return subprocess.run(["curl", "-s", "--max-time", "120", "-H", f"Authorization: Bearer {KEY}", *args],
                          capture_output=True, text=True).stdout

def acted(l, mp3):
    """Lines with "emo" go to the generative listenhub-voice model: the emotion is an acting note, not read aloud.
    (Plain /tts reads any bracketed note out loud.)"""
    c = S["cast"][l["who"]]
    note = "，".join(x for x in (c.get("persona"), l["emo"]) if x)  # persona tells the acted model who is speaking (meant to curb mid-line speaker drift; not proven)
    body = {"text": f'{note}：{l.get("say", l["text"])}',
            "voices": [{"type": "speaker", "id": S["cast"][l["who"]]["voice"]}]}
    for _ in range(20):  # submit is rate-limited to 5/min (code 29998): wait and retry
        r = json.loads(curl("-X", "POST", f"{API}/listenhub-voice/generate", "-H", "Content-Type: application/json",
                            "--data-binary", json.dumps(body, ensure_ascii=False)))
        if r.get("code") != 29998:
            break
        time.sleep(15)
    tid = r.get("data", {}).get("taskId")
    for _ in range(60 if tid else 0):
        time.sleep(4)
        d = json.loads(curl(f"{API}/listenhub-voice/tasks/{tid}") or "{}").get("data")
        if not d:  # transient poll error (rate limit / timeout): keep polling
            continue
        if d["status"] == "success":
            subprocess.run(["curl", "-s", "-o", mp3, d["audioUrl"]], check=True)
            return None
        if d["status"] == "failed":
            break
    return "FAIL " + json.dumps(r, ensure_ascii=False)[:200]

def run(item):
    lid, l = item
    mp3, wav = f"assets/vo/raw/{lid}.mp3", f"assets/vo/{lid}.wav"
    sp = l.get("speed", S.get("speed", 1.0))
    if LOCAL:  # re-trim / re-speed the cached raw mp3, no API call
        pass
    elif l.get("emo"):
        err = acted(l, mp3)
        if err:
            return lid, 0, err
    else:
        body = {"input": l.get("say", l["text"]), "voice": S["cast"][l["who"]]["voice"],
                "response_format": "mp3", "speed": sp}
        ct = curl("-o", mp3, "-w", "%{content_type}", "-X", "POST", f"{API}/tts",
                  "-H", "Content-Type: application/json", "--data-binary", json.dumps(body, ensure_ascii=False))
        if "audio" not in ct:  # failures come back as a JSON error body
            return lid, 0, "FAIL " + open(mp3).read()[:200]
    af = (f"atempo={sp}," if l.get("emo") else "") + TRIM  # acted audio has no speed knob: tempo it here
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af", af, "-ar", "48000", "-ac", "2", wav], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", wav]))
    return lid, round(d, 2), l["text"]

args = [a for a in sys.argv[1:] if a not in ("--force", "--local")]
LOCAL = "--local" in sys.argv
force = "--force" in sys.argv or LOCAL
os.makedirs("assets/vo/raw", exist_ok=True)
todo = [x for x in lines() if (x[0] in args) or (not args and (force or not os.path.exists(f"assets/vo/{x[0]}.wav")))]
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(run, todo):
        print(*r, flush=True)
