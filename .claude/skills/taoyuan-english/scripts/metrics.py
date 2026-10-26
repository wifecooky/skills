# Feedback loop data: daily snapshots of every published video + its comments (read-only, never replies).
#   python3 metrics.py fetch <store> <url> ...   public data via yt-dlp, no login; url = a channel's /shorts tab,
#                                                a TikTok profile, or single video links
#   python3 metrics.py add <store> <platform> <id> views=N likes=N comments=N [shares=N] [title=..] [published=YYYY-MM-DD]
#                                                                       numbers read off a creator dashboard (抖音/视频号/小红书)
#   python3 metrics.py report <store>                                   table (views at ~48h, so old videos don't win) + new comments + judge
#   python3 metrics.py judge <store>     per-episode views vs the thresholds in <store>/hypotheses.json, same-day double posts,
#                                        LEARNINGS.md length (also printed at the end of every report)
# <store> holds metrics.jsonl (one row per video per day) and comments.jsonl (deduped by comment id).
import json, sys, subprocess, datetime, re, statistics
from pathlib import Path
TODAY = datetime.date.today().isoformat()
BASE = {"date", "platform", "id", "title", "published", "views", "likes", "comments"}

days = lambda a, b: (datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days

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

def videos(store):
    by = {}
    for r in rows(store / "metrics.jsonl"):
        by.setdefault((r["platform"], r["id"]), []).append(r)
    return by

def early(rs):  # (views, age in days) of the first snapshot at ≥48h, else the latest
    pub = rs[-1].get("published")
    r = next((r for r in rs if days(r["date"], pub) >= 2), rs[-1]) if pub else rs[-1]
    return r.get("views"), days(r["date"], pub) if pub else 0

def report(store):
    by = videos(store)
    print("platform | published | title | views@~48h (age) | views now | likes | comments")
    for (pl, vid), rs in sorted(by.items(), key=lambda kv: kv[1][-1].get("published", "")):
        last = rs[-1]
        pub = last.get("published")
        views, age = early(rs)
        extra = " ".join(f"{k}={v}" for k, v in last.items() if k not in BASE)  # dashboard-only fields: completion, bounce2s …
        print(f"{pl} | {pub} | {last.get('title', '')[:40]} | {views} ({f'{age}d' if pub else '?'}) | {last.get('views')} | {last.get('likes')} | {last.get('comments')} {extra}")
    new = [c for c in rows(store / "comments.jsonl") if c["first_seen"] == TODAY]
    print(f"\nnew comments today: {len(new)}")
    for c in new:
        print(f"- [{c['platform']} {c['video']}] {c['text'][:200]!r}")
    judge(store)

def judge(store):
    by = videos(store)
    p = store / "hypotheses.json"
    if p.exists():
        h = json.load(open(p))
        eps = h["episodes"]
        pls = sorted({pl for e in eps.values() for pl in e})
        v = {(ep, pl): early(by[pl, vid]) for ep, e in eps.items() for pl, vid in e.items() if (pl, vid) in by}
        print("\njudge: views@~48h (age)\nep | " + " | ".join(pls))
        for ep in eps:
            print(f"{ep} | " + " | ".join(f"{v[ep, pl][0]} ({v[ep, pl][1]}d)" if (ep, pl) in v else "-" for pl in pls))
        med = {pl: statistics.median([x for (_, q), (x, age) in v.items() if q == pl and age >= 2] or [0]) for pl in pls}
        print("median (age ≥2d) | " + " | ".join(f"{med[pl]:g}" for pl in pls))
        for hy in h["hypotheses"]:
            out, ok = [], {}
            for ep in hy["eps"]:
                for pl, thr in hy["views"].items():
                    x, age = v.get((ep, pl), (None, 0))
                    s = "达标" if x is not None and x >= thr else "未达标" if x is not None and age >= 2 else "待定"
                    out.append(f"{ep} {pl} {'-' if x is None else x}/{thr} {s}")
                    ok.setdefault(pl, []).append(s)
            tally = " ".join(f"{pl} {s.count('达标')}/{len(s)}" + (f" 待定{s.count('待定')}" if "待定" in s else "") for pl, s in ok.items())
            print(f"{hy['id']} {hy['desc']}: " + " · ".join(out) + f" → {tally}")
    ts = lambda s: datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M")
    posts = sorted((ts(vid), pl, rs[-1].get("title", "")) for (pl, vid), rs in by.items() if re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d", vid))
    week = datetime.datetime.now() - datetime.timedelta(days=7)
    for pl in sorted({pl for _, pl, _ in posts}):
        mine = [x for x in posts if x[1] == pl]
        for (a, _, ta), (b, _, tb) in zip(mine, mine[1:]):
            if b - a < datetime.timedelta(hours=24) and b > week:
                print(f"间隔不足 24h {pl}: {ta} {a:%m-%d %H:%M} → {tb} {b:%m-%d %H:%M}（隔 {(b - a).total_seconds() / 3600:.1f}h）")
    if posts:
        print(f"最近一次发布 {posts[-1][0]:%m-%d %H:%M}，下一集最早 {posts[-1][0] + datetime.timedelta(hours=24):%m-%d %H:%M}（看板时间）")
    n = len(open(store / "LEARNINGS.md").read().splitlines()) if (store / "LEARNINGS.md").exists() else 0
    print(f"LEARNINGS.md {n} 行" + ("，超过 40 行：先压缩再写" if n > 40 else "（≤40）"))

store = Path(sys.argv[2]).expanduser()
store.mkdir(parents=True, exist_ok=True)
cmd, rest = sys.argv[1], sys.argv[3:]
if cmd == "fetch":
    for url in rest:
        fetch(store, "tiktok" if "tiktok.com" in url else "youtube", url)
elif cmd == "add":
    add(store, rest[0], rest[1], rest[2:])
judge(store) if cmd == "judge" else report(store)
