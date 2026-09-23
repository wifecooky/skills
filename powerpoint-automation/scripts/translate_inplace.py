#!/usr/bin/env python3
"""
translate_inplace.py - In-place PPTX translation preserving all formatting.

Unlike the content.json pipeline (reconstruct → translate → rebuild), this script
directly edits the original PPTX file, replacing text while preserving:
  - All layouts, images, charts, shapes, and positioning
  - Grouped/nested shapes (recursive traversal)
  - Run-level formatting (font, color, size, bold, italic)

Overflow protection (--fit):
  - Proportional font size reduction based on text length ratio
  - Auto-fit fallback (MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE)

Translation history (--stats):
  - View past translation statistics (SQLite)
  - Filter: --stats --lang en  or  --stats --since 2026-03

Usage:
  python translate_inplace.py <input.pptx> <translations.json> <output.pptx>
  python translate_inplace.py <input.pptx> <translations.json> <output.pptx> --fit
  python translate_inplace.py <input.pptx> --extract <output.json>
  python translate_inplace.py --stats
  python translate_inplace.py --stats --lang en
  python translate_inplace.py --stats --since 2026-01
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Pt


STATS_DIR = Path(__file__).parent.parent / "logs"
DB_PATH = STATS_DIR / "translation_history.db"
JSONL_PATH = STATS_DIR / "translation_history.jsonl"

# Font size reduction: don't shrink below this ratio of the original
MIN_FONT_RATIO = 0.6
# Length ratio threshold to trigger font reduction
LENGTH_RATIO_THRESHOLD = 1.15


# ---------------------------------------------------------------------------
# SQLite history
# ---------------------------------------------------------------------------

def _get_db():
    """Get SQLite connection, creating table if needed."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            source      TEXT NOT NULL,
            output      TEXT NOT NULL,
            target_lang TEXT,
            slide_count INTEGER DEFAULT 0,
            total_strings    INTEGER DEFAULT 0,
            translated       INTEGER DEFAULT 0,
            unchanged        INTEGER DEFAULT 0,
            paragraphs_replaced INTEGER DEFAULT 0,
            paragraphs_skipped  INTEGER DEFAULT 0,
            font_adjusted    INTEGER DEFAULT 0,
            autofit_applied  INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def _migrate_jsonl():
    """One-time migration: import existing JSONL records into SQLite."""
    if not JSONL_PATH.exists():
        return
    conn = _get_db()
    count = conn.execute("SELECT COUNT(*) FROM translations").fetchone()[0]
    if count > 0:
        # Already migrated — remove JSONL to avoid re-import
        JSONL_PATH.rename(JSONL_PATH.with_suffix(".jsonl.bak"))
        conn.close()
        return

    migrated = 0
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            conn.execute("""
                INSERT INTO translations
                    (timestamp, source, output, target_lang, slide_count,
                     total_strings, translated, unchanged,
                     paragraphs_replaced, paragraphs_skipped,
                     font_adjusted, autofit_applied)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                r.get("timestamp", ""),
                r.get("source", ""),
                r.get("output", ""),
                r.get("target_lang"),
                r.get("slide_count", 0),
                r.get("total_strings", 0),
                r.get("translated", 0),
                r.get("unchanged", 0),
                r.get("paragraphs_replaced", 0),
                r.get("paragraphs_skipped", 0),
                r.get("font_adjusted", 0),
                r.get("autofit_applied", 0),
            ))
            migrated += 1

    conn.commit()
    conn.close()
    # Rename old file so it won't be re-imported
    JSONL_PATH.rename(JSONL_PATH.with_suffix(".jsonl.bak"))
    print(f"   Migrated {migrated} records from JSONL → SQLite")


def _save_stats(input_path, output_path, translations, stats, lang=None):
    """Insert translation record into SQLite."""
    _migrate_jsonl()
    conn = _get_db()

    total = len(translations)
    changed = sum(1 for k, v in translations.items() if k != v)

    conn.execute("""
        INSERT INTO translations
            (timestamp, source, output, target_lang, slide_count,
             total_strings, translated, unchanged,
             paragraphs_replaced, paragraphs_skipped,
             font_adjusted, autofit_applied)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().isoformat(),
        os.path.basename(input_path),
        os.path.basename(output_path),
        lang,
        stats.get("slide_count", 0),
        total,
        changed,
        total - changed,
        stats["replaced"],
        stats["skipped"],
        stats.get("font_adjusted", 0),
        stats.get("autofit_applied", 0),
    ))
    conn.commit()
    conn.close()


