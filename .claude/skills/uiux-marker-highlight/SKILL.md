---
name: uiux-marker-highlight
description: Add marker-style highlight emphasis to key phrases. Supports multilingual (CJK + EN) with BudouX phrase-aware breaking.
user-invokable: true
args:
  - name: target
    description: CSS class name or target element/phrase (optional)
    required: false
---

# Marker Highlight — Text Emphasis

Add a semi-transparent marker-style highlight to the bottom portion of text, emphasizing key phrases. Works on multi-line inline text across all languages.

## What It Looks Like

A thick, semi-transparent colored underline covering the bottom ~45% of the text line — like a highlighter pen.

## Step 1: CSS Class

Add to your global CSS (e.g., `globals.css`). In Tailwind v4, wrap in `@layer utilities`:

```css
@layer utilities {
  .marker-highlight {
    background: linear-gradient(transparent 55%, rgba(232, 89, 12, 0.2) 55%);
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    padding: 0 4px;
    margin: 0 -4px;
  }
}
```

**Tuning:**
| Parameter | Effect | Range |
|-----------|--------|-------|
| `55%` in gradient | Highlight thickness | 40% (thick) — 70% (thin) |
| `0.2` opacity | Highlight intensity | 0.1 (subtle) — 0.3 (bold) |
| Color `232, 89, 12` | Highlight color | Match your accent color |

## Step 2: Apply to HTML

**Simple (no i18n):**
```html
<p>AI translates to <span class="marker-highlight">preserve your original layout</span>.</p>
```

**With i18n — `th()` helper:**

For multilingual sites, create a helper that parses `{{text}}` markers into highlighted spans:

```tsx
import { createElement, type ReactNode } from 'react'

export function th(key: string, lang: UILang): ReactNode {
  const raw = t(key, lang)  // your translation function
  const parts = raw.split(/(\{\{.+?\}\})/)
  if (parts.length === 1) return raw

  return parts.map((part, i) => {
    if (part.startsWith('{{') && part.endsWith('}}')) {
      return createElement('span', { key: i, className: 'marker-highlight' }, part.slice(2, -2))
    }
    return part
  })
}
```

Then in translation strings:
```
EN: 'AI translates to {{preserve your original layout}}.'
JA: 'AIが翻訳して{{レイアウトを忠実に再現}}します。'
ZH: '...以{{保留原始排版}}。'
KO: '...해 {{원본 레이아웃을 재현}}합니다.'
```

Usage: `<p>{th('hero.subtitle', lang)}</p>`

**With BudouX (CJK phrase-aware breaking):**

If your project uses BudouX, integrate segmentation into `th()`:

```tsx
const parser = parsers[lang as keyof typeof parsers]
const segment = (s: string) => parser ? parser.parse(s).join('\u200B') : s

// In the map callback:
return createElement('span', { key: i, className: 'marker-highlight' }, segment(inner))
```

Combine with `break-keep overflow-wrap-anywhere` on the parent element.

## Anti-patterns

| Pattern | Problem |
|---------|---------|
| `filter: url(#svg-filter)` on inline text | Distorts text characters, not just background |
| `::after` pseudo-element | Only covers bounding box, not per-line on wrap |
| SVG data URL with single quotes in Tailwind v4 | Rule silently dropped by parser |
| Missing `box-decoration-break: clone` | Multi-line text only highlights first line |
| Missing `@layer utilities {}` in Tailwind v4 | Custom class not compiled |
