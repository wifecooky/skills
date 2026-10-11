# Feedback loop: read the numbers before making the next episode

Run this as step 0 of every daily episode run. It is read-only: never reply to, like, delete or hide anything, and never touch a publish/edit button.

## Stores
| series | store (`<S>`) | public sources for `fetch` |
|---|---|---|
| 桃园英语角 (sanguo) | `~/Downloads/funny-short/videos/_metrics/taoyuan` | `https://www.youtube.com/channel/UCyaiX1XN53OMXu-OMNAKQCg/shorts` |
| sengoku | `~/git/manga-chinese-sites/videos/_metrics/sengoku` | every `published.youtube` link in `~/git/manga-chinese-sites/content/sengoku/episodes/*.json`, plus `https://www.tiktok.com/@sengoku_chugokugo` |
| olympus | `~/git/manga-chinese-sites/videos/_metrics/olympus` | the `published.youtube` / `published.tiktok` links in `content/olympus/episodes/*.json` (none yet → skip) |

Each store holds `metrics.jsonl` (one row per video per day), `comments.jsonl`, and `LEARNINGS.md`.

## 1. Collect
1. `python3 $SK/metrics.py fetch <S> <url> ...` (yt-dlp, no login). Videos that are still scheduled return 0, which is fine.
2. 桃园 only: read the Chinese dashboards in the user's Chrome (claude-in-chrome, **read-only**). Open one tab, read it with `get_page_text` / JS `innerText`, then close the tab.
   - **抖音** `https://creator.douyin.com/creator-micro/content/manage`. Every work lists 播放 点赞 评论 分享 收藏 完播率 2秒跳出率 吸粉量. Keep only works whose description has `#桃园英语角` or a 三国 hook; the account also holds old unrelated posts. Record each with
     `python3 $SK/metrics.py add <S> douyin <YYYY-MM-DDTHH:MM> published=<date> title=<短标题> views= likes= comments= shares= saves= completion=<x%> bounce2s=<x%> follows=`
     The id is the publish time shown on the card.
   - **小红书** `https://creator.xiaohongshu.com/new/note-manager?source=official`. It takes about 5 s to render. The five numbers under each note are, in order: 观看 评论 点赞 收藏 分享. Use `add <S> xhs <time> published= title= views= comments= likes= saves= shares=`.
   - **视频号** `https://channels.weixin.qq.com/platform/post/list` (wujie: read `document.querySelector('wujie-app').shadowRoot` text). If it redirects to `login.html`, skip it and say 「视频号需要扫码登录」 in the report. Never try to log in.
   - If Chrome or the extension isn't connected, or a page has changed beyond recognition, skip that platform and say so. Don't retry in a loop.
   - Comments on 抖音/小红书: if a card shows 评论 > 0, open that work's comment view read-only and copy the text into the report. Don't reply.
3. `python3 $SK/metrics.py report <S>` prints the table (views at ~48 h, so older videos don't win by age) and today's new comments.

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
