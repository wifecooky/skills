---
title: Use startTransition for View Transition Animations
impact: MEDIUM
impactDescription: enables smooth View Transition API animations
tags: rendering, transitions, view-transitions, animation
source: https://shud.in/thoughts/build-bulletproof-react-components
---

## Use startTransition for View Transition Animations

State updates that swap UI elements won't animate with the View Transition API unless wrapped in `startTransition`. Direct `setState` calls bypass the transition mechanism.

**Incorrect (no animation):**

```tsx
function ThemeSettings() {
  const [showAdvanced, setShowAdvanced] = useState(false)

  return (
    <>
      {showAdvanced ? <AdvancedPanel /> : <SimplePanel />}
      <button onClick={() => setShowAdvanced(!showAdvanced)}>
        {showAdvanced ? 'Simple' : 'Advanced'}
      </button>
    </>
  )
}
```

**Correct (enables View Transition animation):**

```tsx
import { startTransition } from 'react'

function ThemeSettings() {
  const [showAdvanced, setShowAdvanced] = useState(false)

  return (
    <>
      {showAdvanced ? <AdvancedPanel /> : <SimplePanel />}
      <button onClick={() =>
        startTransition(() => setShowAdvanced(!showAdvanced))
      }>
        {showAdvanced ? 'Simple' : 'Advanced'}
      </button>
    </>
  )
}
```

When the state update is wrapped in `startTransition`, React coordinates with the View Transition API to capture before/after snapshots and animate the DOM swap smoothly. This pattern applies to any UI swap: tab panels, accordions, page transitions, and layout changes.
