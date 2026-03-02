---
title: Use Activity Component for Show/Hide
impact: MEDIUM
impactDescription: preserves state/DOM
tags: rendering, activity, visibility, state-preservation
---

## Use Activity Component for Show/Hide

Use React's `<Activity>` to preserve state/DOM for expensive components that frequently toggle visibility.

**Usage:**

```tsx
import { Activity } from 'react'

function Dropdown({ isOpen }: Props) {
  return (
    <Activity mode={isOpen ? 'visible' : 'hidden'}>
      <ExpensiveMenu />
    </Activity>
  )
}
```

Avoids expensive re-renders and state loss.

**Caveat: Global styles leak when hidden.** `<Activity mode="hidden">` preserves DOM including `<style>` tags, which still apply globally. Use `useLayoutEffect` to toggle the style's media query:

```tsx
function DarkTheme({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLStyleElement>(null)

  useLayoutEffect(() => {
    if (!ref.current) return
    ref.current.media = 'all'
    return () => { ref.current!.media = 'not all' }
  }, [])

  return (
    <>
      <style ref={ref} media="not all">{`
        :root { --bg: #000; --fg: #fff; }
      `}</style>
      {children}
    </>
  )
}
```

When Activity hides the component, `useLayoutEffect` cleanup sets `media="not all"`, disabling the style rule without removing the DOM element.

Source: https://shud.in/thoughts/build-bulletproof-react-components
