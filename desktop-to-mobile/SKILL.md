---
name: desktop-to-mobile
description: Convert desktop-first web UI to mobile-responsive UI. Systematic audit + CSS conversion following WCAG 2.2, Apple HIG, Material Design 3, and Google mobile-friendly standards.
user-invokable: true
args:
  - name: target
    description: Target CSS file path or page URL to audit (optional)
    required: false
---

# Desktop → Mobile UI Conversion

Systematically convert a desktop-first web UI to a fully responsive mobile UI. This skill follows established mobile web standards and produces CSS-only changes (no layout restructuring).

## Principles

1. **CSS-only** — Same HTML, same routes. Mobile styling via `@media (max-width: 768px)`.
2. **Desktop-safe** — Zero changes above 768px. `git diff` on desktop must show no visual difference.
3. **Standards-based** — Every decision references a concrete standard (WCAG, Apple HIG, Material Design 3).
4. **Progressive** — Fix critical issues first (broken layout, unreadable text), then polish (spacing, animation).

## Phase 1: Audit

### 1.1 Route Discovery

Find all pages in the project:

```bash
# Next.js App Router
find src/app -name "page.tsx" -o -name "page.jsx" | sort

# Next.js Pages Router
find src/pages -name "*.tsx" -o -name "*.jsx" | grep -v "_app\|_document\|_error" | sort

# Generic (look for route definitions)
grep -r "path:" src/routes/ 2>/dev/null || grep -r "Route " src/ --include="*.tsx" 2>/dev/null
```

### 1.2 Screenshot Capture

Use Playwright for automated full-page screenshots at mobile viewport:

```javascript
// Viewport: iPhone 14 (390x844)
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
});
```

Capture every route. For pages requiring auth, inject session cookies.

### 1.3 Visual Audit Checklist

For EACH screenshot, check every item. Do not skip any.

#### A. Layout & Viewport

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| A1 | No horizontal scroll | Content fits within 390px width | WCAG 1.4.10 Reflow |
| A2 | No content overflow | No text/elements clipped or hidden | Google Mobile-Friendly |
| A3 | Grid columns reduced | Max 2 columns on mobile (no 3+ col grids) | Material Design: 4-col mobile grid |
| A4 | Fixed-width containers | No `width: NNNpx` on containers | Responsive best practice |
| A5 | Images scale | All images fit viewport, no overflow | Basic responsive |
| A6 | Safe area respected | Bottom nav/fixed elements use `env(safe-area-inset-bottom)` | Apple HIG: Safe Areas |

#### B. Typography & Readability

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| B1 | Body text >= 16px | Minimum 1rem for body text | Google: readable without zoom |
| B2 | Input text >= 16px | Prevents iOS Safari auto-zoom on focus | Apple Safari behavior |
| B3 | Secondary text >= 12px | Absolute floor for any visible text | Industry practice |
| B4 | Line height >= 1.5 | Body text line-height: 1.5 or greater | WCAG 1.4.12 |
| B5 | Text contrast >= 4.5:1 | Normal text against background | WCAG 1.4.3 AA |
| B6 | Large text contrast >= 3:1 | Text >= 18pt or 14pt bold | WCAG 1.4.3 AA |
| B7 | No text truncation | Important content not cut off by `overflow: hidden` | Usability |
| B8 | No awkward line breaks | Words not split mid-word, titles not orphaned | Typography |

#### C. Touch Targets

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| C1 | Interactive elements >= 44x44px | Buttons, links, icons all meet minimum | Apple HIG (44pt), WCAG 2.5.5 AAA |
| C2 | Spacing between targets >= 8px | No adjacent targets touching | Material Design 3 |
| C3 | No overlapping targets | 24px-diameter circles don't intersect | WCAG 2.5.8 AA |
| C4 | Primary actions in thumb zone | Main CTAs in bottom 40% of screen | NNG: Thumb Zone research |

