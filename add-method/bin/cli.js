#!/usr/bin/env node
"use strict";

/**
 * @pilotspace/add installer.
 *
 *   npx @pilotspace/add init [targetDir] [--force] [--stage <stage>] [--name <name>] [--yes|--non-interactive]
 *
 * Installs the ADD skill + tooling + book into a target project:
 *   <target>/.claude/skills/add/   (the skill Claude loads)
 *   <target>/.add/tooling/         (add.py scaffolder + state tracker)
 *   <target>/.add/docs/            (the AIDD book — the trust layer)
 * It DROPS FILES ONLY — it does NOT run `add.py init`. Initialisation is deferred to
 * the AI (via `/add`, which runs `init --await-lock` to arm the v12 lock-down gate) or
 * to a CLI user. A pre-run plain init would grandfather-lock the gate before `/add` runs
 * AND consume the brownfield signal in the terminal, where the AI never sees it.
 *
 * One lazy, optional dependency (@clack/prompts) powers the interactive flow on a real
 * terminal; it is dynamic-import()ed ONLY on that path, so a non-interactive / CI run
 * (and the `--yes` / `--non-interactive` path) never loads it and degrades to plain text
 * if it is missing. No Python needed at install time. Designed for failure: verifies
 * sources exist before copying, never clobbers an existing skill, never throws on a
 * non-TTY or a failed clack import.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const crypto = require("crypto");

const PKG_ROOT = path.resolve(__dirname, "..");

function log(msg) { process.stdout.write(msg + "\n"); }
function warn(msg) { process.stderr.write("warn: " + msg + "\n"); }
function fail(msg) { process.stderr.write("error: " + msg + "\n"); process.exit(1); }

function parseArgs(argv) {
  // stage/name stay null unless EXPLICITLY passed — the engine's own `init`
  // defaults the stage and infers the name from the folder, so the manual-init
  // hint only echoes flags the user actually chose (shortest true command).
  const args = { _: [], force: false, check: false, noSkill: false, stage: null, name: null,
                 yes: false, nonInteractive: false, global: false, globalData: false, ruleFile: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--force") args.force = true;
    else if (a === "--check") args.check = true;
    // --global: ALSO install the managed layer to a shared home + register this project
    // (the per-project self-contained drop still runs). update --global refreshes all.
    else if (a === "--global") args.global = true;
    // --global-data: (implies --global) ALSO persist this project's user-data under
    // <home>/data/<key> keyed by path (opt-in, one-way snapshot).
    else if (a === "--global-data") args.globalData = true;
    // --yes / --non-interactive: skip all prompts, take defaults — the explicit
    // non-interactive selector the interactive() gate honors (CI/pipes do this too).
    else if (a === "--yes" || a === "-y") args.yes = true;
    else if (a === "--non-interactive") args.nonInteractive = true;
    // --no-skill: drop the engine + book ONLY, not the skill. The Claude Code plugin
    // already provides the `add` skill, so a plugin bootstrap uses this to materialize
    // .add/tooling/ + .add/docs/ into the project without a duplicate .claude/skills/add.
    else if (a === "--no-skill") args.noSkill = true;
    // --rule-file: write the ADD block to .claude/rules/add-workflows.md + reference it from
    // CLAUDE.md instead of inlining (auto-on for ccsk projects with a .ccsk/ dir).
    else if (a === "--rule-file") args.ruleFile = true;
    else if (a === "--stage" || a === "--name") {
      const v = argv[++i];
      // fail loudly on a trailing/abutting flag — never silently drop a value
      // the user tried to pass (parity with the pip twin's argparse error)
      if (v == null || v.startsWith("--")) fail(a + " requires a value");
      if (a === "--stage") args.stage = v; else args.name = v;
    }
    else if (a.startsWith("--")) warn("ignoring unknown flag " + a);
    else args._.push(a);
  }
  return args;
}

// --- agent detection: which coding agent is invoking the installer -----------
// ORDERED registry; detectAgent walks it top->bottom, first match wins, `generic` is
// the fallback. Mirror of _installer.py:AGENT_PROFILES. The per-agent env SIGNAL is
// best-effort (a mis-detect degrades to generic + is overridable in the clack confirm)
// — refine via a SPEC delta, never a hard fail.
const GENERIC_NEXT =
  "open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and " +
  "say what you want to build — the agent sets up the foundation, sizes it into a " +
  "milestone, and drives the build with you; you sign off once, at the lock-down.";

const AGENT_PROFILES = [
  { id: "claude", label: "Claude Code / Claude app", integration_file: "CLAUDE.md",
    env: ["CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"], envPrefix: null,
    next_step: "Open Claude Code and run `/add` — the skill drives intake -> milestone -> build." },
  { id: "codex", label: "Codex", integration_file: "AGENTS.md",
    env: ["CODEX_HOME"], envPrefix: "CODEX_",
    next_step: "Open Codex — it reads AGENTS.md; run `/add` or say what you want to build." },
  { id: "opencode", label: "OpenCode", integration_file: "AGENTS.md",
    env: ["OPENCODE"], envPrefix: "OPENCODE",
    next_step: "Open OpenCode — it reads AGENTS.md; say what you want to build." },
  { id: "cursor", label: "Cursor", integration_file: "AGENTS.md",
    env: ["CURSOR_AGENT", "CURSOR_TRACE_ID"], envPrefix: "CURSOR_",
    next_step: "Open Cursor — it reads AGENTS.md; say what you want to build." },
  { id: "windsurf", label: "Windsurf", integration_file: "AGENTS.md",
    env: ["WINDSURF", "WINDSURF_ENV"], envPrefix: "WINDSURF_",
    next_step: "Open Windsurf — Cascade reads AGENTS.md; say what you want to build." },
  { id: "trae", label: "Trae", integration_file: "AGENTS.md",
    env: ["TRAE_AI_IDE"], envPrefix: "TRAE_",
    next_step: "Open Trae — it reads AGENTS.md; say what you want to build." },
  { id: "copilot", label: "GitHub Copilot", integration_file: "AGENTS.md",
    env: ["COPILOT_AGENT"], envPrefix: null,   // NOT a GITHUB_ prefix — too broad (CI sets GITHUB_*)
    next_step: "Open GitHub Copilot — it reads AGENTS.md; say what you want to build." },
  { id: "cline", label: "Cline", integration_file: ".clinerules",
    env: ["CLINE_ACTIVE"], envPrefix: "CLINE_",
    next_step: "Open Cline — it reads .clinerules; say what you want to build." },
  { id: "aider", label: "Aider", integration_file: "AGENTS.md",
    env: [], envPrefix: "AIDER_",
    next_step: "Open Aider — add AGENTS.md to its context (`.aider.conf.yml` `read:` or `--read AGENTS.md`), then say what you want to build." },
  { id: "gemini", label: "Gemini CLI", integration_file: "AGENTS.md",
    env: ["GEMINI_CLI", "GEMINI_SANDBOX"], envPrefix: "GEMINI_",
    next_step: "Open Gemini CLI — ADD wired .gemini/settings.json to load AGENTS.md; say what you want to build." },
  { id: "generic", label: "your AI agent", integration_file: "AGENTS.md",
    env: [], envPrefix: null, next_step: GENERIC_NEXT },
];

// The SAME markers add.py:sync-guidelines uses, so init's sync-guidelines REPLACES this
// drop-time pointer in place (one block, never a duplicate).
const GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->";
const GUIDE_END = "<!-- ADD:END -->";

function profileMatches(profile, env) {
  for (const key of profile.env) { if (env[key]) return true; }
  if (profile.envPrefix) {
    for (const k of Object.keys(env)) {
      if (env[k] && k.startsWith(profile.envPrefix)) return true;
    }
  }
  return false;
}

// Pure, total, deterministic: same env -> same profile; never throws. Generic is last.
function detectAgent(env) {
  const generic = AGENT_PROFILES[AGENT_PROFILES.length - 1];
  for (const profile of AGENT_PROFILES.slice(0, -1)) {
    if (profileMatches(profile, env)) return profile;
  }
  return generic;
}

// A PATH lookup (no spawn): is an executable named `cmd` on PATH? Fail-soft -> null.
// Injectable into the enriched detector so the dev machine's installed agents never pollute tests.
function whichSync(cmd) {
  try {
    const dirs = (process.env.PATH || "").split(path.delimiter).filter(Boolean);
    const exts = process.platform === "win32"
      ? (process.env.PATHEXT || ".EXE;.CMD;.BAT").split(";")
      : [""];
    for (const dir of dirs) {
      for (const ext of exts) {
        const hit = path.join(dir, cmd + ext);
        if (fs.existsSync(hit)) return hit;
      }
    }
  } catch (_e) { /* fail-soft */ }
  return null;
}

