#!/usr/bin/env node
"use strict";

/**
 * @pilotspace/add installer.
 *
 *   npx @pilotspace/add init [targetDir] [--force] [--stage <stage>] [--name <name>]
 *
 * Installs the ADD skill + tooling + book into a target project:
 *   <target>/.claude/skills/add/   (the skill Claude loads)
 *   <target>/.add/tooling/         (add.py scaffolder + state tracker)
 *   <target>/.add/docs/            (the AIDD book — the trust layer)
 * Then runs `add.py init` to create .add/state.json and survivor files.
 *
 * Zero npm dependencies. Designed for failure: verifies sources, never clobbers
 * an existing state.json, and degrades gracefully if python3 is absent.
 */

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const PKG_ROOT = path.resolve(__dirname, "..");

function log(msg) { process.stdout.write(msg + "\n"); }
function warn(msg) { process.stderr.write("warn: " + msg + "\n"); }
function fail(msg) { process.stderr.write("error: " + msg + "\n"); process.exit(1); }

function parseArgs(argv) {
  const args = { _: [], force: false, stage: "prototype", name: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--force") args.force = true;
    else if (a === "--stage") args.stage = argv[++i];
    else if (a === "--name") args.name = argv[++i];
    else if (a.startsWith("--")) warn("ignoring unknown flag " + a);
    else args._.push(a);
  }
  return args;
}

function copyDir(src, dest, { skipIfExists, cleanReplace } = {}) {
  if (!fs.existsSync(src)) fail("missing packaged source: " + src);
  if (skipIfExists && fs.existsSync(dest)) {
    warn(dest + " exists — leaving it untouched");
    return;
  }
  // Clean replace: drop a stale dest before copying so a `--force` re-install can
  // never leave orphaned files from a previous version behind. fs.cpSync merges
  // (it never removes), so without this `--force` is a merge, not a replace. Mirrors
  // _installer.py's `shutil.rmtree(skill_dest)` so npm and pip behave identically.
  if (cleanReplace && fs.existsSync(dest)) {
    fs.rmSync(dest, { recursive: true, force: true });
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.cpSync(src, dest, { recursive: true });
}

function hasPython() {
  // python3/python cover macOS+Linux; `py` is the Windows Python launcher, where
  // python3 is often absent and bare `python` may be a no-op Store shim.
  for (const py of ["python3", "python", "py"]) {
    const r = spawnSync(py, ["--version"], { stdio: "ignore" });
    if (r.status === 0) return py;
  }
  return null;
}

function cmdInit(args) {
  const target = path.resolve(args._[0] || ".");
  if (!fs.existsSync(target)) fail("target directory does not exist: " + target);
  log("Installing ADD into " + target);

  // 1. skill -> .claude/skills/add
  copyDir(
    path.join(PKG_ROOT, "skill", "add"),
    path.join(target, ".claude", "skills", "add"),
    { skipIfExists: !args.force, cleanReplace: args.force }
  );
  log("  ✓ skill      -> .claude/skills/add/");

  // 2. tooling -> .add/tooling  (exclude tests from the installed copy)
  const toolingDest = path.join(target, ".add", "tooling");
  copyDir(path.join(PKG_ROOT, "tooling"), toolingDest, { skipIfExists: false });
  // installed copy is runtime-only: drop ALL test files and any compiled cache
  // (glob test_*.py — not just test_add.py — so no test leaks into installs)
  fs.rmSync(path.join(toolingDest, "__pycache__"), { recursive: true, force: true });
  for (const entry of fs.readdirSync(toolingDest)) {
    if (/^test_.*\.py$/.test(entry)) {
      fs.rmSync(path.join(toolingDest, entry), { force: true });
    }
  }
  log("  ✓ tooling    -> .add/tooling/add.py (+ templates)");

  // 3. docs (the book / trust layer) -> .add/docs
  copyDir(path.join(PKG_ROOT, "docs"), path.join(target, ".add", "docs"),
    { skipIfExists: false });
  log("  ✓ trust docs -> .add/docs/ (the AIDD book)");

  // 4. run add.py init (idempotent — add.py refuses to clobber state.json)
  const py = hasPython();
  const addPy = path.join(toolingDest, "add.py");
  if (!py) {
    const launcher = process.platform === "win32" ? "py" : "python3";
    warn("Python not found on PATH — skipping `add.py init`.");
    log("\nInstall Python 3.10+ and finish setup manually:");
    log(`  ${launcher} .add/tooling/add.py init` +
        (args.name ? ` --name "${args.name}"` : "") + ` --stage ${args.stage}`);
    return;
  }
  const initArgs = [addPy, "init", "--dir", target, "--stage", args.stage];
  if (args.name) initArgs.push("--name", args.name);
  if (args.force) initArgs.push("--force");
  const r = spawnSync(py, initArgs, { stdio: "inherit" });
  if (r.status !== 0 && r.status !== null) {
    warn("`add.py init` exited non-zero (state may already exist). Run `add.py status` to check.");
  }

  log("\nDone. In Claude Code, the `add` skill is now installed.");
  log("Next:  open Claude Code, run `/add`, and say what you want to build —");
  log("       the agent sizes it into a milestone and drives the build with you.");
}

function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0] && !argv[0].startsWith("--") ? argv.shift() : "init";
  const args = parseArgs(argv);
  switch (cmd) {
    case "init":
      cmdInit(args);
      break;
    case "help":
    case "--help":
      log("usage: npx @pilotspace/add init [targetDir] [--force] [--stage <s>] [--name <n>]");
      break;
    default:
      fail("unknown command '" + cmd + "'. Try: npx @pilotspace/add init");
  }
}

main();
