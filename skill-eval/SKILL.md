---
name: skill-eval
description: Unit tests for skills. Replays the bugs a skill exists to stop, once with the full skill and once with one section removed, and scores the result with scripted checks. Use after changing a skill, after adding a pack rule, when a user-found bug becomes a new case, or when asked if a skill or a section of it still earns its place. Cases live in <skill>/evals/*.json.
---

# skill-eval

A skill is a claim: "with this text, the agent does X". An eval tests the claim. It runs the bug the skill was written for, then scores the result with a script, not by reading the answer.

Without evals, a skill edit can make things worse, and you cannot see it. With evals, every edit is a hill climb (Lauren Tan, Cursor: "evals are the agent's unit tests").

## How it fits

```
  user finds a bug in project X
              |
              v
  fix + a check that fails on the old code          project-kickoff step 5
              |   lesson-gate (Stop hook) asks where the lesson goes
     +--------+-----------------+-------------------------+
     v                          v                         v
  project skill            whole stack?                agent behaviour?
  (or site-verify)         packs/<stack>.md row        <skill>/evals/<id>.json
                           + a rule case               kind: agent
     +--------+-----------------+-------------------------+
              v
     node skill-eval/run.mjs <skill-dir> [--ablate <section>]
              |
     +--------+------------------------------------+
     v                                             v
  rule case: no model, seconds              agent case: claude -p, minutes, costs $
  checker on the bad tree  -> must fail     repo copy at the bug commit, neutral path
  checker on the good tree -> must pass     arms: full skill | skill minus one section
                                            reps x arms -> scripted checks -> score
     +--------+------------------------------------+
              v
  rule case broken        -> the rule stopped catching its bug: fix it before the commit
  ablated < full          -> the section earns its place
  ablated ~ full          -> the section is dead weight, or the case does not test it
```

## Case files

One JSON file per case in `<skill>/evals/`. `about` says what the case protects and how to ablate it.

**Rule case** (`kind: "rule"`). A scripted rule must still catch the commit it came from.
- `repo`, `bad` (the commit with the bug, often `<fix>^`), `good` (the fix).
- `checker`: the paths copied from the good tree onto the bad tree (the rule itself).
- `cmd`: the check. It must exit 0 on the good tree and non-zero on the bad tree.

**Agent case** (`kind: "agent"`). The agent, given the skill, behaves as the skill says.
- `repo`, `at`: the tree the agent starts from.
- `task`: the message, written the way the user wrote it. Never say "test" or "eval": an agent that knows it is tested behaves differently.
- `checks`: shell commands run in the agent's tree. Each passes on exit 0. `$OLD` is an untouched copy of `at`, so a check can prove that the agent's new guard fails on the old code.

## Run

```sh
node skill-eval/run.mjs <skill-dir> --rules-only                       # every rule case, free
node skill-eval/run.mjs <skill-dir> --case <id> --ablate '<regex>'     # full vs ablated, 3 reps each
```

Options: `--baseline` (add an arm with no skill at all), `--reps 3`, `--jobs 3`, `--model <m>` (run the same case across models), `--budget 2` (USD cap per episode).

- The episode agent may edit only inside its tree (`--permission-mode acceptEdits`) and may run only `node`, `grep`, `ls` and read-only `git` (`TOOLS` in `run.mjs`). Widen `TOOLS` for a case that needs more; never use `--dangerously-skip-permissions`.
- The episode runs `claude -p` with `--setting-sources project` (your hooks do not fire) and `--disable-slash-commands` (no other skill loads). The skill text arrives with `--append-system-prompt-file`.
- `--ablate` takes a regex for the first line of a section: a heading drops the heading block, a list item drops that item. No match is an error, so an ablation never silently changes nothing.
- One rep proves nothing; the agent is not deterministic. Compare means over 3 or more reps.

## Rules

1. **Every case fails once.** A rule case must fail when the checker comes from the bad tree. An agent case must score lower with `--baseline` than with the full skill, and the untouched `at` tree must not pass every check. If not, the case tests nothing: fix it or delete it.
   - An ablation that changes nothing usually means the idea is stated in more places. sanguo-markup-agent: removing step 5 kept 3/3, because 4 other lines say "a check that fails once". `--baseline` gave full 1.00 vs none 0.67 (guard 3/3 vs 0/3), $1.60 for 6 episodes.
2. **A check must accept every valid fix.** Read the episode trees before you trust a low score. sanguo-markup-agent first required the data to lose its `**`; one baseline episode rendered them as emphasis in the view instead, a valid fix, and was marked wrong. The check now accepts both.
3. **Script the score.** Prefer `grep`, the repo's own check scripts and exit codes to a model judging a model. Add a rubric judge only when no script can tell.
4. **Rule cases are free, so run them always.** Run `--rules-only` after every pack or rule edit. Agent cases cost money; run them after a skill edit that changes behaviour.
5. **Report the cost.** The runner prints the dollar total; say it with the scores.
6. **Leave the source repos alone.** The runner reads them with `git archive` only. Trees go to a temp dir that the runner prints.

## Known limits

- In real use a skill loads only when invoked. Here it is always in the system prompt, so a case measures what the text does once it is read, not whether it gets triggered.
- Your global CLAUDE.md still loads in the episode. It is the same for both arms, so the difference is the section.
- A check that needs a browser (`verify.mjs`) does not run in an episode yet.
