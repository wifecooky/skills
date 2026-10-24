---
name: site-verify
description: Acceptance check for a static site that keeps a FEATURES.md feature map and scripts/verify.mjs (honglou-shici first; yewenwu, onemin site, sanguo to follow). Use before a deploy, after changing any interaction, when adding or removing a feature, or when the user asks to 验收 / check that the site still works. Also use to add the feature map and verify script to a site that has none.
---

# site-verify

The user should not be the one who clicks through every feature. The repo holds the list; the script clicks; you look at the screenshots; the user gets one page to skim plus a short list of what only a human can judge.

## Files in a site repo

- `FEATURES.md`: one table row per user action: `` | `id` | 区域 | 操作 | 期望 | ``. 期望 is a visible, checkable result, never 「正常」. A `## 只能人工验收` list holds what a script cannot judge (sound, sync, feel, the screenshots themselves).
- `scripts/verify.mjs`: one test per id in `TESTS`. Opens the site at 390px and 1440px, runs each test in a fresh browser context, asserts DOM state, screenshots, writes `.verify/index.html` (gitignored). Fails when an id is in one file and not the other.
- `scripts/deploy.sh` runs it under `set -e`, so a broken feature blocks the deploy.

Playwright comes from `~/Documents/git/skills/desktop-to-mobile/scripts` (pinned 1.63.0, shared with `ui-check.mjs`). First run there: `npm install`.

## Run

From the site repo:

1. The project's own checks (honglou: `node scripts/check-data.js && node scripts/check-rules.js`).
2. `node ~/Documents/git/skills/desktop-to-mobile/scripts/ui-check.mjs .` (add `--strict` on a project started after 2026-10-24).
3. `node scripts/verify.mjs` (or `node scripts/verify.mjs <id> ...` while working on one feature).
4. Read the screenshots yourself, at least each changed feature at both widths. Look for overlap, cut-off text, empty areas, a dialog that is not on top.
5. Report to the user: the pass count, any ✗ with its cause, the path `.verify/index.html`, and the `只能人工验收` list.

**Done when** steps 1–3 exit 0, you have looked at the screenshots of every changed feature, and the user has the sheet path and the manual list. A deploy still needs the user's OK where the project says so (honglou does).

## Adding or changing a feature

1. Add or edit the row in `FEATURES.md` first.
2. Write the test with the same id. Assert what the user would see: class, `aria-*`, text, `hidden`, scroll position, hash, `:modal`.
3. Prove the test can fail: copy the site to the scratchpad (rsync, skip big source dirs), break that one feature, run `node scripts/verify.mjs <id>`, expect ✗. A test that never failed proves nothing.

## Test-writing traps (each one cost a red run)

| Trap | Do this |
|---|---|
| `page.goto(url + "#x")` on the same page only changes the hash; the page does not reload, hash routing on load never runs | `goto("about:blank")` first |
| `dialog.close()` fires `close` asynchronously; a check right after the click sees the old hash | Wait with a condition (`waitForFunction`), not a direct read |
| `dialog.show()` also sets `open`, so a broken `showModal()` passes an `open` check | Assert `dialog.matches(":modal")` |
| A screenshot right after a click catches a flip or fade halfway | Wait for `document.getAnimations()` with finite iterations to finish, max 3 s |
| Fixed sleeps are flaky under 4 parallel pages | Wait for the end state; sleep only to prove that something did *not* happen |
| Before `load`, Chrome keeps scrolling to an element whose id equals the hash, which can override a JS scroll on a busy machine | Assert where the user lands (the section is in mid-viewport), not the exact offset. Check the live site before you call it a site bug |
| An element that is hidden at one width (honglou's 卷次栏 on phones) | Branch on width in the test and assert the hidden state |
| Clipboard reads fail without permission | Give that test's context `permissions: ["clipboard-read", "clipboard-write"]` |

A flaky test is a bug. Rerun 3 times after any change; trace the failing state (scroll position, element rect, timing) until you know the cause, then fix the test or the site.

## Adding verify to another site

Copy honglou-shici's `scripts/verify.mjs`. Keep the harness (server, id cross-check, pool, contact sheet). Replace `TESTS`, `START` (hash or path per test) and `CTX` (per-test browser options). For a multi-page or built site, serve the built dir and let `START` carry the path. Write `FEATURES.md` from the code (event handlers, routes, dialogs), not from memory. Then run it, fault-inject it, and add it to `deploy.sh`.

| Site | Repo | State |
|---|---|---|
| 红楼一梦 | `~/Documents/git/honglou-shici` | done: 34 features × 2 widths |
| 野文物 | `~/Documents/git/yewenwu` | todo |
| 一分钟看懂日本 site | `~/Documents/git/onemin-japan` | todo |
| 三国 | `~/Documents/git/sanguo` | todo |
