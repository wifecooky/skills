---
name: desktop-to-mobile
description: Convert desktop-first web UI to mobile-responsive UI. Three-layer audit (static analysis → screenshots → checklist) + CSS conversion following WCAG 2.2, Apple HIG, Material Design 3 standards.
user-invokable: true
args:
  - name: target
    description: Target CSS file path or page URL to audit (optional)
    required: false
---

# Desktop → Mobile UI Conversion

Systematically convert a desktop-first web UI to a fully responsive mobile UI.

## Principles

1. **CSS-only where possible** — Same HTML, same routes. Mobile styling via `@media (max-width: 768px)`. If a component addition is needed (e.g., bottom nav), flag it explicitly.
2. **Desktop-safe** — Zero changes above 768px. Desktop must show no visual difference.
3. **Standards-based** — Every decision references a concrete standard (WCAG, Apple HIG, Material Design 3).
4. **Machine first, eyes second** — Static analysis catches structural issues mechanically. Screenshots catch contextual issues visually. Never rely on screenshots alone.

---

## Phase 1: Audit (Three Layers)

Audit in this EXACT order. Do not skip layers.

### Layer 1: Static CSS Analysis (grep-based, no rendering needed)

Run ALL of these. Each grep pattern catches a specific class of mobile issues.

```bash
# === CRITICAL: Layout breakers ===

# 1. Grids with 3+ columns (need 2-col breakpoint)
grep -rn "repeat([3-9]" src/**/*.css

# 2. Fixed widths that overflow 390px viewport
grep -rn "width:\s*[0-9]\+px" src/**/*.css | grep -v "max-width\|min-width\|border-width\|outline-width"

# 3. min-width values that force overflow
grep -rn "min-width:\s*[2-9][0-9][0-9]px\|min-width:\s*[0-9]\{4,\}px" src/**/*.css

# === MAJOR: Interaction issues ===

# 4. Hover-dependent transforms (meaningless on touch)
grep -rn "hover" src/**/*.css | grep "translateY\|translateX\|scale"

# 5. Hover-only visual changes (may need tap alternatives)
grep -c ":hover" src/**/*.css

# === TABLET: Intermediate breakpoint issues ===

# 6. Nav/tab bars with large padding (wrap at iPad width)
grep -rn "nav-links\|\.tabs\|\.tab-bar" src/**/*.css | grep "padding"

# === CJK: Japanese/Chinese text wrapping ===

# 7. CJK label wrapping risk: min-width: 0 allows flex children to shrink below content
#    CJK text breaks at EVERY character (unlike English word-based breaks).
#    Any flex container with min-width: 0 ancestry + small labels = will break mid-word.
grep -rn "min-width:\s*0" src/**/*.css

# === MODERATE: Typography & flex issues ===

# 8. Flex rows that may need column direction on mobile
grep -rn "display:\s*flex" src/**/*.css | head -30

# 9. Desktop-only elements that should be hidden
grep -rn "breadcrumb\|\.footer\|\.sidebar\|\.desktop-only\|\.search-bar" src/**/*.css

# === VERIFICATION: Existing mobile support ===

# 10. Count existing 768px breakpoints
grep -rn "max-width.*768" src/**/*.css

# 11. Count existing 1024px breakpoints (tablet)
grep -rn "max-width.*1024" src/**/*.css
```

**Cross-reference results**: For each `repeat(3+)` grid found in step 1, check if the same selector appears in a `@media (max-width: 768px)` block. Report only UNPROTECTED grids.

### Layer 2: Screenshot Capture

After static analysis, take full-page screenshots at mobile viewport:

```javascript
// Viewport: iPhone 14 (390x844)
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
});
```

Capture every route discovered in Route Discovery. For auth-required pages, inject session cookies.

### Layer 3: Visual Checklist (per screenshot)

For EACH screenshot, check every item. Mark PASS/FAIL explicitly.

#### A. Layout & Viewport

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| A1 | No horizontal scroll | Content fits within 390px | WCAG 1.4.10 |
| A2 | No content overflow | No clipped or hidden elements | Google Mobile-Friendly |
| A3 | Grids max 2 columns | No 3+ col grids visible | Material Design |
| A4 | No fixed-width overflow | No elements wider than viewport | Responsive |
| A5 | Images scale properly | All images fit viewport | Basic responsive |
| A6 | Safe area respected | Fixed bottom elements clear home bar | Apple HIG |

#### B. Typography & Readability

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| B1 | Body text >= 16px | Minimum 1rem | Google Mobile-Friendly |
| B2 | Input text >= 16px | No iOS auto-zoom on focus | Apple Safari |
| B3 | No mid-word breaks | Titles/labels don't split mid-word | Typography |
| B4 | No orphaned text | Section titles stay on one line | Typography |
| B5 | Text contrast >= 4.5:1 | Normal text against background | WCAG 1.4.3 AA |
| B6 | Flex containers don't compress text | Text in flex rows remains readable | Layout |
| B7 | CJK labels don't break mid-character | Short labels (締切, 出荷) stay on one line | CJK Typography |

