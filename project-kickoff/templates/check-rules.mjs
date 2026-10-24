// Hard checks for the project's rules. scripts/gate.sh runs it; any ✗ stops the push or the deploy.
// One numbered block per rule. Its comment says what the rule is, why, and the incident or commit it came from.
// A rule counts once you have seen it fail: break the thing on purpose, run this, see exit 1.
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
let failed = 0;
const fail = (m) => { failed++; console.error("✗ " + m); };

// 1. The feature map exists: it is the definition of done (project-kickoff step 1).
if (!existsSync(path.join(root, "FEATURES.md"))) fail("no FEATURES.md");

// 2. ...

if (failed) { console.error(`${failed} rule(s) broken`); process.exit(1); }
console.log("✓ rules ok");
