---
name: cjk-typography
description: Use when building web pages with Chinese, Japanese, or Korean text. Prevents broken word wrapping, mid-word line breaks, and poor CJK text layout. Includes Pretext for reflow-free text measurement.
---

# CJK Typography

Proper line breaking, text layout, and reflow-free measurement for Chinese, Japanese, and Korean web content.

## When to Use

- Page contains CJK text (Chinese/Japanese/Korean)
- Text wraps mid-word or breaks phrases awkwardly
- Mixed CJK + Latin text has poor line breaks
- Mobile viewport causes ugly text reflow
- Need text height measurement without DOM reflow (virtualization, masonry, canvas)
- Rendering text to Canvas/SVG with proper line breaking

## Step 1: CSS Baseline

Always add to `body` or root container:

```css
body {
  word-break: keep-all;      /* never break inside CJK word clusters */
  overflow-wrap: break-word;  /* allow break at word boundaries to prevent overflow */
}
```

| Property | Effect |
|----------|--------|
| `word-break: keep-all` | Keeps CJK phrases intact, no mid-cluster breaks |
| `overflow-wrap: break-word` | Fallback for long strings that would overflow |

## Step 2: BudouX (Smart Phrase Breaking)

[Google BudouX](https://github.com/nicekid1/BudouX) inserts `<wbr>` tags at semantically correct break points. The browser only wraps at these positions.

### CDN Integration (Static Sites)

```html
<!-- Simplified Chinese -->
<script src="https://unpkg.com/budoux/bundle/budoux-zh_hans.min.js"></script>
<script>
var parser = new budoux.ZhHansParser();
document.querySelectorAll('p, h1, h2, h3, blockquote').forEach(function(el) {
  parser.applyElement(el);
});
</script>
```

### Available Parsers

| Language | Bundle | Parser Class |
|----------|--------|-------------|
| Simplified Chinese | `budoux-zh_hans.min.js` | `ZhHansParser` |
| Traditional Chinese | `budoux-zh_hant.min.js` | `ZhHantParser` |
| Japanese | `budoux-ja.min.js` | `JaParser` |
| Thai | `budoux-th.min.js` | `ThParser` |

### NPM / React Integration

```bash
npm install budoux
```

```tsx
import { loadDefaultSimplifiedChineseParser } from 'budoux';

const parser = loadDefaultSimplifiedChineseParser();

function CJKText({ children }: { children: string }) {
  const html = parser.translateHTMLString(children);
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
```

## Step 3: Pretext (Reflow-Free Text Measurement & Layout)

[Pretext](https://github.com/chenglou/pretext) — pure JS text measurement without triggering browser reflow. Supports all languages, emojis, mixed bidi text. Renders to DOM, Canvas, or SVG.

```bash
npm install @chenglou/pretext
```

### Quick Height Measurement (No DOM)

```ts
import { prepare, layout } from '@chenglou/pretext'

const prepared = prepare('AGI 春天到了. بدأت الرحلة 🚀', '16px Inter')
const { height, lineCount } = layout(prepared, maxWidth, 20) // pure arithmetic, no reflow
```

`prepare()` — one-time analysis + measurement (~19ms for 500 texts). `layout()` — fast arithmetic hot path (~0.09ms).

### Pre-wrap Mode (Textarea-like)

```ts
const prepared = prepare(text, '16px Inter', { whiteSpace: 'pre-wrap' })
const { height } = layout(prepared, containerWidth, 20)
```

### Manual Line Layout (Canvas / SVG)

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments('AGI 春天到了', '18px "Helvetica Neue"')
const { lines } = layoutWithLines(prepared, 320, 26)
for (let i = 0; i < lines.length; i++) ctx.fillText(lines[i].text, 0, i * 26)
```

### Shrink-Wrap (Tightest Container Width)

```ts
import { walkLineRanges } from '@chenglou/pretext'

let maxW = 0
walkLineRanges(prepared, 320, line => { if (line.width > maxW) maxW = line.width })
// maxW = tightest container width that still fits the text
```

### Variable-Width Lines (Float Around Images)

```ts
import { layoutNextLine } from '@chenglou/pretext'

let cursor = { segmentIndex: 0, graphemeIndex: 0 }
let y = 0
while (true) {
  const width = y < image.bottom ? columnWidth - image.width : columnWidth
  const line = layoutNextLine(prepared, cursor, width)
  if (line === null) break
  ctx.fillText(line.text, 0, y)
  cursor = line.end
  y += 26
}
```

### API Reference

| Function | Purpose |
|----------|---------|
| `prepare(text, font, opts?)` | One-time analysis, returns opaque handle for `layout()` |
| `layout(prepared, maxWidth, lineHeight)` | Returns `{ height, lineCount }` — pure arithmetic |
| `prepareWithSegments(text, font, opts?)` | Like `prepare()` but returns richer structure for line APIs |
| `layoutWithLines(prepared, maxWidth, lineHeight)` | Returns `{ height, lineCount, lines }` at fixed width |
| `walkLineRanges(prepared, maxWidth, onLine)` | Calls `onLine` per line with width + cursors (no string allocation) |
| `layoutNextLine(prepared, cursor, maxWidth)` | Iterator: one line at a time, variable width per line |
| `clearCache()` | Release internal caches (many fonts/text variants) |
| `setLocale(locale?)` | Set measurement locale for future `prepare()` calls |

### Pretext Caveats

- Targets: `word-break: normal`, `overflow-wrap: break-word`, `line-break: auto`
- `system-ui` font is inaccurate on macOS — use named fonts
- `font` parameter must match your CSS font shorthand (size, weight, style, family)
- `lineHeight` parameter must match your CSS `line-height`

### When to Use Pretext vs CSS

| Scenario | Use |
|----------|-----|
| Standard DOM text rendering | CSS baseline + BudouX |
| Virtualized lists / infinite scroll | Pretext `layout()` for height |
| Canvas / SVG text rendering | Pretext `layoutWithLines()` |
| Masonry / custom JS layouts | Pretext `walkLineRanges()` |
| Text around floated elements (canvas) | Pretext `layoutNextLine()` |
| Prevent layout shift on text load | Pretext `layout()` to pre-calculate |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `word-break: break-all` | Use `keep-all` — `break-all` breaks everywhere |
| Applying BudouX to containers with child elements | Apply to leaf text elements only |
| Missing `overflow-wrap` fallback | Always pair `keep-all` with `overflow-wrap: break-word` |
| Loading wrong language bundle | Match bundle to page content language |
| Using `system-ui` with Pretext on macOS | Use named fonts like `Inter`, `Helvetica Neue` |
| Calling `layout()` with mismatched font/lineHeight | Must match CSS declarations exactly |