#### D. Navigation

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| D1 | Nav accessible on mobile | Bottom nav, hamburger, or tab bar present | Mobile UX pattern |
| D2 | Desktop nav hidden | Sidebar/horizontal nav hidden at 768px | Responsive pattern |
| D3 | Fixed elements don't obscure | Sticky header/footer don't cover content | Usability |
| D4 | Modals are dismissible | Can close via X, outside tap, or back | NNG: User control |
| D5 | Scroll position preserved | Back navigation restores scroll | UX best practice |

#### E. Components

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| E1 | Tables horizontally scrollable | Wide tables scroll independently, page doesn't | WCAG 1.4.10 exception |
| E2 | Forms stack vertically | Side-by-side inputs stack on mobile | Mobile form pattern |
| E3 | Dropdowns/selects usable | Full-width, adequate height | Touch target compliance |
| E4 | Cards readable | Card content not compressed to illegibility | Layout |
| E5 | Hover states have tap alternatives | No hover-only tooltips or dropdowns | Touch device requirement |

---

## Phase 2: CSS Conversion Patterns

### 2.1 Breakpoint Strategy

Use a single mobile breakpoint. Desktop-first approach (matches most existing codebases):

```css
/* All mobile overrides go here */
@media (max-width: 768px) {
  /* ... */
}
```

**Rule**: ONE media query block per CSS file. Consolidate all mobile rules together. Never scatter mobile rules across the file.

### 2.2 Grid → 2-Column or Stack

```css
/* Desktop: 3-4 column grid */
.grid-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}

/* Mobile: 2 columns or stack */
@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: repeat(2, 1fr);  /* 2-col for cards */
  }
  .form-grid {
    grid-template-columns: 1fr;  /* Stack for forms */
  }
}
```

### 2.3 Flex Row → Column

```css
@media (max-width: 768px) {
  .flex-row-container {
    flex-direction: column;
  }
  .flex-row-container > * {
    width: 100%;  /* Children take full width */
  }
}
```

### 2.4 Sidebar → Hidden or Drawer

```css
@media (max-width: 768px) {
  .sidebar {
    display: none;  /* or: position: fixed; transform: translateX(-100%); */
  }
  .main-content {
    width: 100%;
    margin-left: 0;
  }
}
```

### 2.5 Tables → Horizontal Scroll

```css
@media (max-width: 768px) {
  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .table-wrapper table {
    min-width: 600px;  /* Preserve table structure */
  }
}
```

### 2.6 Touch Target Sizing

```css
@media (max-width: 768px) {
  button, a.btn, .interactive {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 16px;
  }
}
```

### 2.7 Typography Scaling

```css
@media (max-width: 768px) {
  h1 { font-size: 1.5rem; }    /* 24px */
  h2 { font-size: 1.25rem; }   /* 20px */
  h3 { font-size: 1.125rem; }  /* 18px */
  body, p { font-size: 1rem; } /* 16px — never smaller */
  .caption { font-size: 0.875rem; } /* 14px */
  /* 12px is the absolute floor — use only for tertiary labels */
}
```

### 2.8 Spacing Reduction

```css
@media (max-width: 768px) {
  .container {
    padding-left: 16px;
    padding-right: 16px;  /* Material Design: 16dp margins */
  }
  .section {
    padding-top: 24px;
    padding-bottom: 24px;
    gap: 12px;  /* Tighter gaps */
  }
}
```

### 2.9 Fixed Bottom Elements (iOS Safe Area)

```css
@media (max-width: 768px) {
  .bottom-nav, .fixed-bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding-bottom: env(safe-area-inset-bottom);
    z-index: 1000;
  }
  /* Prevent content from hiding behind fixed bottom */
  body {
    padding-bottom: calc(56px + env(safe-area-inset-bottom));
  }
}
```

### 2.10 Hover → Active State

```css
@media (max-width: 768px) {
  .card:hover {
    transform: none;  /* Disable hover lift on touch */
    box-shadow: inherit;
  }
  .card:active {
    opacity: 0.85;  /* Use active state instead */
  }
}
```