#### C. Touch Targets

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| C1 | Buttons >= 44x44px | All interactive elements meet minimum | Apple HIG |
| C2 | Spacing >= 8px between targets | No adjacent targets touching | Material Design 3 |
| C3 | +/- quantity buttons adequate | Not compressed by flex shrink | Usability |
| C4 | Primary actions in thumb zone | Main CTAs in bottom 40% | NNG Research |

#### D. Navigation & Chrome

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| D1 | Mobile nav exists | Bottom nav, hamburger, or tab bar | Mobile UX |
| D2 | Desktop elements hidden | Search bar, breadcrumb, sidebar, footer hidden | Responsive |
| D3 | Fixed elements don't obscure | Sticky header/footer don't cover content | Usability |
| D4 | Toolbar adapts | Multi-filter toolbars stack or scroll | Mobile UX |

#### E. Components

| # | Check | Pass Criteria | Standard |
|---|-------|---------------|----------|
| E1 | Tables scroll horizontally | Wide tables scroll independently | WCAG 1.4.10 |
| E2 | Forms stack vertically | Side-by-side inputs become full-width | Mobile form |
| E3 | Cards are readable | No illegible compressed cards | Layout |
| E4 | Images centered | Product/hero images centered in viewport | Layout |
| E5 | Toast/alerts positioned for mobile | Not obscured by bottom nav | Usability |

---

## Phase 2: CSS Conversion Patterns

### 2.1 Breakpoint Strategy

```css
@media (max-width: 1024px) {
  /* Tablet overrides (iPad portrait) — nav, grid 4→3 col */
}

@media (max-width: 768px) {
  /* Mobile overrides — grid 2 col, stack, hide desktop elements */
}
```

**Rule**: Two breakpoints maximum. 1024px for tablet-specific issues (nav overflow, 4→3 col grids). 768px for all mobile overrides.

### 2.2 Grid → 2-Column or Stack

```css
@media (max-width: 768px) {
  .card-grid   { grid-template-columns: repeat(2, 1fr); }
  .form-grid   { grid-template-columns: 1fr; }
  .stats-grid  { grid-template-columns: repeat(2, 1fr); }
}
```

**Decision rule**: Cards/products → 2-col. Forms/text-heavy → 1-col. Stats/KPIs → 2-col.

### 2.3 Flex Row → Column (with text wrap protection)

```css
@media (max-width: 768px) {
  .header-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-row > * {
    width: 100%;
    min-width: unset;  /* Remove desktop min-width constraints */
  }
}
```

**Critical**: Also add `flex-wrap: wrap` and `white-space: nowrap` on section titles to prevent mid-word breaks:

```css
@media (max-width: 768px) {
  .section-header {
    flex-wrap: wrap;
    gap: 8px;
  }
  .section-title {
    white-space: nowrap;
  }
}
```

### 2.4 Desktop Elements → Hidden

```css
@media (max-width: 768px) {
  .breadcrumb,
  .desktop-search-bar,
  .sidebar,
  .footer {
    display: none;
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
}
```

### 2.6 Touch Target Sizing

```css
@media (max-width: 768px) {
  .btn, .icon-btn {
    min-height: 44px;
    min-width: 44px;
  }
  /* Quantity buttons: prevent flex compression */
  .qty-btn {
    width: 44px;
    height: 48px;
    flex-shrink: 0;
  }
}
```

### 2.7 Hover → Disabled on Touch

```css
@media (max-width: 768px) {
  .card:hover,
  .btn:hover {
    transform: none;
  }
}
```

### 2.8 Toolbar → Vertical Stack

```css
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 12px;
  }
  .toolbar-filters {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    width: 100%;
  }
  .toolbar-actions {
    overflow-x: auto;
    white-space: nowrap;
  }
}
```

### 2.9 Fixed Bottom Elements (iOS Safe Area)

```css
@media (max-width: 768px) {
  .bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding-bottom: env(safe-area-inset-bottom);
    z-index: 1000;
  }
  body {
    padding-bottom: calc(56px + env(safe-area-inset-bottom));
  }
}
```

### 2.10 Image Centering

```css
@media (max-width: 768px) {
  .product-image,
  .hero-image {
    display: block;
    margin: 0 auto;
  }
}
```

### 2.11 Toast → Bottom Position

```css
@media (max-width: 768px) {
  .toast {
    top: auto;
    bottom: calc(56px + env(safe-area-inset-bottom) + 12px);
    left: 16px;
    right: 16px;
    width: auto;
  }
}
```

### 2.12 Cart/Action Row → Two-Line Layout

When a row has quantity controls + action button and compresses too much:

```css
@media (max-width: 768px) {
  .action-row {
    flex-wrap: wrap;
  }
  .action-row .primary-btn {
    flex: 1 0 100%;
    order: 3;
  }
}
```

### 2.13 CJK Label Wrapping Protection