def _show_stats(lang_filter=None, since=None):
    """Display translation history from SQLite."""
    _migrate_jsonl()
    conn = _get_db()

    query = "SELECT * FROM translations WHERE 1=1"
    params = []
    if lang_filter:
        query += " AND target_lang = ?"
        params.append(lang_filter)
    if since:
        query += " AND timestamp >= ?"
        params.append(since)
    query += " ORDER BY timestamp"

    rows = conn.execute(query, params).fetchall()
    cols = [d[0] for d in conn.execute(query, params).description] if rows else []

    if not rows:
        print("No translation history found.")
        conn.close()
        return

    # Summary query
    sum_query = """
        SELECT COUNT(*) as cnt,
               COALESCE(SUM(slide_count), 0),
               COALESCE(SUM(total_strings), 0),
               COALESCE(SUM(paragraphs_replaced), 0)
        FROM translations WHERE 1=1
    """
    sum_params = []
    if lang_filter:
        sum_query += " AND target_lang = ?"
        sum_params.append(lang_filter)
    if since:
        sum_query += " AND timestamp >= ?"
        sum_params.append(since)
    cnt, sum_slides, sum_strings, sum_replaced = conn.execute(sum_query, sum_params).fetchone()

    # Column indices
    ci = {name: i for i, name in enumerate(cols)}

    title = f"Translation History ({cnt} records)"
    if lang_filter:
        title += f" [lang={lang_filter}]"
    if since:
        title += f" [since {since}]"

    print(f"\n📊 {title}")
    print("=" * 100)
    print(f"{'Date':<20} {'Source':<30} {'Lang':<6} {'Slides':<8} {'Strings':<10} {'Replaced':<10} {'Fit':<5}")
    print("-" * 100)

    for row in rows:
        ts = row[ci["timestamp"]][:16].replace("T", " ")
        src = row[ci["source"]][:28]
        lang = (row[ci["target_lang"]] or "?")[:5]
        slides = row[ci["slide_count"]] or "-"
        strings = row[ci["total_strings"]]
        replaced = row[ci["paragraphs_replaced"]]
        fit = "Y" if (row[ci["font_adjusted"]] or 0) > 0 else "-"
        print(f"{ts:<20} {src:<30} {lang:<6} {str(slides):<8} {strings:<10} {replaced:<10} {fit:<5}")

    print("-" * 100)
    print(f"{'TOTAL':<20} {'':<30} {'':<6} {str(sum_slides):<8} {sum_strings:<10} {sum_replaced:<10}")
    print()

    conn.close()


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_all_text(pptx_path):
    """Extract all translatable text from PPTX, including grouped shapes."""
    prs = Presentation(pptx_path)
    by_slide = {}
    flat = {}

    for i, slide in enumerate(prs.slides, 1):
        texts = []
        _collect_texts(slide.shapes, texts)
        by_slide[f"slide_{i}"] = texts
        for t in texts:
            if t not in flat:
                flat[t] = t

    return by_slide, flat


def _collect_texts(shapes, out):
    """Recursively collect paragraph-level text from shapes."""
    for shape in shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    out.append(text)
        if hasattr(shape, 'shapes'):
            _collect_texts(shape.shapes, out)
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for para in cell.text_frame.paragraphs:
                        text = para.text.strip()
                        if text:
                            out.append(text)


# ---------------------------------------------------------------------------
# Overflow protection
# ---------------------------------------------------------------------------

def _adjust_font_size(runs, original_text, translated_text):
    """Proportionally reduce font size if translated text is longer."""
    if not original_text or not translated_text:
        return False

    ratio = len(translated_text) / len(original_text)
    if ratio <= LENGTH_RATIO_THRESHOLD:
        return False

    shrink = max(1.0 / ratio, MIN_FONT_RATIO)

    adjusted = False
    for run in runs:
        if run.font.size is not None:
            run.font.size = int(run.font.size * shrink)
            adjusted = True

    return adjusted


def _enable_autofit(text_frame):
    """Enable auto-fit on a text frame as fallback overflow protection."""
    try:
        text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Translation engine
# ---------------------------------------------------------------------------

