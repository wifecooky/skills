#!/usr/bin/env node
// Replay a skill's eval cases. Usage:
//   node run.mjs <skill-dir> [--case <id>] [--rules-only] [--ablate <regex>] [--baseline] [--reps 3] [--jobs 3] [--model <m>] [--budget 2]
// Cases are <skill-dir>/evals/*.json. A rule case runs a checker on the bad and the good tree, no model.
// An agent case gives a task to `claude -p` in a copy of the repo at the bug, once with the full skill
// and once with the --ablate section removed, then scores the result with scripted checks.
import { execFileSync, spawn } from "node:child_process";
import { cpSync, mkdtempSync, readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i < 0 ? d : argv[i + 1]; };
const skillDir = path.resolve(argv[0] || "");
if (!existsSync(path.join(skillDir, "SKILL.md"))) { console.error("usage: node run.mjs <skill-dir> [options]"); process.exit(2); }
const only = opt("--case"), ablate = opt("--ablate"), model = opt("--model");
const reps = +opt("--reps", 3), jobs = +opt("--jobs", 3), budget = opt("--budget", "2");
const work = mkdtempSync(path.join(os.tmpdir(), "w-"));
const home = (p) => p.replace(/^~(?=\/)/, os.homedir());
const sh = (cmd, cwd, env = {}) => {
  try { execFileSync("sh", ["-c", cmd], { cwd, env: { ...process.env, ...env }, stdio: "pipe" }); return true; }
  catch { return false; }
};

// A tree of <repo> at <rev>, with no .git, at a neutral path so the agent cannot tell it is a test.
// The episode agent edits only inside its tree (acceptEdits) and runs only these commands; anything else is denied.
const TOOLS = ["Read", "Edit", "Write", "Glob", "Grep", "Bash(node:*)", "Bash(git diff:*)", "Bash(git status:*)", "Bash(git log:*)", "Bash(grep:*)", "Bash(ls:*)"];
let n = 0;
function tree(repo, rev) {
  const dir = path.join(work, String(++n), path.basename(home(repo)));
  execFileSync("mkdir", ["-p", dir]);
  execFileSync("sh", ["-c", `git -C "${home(repo)}" archive "${rev}" | tar -x -C "${dir}"`]);
  return dir;
}

// Drop the block that starts at the first line matching re. A heading block ends at the next heading
// of the same or a higher level; a list item or paragraph ends at the next line at its indent or less.
function cut(text, re) {
  const lines = text.split("\n"), i = lines.findIndex((l) => new RegExp(re).test(l));
  if (i < 0) throw new Error(`--ablate ${re}: no line matches`);
  const level = (l) => (l.match(/^(#+) /) || ["", ""])[1].length, ind = (l) => l.match(/^ */)[0].length;
  const end = level(lines[i])
    ? (l) => level(l) && level(l) <= level(lines[i])
    : (l) => l.trim() && ind(l) <= ind(lines[i]);
  let j = i + 1;
  while (j < lines.length && !end(lines[j])) j++;
  return [...lines.slice(0, i), ...lines.slice(j)].join("\n");
}

function ruleCase(c) {
  const bad = tree(c.repo, c.bad), good = tree(c.repo, c.good);
  for (const f of c.checker) cpSync(path.join(good, f), path.join(bad, f), { recursive: true });
  const ok = sh(c.cmd, good) && !sh(c.cmd, bad);
  console.log(`${ok ? "✓" : "✗"} rule ${c.id}: ${ok ? "fails on the bug, passes on the fix" : "does not separate bug from fix"}`);
  return ok;
}

function episode(c, arm, prompt) {
  const old = tree(c.repo, c.at), dir = tree(c.repo, c.at);
  sh("git init -q && git add -A && git -c user.name=dev -c user.email=dev@example.com commit -qm init", dir);
  const sys = path.join(work, `${++n}.md`);
  writeFileSync(sys, `Base directory for the ${path.basename(skillDir)} skill: ${skillDir}\n\n${prompt}`);
  const args = ["-p", c.task, "--setting-sources", "project", "--disable-slash-commands", "--append-system-prompt-file", sys,
    "--permission-mode", "acceptEdits", "--allowedTools", ...TOOLS, "--no-session-persistence", "--max-budget-usd", budget, "--output-format", "json"];
  if (model) args.push("--model", model);
  return new Promise((done) => {
    const p = spawn("claude", args, { cwd: dir, stdio: ["ignore", "pipe", "ignore"] });
    let out = "";
    p.stdout.on("data", (d) => { out += d; });
    p.on("close", () => {
      let cost = 0; try { cost = JSON.parse(out).total_cost_usd || 0; } catch { /* no json */ }
      const passed = c.checks.filter((k) => sh(k.run, dir, { OLD: old })).map((k) => k.name);
      console.log(`  ${arm}: ${passed.length}/${c.checks.length} [${passed.join(", ")}] $${cost.toFixed(2)} ${dir}`);
      done({ arm, score: passed.length / c.checks.length, cost });
    });
  });
}

async function agentCase(c) {
  const full = readFileSync(path.join(skillDir, "SKILL.md"), "utf8");
  const arms = { full, ...(ablate && { ablated: cut(full, ablate) }), ...(argv.includes("--baseline") && { none: "" }) };
  const queue = Object.entries(arms).flatMap(([a, t]) => Array.from({ length: reps }, () => [a, t]));
  console.log(`agent ${c.id}: ${queue.length} episodes`);
  const res = [];
  while (queue.length) res.push(...await Promise.all(queue.splice(0, jobs).map(([a, t]) => episode(c, a, t))));
  for (const a of Object.keys(arms)) {
    const r = res.filter((x) => x.arm === a);
    console.log(`  = ${a}: ${(r.reduce((s, x) => s + x.score, 0) / r.length).toFixed(2)} over ${r.length}`);
  }
  return res;
}

const cases = readdirSync(path.join(skillDir, "evals")).filter((f) => f.endsWith(".json"))
  .map((f) => JSON.parse(readFileSync(path.join(skillDir, "evals", f), "utf8")))
  .filter((c) => !only || c.id === only);
let bad = 0, cost = 0;
for (const c of cases) {
  if (c.kind === "rule") bad += !ruleCase(c);
  else if (!argv.includes("--rules-only")) cost += (await agentCase(c)).reduce((s, x) => s + x.cost, 0);
}
console.log(`${cases.length} case(s); ${bad} rule case(s) broken; agent cost $${cost.toFixed(2)}; trees in ${work}`);
process.exit(bad ? 1 : 0);
