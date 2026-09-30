#!/usr/bin/env node
"use strict";

/**
 * @pilotspace/add — installs the ADD skill. No engine, no prompts, no dependencies.
 *
 *   npx @pilotspace/add [init|update] [dir] [--name <name>]    install into a project
 *   npx @pilotspace/add --global                               install for this user
 *
 * Twin of src/add_method/_installer.py: same flags, same files, same output
 * (tests/test_npm_pip_parity.py runs both and compares). Rules:
 *   - what ADD owns (the skill, the persona corpus + index) is refreshed on every run by a
 *     stage-then-swap, so a crash never leaves a half-copied tree;
 *   - what the user owns (PROJECT.md, personas, text outside the managed block) is never
 *     overwritten;
 *   - a 3.x engine (.add/tooling/) and ADD's 3.x agents are removed only AFTER the new
 *     layout has landed, and only when they are recognisably ours;
 *   - any failure stops the run, says what landed, and exits non-zero. Re-running is safe.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const PKG_ROOT = path.resolve(__dirname, "..");
const PROG = "npx @pilotspace/add";

const GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by the ADD installer; do not edit inside -->";
const GUIDE_END = "<!-- ADD:END -->";
const BEGIN_PREFIX = "<!-- ADD:BEGIN";   // also matches a 3.x block, so it is replaced, not duplicated
const RETIRED_AGENTS = ["add-worker", "add-advisor", "add", "add-design", "add-build",
                        "add-verify", "add-persona"];
// 3.x also wrote the block to .clinerules (the rest: defensive). Refreshed if a block is there; never created.
const LEGACY_POINTERS = [".clinerules", "GEMINI.md", ".cursorrules", ".windsurfrules", ".github/copilot-instructions.md"];
const IGNORED = ["personas-teacher/", "personas-index/"];
const JUNK = /(^|[\\/])(__pycache__|\.DS_Store)$|\.py[co]$/;

class Usage extends Error {}

function out(msg) { process.stdout.write(msg + "\n"); }
function row(label, text) { out("  " + label.padEnd(10) + "  " + text); }
function version() { return require(path.join(PKG_ROOT, "package.json")).version; }
function exists(p) { try { fs.lstatSync(p); return true; } catch (_e) { return false; } }
function isLink(p) { try { return fs.lstatSync(p).isSymbolicLink(); } catch (_e) { return false; } }
function isDir(p) { try { return fs.statSync(p).isDirectory(); } catch (_e) { return false; } }
function rm(p) { fs.rmSync(p, { recursive: true, force: true }); }
function readText(p) {   // refuse to rewrite a file that is not UTF-8 rather than mangle it
  const buf = fs.readFileSync(p);
  const text = buf.toString("utf8");
  if (!Buffer.from(text, "utf8").equals(buf)) throw new Error(p + " is not UTF-8 text - left as is");
  return text;
}

function usage() {
  return [
    "usage: " + PROG + " [init|update] [dir] [--name <name>]",
    "       " + PROG + " --global",
    "",
    "Installs the ADD skill into a project (default: the current folder):",
    "  .claude/skills/add/     the skill, refreshed on every run",
    "  .add/                   PROJECT.md, specs/ milestones/ tasks/, personas - never overwritten",
    "  CLAUDE.md, AGENTS.md    a short managed block that points your agent at the skill",
    "Re-running is safe. Over a 3.x project it also removes the vendored engine",
    "(.add/tooling/) and ADD's 3.x agents in .claude/agents/.",
    "",
    "options:",
    "  --name <name>   project name for a new .add/PROJECT.md (default: the folder name)",
    "  --global        install the skill for your user (~/.claude/skills/add), no project",
    "  --version       print the version",
    "  -h, --help      show this help",
  ].join("\n");
}

function parse(argv) {
  const a = { positional: [], name: null, global: false, help: false, version: false };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "-h" || arg === "--help") a.help = true;
    else if (arg === "--version") a.version = true;
    else if (arg === "--global") a.global = true;
    else if (arg === "--yes" || arg === "-y" || arg === "--non-interactive") { /* 3.x scripts: no prompts now */ }
    else if (arg === "--name") {
      const v = argv[++i];
      if (v === undefined || v.startsWith("-")) throw new Usage("--name needs a value");
      a.name = v;
    } else if (arg.startsWith("-")) throw new Usage("unknown option " + arg);
    else a.positional.push(arg);
  }
  if (["init", "update", "help"].includes(a.positional[0])) {
    if (a.positional.shift() === "help") a.help = true;
  }
  if (a.help || a.version) return a;
  if (a.positional[0] === "prune-data") throw new Usage("prune-data was retired in ADD 4.0");
  if (a.positional.length > 1) throw new Usage("too many arguments: " + a.positional.join(" "));
  if (a.global && a.positional.length) throw new Usage("--global installs for your user and takes no directory");
  return a;
}

