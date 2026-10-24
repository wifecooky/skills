---
name: project-kickoff
description: The development flow for every new project, and for adding guardrails to a young one. Feature map first; a verify script so the agent accepts its own work; one gate script that a local hook and CI both run; rules as scripts, not prose; every user-found bug turned into a check that has failed once; small commits. Use when starting a repo (git init, a new app, site, tool or video channel), when the kickoff-gate hook says a repo has no FEATURES.md or a dead git hook, when a project's rules live only in prose, or when a gate may be dead. Rule packs for static sites and Next.js.
---

# project-kickoff

An agent takes the shortest path. Without guardrails, the shortest path rots a new codebase into an "organic" architecture (Lauren Tan, Cursor). So on day 1 you build the guardrails that make the shortest path the correct one.

The flow below does not depend on the stack. The rules do, so they live in `packs/`.

The flow comes from 5 projects:
- jam-bo: 498 fix commits, Next.js.
- honglou, sanguo, onemin, yewenwu: 4 static sites. Each got the same gates in 2026-10.

## Pick the tier

| Project | Do |
|---|---|
| Throwaway: a demo, a spike, a one-off script | Step 1 only, then `touch .kickoff-skip` |
| Ships to users: a site, a channel, a tool others run | Steps 1–5 |
| Long-lived; several agents or people; auto-merge wanted | Steps 1–6, and the whole stack pack |

Raise the tier when a project outlives its plan. jam-bo started as a prototype. It grew to 29k lines of CSS with no working gate.

## The flow

1. **Write the feature map before the code.**
   - Copy `templates/FEATURES.md` to the repo root.
   - Write one row per user action, with a visible result.
   - The map defines "done". Without it, the user becomes the acceptance tester, and that does not scale past one agent.

2. **Make the agent accept its own work.**
   - A verify script runs every row at phone and desktop width. It asserts the page state and takes screenshots.
   - For sites, use the site-verify skill and its shared harness.
   - Other stacks use the same shape:
     - The map ids must equal the test ids.
     - Each test must fail once on purpose (fault injection).
   - The user then checks only the 只能人工验收 list.

3. **Run one gate on the only path, and watch it from outside.**
   - `templates/gate.sh` runs every check. The pre-push hook (or `deploy.sh`) and CI both call it, and nothing else, so the local gate and CI cannot drift.
   - Local hooks die silently. jam-bo renamed `src/` to `frontend/` (36912c3) and missed one path in `prepare`. Its pre-commit then did nothing for 5 months, and ~25 lint errors reached main.
   - Three things watch the gate:
     - CI on every push.
     - `gate.sh`'s self-check: the hook exists and calls the gate.
     - The kickoff-gate hook: it warns when a repo ships git hooks that git does not run.

4. **Write rules as scripts, not prose.**
   - Before you write a rule into CLAUDE.md, a brief or a skill, ask if a script can check it.
   - If yes, the rule goes into `scripts/check-rules.mjs`. The prose keeps only the reason.
   - Start from the stack pack.
   - Prose drifts. jam-bo's release notes said 3 breakpoints; the CSS had 11.
   - Make the shortest path the correct one:
     - A helper that is safe by default beats a rule that every call site must remember.
     - jam-bo's price masking was opt-in, so every new page leaked prices (~30 fixes).
     - Ban the unsafe form with lint, so the safe helper is the only way that compiles.

5. **Turn every bug the user finds into a check that has failed once.**
   - Find the cause, then write the test or the rule.
   - Run it on the broken code and see ✗.
   - Fix the code and see ✓.
   - Write the lesson into the owning skill. The lesson-gate Stop hook asks for this.
   - If every project on this stack can make the same mistake, also add a row to `packs/<stack>.md` with the commit as evidence, and a rule case in `evals/`. This is how lessons from new projects come back here.
   - Guessing does not converge. jam-bo's KOL scroll took 7 rounds; a spec plus a failing e2e test stopped it (5cd738c).
   - sanguo 9169304 shows the pattern on a small fix.

