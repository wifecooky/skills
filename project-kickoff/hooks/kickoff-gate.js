#!/usr/bin/env node
/**
 * PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit): the project-kickoff reminder.
 *
 * Finds the git root of the file being edited and denies the edit ONCE per repo
 * per session when either holds:
 *   - a new repo (first commit in the last 14 days, <= 20 commits) has no
 *     FEATURES.md and no .kickoff-skip;
 *   - the repo ships .githooks/ or .husky/ hooks that git's core.hooksPath does
 *     not run (jam-bo: a dir rename left pre-commit dead for 5 months).
 * The retry always passes. Writing FEATURES.md or .kickoff-skip is never blocked.
 *
 * Off switch: SKIP_KICKOFF_GATE=1. Fail-open: any error lets the edit through.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');

const YOUNG = { commits: 20, days: 14 };
const HOOKS = ['pre-commit', 'pre-push'];
const STATE_DIR = process.env.KICKOFF_GATE_STATE_DIR || path.join(os.homedir(), '.claude', 'hooks', '.state');

const git = (root, ...args) => {
    try { return execFileSync('git', ['-C', root, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); }
    catch { return ''; }
};

function gitRoot(file) {
    let dir = path.dirname(path.resolve(file));
    while (dir !== path.dirname(dir)) {
        if (fs.existsSync(path.join(dir, '.git'))) return dir;
        dir = path.dirname(dir);
    }
    return null;
}

// Hook files the repo ships: .githooks/<name>, or .husky/<name> at the root or one level down.
function shippedHooks(root) {
    const dirs = [path.join(root, '.githooks'), path.join(root, '.husky')];
    for (const e of fs.readdirSync(root, { withFileTypes: true })) {
        if (e.isDirectory() && !e.name.startsWith('.') && e.name !== 'node_modules') dirs.push(path.join(root, e.name, '.husky'));
    }
    return dirs.flatMap((d) => HOOKS.filter((n) => fs.existsSync(path.join(d, n))).map((n) => path.join(d, n)));
}

// A shipped hook is live when git's hooks dir runs it: <hooksPath>/<name>, or for husky (<dir>/_) <dir>/<name>.
function deadHooks(root) {
    const shipped = shippedHooks(root);
    if (!shipped.length) return [];
    const hp = git(root, 'config', 'core.hooksPath');
    const dir = hp ? path.resolve(root, hp) : path.resolve(root, git(root, 'rev-parse', '--git-path', 'hooks') || '.git/hooks');
    const runs = (n) => (path.basename(dir) === '_' ? fs.existsSync(path.join(path.dirname(dir), n)) : fs.existsSync(path.join(dir, n)));
    return HOOKS.filter((n) => shipped.some((f) => path.basename(f) === n) && !runs(n))
        .map((n) => `${path.relative(root, shipped.find((f) => path.basename(f) === n))} (core.hooksPath: ${hp || 'unset'})`);
}

function noMap(root) {
    if (['FEATURES.md', '.kickoff-skip'].some((f) => fs.existsSync(path.join(root, f)))) return false;
    const n = parseInt(git(root, 'rev-list', '--count', 'HEAD'), 10) || 0;
    if (!n) return true;
    const first = parseInt(git(root, 'log', '--max-parents=0', '--format=%ct').split('\n').pop(), 10) || 0;
    return n <= YOUNG.commits && Date.now() / 1000 - first <= YOUNG.days * 86400;
}

function main(raw) {
    if (process.env.SKIP_KICKOFF_GATE === '1') return;
    const input = JSON.parse(raw);
    const file = (input.tool_input || {}).file_path || (input.tool_input || {}).notebook_path;
    if (!file || ['FEATURES.md', '.kickoff-skip'].includes(path.basename(file))) return;
    const root = gitRoot(file);
    if (!root || root === os.homedir()) return;

    const statePath = path.join(STATE_DIR, 'kickoff-' + String(input.session_id).replace(/[^\w-]/g, '_') + '.json');
    let state = [];
    try { state = JSON.parse(fs.readFileSync(statePath, 'utf8')); } catch { /* first edit this session */ }
    if (state.includes(root)) return;

    const problems = [];
    const dead = deadHooks(root);
    if (dead.length) problems.push(`git never runs these shipped hooks, so the gate is dead: ${dead.join('; ')}. Fix the hooks path (usually \`git config core.hooksPath .githooks\`, or the husky \`prepare\` path) after asking the user.`);
    if (noMap(root)) problems.push('this repo is new and has no FEATURES.md. Load the project-kickoff skill and pick the tier with the user; a throwaway gets `touch .kickoff-skip`.');
    if (!problems.length) return;

    fs.mkdirSync(STATE_DIR, { recursive: true });
    fs.writeFileSync(statePath, JSON.stringify([...state, root]));
    process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
            hookEventName: 'PreToolUse',
            permissionDecision: 'deny',
            permissionDecisionReason: `kickoff-gate (${root}): ${problems.join(' Also: ')} One-time reminder for this repo in this session; retrying this edit will pass.`,
        },
    }));
}

let raw = '';
process.stdin.on('data', (c) => { raw += c; });
process.stdin.on('end', () => { try { main(raw); } catch { /* fail open */ } });