// Stage a full copy beside dest, then swap it in with two renames — dest is never half-written.
function replaceTree(src, dest) {
  if (isLink(dest)) return "kept (a symlink - not replaced)";
  const parent = path.dirname(dest);
  const base = path.basename(dest);
  fs.mkdirSync(parent, { recursive: true });
  for (const n of fs.readdirSync(parent)) {
    if (n.startsWith(base + ".add-tmp-")) rm(path.join(parent, n));   // a crashed earlier run
  }
  const old = path.join(parent, base + ".add-old");
  if (!exists(dest) && exists(old)) fs.renameSync(old, dest);         // heal a crash mid-swap
  rm(old);
  const tmp = path.join(parent, base + ".add-tmp-" + process.pid);
  try {
    fs.cpSync(src, tmp, { recursive: true, dereference: true, filter: (s) => !JUNK.test(s) });
  } catch (e) { rm(tmp); throw e; }
  const had = exists(dest);
  if (had) fs.renameSync(dest, old);
  try { fs.renameSync(tmp, dest); }
  catch (e) { if (had) fs.renameSync(old, dest); rm(tmp); throw e; }
  rm(old);
  return had ? "refreshed" : "installed";
}

function pointerBlock() {
  return [
    GUIDE_BEGIN,
    "## ADD — how to work in this repo",
    "",
    "This project uses **ADD (AI-Driven Development)**. The method is one skill file,",
    "`.claude/skills/add/SKILL.md` — read it and follow it (Claude Code: run `/add`).",
    "State lives in `.add/`: read `.add/PROJECT.md` first each session, then the open work in",
    "`.add/tasks/` and `.add/milestones/`. Your tools are git and this project's test command.",
    "",
    "Size before ceremony: a change of at most 3 adjacent files with no unknowns goes Quick — a failing test, the fix, one commit.",
    "Anything touching security · data · architecture, or a surface other code consumes, is at least a Task.",
    "PROJECT.md `invariants:` bind every change. Never weaken a sealed check to get green; a security finding is a HARD-STOP.",
    "",
    "Edit outside the markers, not inside.",
    GUIDE_END,
  ].join("\n");
}

// Rewrite only the managed block; text outside it is never touched. created|updated|unchanged.
function writePointer(file) {
  const block = pointerBlock();
  if (!exists(file)) { fs.writeFileSync(file, block + "\n"); return "created"; }
  const cur = readText(file);
  const end = cur.lastIndexOf(GUIDE_END);
  const begin = end === -1 ? -1 : cur.lastIndexOf(BEGIN_PREFIX, end);
  let next;
  if (begin !== -1) next = cur.slice(0, begin) + block + cur.slice(end + GUIDE_END.length);
  else if (cur.trim() === "") next = block + "\n";
  else next = cur.replace(/\n+$/, "") + "\n\n" + block + "\n";
  if (next === cur) return "unchanged";
  fs.writeFileSync(file + ".bak", cur);   // a rollback copy before any real change
  fs.writeFileSync(file, next);
  return "updated";
}

// A whole managed block (BEGIN ... END) is present. Unreadable or non-UTF-8 reads as no block.
function hasBlock(file) {
  let text;
  try { if (!fs.statSync(file).isFile()) return false; text = readText(file); } catch (_e) { return false; }
  const end = text.lastIndexOf(GUIDE_END);
  return end !== -1 && text.lastIndexOf(BEGIN_PREFIX, end) !== -1;
}

