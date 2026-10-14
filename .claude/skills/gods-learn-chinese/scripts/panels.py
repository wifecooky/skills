# Generate the character sheet + every panel/dream image with OpenAI gpt-image-2.
# Run in the project dir:  python3 panels.py [ids...]   (no ids = all missing; existing PNGs are skipped)
# Every panel is an /images/edits call with the character sheet as reference -> same faces in every panel.
import json, base64, os, sys, subprocess, concurrent.futures as cf

def key():
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    for l in open(os.path.expanduser("~/.baoyu-skills/.env")):
        if l.startswith("OPENAI_API_KEY"):
            return l.split("=", 1)[1].strip()

KEY = key()
S = json.load(open("script.json"))
OUT = "assets/panels"
SHEET = f"{OUT}/00-charsheet.png"
LOOKS = "CHARACTERS (original characters, not real people):\n" + "\n".join(f"- {c['look']}" for c in S["cast"].values() if c.get("look"))  # narrators have no look
REF = "Use the characters in the reference character sheet as the exact same identities (face, hair, outfits). Do not redesign them.\n"

def call(endpoint, prompt, size, out, ref=None):
    cmd = ["curl", "-sS", "--http1.1", "--max-time", "480", f"https://api.openai.com/v1/images/{endpoint}",  # HTTP/2 hit framing errors / empty replies
           "-H", f"Authorization: Bearer {KEY}"]
    if ref:  # edits = multipart with the reference image
        cmd += ["-F", "model=gpt-image-2", "-F", f"size={size}", "-F", "quality=medium",
                "--form-string", f"prompt={prompt}", "-F", f"image[]=@{ref}"]  # -F would cut the prompt at the first ";"
    else:    # generations = JSON body
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(
            {"model": "gpt-image-2", "size": size, "quality": "medium", "prompt": prompt})]
    err = ""
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            open(out, "wb").write(base64.b64decode(json.loads(r.stdout)["data"][0]["b64_json"]))
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "88", out,
                            "--out", out[:-4] + ".jpg"], capture_output=True)
            return "ok"
        except Exception:
            err = r.stdout[:300] + r.stderr[:200]
    return "FAIL " + err

def jobs():
    for s in S["scenes"]:
        yield s["id"], "1024x1280", s["art"]
        d = s.get("dream") or {}
        if d.get("img"):
            yield d["img"], "1024x1024", d["art"]

def run(job):
    k, size, desc = job
    out = f"{OUT}/{k}.png"
    if os.path.exists(out):
        return k, "skip"
    return k, call("edits", REF + S["style"] + "\n" + LOOKS + "\nSCENE: " + desc, size, out, SHEET)

os.makedirs(OUT, exist_ok=True)
if not os.path.exists(SHEET):
    print("charsheet", call("generations", S["style"] + "\n" + LOOKS +
          "\nSCENE: Character model sheet on plain paper: each character full body front view and a face close-up "
          "with 3 expressions (neutral, happy, shocked). No text labels.", "1536x1024", SHEET), flush=True)
    print("CHECK the character sheet before continuing; delete it and rerun to redo.")
    sys.exit(0)
want = [j for j in jobs() if not sys.argv[1:] or j[0] in sys.argv[1:]]
with cf.ThreadPoolExecutor(6) as ex:
    for k, st in ex.map(run, want):
        print(k, st, flush=True)
