# Publish to 视频号 (WeChat Channels「双言两语」)

Outward-facing: publish/schedule only after the user explicitly says so. Upload `renders/video-web.mp4`.

## Copy template (channel style)

| field | rule | example |
|---|---|---|
| 短标题 (≤16 chars) | question + "N分钟看懂" | `AI是怎么说话的？1分钟看懂` |
| 描述 | hook question → one-sentence mechanism → carrier example → `和孩子一起看懂…` | `…用一句《静夜思》，和孩子一起看懂 ChatGPT 们背后的大语言模型。` |
| 话题 | 4–5 tags at the end of 描述 | `#AI #大模型 #ChatGPT #人工智能 #科普` (channel tags: #双言两语 #AI科普 #儿童科普 #亲子教育) |
| 合集 | topic collection | `AI` |
| 发表时间 | 定时, **19:00** (channel habit); several videos → same day, same time is fine | `2026-10-09 19:00` |
| 原创 | channel normally declares 原创 — but the checkbox opens a terms dialog; let the user agree, never click it for them | |
| 封面 | default is frame 1 (often the black fade) — suggest the most telling frame (e.g. probability bars) | |

Show the user the filled copy before publishing.

## Browser (gstack browse)

```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse"   # pass --headed on EVERY call, else daemon config mismatch
$B --headed goto https://channels.weixin.qq.com/platform/post/create
```

- Login: the user scans the QR code in the headed window themselves; the session persists across daemon restarts (page state does not — refill if the daemon restarted).
- The form lives in `document.querySelector('wujie-app').shadowRoot`. Playwright selectors pierce it; `js` reads need `.shadowRoot`.
- Selectors: video `input[type=file][accept*='video']` (`upload`), 描述 `.input-editor` (contenteditable), 短标题 `input[placeholder*='短标题']`, 时间 `input[placeholder='请选择发表时间']`, publish `button.weui-desktop-btn_primary:has-text('发表')`.
- `text=发表视频` / `text=取消` match several elements → navigate by URL or use a scoped selector.
- 话题: type `#tag ` then `Escape` to close the suggestion list. The **last** tag only becomes a topic (`span.hl.topic`) after one more space typed at the end of the editor — verify all tags converted.
- 定时: click label `定时`, then the time input. Day cells: `.weui-desktop-picker__table-row a`; open `input[placeholder='请选择时间']`, then `.weui-desktop-picker__time__hour li:nth-child(H+1)` and `.weui-desktop-picker__time__minute li:nth-child(M+1)`.

### ⚠ Time picker: JS `.click()` is a fake success

JS-clicking picker items updates the displayed input (`19:00`) but NOT the form model — the post was scheduled at the old value (22:00). Always use real `$B --headed click`. If the value may be stale, click a different hour first, then the target, so a change event fires.

## Verify (mandatory)

After 发表 it redirects to `/platform/post/list`. Read each item: `将于YYYY年MM月DD日 HH:MM发表` must match the plan. Wrong → item's 「修改并重新发表」, fix with real clicks, re-verify. (「删除」 also exists — don't use it without asking.)
