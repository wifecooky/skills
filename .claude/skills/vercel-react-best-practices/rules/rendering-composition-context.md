---
title: Use Context Over cloneElement for Composition
impact: MEDIUM
impactDescription: works with Server Components, lazy, and portals
tags: rendering, composition, context, cloneElement, server-components
source: https://shud.in/thoughts/build-bulletproof-react-components
---

## Use Context Over cloneElement for Composition

`React.cloneElement` breaks with Server Components, lazy-loaded components, Suspense boundaries, and opaque component references. Use Context API for cross-component communication instead.

**Incorrect (breaks with Server Components and lazy):**

```tsx
function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')

  return React.Children.map(children, child =>
    React.isValidElement(child)
      ? React.cloneElement(child, { theme })
      : child
  )
}
```

This fails silently when children are Server Components, `React.lazy()` wrappers, Suspense boundaries, or Fragments.

**Correct (works everywhere):**

```tsx
const ThemeContext = createContext<string>('light')

function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  )
}

// Any descendant can consume, regardless of how it's rendered
function ThemedButton() {
  const theme = useContext(ThemeContext)
  return <button className={theme}>Click</button>
}
```

Context works through Server Components, lazy boundaries, portals, and Suspense without any assumptions about children structure.
