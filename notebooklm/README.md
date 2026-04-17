# notebooklm

Merged Claude Code skill for full Google NotebookLM automation.

Combines two upstream skills:
- [`teng-lin/notebooklm-py`](https://github.com/teng-lin/notebooklm-py) — the CLI (create / source / chat / generate / download)
- [`joeseesun/anything-to-notebooklm`](https://github.com/joeseesun/anything-to-notebooklm) — multi-source ingestion (URL / PDF / DOCX / EPUB / audio / image / WeChat / etc.)

## Install

```bash
# Skill (this directory) is auto-loaded by Claude Code if placed under your skills dir.
# Then install the underlying CLI:
pip install notebooklm-py
pip install 'markitdown[all]'   # optional, for file conversion

# Authenticate
notebooklm login
notebooklm list   # verify
```

For WeChat support, see the **WeChat Setup** section in `SKILL.md`.

## Usage

Trigger with `/notebooklm` or natural language like:

- "Create a podcast about climate change"
- "Add this PDF to NotebookLM and generate a mind map"
- "把这篇微信文章传到 NotebookLM 然后做成报告"
- "Summarize these YouTube videos"

See `SKILL.md` for the complete command reference.

## License

This skill is a thin documentation layer combining two MIT-licensed projects. See upstream repos for their licenses.