// Gemini CLI reads GEMINI.md unless told otherwise; name AGENTS.md in its settings.
function writeGemini(dir) {
  const file = path.join(dir, "settings.json");
  let data = {};
  if (exists(file)) {
    try { data = JSON.parse(readText(file)); } catch (_e) { return "skipped (not valid JSON)"; }
    if (data === null || typeof data !== "object" || Array.isArray(data)) return "skipped (not a JSON object)";
  }
  const ctx = data.context && typeof data.context === "object" && !Array.isArray(data.context) ? data.context : {};
  let names = ctx.fileName;
  names = typeof names === "string" ? [names] : Array.isArray(names) ? names : [];
  if (names.includes("AGENTS.md")) return "unchanged";
  ctx.fileName = names.concat(["AGENTS.md"]);
  data.context = ctx;
  const created = !exists(file);
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
  return created ? "created" : "updated";
}

function projectCard(name) {
  const title = /^[\w .\-/()]+$/.test(name) ? name : JSON.stringify(name);
  return [
    "---", "type: Project", "title: " + title,
    "goal: <one line — what this project is for>",
    "invariants: []",
    "test_cmd: <the full test suite command>",
    "stage: prototype",
    "---", "## CARD",
    "goal: <the goal, in plain words>",
    "state: ADD installed — no work yet",
    "next: open your agent and run /add", "",
  ].join("\n");
}

// An agent file is ours only if its frontmatter names itself after a retired ADD agent.
function isOurAgent(file, stem) {
  let lines;
  try { lines = readText(file).split(/\r?\n/); } catch (_e) { return false; }
  if (lines[0].trim() !== "---") return false;
  for (const line of lines.slice(1)) {
    if (line.trim() === "---") return false;
    const m = line.match(/^name:\s*["']?([^"'\s]+)["']?\s*$/);
    if (m) return m[1] === stem;
  }
  return false;
}

function retireAgents(agentsDir, shown) {
  for (const stem of RETIRED_AGENTS) {
    const file = path.join(agentsDir, stem + ".md");
    if (!isLink(file) && exists(file) && isOurAgent(file, stem)) {
      rm(file);
      row("removed", shown(stem + ".md") + " (3.x agent)");
    }
  }
}

function step(what, fn) {
  try { return fn(); }
  catch (e) {
    const err = new Error("could not write " + what + ": " + (e && e.message ? e.message : e));
    err.step = true;
    throw err;
  }
}

function installProject(target, name) {
  const src = (p) => path.join(PKG_ROOT, p);
  const at = (p) => path.join(target, ...p.split("/"));
  out("Installing ADD " + version() + " into " + target);
  row("skill", ".claude/skills/add/ " + step(".claude/skills/add", () => replaceTree(src("skill/add"), at(".claude/skills/add"))));
  row("personas", ".add/personas-teacher/ " + step(".add/personas-teacher", () => replaceTree(src("personas-teacher"), at(".add/personas-teacher"))));
  row("routing", ".add/personas-index/ " + step(".add/personas-index", () => replaceTree(src("personas-index"), at(".add/personas-index"))));
  step(".add/personas", () => {
    let added = 0, kept = 0;
    fs.mkdirSync(at(".add/personas"), { recursive: true });
    for (const n of fs.readdirSync(src("personas")).sort()) {
      if (!n.endsWith(".md") || !fs.statSync(path.join(src("personas"), n)).isFile()) continue;
      const dest = path.join(at(".add/personas"), n);
      if (exists(dest)) { kept++; continue; }
      fs.copyFileSync(path.join(src("personas"), n), dest);
      added++;
    }
    row("starters", ".add/personas/: " + added + " added, " + kept + " kept");
  });
  step(".add/PROJECT.md", () => {
    const card = at(".add/PROJECT.md");
    const had = exists(card);
    if (!had) fs.writeFileSync(card, projectCard(name || path.basename(target)));
    row("project", ".add/PROJECT.md " + (had ? "kept" : "created"));
  });
  for (const d of ["specs", "milestones", "tasks"]) {
    step(".add/" + d, () => {
      fs.mkdirSync(at(".add/" + d), { recursive: true });
      if (fs.readdirSync(at(".add/" + d)).length === 0) fs.writeFileSync(at(".add/" + d + "/.gitkeep"), "");
    });
  }
  row("folders", ".add/specs/ .add/milestones/ .add/tasks/ ready");
  step(".add/.gitignore", () => {
    const file = at(".add/.gitignore");
    if (!exists(file)) {
      fs.writeFileSync(file, "# vendored copies the ADD installer refreshes - not project-authored\n" + IGNORED.join("\n") + "\n");
      return;
    }
    const cur = readText(file);
    const have = new Set(cur.split(/\r?\n/).map((l) => l.trim()));
    const missing = IGNORED.filter((l) => !have.has(l));
    if (missing.length) fs.writeFileSync(file, cur + (cur === "" || cur.endsWith("\n") ? "" : "\n") + missing.join("\n") + "\n");
  });
  for (const f of ["CLAUDE.md", "AGENTS.md"]) row("guidance", f + " " + step(f, () => writePointer(at(f))));
  for (const f of LEGACY_POINTERS) if (hasBlock(at(f))) row("guidance", f + " " + step(f, () => writePointer(at(f))));
  if (isDir(at(".gemini"))) row("gemini", ".gemini/settings.json " + step(".gemini/settings.json", () => writeGemini(at(".gemini"))));
  // 3.x leftovers go last: only once the new layout is in place.
  step(".add/tooling", () => {
    const tooling = at(".add/tooling");
    if (isLink(tooling) || (isDir(tooling) && (exists(path.join(tooling, "add.py")) || exists(path.join(tooling, "cli.py"))))) {
      rm(tooling);
      row("removed", ".add/tooling/ (the 3.x engine)");
    }
  });
  step(".claude/agents", () => retireAgents(at(".claude/agents"), (n) => ".claude/agents/" + n));
  out("Done. Next: open your agent in this folder and run /add");
  out("      (no slash commands? ask it to follow .claude/skills/add/SKILL.md)");
}