### 2.11 Toast / Notification on Mobile

```css
@media (max-width: 768px) {
  .toast {
    /* Move from top-right to bottom, above bottom nav */
    top: auto;
    right: 0;
    bottom: calc(56px + env(safe-area-inset-bottom) + 12px);
    left: 0;
    width: calc(100% - 32px);
    margin: 0 auto;
  }
}
```

---

## Phase 3: Systematic Execution

### 3.1 Priority Order

Fix pages in this order (most impactful first):

1. **Global layout** — Bottom nav, header, footer, body padding
2. **High-traffic pages** — Home, product list, product detail, cart
3. **Auth pages** — Login, registration
4. **Secondary pages** — Orders, notifications, settings, profile
5. **Utility pages** — Search results, brand list, tools

### 3.2 Per-Page Workflow

For each page:

1. **Screenshot** at 390x844 viewport
2. **Audit** against the checklist (Phase 1.3)
3. **List issues** with severity: CRITICAL (broken) / MAJOR (hard to use) / MINOR (polish)
4. **Write CSS** — All rules inside the single `@media (max-width: 768px)` block
5. **Re-screenshot** to verify fix
6. **Verify desktop** — Confirm no regression at 1440px width

### 3.3 CSS Audit Before Writing

Before adding ANY mobile CSS, audit what already exists:

```bash
# Find existing mobile breakpoints
grep -n "max-width.*768" src/**/*.css

# Find potential overflow-causing fixed widths
grep -n "width:\s*[0-9]\+px" src/**/*.css | grep -v "max-width\|min-width"

# Find grids that need mobile breakpoints
grep -n "repeat([3-9]" src/**/*.css

# Find hover-dependent interactions
grep -n ":hover" src/**/*.css
```

### 3.4 Validation

After all pages are converted:

1. **Full screenshot audit** — All pages at 390x844
2. **Desktop regression check** — All pages at 1440x900
3. **Interaction testing** — Search, forms, modals, navigation
4. **Real device test** — iOS Safari + Android Chrome (if available)

---

## Quick Reference: Standards Summary

| Standard | Touch Target | Body Text | Contrast |
|----------|-------------|-----------|----------|
| WCAG 2.2 AA | >= 24x24px (floor) | Scalable units | >= 4.5:1 |
| WCAG 2.1 AAA | >= 44x44px | Resize to 200% | >= 7:1 |
| Apple HIG | >= 44x44pt | System font | Platform default |
| Material Design 3 | >= 48x48dp | >= 14sp | >= 4.5:1 |
| Google Mobile-Friendly | >= 48x48px | >= 16px | — |
| NNG Research | >= 1cm x 1cm (~38px) | — | — |

**Working target**: 44x44px touch targets, 16px body text, 4.5:1 contrast.

| Viewport | Use |
|----------|-----|
| 320px | WCAG 1.4.10 reflow test (minimum) |
| 375px | iPhone SE (smallest common device) |
| 390px | iPhone 14 (primary test device) |
| 414px | iPhone Plus / large Android |
| 768px | Breakpoint threshold (iPad portrait) |

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| `user-scalable=no` | Blocks zoom; accessibility violation | Remove it |
| `input { font-size: 14px }` | iOS Safari auto-zooms on focus | Use `font-size: 16px` or `1rem` |
| `100vh` for full height | iOS Safari: includes area behind browser chrome | Use `100dvh` |
| Hover-only tooltips | No hover on touch devices | Add tap/click alternative |
| `position: fixed` without safe area | Content hidden behind iPhone notch/home bar | Add `env(safe-area-inset-*)` |
| 3+ column grid without breakpoint | Columns too narrow at 390px | Add `repeat(2, 1fr)` at 768px |
| `transform: translateY()` on hover | Meaningless on touch; causes visual glitch | Disable in mobile media query |