// ADDITIVE enrichment for the INTERACTIVE default — never replaces detectAgent (which stays
// env-only; test_agent_detect pins it, the non-interactive write uses it). Precedence:
// env signal (authoritative) > a CLAUDE.md in the target (repo signal; AGENTS.md is ambiguous,
// so it does NOT pick) > an installed agent CLI (machine signal; PATH lookup only) > generic.
// Pure + fail-soft: a throwing probe reads as absent. `which` is injectable for hermetic tests.
function detectAgentEnriched(env, target, which) {
  which = which || whichSync;
  const base = detectAgent(env);
  if (base.id !== "generic") return base;              // env signal wins
  const byId = {};
  for (const p of AGENT_PROFILES) byId[p.id] = p;
  try {
    if (target && fs.existsSync(path.join(target, "CLAUDE.md"))) return byId.claude;   // repo signal
  } catch (_e) { /* fall through */ }
  for (const id of ["claude", "codex", "opencode", "cursor", "windsurf", "trae", "copilot", "cline", "aider"]) {
    try { if (which(id)) return byId[id]; } catch (_e) { /* probe absent */ }   // machine signal
  }
  return base;                                         // generic
}

// Fail-soft pre-flight summary for the INTERACTIVE path (the caller gates):
// "Pre-flight: git <✓|–> · python3 <✓|–> · agent: <label>". Each probe is a PATH lookup;
// a failure reads as absent. Never throws.
function readinessLine(env, target, which) {
  env = env || process.env;
  which = which || whichSync;
  const caps = terminalCaps(env, process.stdout);
  const tick = caps.unicode ? "✓" : "+";
  const cross = caps.unicode ? "–" : "-";
  const sep = caps.unicode ? " · " : " | ";
  const have = (cmd) => { try { return !!which(cmd); } catch (_e) { return false; } };
  let label;
  try { label = detectAgentEnriched(env, target, which).label; }
  catch (_e) { label = "your AI agent"; }
  const mark = (ok) => (ok ? tick : cross);
  return "Pre-flight: git " + mark(have("git")) + sep +
         "python3 " + mark(have("python3")) + sep + "agent: " + label;
}

function agentPointerBlock(profile) {
  return (
    GUIDE_BEGIN + "\n" +
    "## ADD — how to work in this repo\n" +
    "\n" +
    "This project uses **ADD (AI-Driven Development)**. The engine + book are installed.\n" +
    "To begin: run `python3 .add/tooling/add.py status` (the resume point), read\n" +
    "`.add/PROJECT.md`, then `python3 .add/tooling/add.py guide` for the current phase.\n" +
    "\n" +
    profile.next_step + "\n" +
    "\n" +
    "This pointer is replaced by the full guideline block when `add.py sync-guidelines`\n" +
    "runs (at `/add`->init). Edit outside the markers, not inside.\n" +
    GUIDE_END
  );
}

