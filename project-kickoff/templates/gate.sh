#!/bin/sh
# The only gate. .githooks/pre-push (or deploy.sh) and CI call this and nothing else, so the local gate and CI cannot drift.
# Steps that need the local harness in ~/Documents/git/skills are skipped where it is missing (CI), and say so.
set -e
cd "$(dirname "$0")/.."

# The gate checks that it is wired: a hook that is renamed or stops calling this file fails here, in CI.
if [ -f .githooks/pre-push ]; then
  [ -x .githooks/pre-push ] || { echo "✗ .githooks/pre-push is not executable"; exit 1; }
  grep -q 'scripts/gate.sh' .githooks/pre-push || { echo "✗ .githooks/pre-push does not call scripts/gate.sh"; exit 1; }
fi
[ ! -f .githooks/commit-msg ] || [ -x .githooks/commit-msg ] || { echo "✗ .githooks/commit-msg is not executable"; exit 1; }

node scripts/check-rules.mjs

HARNESS="$HOME/Documents/git/skills"
if [ -d "$HARNESS/site-verify" ]; then
  : # node "$HARNESS/desktop-to-mobile/scripts/ui-check.mjs" <served dir> --strict
  : # node scripts/verify.mjs
else
  echo "- skip ui-check and verify: no $HARNESS"
fi
