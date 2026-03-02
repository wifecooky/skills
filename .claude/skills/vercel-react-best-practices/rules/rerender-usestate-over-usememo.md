---
title: Use useState Over useMemo When Correctness Requires Persistence
impact: MEDIUM
impactDescription: prevents broken behavior when React discards memoized values
tags: rerender, useMemo, useState, cache, correctness
source: https://shud.in/thoughts/build-bulletproof-react-components
---

## Use useState Over useMemo When Correctness Requires Persistence

`useMemo` is a performance hint, not a semantic guarantee. React may discard cached values during HMR, for offscreen components, or in future optimizations. If your component's correctness depends on a value being computed only when inputs change, use `useState` with a change check instead.

**Incorrect (breaks if React discards memo):**

```tsx
function ThemeProvider({ baseTheme, children }: Props) {
  // React may recompute this even if baseTheme hasn't changed
  const colors = useMemo(
    () => generateAccentColors(baseTheme),
    [baseTheme]
  )

  return <div style={colors}>{children}</div>
}
```

If `generateAccentColors` produces randomized accents, discarding the memo produces different colors each time - a visible bug.

**Correct (persists across React's internal cache evictions):**

```tsx
function ThemeProvider({ baseTheme, children }: Props) {
  const [colors, setColors] = useState(() =>
    generateAccentColors(baseTheme)
  )
  const [prevTheme, setPrevTheme] = useState(baseTheme)

  if (baseTheme !== prevTheme) {
    setPrevTheme(baseTheme)
    setColors(generateAccentColors(baseTheme))
  }

  return <div style={colors}>{children}</div>
}
```

`useState` values are never discarded by React unless the component unmounts. Use this pattern when:
- The computation produces non-deterministic results (random IDs, timestamps)
- The value is used as a key or identity that must remain stable
- Downstream code assumes referential stability between renders
