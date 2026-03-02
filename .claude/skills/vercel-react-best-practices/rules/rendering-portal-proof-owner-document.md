---
title: Use ownerDocument for Portal-Safe Event Listeners
impact: MEDIUM
impactDescription: ensures correct window context in portals and iframes
tags: rendering, portal, iframe, events, ownerDocument
source: https://shud.in/thoughts/build-bulletproof-react-components
---

## Use ownerDocument for Portal-Safe Event Listeners

Event listeners attached to `window` directly break when components render inside portals, iframes, or pop-out windows. Use `ownerDocument.defaultView` to resolve the correct window for the component's actual DOM location.

**Incorrect (breaks in portals/iframes):**

```tsx
function KeyboardShortcut({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    const toggle = (e: KeyboardEvent) => {
      if (e.metaKey && e.key === 'd') {
        e.preventDefault()
        setTheme(t => t === 'dark' ? 'light' : 'dark')
      }
    }
    // Always attaches to the top-level window
    window.addEventListener('keydown', toggle)
    return () => window.removeEventListener('keydown', toggle)
  }, [])

  return <div className={theme}>{children}</div>
}
```

**Correct (works in any rendering context):**

```tsx
function KeyboardShortcut({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const win = ref.current?.ownerDocument.defaultView || window
    const toggle = (e: KeyboardEvent) => {
      if (e.metaKey && e.key === 'd') {
        e.preventDefault()
        setTheme(t => t === 'dark' ? 'light' : 'dark')
      }
    }
    win.addEventListener('keydown', toggle)
    return () => win.removeEventListener('keydown', toggle)
  }, [])

  return <div ref={ref} className={theme}>{children}</div>
}
```

`ref.current.ownerDocument.defaultView` resolves to the correct `window` whether the component is in the main document, a portal, an iframe, or a pop-out window.