def translate_pptx(pptx_path, translations, output_path, fit=False):
    """Translate PPTX in-place using translation map."""
    prs = Presentation(pptx_path)

    stats = {"replaced": 0, "skipped": 0, "font_adjusted": 0, "autofit_applied": 0,
             "slide_count": len(prs.slides)}

    for slide in prs.slides:
        _translate_shapes(slide.shapes, translations, fit, stats)

    prs.save(output_path)
    print(f"\n✅ Saved: {output_path}")
    print(f"   Slides: {stats['slide_count']}")
    print(f"   Replaced: {stats['replaced']} paragraphs")
    print(f"   Skipped (no match): {stats['skipped']} paragraphs")
    if fit:
        print(f"   Font adjusted: {stats['font_adjusted']} paragraphs")
        print(f"   Auto-fit applied: {stats['autofit_applied']} text frames")
    return stats


def _translate_shapes(shapes, translations, fit, stats):
    """Recursively translate text in shapes, preserving formatting."""
    for shape in shapes:
        if shape.has_text_frame:
            _translate_text_frame(shape.text_frame, translations, fit, stats)
            if fit:
                _enable_autofit(shape.text_frame)
                stats["autofit_applied"] += 1

        if hasattr(shape, 'shapes'):
            _translate_shapes(shape.shapes, translations, fit, stats)

        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    _translate_text_frame(cell.text_frame, translations, fit, stats)


def _translate_text_frame(text_frame, translations, fit, stats):
    """Translate paragraphs in a text frame, preserving run-level formatting."""
    for para in text_frame.paragraphs:
        full_text = para.text.strip()
        if not full_text:
            continue

        if full_text in translations:
            translated = translations[full_text]
            if translated == full_text:
                continue

            runs = para.runs
            if runs:
                if fit:
                    if _adjust_font_size(runs, full_text, translated):
                        stats["font_adjusted"] += 1
                runs[0].text = translated
                for r in runs[1:]:
                    r.text = ""
            stats["replaced"] += 1
        else:
            stats["skipped"] += 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='In-place PPTX translation preserving all formatting')
    parser.add_argument('input', nargs='?', help='Input PPTX file path')
    parser.add_argument('translations_or_output', nargs='?',
                        help='translations.json (translate mode) or output.json (extract mode)')
    parser.add_argument('output', nargs='?', help='Output PPTX file path')
    parser.add_argument('--extract', action='store_true',
                        help='Extract all text to JSON for translation')
    parser.add_argument('--lang', default=None,
                        help='Target language hint / filter for --stats')
    parser.add_argument('--fit', action='store_true',
                        help='Enable overflow protection (font reduction + auto-fit)')
    parser.add_argument('--stats', action='store_true',
                        help='Show translation history statistics')
    parser.add_argument('--since', default=None,
                        help='Filter stats from date (e.g. 2026-01, 2026-03-15)')

    args = parser.parse_args()

    # Stats mode
    if args.stats:
        _show_stats(lang_filter=args.lang, since=args.since)
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    if args.extract:
        if not args.translations_or_output:
            print("Error: output JSON path required in extract mode", file=sys.stderr)
            sys.exit(1)
        by_slide, flat = extract_all_text(args.input)
        result = {
            "_meta": {
                "source": args.input,
                "target_lang": args.lang or "TODO",
                "total_strings": len(flat),
                "instruction": "Replace values with translated text. Keys are original text."
            },
            "by_slide": by_slide,
            "translations": flat
        }
        with open(args.translations_or_output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Extracted {len(flat)} unique strings to: {args.translations_or_output}")
        print(f"   Edit the 'translations' section, then run:")
        print(f"   python translate_inplace.py {args.input} {args.translations_or_output} output.pptx")
        return

    # Translate mode
    if not args.translations_or_output:
        print("Error: translations.json path required", file=sys.stderr)
        sys.exit(1)
    if not args.output:
        print("Error: output PPTX path required in translate mode", file=sys.stderr)
        sys.exit(1)

    with open(args.translations_or_output, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'translations' in data:
        translations = data['translations']
    else:
        translations = data

    lang = data.get("_meta", {}).get("target_lang") if isinstance(data, dict) else None
    lang = lang or args.lang

    print(f"Loading: {args.input}")
    print(f"Translations: {len(translations)} entries")
    if args.fit:
        print(f"Overflow protection: ON (font reduction + auto-fit)")

    stats = translate_pptx(args.input, translations, args.output, fit=args.fit)

    _save_stats(args.input, args.output, translations, stats, lang=lang)
    print(f"   📊 Stats saved to: {DB_PATH}")


if __name__ == '__main__':
    main()
