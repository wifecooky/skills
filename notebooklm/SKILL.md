---
name: notebooklm
description: Complete NotebookLM automation - create notebooks, ingest multi-source content (URLs, YouTube, PDFs, DOCX, EPUB, audio, images, WeChat), chat with sources, and generate audio podcasts, slide decks, mind maps, quizzes, videos, reports, infographics, data tables, and flashcards. Activates on /notebooklm or intent like "create a podcast about X" / "把这个PDF做成播客".
---

# NotebookLM Automation

Full programmatic access to Google NotebookLM via the `notebooklm-py` CLI, plus a multi-source ingestion layer that converts WeChat articles, YouTube videos, Office documents, PDFs, EPUBs, audio, images, and more into NotebookLM-ready sources.

This is a merged skill combining:
- **`teng-lin/notebooklm-py`** — the NotebookLM CLI (create, source add, chat, generate, download)
- **`joeseesun/anything-to-notebooklm`** — multi-source ingestion + format conversion

## Installation

```bash
# 1. Install the CLI (Python package)
pip install notebooklm-py

# 2. (Optional, for file conversion) Install markitdown
pip install 'markitdown[all]'

# 3. Authenticate
notebooklm login          # Opens browser for Google OAuth
notebooklm list           # Verify it works
```

For WeChat article support, see the **WeChat (微信公众号) Setup** section below.

### Auth Migration from Old Skill

If you previously used `pleaseprompto/notebooklm-skill`, that auth (patchright-based, in `~/.agents/skills/notebooklm/data/browser_state/state.json`) is **not directly reusable** by `notebooklm-py`. Run `notebooklm login` once to set up new auth at `~/.notebooklm/`. You can keep the old skill's data dir as backup.

## When This Skill Activates

**Explicit:** `/notebooklm`, `use notebooklm`, mentions tool by name

**Intent:**
- "Create a podcast about [topic]" / "做成播客"
- "Summarize these URLs/documents"
- "Generate a quiz / mind map / slides / flashcards / video"
- "Add these sources to NotebookLM"
- "把这篇微信文章传到 NotebookLM"
- "这个 PDF 生成 PPT"

## Autonomy Rules

**Run automatically (no confirmation):**
- `notebooklm status`, `auth check`, `list`, `source list`, `artifact list`, `language *`
- `notebooklm use <id>` (single-agent only — use `-n <id>` flag in parallel workflows)
- `notebooklm create`, `source add`, `ask "..."` (without `--save-as-note`)
- `notebooklm history` (read-only), `profile *`, `doctor`
- `notebooklm artifact wait`, `source wait`, `research wait` (in subagent context only)

**Ask before running:**
- `notebooklm delete` — destructive
- `notebooklm generate *` — long-running, may fail
- `notebooklm download *` — writes to filesystem
- `notebooklm artifact|source|research wait` — long-running (when in main conversation)
- `notebooklm ask "..." --save-as-note` — writes a note
- `notebooklm history --save` — writes a note

## Quick Reference (CLI)

| Task | Command |
|------|---------|
| Authenticate | `notebooklm login` |
| Diagnose auth | `notebooklm auth check` |
| List notebooks | `notebooklm list` |
| Create notebook | `notebooklm create "Title"` |
| Set context | `notebooklm use <notebook_id>` |
| Show context | `notebooklm status` |
| Add URL/file/YouTube | `notebooklm source add "<url-or-path>"` |
| List sources | `notebooklm source list` |
| Delete source | `notebooklm source delete <source_id>` |
| Wait for source processing | `notebooklm source wait <source_id>` |
| Web research (fast) | `notebooklm source add-research "query"` |
| Web research (deep) | `notebooklm source add-research "query" --mode deep --no-wait` |
| Chat | `notebooklm ask "your question"` |
| Save chat as note | `notebooklm ask "..." --save-as-note` |
| History | `notebooklm history` |
| Generate audio (podcast) | `notebooklm generate audio` |
| Generate slide deck | `notebooklm generate slide-deck` |
| Generate mind map | `notebooklm generate mind-map` |
| Generate quiz | `notebooklm generate quiz` |
| Generate video | `notebooklm generate video` |
| Generate report | `notebooklm generate report` |
| Generate infographic | `notebooklm generate infographic` |
| Generate data table | `notebooklm generate data-table` |
| Generate flashcards | `notebooklm generate flashcards` |
| Wait for artifact | `notebooklm artifact wait <artifact_id>` |
| Download artifact | `notebooklm download <artifact_id>` |
| Set language | `notebooklm language set <code>` |

## Multi-Source Ingestion (from anything-to-notebooklm)

Auto-detect input type and convert to a NotebookLM-acceptable source.

