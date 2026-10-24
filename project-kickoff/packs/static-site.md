# Static-site pack

These rules come from the 4 sites that got gates in 2026-10. All of them are scripted in some site. Copy the rule from the site that has it, then change the paths.

| Rule | Check | From |
|---|---|---|
| Every local file a page references exists and is in the upload set | Parse `src`/`href` from the pages; each target exists and is under a deployed dir | honglou `check-rules.js` 1; sanguo `check-rules.js` |
| Every source file is loaded by a page | No file under `js/` that `index.html` does not load | sanguo `check-rules.js` |
| No-build stays no-build | No `type="module"`, no `import`/`export`, no CDN script | sanguo `check-rules.js` |
| The published output holds no private files, no repo link, nothing you did not mean to publish | Walk the output dir: deny a list of private paths; deny regexes (coordinates, `github.com/<account>`) | yewenwu `check-rules.mjs` 3, 4 |
| Files fit the host's limit | Cloudflare Pages: every file ≤ 25 MiB | honglou `check-rules.js` 5 |
| The font subset covers every character used | Diff the characters in the pages and data against the woff2 cmap | honglou `check-rules.js` 3 |
| Data cross-references resolve | Every id a record points to exists | sanguo `check-data.js`, honglou `check-data.js` |
| Data shown as plain text holds no markup | No `**`, `__` or backticks in any data string | sanguo `check-data.js` (9169304: 「**不是**」 showed its asterisks) |
| Two lists that must agree are checked against each other | Set equality, reported in both directions | yewenwu `check-rules.mjs` 1 (cases vs workspaces) |
| The brief's content rules | Per project; e.g. no Arabic digits in TTS text, no URL on screen, 9:16 and ≤ 60 s | onemin `check-rules.mjs` |
| The layout floor | `ui-check.mjs`: no horizontal scroll, text ≥ 12px, tap targets ≥ 24px, no overlapping targets; `--strict` adds the 16px body and 44px targets | `~/Documents/git/skills/desktop-to-mobile/scripts/ui-check.mjs` |
| Every feature works at 390 and 1440 | `scripts/verify.mjs` with the site-verify harness | site-verify skill |

Not scripted yet:
- Every page is reachable from the nav. verify's `links` test checks that each link on a page opens; it does not check the reverse, that each page has a link.
- The page survives when an offsite service fails (a font CDN or Turnstile returns 500). The harness answers every offsite request with an empty 200, so this case is never tested.