// Inject the ADD pointer into <target>/<integration_file>, mirroring add.py:_inject_block.
// created|updated|unchanged|skipped. Only the marked region is (re)written; content outside
// the markers is preserved; a real change backs up <file>.bak first. Fail-soft (warn+skip).
function writeAgentPointer(target, profile) {
  const dest = path.join(target, profile.integration_file);
  const block = agentPointerBlock(profile);
  try {
    if (fs.existsSync(dest)) {
      const current = fs.readFileSync(dest, "utf8");
      const begin = current.indexOf(GUIDE_BEGIN);
      let next;
      if (begin !== -1) {
        const endIdx = current.indexOf(GUIDE_END, begin);
        if (endIdx !== -1) {
          next = current.slice(0, begin) + block + current.slice(endIdx + GUIDE_END.length);
        } else {                       // begin with no end: corrupt — append fresh
          next = current.replace(/\n+$/, "") + "\n\n" + block + "\n";
        }
      } else {                         // no block yet — append, keep user content
        next = current.replace(/\n+$/, "") + "\n\n" + block + "\n";
      }
      if (next === current) return "unchanged";
      fs.writeFileSync(dest + ".bak", current);   // rollback path before mutate
      fs.writeFileSync(dest, next);
      return "updated";
    }
    fs.writeFileSync(dest, block + "\n");
    return "created";
  } catch (e) {
    warn("could not write " + profile.integration_file + " — " +
         (e && e.message ? e.message : e) + "; skipped");
    return "skipped";
  }
}

// --- rule-file mode: ccsk-style relocation of the CLAUDE.md block ---------------------
// Mirror of add.py / _installer.py rule-file logic (twins by duplication). For ccsk projects
// (.ccsk/ dir) or an explicit --rule-file, the ADD pointer goes to .claude/rules/add-workflows.md
// and CLAUDE.md keeps only a reference bullet. CLAUDE-only — AGENTS.md/.clinerules stay inline.
const RULES_FILE_REL = path.join(".claude", "rules", "add-workflows.md");
const WORKFLOW_HEADINGS = ["Rules & Workflows", "Workflows", "Rules"];
const RULE_REF_LINE = "- ADD (AI-Driven Development) Workflows rules: ./.claude/rules/add-workflows.md";

// True when the ADD block belongs in .claude/rules/add-workflows.md instead of inline.
// Re-derived from disk: explicit flag, a ccsk project (.ccsk/), or a rule file already present.
function ruleFileMode(root, flag) {
  if (flag) return true;
  try {
    if (fs.existsSync(path.join(root, ".ccsk")) &&
        fs.statSync(path.join(root, ".ccsk")).isDirectory()) return true;
    if (fs.existsSync(path.join(root, RULES_FILE_REL))) return true;
  } catch (_e) { /* fail-soft */ }
  return false;
}

// Remove an inline ADD:BEGIN..END region (migration), collapsing the gap. An unterminated
// BEGIN is left as-is rather than eating the rest of the file.
function stripInlineBlock(text) {
  const begin = text.indexOf(GUIDE_BEGIN);
  if (begin === -1) return text;
  let end = text.indexOf(GUIDE_END, begin);
  if (end === -1) return text;
  end += GUIDE_END.length;
  const head = text.slice(0, begin).replace(/\n+$/, "");
  const tail = text.slice(end).replace(/^\n+/, "");
  if (head && tail) return head + "\n\n" + tail;
  return head || tail;
}