| Input | Detection | Handling |
|---|---|---|
| `https://mp.weixin.qq.com/s/...` | WeChat article | MCP scraper → text → `source add` (TXT) |
| `https://youtube.com/...` / `youtu.be/...` | YouTube | Direct: `notebooklm source add "<url>"` |
| `https://...` (other) | Web page | Direct: `notebooklm source add "<url>"` |
| `*.pdf` (text) | PDF | `markitdown file.pdf > file.md` → `source add file.md` |
| `*.pdf` (scanned) | Scanned PDF | OCR via `markitdown` (with vision) or `tesseract` → `source add` |
| `*.docx` / `*.pptx` / `*.xlsx` | Office | `markitdown` → markdown → `source add` |
| `*.epub` | EPUB | `python -m ebooklib` (preferred over Calibre) → text → `source add` |
| `*.md` | Markdown | Direct: `notebooklm source add file.md` |
| `*.jpg/png/gif/webp` | Image | OCR via `markitdown` → `source add` (or pass image to source if supported) |
| `*.mp3/wav/m4a` | Audio | `notebooklm source add file.mp3` (NotebookLM does transcription) |
| `*.csv/json/xml` | Structured data | Convert to markdown table or pretty-print → `source add` |
| `*.zip` | Archive | `unzip`, recurse over contents |
| Plain text | Text | `echo "..." > /tmp/x.txt && source add /tmp/x.txt` |
| Search query (no URL) | Keyword | Use `notebooklm source add-research "query"` |

### Natural Language → Generation Mapping

| User says | Intent | Command |
|---|---|---|
| "podcast" / "audio" / "播客" / "音声" | audio | `generate audio` |
| "slides" / "PPT" / "幻灯片" / "スライド" | slide-deck | `generate slide-deck` |
| "mind map" / "思维导图" / "マインドマップ" | mind-map | `generate mind-map` |
| "quiz" / "测验" / "クイズ" | quiz | `generate quiz` |
| "video" / "视频" / "動画" | video | `generate video` |
| "report" / "summary" / "总结" / "レポート" | report | `generate report` |
| "infographic" / "信息图" / "インフォグラフ" | infographic | `generate infographic` |
| "data table" / "表格" / "テーブル" | data-table | `generate data-table` |
| "flashcards" / "闪卡" / "フラッシュカード" | flashcards | `generate flashcards` |

If no explicit instruction, **only upload sources** and wait for follow-up.

## Workflow Patterns

### Pattern A: Quick "URL → Podcast"
```bash
notebooklm create "Topic"           # if no notebook yet
notebooklm use <id>                 # set context
notebooklm source add "<url>"       # add source
notebooklm source wait <source_id>  # wait for processing
notebooklm generate audio           # produce podcast
notebooklm artifact wait <id>       # wait for completion
notebooklm download <id>            # download MP3
```

### Pattern B: Multi-source → Report
```bash
notebooklm use <id>
for src in url1 url2 file.pdf file.docx; do
  notebooklm source add "$src"
done
# Wait for all sources to process
notebooklm source list  # check states
notebooklm generate report
```

### Pattern C: Chat-only research
```bash
notebooklm use <id>
notebooklm ask "What does source X say about Y?"
notebooklm ask "Compare claims between sources A and B" --save-as-note
```

### Pattern D: Parallel agents (avoid `use`)
```bash
# In each parallel agent, pass --notebook explicitly:
notebooklm source add "$URL" --notebook <id>
notebooklm ask "..." --notebook <id>
```

## WeChat (微信公众号) Setup

WeChat articles are anti-scraping; need an MCP server.

1. Clone the MCP server (one-time):
   ```bash
   git clone https://github.com/joeseesun/anything-to-notebooklm.git /tmp/atn
   cp -r /tmp/atn/feishu-read-mcp ~/mcp-servers/wexin-read-mcp
   ```

2. Add to your Claude Code `mcp.json` (or equivalent):
   ```json
   {
     "mcpServers": {
       "weixin-reader": {
         "command": "python",
         "args": ["/Users/$USER/mcp-servers/wexin-read-mcp/src/server.py"]
       }
     }
   }
   ```

3. Restart Claude Code. Now WeChat URLs auto-route through the MCP scraper.

## CI/CD, Multiple Accounts, Parallel Agents

| Variable | Purpose |
|----------|---------|
| `NOTEBOOKLM_HOME` | Custom config directory (default `~/.notebooklm`) |
| `NOTEBOOKLM_PROFILE` | Active profile (default `default`) |
| `NOTEBOOKLM_AUTH_JSON` | Inline auth JSON (no file writes — for CI secrets) |

**CI/CD:** set `NOTEBOOKLM_AUTH_JSON` from a secret containing your `storage_state.json` contents.

**Multi-account:** `notebooklm profile create work && notebooklm -p work login`.

**Parallel agents:** `notebooklm use` writes a shared context file. To avoid races, always pass explicit `-n <id>` (or `--notebook <id>`).

## Troubleshooting

| Problem | Fix |
|---|---|
| `notebooklm` command not found | `pip install notebooklm-py` (in active venv) |
| Auth errors | `notebooklm login` (re-auth) or `notebooklm auth check --test` |
| Rate limit (50 queries/day on free Google) | Wait or switch profile/account |
| Source stuck "processing" | `notebooklm source wait <id>`; if it never settles, delete and re-add |
| Conversion fails for a file | Try `markitdown file.x > /tmp/x.md` manually, then `source add /tmp/x.md` |
| WeChat URL fails | Verify MCP server is running and config registered |

## Reference Links

- CLI source: https://github.com/teng-lin/notebooklm-py
- Multi-source pipeline (original): https://github.com/joeseesun/anything-to-notebooklm
- NotebookLM: https://notebooklm.google.com
