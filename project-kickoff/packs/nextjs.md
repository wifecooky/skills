# Next.js pack (App Router)

Every rule here comes from jam-bo's fix history: 498 fix commits, 2026-01 to 08.

**Status:** no rule is scripted yet. The first Next.js project (yuanzhuo) writes each rule. It then proves each rule against the jam-bo commit in the Evidence column:
- the parent of the fix must fail;
- the fix must pass.

Read jam-bo only, never change it: no checkout, no branch, no config, no worktree. Export the old code with:

```sh
git -C ~/Documents/git/jam-bo archive <sha>^ frontend | tar -x -C <scratch>/before
git -C ~/Documents/git/jam-bo archive <sha> frontend | tar -x -C <scratch>/after
```

Put each rule in ESLint (`no-restricted-syntax`, `no-restricted-imports`) when it can live there. Otherwise put it in `scripts/check-rules.mjs`. Either way, `scripts/gate.sh` runs it.

## Day 1: before the first feature

| Rule | Check | Evidence (jam-bo) |
|---|---|---|
| The gate runs locally and in CI, on every push to main | `gate.sh` self-check; `gate.yml` on `push`; kickoff-gate hook | 36912c3: a rename left `prepare` pointing at `src/.husky`; pre-commit dead 5 months, ~25 lint errors on main; CI linted PRs only, and 245 commits went straight to main |
| Every class used in TSX compiles to CSS | Build the CSS; diff the class tokens in `className` against the selectors in the output | #88: Tailwind v4 never loaded `tailwind.config.ts` (no `@config`), so `brand-*` was never generated; a submit button was white on white |
| Colors only from tokens | No hex or `rgb(` outside the token file (`:root` / `@theme`) | 1207 hex literals in CSS; ~70 「统一颜色」 fixes (35586ec, 29e65a0) |
| Breakpoints and z-index only from a fixed set | stylelint: media queries match the token breakpoints; z-index is one of the tokens | 11 breakpoints (480/640/768/769/960/1023/1024/1025…) against a documented 3; z-index 0–100000; ~110 overlap fixes |
| A selector is defined in one CSS file | Script: no top-level class in more than one file | `.analysis-grid` twice (7815bcc); 60 classes in both `components.css` and `pages.css` |
| No transition on a pixel `max-height` | stylelint | 64ce5af: `max-height: 1000px` cut the last items off |
| Dates format only in `lib/date.ts`, always with `timeZone` | Lint: `toLocale*String` and `Intl.DateTimeFormat` are banned elsewhere; ban `new Date('YYYY-MM-DD')`; run tests under `TZ=UTC` and `TZ=Asia/Tokyo` | 5c846ba and 9654e5b (same day, two tries); 9 calls without `timeZone`, rendered on a UTC server |
| No `redirect()` or `notFound()` inside `try` | Lint (AST: a call inside a `TryStatement` block) | f0b41f2: the `catch` swallowed the redirect |
| Every env name used in code is in `.env.example` and in the deploy's required list | Script: diff the `process.env.X` names | 21 names missing (`SHOPIFY_SECRET_TOKEN`, `LARK_*_TABLE_ID`…); 7e83537, 3be68b0 |
| A page that fetches data declares `dynamic` or `revalidate` | Script over `app/**/page.tsx` | c42adbd, 79e8b81: empty build-time data was cached |
| Outside APIs only through one wrapper with a fallback | Lint: SDK imports allowed only in `lib/<service>.ts`; the wrapper returns the fallback on error | a9f325f: a Lark 500 crashed SSR |
| URLs only from a helper that encodes | Lint: ban template literals that start with a route prefix (`` `/products/${…}` ``) outside the helper; `[param]` pages decode through the helper | 85ed23d (an unencoded GID), 61ce46e (an undecoded Japanese handle); 18 raw templates left |
| No PII in logs | Lint: ban logging `email` or raw response bodies | 97b9062 |

## Safe by default: data that must not leak

| Rule | Check | Evidence |
|---|---|---|
| Sensitive values reach the UI only as a masked type; showing the raw value is explicit | A branded `Masked<T>` type is the only input the card components accept; an e2e check asserts no 「0 円」 or 「-1 円」 text appears | ~30 price fixes; masking was opt-in per call site (`batchMaskProductsPrices`), and `pricePublic` defaulted to true (5f7cdbc) |
| A loading or unknown state is never shown as a value | Fetched state is a `loading \| error \| ok` union; pure badge and stock functions get `node --test` unit tests; no magic numbers like `999` | 86b43a5 → d700bc0 → 046d411 (a badge flipped 3 times in 28 minutes); 0efcde4 → c7dbea7 |

## Verify (site-verify shape, Next.js server)

| Rule | Check | Evidence |
|---|---|---|
| Layout holds at 375/768/1024/1440 | `ui-check.mjs --strict` against the running app; `verify.mjs` asserts that sibling cards don't overlap | ~110 overlap and clip fixes; 20+ on 2026-06-16 alone, after the first e2e spec existed but before CI ran it |
| Every page is reachable from the nav | Crawl from `/`; every `app/**/page.tsx` route is reached | #86: the 合算入金報告 UI lived on `/orders`, which had lost its nav link in 7e220be |
| The build runs in CI | CI runs `next build`, builds the Docker image, starts it, and checks `/api/health` | 2eca436: `loaderFile` was not copied into the image, causing a 503 |

The harness serves static files today. A Next.js project adds a start-command mode (`next start` on a free port) before it uses `verify()`.