6. **Keep commits small.**
   - Make one change per commit. Git history then becomes context, and a revert is cheap.
   - jam-bo's 4 reverts were all big changes, undone within minutes. One was a 223-line redesign (6aef797).
   - For the long-lived tier, every pack rule keeps the commit it would have caught. Replaying those commits is the eval for the rules and the skills.

## Start a repo

1. `git init`, then pick the tier.
2. Copy the templates:
   - `FEATURES.md`
   - `scripts/gate.sh`
   - `scripts/check-rules.mjs`
   - `.githooks/pre-push`
   - `.github/workflows/gate.yml`
3. Make the scripts executable: `chmod +x scripts/gate.sh .githooks/pre-push`.
4. Wire the local hook: `git config core.hooksPath .githooks`.
5. Copy the stack pack's day-1 rules into `check-rules.mjs` (and into the lint config for Next.js).
6. Prove each rule fails once. Break one thing, run `scripts/gate.sh`, see exit 1.
7. Then write the first feature.

A site where a push deploys (GitHub Pages) uses the pre-push hook. A site with a deploy script calls `scripts/gate.sh` at the top of `deploy.sh`.

**Done when:**
- `FEATURES.md` exists.
- For tier 2 and up, also:
  - `scripts/gate.sh` exits 0.
  - The pre-push hook or `deploy.sh`, and CI, all call it.
  - `git config core.hooksPath` is `.githooks`.
  - You have seen every rule and every verify test fail once.

## Files

- `templates/`: `FEATURES.md`, `gate.sh`, `check-rules.mjs`, `pre-push`, `gate.yml`.
- `packs/static-site.md`: rules from the 4 static sites, each with where it came from.
- `packs/nextjs.md`: rules from jam-bo's fix history, each with the commit it would have caught.
- `evals/`: cases for the skill-eval skill. A rule case replays a pack rule against its evidence commit; an agent case checks a step of the flow. Run `node ../skill-eval/run.mjs . --rules-only` after every pack edit.
- `hooks/kickoff-gate.js`: a PreToolUse hook on Edit and Write, wired in `~/.claude/settings.json`. It finds the git root of the file being edited. It denies the edit once per repo per session in two cases:
  - A new repo (first commit in the last 14 days, 20 commits or fewer) has no `FEATURES.md` and no `.kickoff-skip`.
  - A repo ships `.githooks/` or `.husky/` hooks that git's `core.hooksPath` does not run.

  Writing `FEATURES.md` or `.kickoff-skip` is never blocked. Set `SKIP_KICKOFF_GATE=1` to turn the hook off. The hook fails open: on any error, the edit goes through.

## Projects

| Project | Tier | Gate | Gap |
|---|---|---|---|
| honglou-shici | 2 | `deploy.sh` | no CI |
| sanguo | 2 | `.githooks/pre-push` + CI | CI runs check-data and check-rules only; verify and ui-check need the local harness |
| onemin-japan | 2 | `deploy.sh` | no CI |
| yewenwu | 2 | `deploy.sh` | no CI |
| yuanzhuo (圆桌) | 3, Next.js | none yet | not kicked off; apply `packs/nextjs.md` before the first feature |

These 4 sites predate `gate.sh`. Each one calls its checks directly from its own gate. Move them to `gate.sh` when you next touch the gate, not as a drive-by.

## Where the talk lives

The flow generalises Lauren Tan's talk (Cursor, 2026) with what our projects taught. Each idea in the talk maps to one place:

| Talk | Here |
|---|---|
| Verification: the agent runs the product and accepts its own work | Step 2; site-verify |
| Feature map: the agent knows where each feature is | Step 1; `templates/FEATURES.md` |
| Turn failure modes into skills | Step 5; the lesson-gate hook |
| Evals are the agent's unit tests; hill-climb on them | The skill-eval skill; `evals/` |
| Hard constraints beat soft rules; shortest path = correct path | Step 4; `packs/` |
| Greenfield: add the constraints before the first feature | The kickoff-gate hook |
| Atomic PRs; git history as context | Step 6 |
| Trust curve: local, then cloud, then auto-merge | Not adopted. The user checks each deploy locally, and only the user changes that |
