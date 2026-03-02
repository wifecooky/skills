---
title: Taint Sensitive Server Data to Prevent Client Leaks
impact: HIGH
impactDescription: prevents accidental exposure of secrets to client
tags: server, security, taint, data-leak, server-components
source: https://shud.in/thoughts/build-bulletproof-react-components
---

## Taint Sensitive Server Data to Prevent Client Leaks

Sensitive data (session tokens, API keys, internal IDs) from Server Components can accidentally leak to Client Components through props. Use `taintUniqueValue` or `taintObjectReference` to make React throw at build time if sensitive values cross the server-client boundary.

**Incorrect (token silently leaks to client):**

```tsx
// Server Component
async function Dashboard() {
  const user = await getUser()
  // user.token is a session secret
  return <UserThemeConfig user={user} />
}

// Client Component - token is now in the browser bundle
'use client'
function UserThemeConfig({ user }: { user: User }) {
  // user.token is exposed in client-side JavaScript
  return <div>{user.name}</div>
}
```

**Correct (React throws if token reaches client):**

```tsx
import { experimental_taintUniqueValue as taintUniqueValue } from 'react'

async function Dashboard() {
  const user = await getUser()

  taintUniqueValue(
    'Do not pass the user token to the client.',
    user,
    user.token
  )

  return <UserThemeConfig user={user} />
}
```

If `user.token` is accidentally serialized to a Client Component, React throws an error with the message you provided. This catches data leaks at development time rather than in production.

For entire objects:

```tsx
import { experimental_taintObjectReference as taintObjectReference } from 'react'

const config = await getServerConfig()
taintObjectReference('Server config must not be sent to client.', config)
```