// Insert the ADD rule-file bullet under an existing Workflows/Rules heading, or append a fresh
// '## Workflows' section. Caller guarantees the bullet is absent.
function insertRuleReference(text) {
  const lines = text.split("\n");
  let headingIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(#{1,6})\s+(.*?)\s*$/);
    if (m && WORKFLOW_HEADINGS.some((h) => m[2].trim().toLowerCase() === h.toLowerCase())) {
      headingIdx = i;
      break;
    }
  }
  if (headingIdx === -1) {
    const body = text.replace(/\n+$/, "");
    const sep = body ? "\n\n" : "";
    return body + sep + "## Workflows\n\n" + RULE_REF_LINE + "\n";
  }
  const level = lines[headingIdx].match(/^(#{1,6})/)[1].length;
  let end = lines.length;
  for (let j = headingIdx + 1; j < lines.length; j++) {
    const m = lines[j].match(/^(#{1,6})\s+/);
    if (m && m[1].length <= level) { end = j; break; }
  }
  let insertAt = headingIdx + 1;
  for (let j = headingIdx + 1; j < end; j++) {
    if (lines[j].trim()) insertAt = j + 1;
  }
  lines.splice(insertAt, 0, RULE_REF_LINE);
  return lines.join("\n");
}

// Make CLAUDE.md reference the ADD rule file under a Workflows/Rules heading, migrating any prior
// inline ADD block out. created|updated|unchanged|skipped; .bak on change; fail-soft.
function ensureClaudeReference(claudeMd) {
  try {
    const existed = fs.existsSync(claudeMd);
    const current = existed ? fs.readFileSync(claudeMd, "utf8") : "";
    let next = stripInlineBlock(current);
    if (next.indexOf("add-workflows.md") === -1) next = insertRuleReference(next);
    if (!next.endsWith("\n")) next += "\n";
    if (next === current) return "unchanged";
    if (existed) fs.writeFileSync(claudeMd + ".bak", current);
    fs.writeFileSync(claudeMd, next);
    return existed ? "updated" : "created";
  } catch (e) {
    warn("could not write CLAUDE.md — " + (e && e.message ? e.message : e) + "; skipped");
    return "skipped";
  }
}

// Rule-file variant of writeAgentPointer for the Claude profile: write the ADD pointer block to
// .claude/rules/add-workflows.md and leave a reference in CLAUDE.md. Fail-soft.
function writeRuleFilePointer(target, profile) {
  const rulesPath = path.join(target, RULES_FILE_REL);
  const block = agentPointerBlock(profile);
  try {
    if (fs.existsSync(rulesPath)) {
      const current = fs.readFileSync(rulesPath, "utf8");
      const begin = current.indexOf(GUIDE_BEGIN);
      let next;
      if (begin !== -1) {
        const endIdx = current.indexOf(GUIDE_END, begin);
        if (endIdx !== -1) {
          next = current.slice(0, begin) + block + current.slice(endIdx + GUIDE_END.length);
        } else {
          next = current.replace(/\n+$/, "") + "\n\n" + block + "\n";
        }
      } else {
        next = current.replace(/\n+$/, "") + "\n\n" + block + "\n";
      }
      if (next !== current) {
        fs.writeFileSync(rulesPath + ".bak", current);
        fs.writeFileSync(rulesPath, next);
      }
    } else {
      fs.mkdirSync(path.dirname(rulesPath), { recursive: true });
      fs.writeFileSync(rulesPath, block + "\n");
    }
  } catch (e) {
    warn("could not write " + RULES_FILE_REL + " — " + (e && e.message ? e.message : e) + "; skipped");
    return "skipped";
  }
  ensureClaudeReference(path.join(target, "CLAUDE.md"));
  return "ok";
}

// --- interactive layer (clack on a real TTY; plain text everywhere else) -----
// Designed-for-failure: any doubt (non-TTY, CI, --yes, a failed import, an
// un-promptable stream) degrades to the EXACT plain-text path below. The clack
// import is dynamic + lazy (clack 1.x is ESM-only) so a non-interactive / CI run
// never loads it. A test seam (ADD_INSTALLER_FORCE_INTERACTIVE) reaches the branch
// without a PTY: "1" forces interactive, "fail" forces it but throws on import.

function interactive(args) {
  if (args.yes || args.nonInteractive) return false;       // explicit opt-out wins
  const seam = process.env.ADD_INSTALLER_FORCE_INTERACTIVE;
  if (seam === "1" || seam === "fail") return true;        // documented test seam
  return Boolean(process.stdout.isTTY && process.stdin.isTTY) && !process.env.CI;
}

async function loadClack() {
  // honors the "fail" seam so the clack_unavailable fallback is testable without
  // uninstalling the dependency.
  if (process.env.ADD_INSTALLER_FORCE_INTERACTIVE === "fail") {
    throw new Error("forced clack import failure (test seam)");
  }
  return import("@clack/prompts");
}

// --- brand + feature showcase (interactive path only; fail-soft) -------------
// Wordmark + value line + the 7-step Specify->Observe loop, rendered BEFORE the first
// prompt on the interactive path only — so the non-interactive byte stream is unchanged.
// The 7 labels are the real ADD phases (grounded in the method, never invented). Fail-soft:
// any draw error is swallowed so a banner can never abort the install. No color is emitted
// (default accent: none); the glyphs / tagline / accent are a SWAPPABLE content slot.
const BRAND_LOOP = ["Specify", "Scenarios", "Contract", "Tests", "Build", "Verify", "Observe"];

function terminalCaps(env, stream) {
  const width = Number(env.COLUMNS) || (stream && stream.columns) || 80;
  const enc = env.LC_ALL || env.LC_CTYPE || env.LANG || "";
  const unicode = /utf-?8/i.test(enc) && !env.ADD_INSTALLER_ASCII;
  return { width: width, unicode: unicode };
}

function brandLines(caps) {
  const head = (caps.unicode && caps.width >= 40)
    ? [
        " █████╗ ██████╗ ██████╗",
        "██╔══██╗██╔══██╗██╔══██╗",
        "███████║██║  ██║██║  ██║",
        "██╔══██║██║  ██║██║  ██║",
        "██║  ██║██████╔╝██████╔╝",
        "╚═╝  ╚═╝╚═════╝ ╚═════╝ ",
      ]
    : ["ADD"];                                  // plain-ASCII wordmark fallback
  const arrow = caps.unicode ? " → " : " -> ";
  const dash = caps.unicode ? " — " : " - ";
  return head.concat([
    "AI-Driven Development",
    "",
    "Spec-and-tests-first development" + dash + "any agent, through the CLI, no lost context.",
    "The loop ADD drives with you:",
    "  " + BRAND_LOOP.join(arrow),
    "",
  ]);
}

function renderBrand(env, stream) {
  try {
    env = env || process.env;
    stream = stream || process.stdout;
    stream.write(brandLines(terminalCaps(env, stream)).join("\n") + "\n");
  } catch (_e) { /* fail-soft: a banner must never abort the install */ }
}

// The two install-scope choices — global-first (recommended) vs self-contained. PURE +
// exported (the pip _scope_options twin) so the recommended pick + its why are hermetically
// testable; the interactive scope SELECT renders these.
function scopeOptions() {
  return [
    { value: "global", label: "Global home + this project",
      hint: "a shared ~/.add + ~/.claude/skills/add reused by every project (this project still gets its own copy)",
      recommended: true },
    { value: "project", label: "This project only",
      hint: "self-contained + git-tracked: nothing is written outside this folder" },
  ];
}

// Returns { cancelled, target, profile, global }. A cancel happens BEFORE any file is written, so a
// cancelled run leaves the target untouched. Without a real TTY to read (the forced
// test seam), we cannot prompt — abort safely rather than hang. `askScope` is false when an
// explicit --global already chose the scope (honored, not re-asked).
async function runClackPreamble(clack, target, detected, askScope) {
  renderBrand(process.env, process.stdout);   // brand + showcase BEFORE the first prompt
  try { log(readinessLine(process.env, target)); }   // pre-flight: git · python3 · agent (fail-soft)
  catch (_e) { /* the pre-flight line is informational — never block the install */ }
  clack.intro("ADD — AI-Driven Development");
  if (!process.stdin.isTTY) return { cancelled: true, target: target };
  const chosen = await clack.text({
    message: "Install ADD into which directory?",
    initialValue: target, defaultValue: target,
  });
  if (clack.isCancel(chosen)) return { cancelled: true, target: target };
  const ok = await clack.confirm({ message: "Write the ADD skill + tooling + book here?" });
  if (clack.isCancel(ok) || !ok) return { cancelled: true, target: target };
  // global-first SCOPE step (after the target confirm, before agent-detect) — recommended
  // global home, explicit pick; skipped when --global already chose. global stays ADDITIVE.
  let scopeGlobal = false;
  if (askScope) {
    const opts = scopeOptions();
    const scope = await clack.select({
      message: "Install scope?",
      options: opts.map((o) => ({ value: o.value, label: o.label, hint: o.hint })),
      initialValue: opts.find((o) => o.recommended).value,
    });
    if (clack.isCancel(scope)) return { cancelled: true, target: target };
    scopeGlobal = scope === "global";
  }
  // agent-detect STEP (seeded delta: a STEP in THIS flow, via the clack ui layer) — the
  // user confirms or overrides the detected agent before any file is written.
  const picked = await clack.select({
    message: "Set up for which agent? (detected: " + detected.label + ")",
    options: AGENT_PROFILES.map((p) => ({ value: p.id, label: p.label })),
    initialValue: detected.id,
  });
  if (clack.isCancel(picked)) return { cancelled: true, target: target };
  const profile = AGENT_PROFILES.find((p) => p.id === picked) || detected;
  // LAST optional step — a one-line build intent for `/add` to read. Fully optional: a clack
  // cancel or an empty answer SKIPS (intent ""); the install has already been confirmed, so this
  // never aborts. A NOTE only — it never triggers init.
  let intent = "";
  const typed = await clack.text({
    message: "What do you want to build first? (optional — Enter to skip)",
    placeholder: "", defaultValue: "",
  });
  if (!clack.isCancel(typed) && typed) intent = String(typed).trim();
  return { cancelled: false, target: String(chosen || target), profile: profile, global: scopeGlobal, intent: intent };
}

// Persist `intent` as a NOTE at <target>/.add/.intent for `/add` to read — iff non-empty.
// DEFERRED-INIT: inert text only; never runs add.py/init, never touches state.json. Fail-soft
// (a write error is swallowed — the note is best-effort, never a reason to fail the install).
// Returns whether the note was written. Twin of _installer.py:_write_intent_note.
function writeIntentNote(target, intent) {
  const text = (intent || "").trim();
  if (!text) return false;
  try {
    const addDir = path.join(target, ".add");
    fs.mkdirSync(addDir, { recursive: true });        // .add/ exists post-drop; recursive mkdir is a no-op then
    fs.writeFileSync(path.join(addDir, ".intent"), text + "\n");
    return true;
  } catch (_e) { return false; }
}

// Merge <target>/.gemini/settings.json so context.fileName includes "AGENTS.md" — the pointer
// ADD writes for the gemini profile. Gemini CLI defaults to GEMINI.md and lets it win when both
// exist, so AGENTS.md must be named in the config to load. Read-merge-write: preserves every other
// key; idempotent; fail-soft (an unparsable/unwritable file warns + skips, never aborts the drop).
// Returns created|updated|unchanged|skipped. Twin of _installer.py:_write_gemini_settings.
function writeGeminiSettings(target) {
  const geminiDir = path.join(target, ".gemini");
  const settings = path.join(geminiDir, "settings.json");
  try {
    let data = {};
    let created = true;
    if (fs.existsSync(settings)) {
      created = false;
      let raw;
      try { raw = fs.readFileSync(settings, "utf8"); data = JSON.parse(raw); }
      catch (_e) {
        warn("could not parse " + settings + " — leaving it untouched; skipped");
        return "skipped";
      }
      if (data === null || typeof data !== "object" || Array.isArray(data)) {
        warn(settings + " is not a JSON object — leaving it untouched; skipped");
        return "skipped";
      }
    }
    let context = data.context;
    if (context === null || typeof context !== "object" || Array.isArray(context)) context = {};
    let names = context.fileName;
    if (typeof names === "string") names = [names];
    else if (!Array.isArray(names)) names = [];
    if (names.includes("AGENTS.md")) return "unchanged";   // idempotent
    names = names.concat(["AGENTS.md"]);
    context.fileName = names;
    data.context = context;
    fs.mkdirSync(geminiDir, { recursive: true });
    fs.writeFileSync(settings, JSON.stringify(data, null, 2) + "\n");
    return created ? "created" : "updated";
  } catch (e) {
    warn("could not write " + settings + " — " + (e && e.message ? e.message : e) + "; skipped");
    return "skipped";                                      // design-for-failure: never abort the install
  }
}

// The drop — now a RECONCILE: restore missing managed trees + refresh present ones
// (sweep orphans) + report per-tree status. Byte-compatible handoff with the prior
// installer. The interactive path resolves a target then calls straight into this.
function dropFiles(args, target, profile, intent) {
  profile = profile || detectAgent(process.env);
  log("Installing ADD into " + target);
  reconcile(args, target);

  // Agent detection: write THE detected agent's integration file (a marker-delimited
  // pointer init's sync-guidelines later supersedes) + tailor the closing next-step.
  // Best-effort + fail-soft — never aborts the successful drop above.
  // Rule-file mode (ccsk projects / --rule-file) relocates the CLAUDE.md pointer to
  // .claude/rules/add-workflows.md + a reference — CLAUDE-only; other agents stay inline.
  if (profile.integration_file === "CLAUDE.md" && ruleFileMode(target, args.ruleFile)) {
    if (fs.existsSync(path.join(target, ".ccsk"))) {
      log("  ccsk detected — ADD rules go to .claude/rules/add-workflows.md");
    }
    writeRuleFilePointer(target, profile);
  } else {
    writeAgentPointer(target, profile);
  }

  // Gemini CLI auto-loads GEMINI.md, not AGENTS.md — so for the gemini profile we ALSO merge
  // .gemini/settings.json (context.fileName) to load the AGENTS.md pointer. Fail-soft + idempotent.
  if (profile.id === "gemini") writeGeminiSettings(target);

  // Optional build-intent NOTE for `/add` to read — "" (skip / non-interactive) -> no-op.
  writeIntentNote(target, intent);

  // NO step 4: the installer DROPS FILES ONLY. Initialisation is deferred to the AI
  // (via `/add`) or a CLI user — a pre-run plain `add.py init` would grandfather-lock
  // the v12 lock-down gate before `/add` runs (see file header). So no Python is run here.
  log("\nDone. " + (args.noSkill ? "The engine + book are" : "The `add` skill + tooling are") +
      " installed (no project state yet — that's intentional).");
  if (profile.id === "generic") {
    // the generic onramp line — kept literal so the conversational-only handoff is stable
    log("Next:  open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and say what you want to build — the agent");
    log("       sets up the foundation, sizes it into a milestone, and drives the build with you;");
    log("       you sign off once, at the lock-down.");
  } else {
    log("Detected " + profile.label + ".");
    log("Next:  " + profile.next_step);
  }
  log("");
}

async function cmdInit(args) {
  const target = path.resolve(args._[0] || ".");
  if (!fs.existsSync(target)) fail("target directory does not exist: " + target);

  let chosenTarget = target;
  let profile = detectAgent(process.env);     // default: non-interactive / fallback
  let intent = "";                            // build-intent NOTE — stays "" on the non-interactive path
  if (interactive(args)) {
    let clack = null;
    try { clack = await loadClack(); }
    catch (_e) { warn("clack unavailable — falling back to plain-text install"); }
    if (clack) {
      // enriched seed (env > CLAUDE.md > installed CLI) for the agent-select default; the user
      // still confirms/overrides before any write. The non-interactive write below stays env-only.
      const detected = detectAgentEnriched(process.env, target);
      // an explicit --global/--global-data already chose the scope — don't re-ask it.
      const askScope = !(args.global || args.globalData);
      const outcome = await runClackPreamble(clack, target, detected, askScope);
      if (outcome.cancelled) {
        // the exit code IS the contract; a closed-pipe stdout (EPIPE) must not
        // mask the cancel — guard the courtesy message, never let it throw.
        try { clack.cancel("Installation cancelled — nothing was written."); }
        catch (_e) { /* stdout unavailable (e.g. closed pipe) — exit code carries it */ }
        process.exit(130);                // user_cancelled: nothing written
      }
      chosenTarget = path.resolve(outcome.target);
      if (!fs.existsSync(chosenTarget)) fail("target directory does not exist: " + chosenTarget);
      if (outcome.profile) profile = outcome.profile;   // honor the user's override
      if (outcome.global) args.global = true;           // honor the interactive scope pick (additive)
      intent = outcome.intent || "";                    // optional build-intent NOTE (written after the drop)
    }
  }
  if (args.globalData) args.global = true;   // --global-data implies --global (need a home)
  // OPT-IN global home, BEFORE the per-project drop (fail-closed if the home is unwritable
  // or its registry is corrupt — the package + the self-contained default stay usable).
  if (args.global) installGlobal(args, chosenTarget);
  dropFiles(args, chosenTarget, profile, intent);
  // OPT-IN data persist, AFTER the drop (one-way snapshot of existing user-data).
  if (args.globalData) installGlobalData(chosenTarget);
}

// --- update: re-materialize the managed layer without a re-install -----------
// The managed trees (ship-controlled). `update` clean-replaces each, so a file removed
// upstream leaves no orphan — and never touches .add/state.json, PROJECT.md, milestones,
// tasks, or archive (user data). Pure file-copy (npm <-> pip parity with _installer.py).
const MANAGED = [
  ["skill/add", [".claude", "skills", "add"], false],
  ["tooling", [".add", "tooling"], true],
  ["docs", [".add", "docs"], false],
];
const STAMP_FILE = ".add-version";

function pkgVersion() {
  try { return require(path.join(PKG_ROOT, "package.json")).version; }
  catch (_e) { return "0.0.0"; }
}

function readStamp(addDir) {
  const p = path.join(addDir, STAMP_FILE);
  if (!fs.existsSync(p)) return null;
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (_e) { return null; }
}

function writeStamp(addDir, version, channel) {
  fs.mkdirSync(addDir, { recursive: true });
  fs.writeFileSync(
    path.join(addDir, STAMP_FILE),
    JSON.stringify({ version: version, channel: channel || "npm", installed_at: new Date().toISOString() }, null, 2) + "\n"
  );
}

function cleanReplaceTree(src, dest, stripTests) {
  if (!fs.existsSync(src)) fail("missing packaged source: " + src);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (fs.existsSync(dest)) fs.rmSync(dest, { recursive: true, force: true });
  fs.cpSync(src, dest, { recursive: true });
  if (stripTests) {
    fs.rmSync(path.join(dest, "__pycache__"), { recursive: true, force: true });
    for (const entry of fs.readdirSync(dest)) {
      if (/^test_.*\.py$/.test(entry)) fs.rmSync(path.join(dest, entry), { force: true });
    }
  }
}

const TREE_LABEL = { "skill/add": "skill", "tooling": "tooling", "docs": "docs" };

// Per managed tree: "missing" (dest absent OR empty) or "present".
function managedStatus(target) {
  const status = {};
  for (const [sub, destParts] of MANAGED) {
    const dest = path.join(target, ...destParts);
    const present = fs.existsSync(dest) && fs.readdirSync(dest).length > 0;
    status[sub] = present ? "present" : "missing";
  }
  return status;
}

// reconcile: restore-missing + refresh-present (sweep orphans) across the managed trees,
// reporting per-tree status. Honors --no-skill (the plugin provides the skill). Touches
// ONLY managed trees — never user data. Prechecks ALL sources first (design-for-failure:
// a corrupt package leaves the target untouched).
function reconcile(args, target, srcRoot) {
  srcRoot = srcRoot || PKG_ROOT;   // default: the package; the global home feeds propagation
  const trees = MANAGED.filter(([sub]) => !(sub === "skill/add" && args.noSkill));
  for (const [sub] of trees) {
    if (!fs.existsSync(path.join(srcRoot, sub))) {
      fail("missing packaged source: " + path.join(srcRoot, sub));
    }
  }
  const status = managedStatus(target);
  for (const [sub, destParts, stripTests] of trees) {
    cleanReplaceTree(path.join(srcRoot, sub), path.join(target, ...destParts), stripTests);
    const dest = destParts.join("/");
    if (status[sub] === "missing") {
      log("  ✓ restored  " + TREE_LABEL[sub].padEnd(8) + "-> " + dest + "  (was missing)");
    } else {
      log("  ✓ refreshed " + TREE_LABEL[sub].padEnd(8) + "-> " + dest);
    }
  }
  return status;
}

// --- global home: an OPT-IN shared install (engine+book+skill) updated for all projects ----
// Resolution is PURE + total (never throws); the home MIRRORS the bundled managed layer so
// `update --global` propagation reuses reconcile() unchanged. Mirror of _installer.py.
function resolveGlobalHome(env) {
  // ADD_HOME (set, non-empty) -> else XDG_DATA_HOME/add -> else <HOME>/.add. Reads HOME from
  // the env mapping (never $HOME directly) so tests can inject a hermetic home.
  env = env || process.env;
  if (env.ADD_HOME) return path.resolve(env.ADD_HOME);
  if (env.XDG_DATA_HOME) return path.join(path.resolve(env.XDG_DATA_HOME), "add");
  return path.join(env.HOME || os.homedir(), ".add");
}

function claudeSkillsDir(env) {
  env = env || process.env;
  return path.join(env.HOME || os.homedir(), ".claude", "skills", "add");
}

function registryPath(home) { return path.join(home, "registry.json"); }

// [] when ABSENT; THROWS on present-but-corrupt so the caller fails LOUD (never a silent
// empty-list no-op that quietly skips every registered project).
function readRegistry(home) {
  const p = registryPath(home);
  if (!fs.existsSync(p)) return [];
  let data;
  try { data = JSON.parse(fs.readFileSync(p, "utf8")); }
  catch (_e) { throw new Error("registry_corrupt"); }
  if (!Array.isArray(data)) throw new Error("registry_corrupt");
  return data;
}

// ATOMIC (temp + rename), de-duplicated preserving first-seen order.
function writeRegistry(home, paths) {
  fs.mkdirSync(home, { recursive: true });
  const seen = [];
  for (const p of paths) { if (!seen.includes(p)) seen.push(p); }
  const target = registryPath(home);
  const tmp = target + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(seen, null, 2) + "\n");
  fs.renameSync(tmp, target);   // atomic on the same filesystem (POSIX + Windows)
}

// The home mirrors the bundled layout (skill/add + tooling + docs at the SAME relative paths
// the package ships) so reconcile(args, project, home) reuses MANAGED unchanged.
const GLOBAL_TREES = [
  ["skill/add", ["skill", "add"], false],
  ["tooling", ["tooling"], true],
  ["docs", ["docs"], false],
];

// Clean-replace the bundled managed layer INTO <home> (canonical mirror), then DEPLOY the
// skill to ~/.claude/skills/add. Throws if a dir can't be written (caller -> home_unwritable).
// Prechecks ALL sources first (design-for-failure: a corrupt package leaves the home as-is).
function reconcileGlobal(home, claudeDir, noSkill) {
  for (const [sub] of GLOBAL_TREES) {
    if (!fs.existsSync(path.join(PKG_ROOT, sub))) {
      fail("missing packaged source: " + path.join(PKG_ROOT, sub));
    }
  }
  for (const [sub, destParts, stripTests] of GLOBAL_TREES) {
    cleanReplaceTree(path.join(PKG_ROOT, sub), path.join(home, ...destParts), stripTests);
  }
  if (!noSkill) cleanReplaceTree(path.join(home, "skill", "add"), claudeDir, false);
}

// --- global DATA: an OPT-IN per-project user-data snapshot under <home>/data/<key> ----------
// Strictly additive; copies ONLY user-data (managed trees + transient excluded), clean-replaced,
// one-way (project->home). Mirror of _installer.py (identical key + include/exclude rule).
const DATA_EXCLUDE = ["tooling", "docs", ".update-cache", STAMP_FILE];   // managed trees + meta

// data_key twin: <sanitized-basename>-<sha1(abspath_utf8)[:12]>. Pure · total · separator-free.
function dataKey(projectAbspath) {
  const p = String(projectAbspath);
  const digest = crypto.createHash("sha1").update(p, "utf8").digest("hex").slice(0, 12);
  const base = (path.basename(p) || "root").replace(/[^A-Za-z0-9._-]/g, "_");
  return base + "-" + digest;
}

// A top-level .add/ entry is user-data unless it is a managed tree or a transient artifact.
function isUserData(name) {
  if (DATA_EXCLUDE.includes(name)) return false;
  if (name.startsWith("scope-snapshot")) return false;
  if (name.includes("pre-archive-bak")) return false;
  if (name.endsWith(".bak.json")) return false;
  return true;
}

// Clean-replace a project's USER-DATA into <home>/data/<key>. true=persisted, false=skipped
// (no .add or no user-data — an honest skip). Throws if the data dir can't be written.
function persistData(home, projectAbspath) {
  const addDir = path.join(projectAbspath, ".add");
  if (!fs.existsSync(addDir)) return false;
  const entries = fs.readdirSync(addDir).filter(isUserData);
  if (entries.length === 0) return false;
  const dest = path.join(home, "data", dataKey(projectAbspath));
  if (fs.existsSync(dest)) fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(dest, { recursive: true });
  for (const e of entries) {
    fs.cpSync(path.join(addDir, e), path.join(dest, e), { recursive: true });
  }
  return true;
}

// init --global-data: persist this project's user-data after the per-project drop. Resolves the
// SAME realpath the registry uses (so the key matches). Skip+notice when empty; fail on unwritable.
function installGlobalData(chosenTarget) {
  const home = resolveGlobalHome(process.env);
  let resolved = chosenTarget;
  try { resolved = fs.realpathSync(chosenTarget); } catch (_e) { /* fall back to the abspath */ }
  let persisted;
  try { persisted = persistData(home, resolved); }
  catch (e) {
    fail("cannot write global data " + path.join(home, "data", dataKey(resolved)) +
         " — " + (e && e.message ? e.message : e));
  }
  if (persisted) log("  ✓ persisted data -> " + path.join(home, "data", dataKey(resolved)));
  else log("  (no project data to persist yet — run /add to create one, then re-run --global-data)");
}

// init --global: install the managed layer ONCE to the shared home + register this project,
// fail-closed BEFORE the per-project drop. Returns the resolved target for the normal drop.
function installGlobal(args, chosenTarget) {
  const home = resolveGlobalHome(process.env);
  const claudeDir = claudeSkillsDir(process.env);
  try { reconcileGlobal(home, claudeDir, args.noSkill); }                 // home_unwritable
  catch (e) { fail("cannot write global home " + home + " — " + (e && e.message ? e.message : e)); }
  writeStamp(home, pkgVersion(), "global");
  let reg;
  try { reg = readRegistry(home); }                                        // registry_corrupt
  catch (_e) { fail("global registry " + registryPath(home) + " is corrupt — fix or delete it; not registering"); }
  let resolved = chosenTarget;
  try { resolved = fs.realpathSync(chosenTarget); } catch (_e) { /* fall back to the abspath */ }
  reg.push(resolved);
  try { writeRegistry(home, reg); }                                        // atomic + dedup
  catch (e) { fail("cannot write global registry " + registryPath(home) + " — " + (e && e.message ? e.message : e)); }
  log("  ✓ global home ready at " + home);
  log("  ✓ registered " + resolved + " (registry: " + readRegistry(home).length + ")");
}

// update --global: refresh the home mirror + skill, then propagate to every registered+existing
// project via reconcile(.., home); prune vanished projects (warn) + rewrite the registry atomically.
function cmdUpdateGlobal(args) {
  const home = resolveGlobalHome(process.env);
  const claudeDir = claudeSkillsDir(process.env);
  if (!fs.existsSync(path.join(home, STAMP_FILE))) {
    fail("no global ADD install at " + home + " (.add-version not found) — run `init --global` first");
  }
  // Read the registry BEFORE refreshing the home — a corrupt registry fails closed with ZERO
  // writes (never a silent empty-list no-op), leaving the file for the user to fix or delete.
  let reg;
  try { reg = readRegistry(home); }
  catch (_e) { fail("global registry " + registryPath(home) + " is corrupt — fix or delete it; not propagating"); }
  try { reconcileGlobal(home, claudeDir, args.noSkill); }
  catch (e) { fail("cannot write global home " + home + " — " + (e && e.message ? e.message : e)); }
  const version = pkgVersion();
  writeStamp(home, version, "global");
  const kept = [];
  let pruned = 0;
  for (const p of reg) {
    if (!fs.existsSync(p)) { log("  ⚠ registered project " + p + " not found — pruning"); pruned++; continue; }
    reconcile(args, p, home);     // standard MANAGED map, sourced from the home mirror
    // re-persist an opted-in project (one that already has a snapshot); a vanished
    // project's snapshot is KEPT above (the backup outlives the dir).
    if (fs.existsSync(path.join(home, "data", dataKey(p)))) persistData(home, p);
    kept.push(p);
  }
  writeRegistry(home, kept);
  log("ADD " + version + " · global home + " + kept.length + " project(s) reconciled" +
      (pruned ? " (" + pruned + " pruned)" : "") + ".");
}

function cmdUpdate(args) {
  if (args.global) return cmdUpdateGlobal(args);
  const target = path.resolve(args._[0] || ".");
  const addDir = path.join(target, ".add");
  if (!fs.existsSync(path.join(addDir, "tooling")) && !fs.existsSync(path.join(addDir, "state.json"))) {
    fail("no ADD project at " + target + " (.add/ not found) — run `init` first");
  }
  const version = pkgVersion();
  const stamp = readStamp(addDir);
  const cur = stamp && stamp.version ? stamp.version : null;

  if (args.check) {
    if (cur === version) log("ADD is current: project and package both at " + version + ".");
    else if (cur === null) log("ADD project is unstamped; installed package is " + version + ". Run `update`.");
    else log("ADD update available: project on " + cur + ", package is " + version + ". Run `update`.");
    return;
  }
  // same-version no-op ONLY when nothing is missing — a missing managed tree HEALS
  // even at the current version (heal-reconcile).
  const status = managedStatus(target);
  const missing = MANAGED.some(([sub]) => status[sub] === "missing");
  if (cur === version && !args.force && !missing) {
    log("ADD already at " + version + " — nothing to update (use --force to re-materialize).");
    return;
  }
  // design-for-failure: back up state BEFORE touching anything.
  const stateFile = path.join(addDir, "state.json");
  if (fs.existsSync(stateFile)) {
    fs.copyFileSync(stateFile, path.join(addDir, "pre-update-state.bak.json"));
  }
  reconcile(args, target);
  writeStamp(addDir, version);
  log("ADD updated " + (cur || "(unstamped)") + " -> " + version +
      " · managed layer reconciled · your project state untouched.");
}

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0] && !argv[0].startsWith("--") ? argv.shift() : "init";
  const args = parseArgs(argv);
  switch (cmd) {
    case "init":
      await cmdInit(args);
      break;
    case "update":
      cmdUpdate(args);
      break;
    case "help":
    case "--help":
      log("usage: npx @pilotspace/add <init|update> [targetDir] [--force] [--check] [--no-skill] [--global] [--yes|--non-interactive]");
      log("  init    install the ADD skill + tooling + book into a project");
      log("          (--no-skill drops the engine + book only — used by the Claude Code plugin)");
      log("          (--global ALSO installs to a shared home [ADD_HOME|XDG_DATA_HOME/add|~/.add] + registers the project)");
      log("          (--global-data implies --global + persists this project's user-data under <home>/data/<key>)");
      log("          (interactive in a real terminal; --yes / --non-interactive force the plain path)");
      log("  update  re-materialize skill/tooling/docs to this package version (preserves your state)");
      log("          (--global refreshes the shared home + propagates to every registered project)");
      break;
    default:
      fail("unknown command '" + cmd + "'. Try: npx @pilotspace/add init");
  }
}

// Run ONLY when invoked directly (the bin / npx entry). When `require()`d — the test harness
// imports the pure detectors — main() must NOT fire (it would parse argv + install). This guard
// changes no runtime behavior on the real CLI path; the non-interactive output stays byte-identical.
if (require.main === module) {
  main().catch((e) => fail(e && e.message ? e.message : String(e)));
}

module.exports = {
  detectAgent: detectAgent,
  detectAgentEnriched: detectAgentEnriched,
  readinessLine: readinessLine,
  whichSync: whichSync,
  scopeOptions: scopeOptions,
  writeIntentNote: writeIntentNote,
  writeGeminiSettings: writeGeminiSettings,
  ruleFileMode: ruleFileMode,
  ensureClaudeReference: ensureClaudeReference,
  writeRuleFilePointer: writeRuleFilePointer,
};
