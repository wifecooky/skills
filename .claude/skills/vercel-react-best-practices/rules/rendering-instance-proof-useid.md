---
title: Use useId() for Instance-Safe DOM IDs
impact: MEDIUM
impactDescription: prevents ID collisions with multiple instances
tags: rendering, ssr, hydration, useId, instances
source: https://shud.in/thoughts/build-bulletproof-react-components
---

## Use useId() for Instance-Safe DOM IDs

Never hardcode DOM IDs in reusable components. Multiple instances on the same page will collide. Use `useId()` to generate stable, unique identifiers per instance that are consistent between server and client.

**Incorrect (ID collision with multiple instances):**

```tsx
function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <div id="theme-wrapper">{children}</div>
  )
}

// Two instances on the same page - both target the same ID
<ThemeProvider><Header /></ThemeProvider>
<ThemeProvider><Sidebar /></ThemeProvider>
```

**Correct (unique ID per instance):**

```tsx
function ThemeProvider({ children }: { children: ReactNode }) {
  const id = useId()
  return (
    <div id={id}>{children}</div>
  )
}
```

`useId()` generates the same ID on server and client, avoiding hydration mismatches while ensuring each instance gets a unique ID. This is critical for inline scripts, `aria-labelledby`, `htmlFor`, and any DOM targeting that references element IDs.
