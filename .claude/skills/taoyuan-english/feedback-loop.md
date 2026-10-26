# Feedback loop: read the numbers before making the next episode

Run this as step 0 of every daily episode run. It is read-only: never reply to, like, delete or hide anything, and never touch a publish/edit button.

## Stores
Each series skill's 「Feedback」 section names its store (`<S>`), the public sources for `fetch`, and any logged-in dashboards.

Each store holds `metrics.jsonl` (one row per video per day), `comments.jsonl`, and `LEARNINGS.md`.

## 1. Collect
1. `python3 $SK/metrics.py fetch <S> <url> ...` (yt-dlp, no login). Videos that are still scheduled return 0, which is fine.
   - Pass each URL as its own argument. The shell is zsh, which does not split an unquoted `$urls`: all URLs arrive as one argument and only the first video is fetched (olympus 2026-10-25: the report showed `youtube: 1 videos from <16 URLs>` and missed ep18's 1014 views). Fix: build an array, `urls=($(… | grep .))`, then pass `"${urls[@]}"`. Verify: one `youtube: 1 videos from <url>` line per URL, and today's row count in `metrics.jsonl` equals the URL count.
2. Dashboards, only if the series skill lists them: read them in the user's Chrome (claude-in-chrome, **read-only**). Open one tab, read it with `get_page_text` / JS `innerText`, then close the tab. Record each work with `python3 $SK/metrics.py add <S> <platform> <id> published= title= ...` as the series skill says. Never try to log in.
   - If Chrome or the extension isn't connected, or a page has changed beyond recognition, skip that platform and say so. Don't retry in a loop.
   - Comments: if a card shows 评论 > 0, open that work's comment view read-only and copy the text into the report. Don't reply.
3. `python3 $SK/metrics.py report <S>` prints the table (views at the first snapshot ≥ 48 h, so older videos don't win by age), today's new comments, then the judge block (`metrics.py judge <S>` prints it alone):
   - Per-episode views per platform and the series median, from `<S>/hypotheses.json`. Each hypothesis's thresholds give 达标 / 未达标 / 待定 (snapshot < 48 h). Copy these verdicts into LEARNINGS instead of recomputing by hand.
   - Posts on one platform less than 24 h apart, and the earliest time for the next episode.
   - LEARNINGS.md line count (warns above 40).
   - After publishing, add the episode's ids to `episodes` in `hypotheses.json` (douyin/wechat id = the publish time on the dashboard card). A new hypothesis with a numeric target goes into `hypotheses` too.

## 2. Learn (update `<S>/LEARNINGS.md`)
- **Sample sizes are tiny** (tens to hundreds of views). One episode proves nothing. Write 「趋势」 until a pattern holds across ≥ 3 episodes, and keep every claim tied to evidence (episode, platform, number).
- Compare like with like: views@48h, 完播率 and 2秒跳出率 on the same platform. 完播率/跳出率 judge the video itself; views mostly judge the topic + title + cover.
- Comments: questions, requests and corrections go to 「选题候选」. List comments worth a reply under 「建议你回复」 for the user, who replies personally.
- Check last run's 「本集验证」: did the episode support the hypothesis? Move it to 已验证 or 推翻.
- Keep the file ≤ 40 lines. Delete stale points instead of piling up.

```
# LEARNINGS — <series>（更新 YYYY-MM-DD）
## 当前结论（趋势 / 已验证，附证据）
## 待验证假设
## 本集验证（这次 run 写，下次 run 回看）
## 选题候选（来自评论）
## 建议你回复（评论原文 + 平台 + 作品）
```

## 3. Use
- Today's topic, hook, length and title must apply at least one point from 当前结论 / 待验证假设. Write which one, plus the expected effect, under 「本集验证」 and in the run report.
- Never change cast, art style, watermark or series format on the strength of data alone. Propose it in the report and let the user decide.