function installGlobal(env) {
  const home = env.HOME || os.homedir();
  const skillDir = path.join(home, ".claude", "skills", "add");
  out("Installing ADD " + version() + " for this user");
  row("skill", skillDir + " " + step(skillDir, () => replaceTree(path.join(PKG_ROOT, "skill", "add"), skillDir)));
  const agentsDir = path.join(home, ".claude", "agents");
  step(agentsDir, () => retireAgents(agentsDir, (n) => path.join(agentsDir, n)));
  const oldHome = env.ADD_HOME ? path.resolve(env.ADD_HOME)
    : env.XDG_DATA_HOME ? path.join(path.resolve(env.XDG_DATA_HOME), "add") : path.join(home, ".add");
  if (exists(path.join(oldHome, ".add-version"))) {
    row("note", oldHome + " is the 3.x global home; ADD 4.0 does not use it.");
    row("", "Delete it once you no longer need anything in it (its data/ holds 3.x snapshots).");
  }
  out("Done. Next: open your agent in any project and run /add");
}

function main(argv) {
  let a;
  try { a = parse(argv); }
  catch (e) {
    if (!(e instanceof Usage)) throw e;
    process.stderr.write("error: " + e.message + "\n" + usage().split("\n").slice(0, 2).join("\n") + "\n");
    return 2;
  }
  if (a.help) { out(usage()); return 0; }
  if (a.version) { out(version()); return 0; }
  for (const p of ["skill/add/SKILL.md", "personas", "personas-teacher", "personas-index"]) {
    if (!exists(path.join(PKG_ROOT, p))) {
      process.stderr.write("error: the package is incomplete - missing " + path.join(PKG_ROOT, p) + "\n");
      return 1;
    }
  }
  const target = path.resolve(a.positional[0] || ".");
  if (!a.global && !isDir(target)) {
    process.stderr.write("error: target directory does not exist: " + target + "\n");
    return 1;
  }
  try {
    if (a.global) installGlobal(process.env);
    else installProject(target, a.name);
  } catch (e) {
    if (!e.step) throw e;
    process.stderr.write("error: " + e.message + "\n" +
      "error: the install stopped part-way (the lines above landed); fix the cause and re-run - re-running is safe\n");
    return 1;
  }
  return 0;
}

if (require.main === module) {
  let code;
  try { code = main(process.argv.slice(2)); }
  catch (e) { process.stderr.write("error: " + (e && e.stack ? e.stack : e) + "\n"); code = 1; }
  process.exitCode = code;
}

module.exports = { pointerBlock: pointerBlock, GUIDE_BEGIN: GUIDE_BEGIN, GUIDE_END: GUIDE_END };