CJK text (Japanese/Chinese) breaks at EVERY character boundary, unlike English which breaks at word boundaries. When a flex container with `min-width: 0` ancestry shrinks, short CJK labels like "締切" (2 chars) split across lines.

```css
/* Prevent CJK label/date rows from breaking mid-character */
.date-row,
.label-row,
.hero-alert-item-dates {
  white-space: nowrap;
}
```

**Why this happens**: `min-width: 0` on flex parents allows shrinking below intrinsic content width. English "Deadline" stays on one line (word-based break), but Japanese "締切" splits into "締" / "切" (character-based break). `white-space: nowrap` prevents this regardless of container width.

**Where to check**: Every flex container with `min-width: 0` in its ancestry chain that contains CJK text labels. Especially date labels, status labels, and short metadata strings.

### 2.14 Nav/Tab Bar → Tablet Padding Reduction (1024px)

Horizontal nav with 5+ items overflows on iPad (768–1024px). Text wraps to 2 lines.

```css
@media (max-width: 1024px) {
  .nav-links a {
    padding: 10px 12px;    /* from 12px 20px */
    font-size: 13px;       /* from 14px */
    gap: 6px;              /* from 8px */
    white-space: nowrap;
  }
}
```

**Detection**: `grep -rn "nav-links\|\.tabs" *.css | grep "padding.*[1-9][0-9]px"` — padding ≥ 16px on nav items with 5+ siblings = will overflow at iPad width.

### 2.15 Fixed Bottom Elements → Clear Bottom Nav

When a bottom nav exists, fixed elements (`position: fixed; bottom: 0`) must be raised above it.

```css
@media (max-width: 768px) {
  .chatbot-button {
    bottom: calc(64px + env(safe-area-inset-bottom));
  }
  .sticky-action-bar,
  .floating-purchase-bar {
    bottom: calc(56px + env(safe-area-inset-bottom));
  }
}
```

**Detection**: `grep -rn "position.*fixed" *.css | grep "bottom.*0"` — any `fixed; bottom: 0` that isn't the bottom nav itself.

---

## Phase 3: Execution

### 3.1 Priority Order

1. **Global layout** — Desktop elements hidden, body padding, safe area
2. **High-traffic pages** — Home, product list, product detail, cart
3. **Auth pages** — Login, registration
4. **Secondary pages** — Orders, notifications, dashboard
5. **Utility pages** — Brands, tools, settings

### 3.2 Per-Page Workflow

1. **Static analysis** — grep for issues in this page's CSS selectors
2. **Screenshot** at 390x844
3. **Checklist** — Every item in Layer 3, marked PASS/FAIL
4. **Write CSS** — Inside the consolidated `@media` block
5. **Re-screenshot** — Verify fix
6. **Desktop check** — Confirm zero regression at 1440px

### 3.3 Scope Boundary

This skill covers **CSS-only responsive changes**. If the audit reveals needs beyond CSS:

| Need | Action |
|------|--------|
| Bottom navigation component | Flag: "Component addition required — outside CSS-only scope" |
| Search overlay for mobile | Flag: "Component addition required" |
| Route restructuring | Flag: "Route change required" |
| Server-side data changes | Flag: "Backend change required" |

Do not attempt these within this skill. Report them as separate tasks.

---

## Quick Reference

| Standard | Touch Target | Body Text | Contrast |
|----------|-------------|-----------|----------|
| WCAG 2.2 AA | >= 24px (floor) | Scalable | >= 4.5:1 |
| Apple HIG | >= 44pt | System font | Platform |
| Material Design 3 | >= 48dp | >= 14sp | >= 4.5:1 |
| Google Mobile-Friendly | >= 48px | >= 16px | — |

| Viewport | Device |
|----------|--------|
| 320px | WCAG reflow minimum |
| 375px | iPhone SE |
| 390px | iPhone 14 (primary test) |
| 768px | Mobile breakpoint threshold |
| 820px | iPad Air (tablet test) |
| 1024px | Tablet breakpoint threshold |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `user-scalable=no` | Remove (blocks accessibility zoom) |
| `input { font-size: 14px }` | Use 16px (prevents iOS auto-zoom) |
| `100vh` | Use `100dvh` (iOS Safari chrome overlap) |
| `position: fixed` without safe area | Add `env(safe-area-inset-*)` |
| 3+ col grid without breakpoint | Add `repeat(2, 1fr)` at 768px |
| `transform: translateY()` on hover | Disable in mobile media query |
| Flex row without `flex-wrap` | Add `flex-wrap: wrap` for titles |
| `min-width` on flex children | Add `min-width: unset` on mobile |
| Toolbar in single row | Stack with `flex-direction: column` |
| Nav padding too wide for iPad | Reduce padding + `white-space: nowrap` at 1024px |
| Fixed elements behind bottom nav | Raise `bottom` by nav height + safe area |
| No 1024px breakpoint | Add for nav/tab bars and 4→3 col grids |
| CJK labels break mid-character | Add `white-space: nowrap` to label/date rows |
| `min-width: 0` + CJK text | Flex shrink causes char-by-char line breaks |
