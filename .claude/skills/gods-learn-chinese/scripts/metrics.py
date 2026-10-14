# Feedback loop data: daily snapshots of every published video + its comments (read-only, never replies).
#   python3 metrics.py fetch <store> <url> ...   public data via yt-dlp, no login; url = a channel's /shorts tab,
#                                                a TikTok profile, or single video links
#   python3 metrics.py add <store> <platform> <id> views=N likes=N comments=N [shares=N] [title=..] [published=YYYY-MM-DD]
#                                                                       numbers read off a creator dashboard (抖音/视频号/小红书)
#   python3 metrics.py report <store>                                   table (views at ~48h, so old videos don't win) + new comments
# <store> holds metrics.jsonl (one row per video per day) and comments.jsonl (deduped by comment id).
import json, sys, subprocess, datetime
from pathlib import Path
TODAY = datetime.date.today().isoformat()
BASE = {"date", "platform", "id", "title", "published", "views", "likes", "comments"}

def rows(p):
    return [json.loads(l) for l in open(p)] if p.exists() else []

def snap(store, r):
    p = store / "metrics.jsonl"
    old = [x for x in rows(p) if (x["date"], x["platform"], x["id"]) != (TODAY, r["platform"], r["id"])]
    with open(p, "w") as f:
        for x in old + [r]:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

def ytdlp(*a):
    out = subprocess.run(["yt-dlp", "--skip-download", "--ignore-errors", *a], capture_output=True, text=True, timeout=600).stdout
    return [json.loads(l) for l in out.splitlines() if l.startswith("{")]

def fetch(store, platform, url):
    seen = {c["cid"] for c in rows(store / "comments.jsonl")}
    vids = ytdlp("--write-comments", "--extractor-args", "youtube:max_comments=100", "-j", url)
    with open(store / "comments.jsonl", "a") as f:
        for v in vids:
            d = v.get("upload_date") or ""
            snap(store, {"date": TODAY, "platform": platform, "id": v["id"], "title": v.get("title", ""),
                         "published": f"{d[:4]}-{d[4:6]}-{d[6:]}" if d else "", "views": v.get("view_count"),
                         "likes": v.get("like_count"), "comments": v.get("comment_count")})
            for c in v.get("comments") or []:
                if c["id"] in seen:
                    continue
                f.write(json.dumps({"platform": platform, "video": v["id"], "cid": c["id"], "text": c.get("text", ""),
                                    "likes": c.get("like_count"), "first_seen": TODAY}, ensure_ascii=False) + "\n")
    print(f"{platform}: {len(vids)} videos from {url}")

def add(store, platform, vid, kv):
    r = {"date": TODAY, "platform": platform, "id": vid, "title": "", "published": ""}
    for k, v in (a.split("=", 1) for a in kv):
        r[k] = int(v.replace(",", "")) if v.replace(",", "").isdigit() else v
    snap(store, r)

def report(store):
    days = lambda a, b: (datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days
    by = {}
    for r in rows(store / "metrics.jsonl"):
        by.setdefault((r["platform"], r["id"]), []).append(r)
    print("platform | published | title | views@~48h (age) | views now | likes | comments")
    for (pl, vid), rs in sorted(by.items(), key=lambda kv: kv[1][-1].get("published", "")):
        last = rs[-1]
        pub = last.get("published")
        early = min(rs, key=lambda r: abs(days(r["date"], pub) - 2)) if pub else last
        age = f"{days(early['date'], pub)}d" if pub else "?"
        extra = " ".join(f"{k}={v}" for k, v in last.items() if k not in BASE)  # dashboard-only fields: completion, bounce2s …
        print(f"{pl} | {pub} | {last.get('title', '')[:40]} | {early.get('views')} ({age}) | {last.get('views')} | {last.get('likes')} | {last.get('comments')} {extra}")
    new = [c for c in rows(store / "comments.jsonl") if c["first_seen"] == TODAY]
    print(f"\nnew comments today: {len(new)}")
    for c in new:
        print(f"- [{c['platform']} {c['video']}] {c['text'][:200]!r}")

store = Path(sys.argv[2]).expanduser()
store.mkdir(parents=True, exist_ok=True)
cmd, rest = sys.argv[1], sys.argv[3:]
if cmd == "fetch":
    for url in rest:
        fetch(store, "tiktok" if "tiktok.com" in url else "youtube", url)
elif cmd == "add":
    add(store, rest[0], rest[1], rest[2:])
report(store)
