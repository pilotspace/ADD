#!/usr/bin/env node
"use strict";

/**
 * @pilotspace/add installer.
 *
 *   npx @pilotspace/add init [targetDir] [--force] [--stage <stage>] [--name <name>] [--yes|--non-interactive]
 *
 * Installs the ADD skill + tooling into a target project:
 *   <target>/.claude/skills/add/   (the skill Claude loads)
 *   <target>/.add/tooling/         (the flat ADD engine: cli.py dispatch entry + add.py library)
 * It DROPS FILES ONLY — it does NOT run `cli.py init`. Initialisation is deferred to
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
                 yes: false, nonInteractive: false, global: false, globalData: false,
                 fromGlobalData: false, lockTimeout: null };
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
    // --from-global-data: the INVERSE — rehydrate this project's user-data FROM the shared
    // home on a fresh clone (non-destructive fill-gaps; --force overwrites with a .bak).
    else if (a === "--from-global-data") args.fromGlobalData = true;
    // --yes / --non-interactive: skip all prompts, take defaults — the explicit
    // non-interactive selector the interactive() gate honors (CI/pipes do this too).
    else if (a === "--yes" || a === "-y") args.yes = true;
    else if (a === "--non-interactive") args.nonInteractive = true;
    // --no-skill: drop the engine ONLY, not the skill. The Claude Code plugin
    // already provides the `add` skill, so a plugin bootstrap uses this to materialize
    // .add/tooling/ into the project without a duplicate .claude/skills/add.
    else if (a === "--no-skill") args.noSkill = true;
    else if (a === "--stage" || a === "--name") {
      const v = argv[++i];
      // fail loudly on a trailing/abutting flag — never silently drop a value
      // the user tried to pass (parity with the pip twin's argparse error)
      if (v == null || v.startsWith("--")) fail(a + " requires a value");
      if (a === "--stage") args.stage = v; else args.name = v;
    }
    // --lock-timeout <seconds>: (--global only) opt into a bounded wait for a LIVE contended
    // home lock before failing "update_in_progress" (default null = today's immediate fail-fast;
    // a STALE lock always self-heals regardless). SAME "requires a value" idiom as --stage/--name.
    else if (a === "--lock-timeout") {
      const v = argv[++i];
      if (v == null || v.startsWith("--")) fail(a + " requires a value");
      args.lockTimeout = Number(v);
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

// The drop-time pointer's marker tokens. The BEGIN token is kept BYTE-IDENTICAL to prior
// releases (and the pip twin) so a re-run REPLACES the existing block in place rather than
// appending a duplicate — it still NAMES the retired `sync-guidelines` verb purely for that
// backward-compatible idempotency. The flat 3.0 engine no longer injects or supersedes this block.
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
    "This project uses **ADD (AI-Driven Development)**. The engine is installed.\n" +
    "To begin: run `python3 .add/tooling/cli.py status` — your resume point (read from\n" +
    "the `.add/` bundle, not the repo), which names the next beat to work.\n" +
    "\n" +
    profile.next_step + "\n" +
    "\n" +
    "Edit outside the markers, not inside.\n" +
    GUIDE_END
  );
}

// Inject the ADD pointer into <target>/<integration_file>.
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
// The 7 labels are the real ADD phases (grounded in the method, never invented; grounding
// itself is folded into step 3, Plan, not a separate phase). Fail-soft: any draw error is
// swallowed so a banner can never abort the install. No color is emitted (default accent:
// none); the glyphs / tagline / accent are a SWAPPABLE content slot.
const BRAND_LOOP = ["Specify", "Plan", "Tests", "Build", "Verify"];

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
  const ok = await clack.confirm({ message: "Write the ADD skill + tooling here?" });
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
// DEFERRED-INIT: inert text only; never runs cli.py/init, never touches state.json. Fail-soft
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

// Seed .add/SOUL.md from the bundled template if it does not yet exist. Mirror of
// _installer.py:_seed_soul_md (npm <-> pip parity): skip-if-exists (SOUL.md is
// user-owned — never clobber); fail-soft (warn + return, never abort install/update).
function seedSoulMd(target) {
  const dest = path.join(target, ".add", "SOUL.md");
  if (fs.existsSync(dest)) return;                       // skip-if-exists (never clobber)
  const source = path.join(PKG_ROOT, "tooling", "templates", "SOUL.md.tmpl");
  if (!fs.existsSync(source)) {
    warn("soul_seed_skipped: SOUL.md.tmpl not found in bundled tooling/templates/");
    return;
  }
  try {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, fs.readFileSync(source, "utf8"));
  } catch (e) {
    warn("soul_seed_skipped: could not write .add/SOUL.md — " + (e && e.message ? e.message : e));
  }
}

// kept OUTSIDE the flat engine's own gitignore body / gitignore.tmpl deliberately: the engine's
// own _GITIGNORE_BODY constant must never contain "personas-teacher" (test_engine_unchanged_
// and_handsoff — the engine stays hands-off of the teacher vendor tree). The INSTALLER
// already names that tree explicitly (MANAGED/OPTIONAL), so it is free to seed this one
// extra ignore line itself. BARE (not repo-root style): .add/.gitignore lives INSIDE
// .add/, so git resolves its patterns relative to .add/ itself. Twin of
// _installer.py:_INSTALLER_MANAGED_IGNORE_EXTRA.
const INSTALLER_MANAGED_IGNORE_EXTRA = ["personas-teacher/"];

// Ensure .add/.gitignore lists the engine's transient artifacts + managed vendor trees.
// Seed it from the bundled tooling/templates/gitignore.tmpl (plus
// INSTALLER_MANAGED_IGNORE_EXTRA) if absent; else APPEND-IF-ABSENT each pattern line that
// combined body carries that the file lacks — additive only, never reorders/removes user
// lines, idempotent; comment/blank lines are not appended to an existing file. Fail-soft.
// Twin of _installer.py:_seed_gitignore.
function seedGitignore(target) {
  const source = path.join(PKG_ROOT, "tooling", "templates", "gitignore.tmpl");
  if (!fs.existsSync(source)) {
    warn("gitignore_seed_skipped: gitignore.tmpl not found in bundled tooling/templates/");
    return;
  }
  const dest = path.join(target, ".add", ".gitignore");
  try {
    let body = fs.readFileSync(source, "utf8");
    if (!body.endsWith("\n")) body += "\n";
    body += INSTALLER_MANAGED_IGNORE_EXTRA.join("\n") + "\n";
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, body);                       // seed-if-missing
      return;
    }
    const current = fs.readFileSync(dest, "utf8");
    const have = new Set(current.split("\n").map((l) => l.trim()));
    const missing = body.split("\n").filter(
      (l) => l.trim() && !l.trim().startsWith("#") && !have.has(l.trim())
    );
    if (missing.length === 0) return;                     // idempotent — nothing to add
    const suffix = current === "" || current.endsWith("\n") ? "" : "\n";
    fs.writeFileSync(dest, current + suffix + missing.join("\n") + "\n");
  } catch (e) {
    warn("gitignore_seed_skipped: could not update .add/.gitignore — " + (e && e.message ? e.message : e));
  }
}

// The drop — now a RECONCILE: restore missing managed trees + refresh present ones
// (sweep orphans) + report per-tree status. Byte-compatible handoff with the prior
// installer. The interactive path resolves a target then calls straight into this.
function dropFiles(args, target, profile, intent) {
  profile = profile || detectAgent(process.env);
  log("Installing ADD into " + target);
  reconcile(args, target);
  seedSoulMd(target);   // pip parity: re-seed a missing user-owned SOUL.md (never clobber)
  seedGitignore(target);   // pip parity: seed/append-if-absent the engine-transient ignore lines

  // Agent detection: write THE detected agent's integration file (a marker-delimited
  // pointer) + tailor the closing next-step.
  // Best-effort + fail-soft — never aborts the successful drop above.
  writeAgentPointer(target, profile);

  // Gemini CLI auto-loads GEMINI.md, not AGENTS.md — so for the gemini profile we ALSO merge
  // .gemini/settings.json (context.fileName) to load the AGENTS.md pointer. Fail-soft + idempotent.
  if (profile.id === "gemini") writeGeminiSettings(target);

  // Optional build-intent NOTE for `/add` to read — "" (skip / non-interactive) -> no-op.
  writeIntentNote(target, intent);

  // NO step 4: the installer DROPS FILES ONLY. Initialisation is deferred to the AI
  // (via `/add`) or a CLI user — a pre-run plain `cli.py init` would grandfather-lock
  // the v12 lock-down gate before `/add` runs (see file header). So no Python is run here.
  log("\nDone. " + (args.noSkill ? "The engine is" : "The `add` skill + tooling are") +
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
  // OPT-IN restore: the home MUST already exist — no_global_home is a HARD fail, checked FAST
  // here so nothing lands in the target on a missing home (the restore itself runs after the drop).
  if (args.fromGlobalData) {
    const home = resolveGlobalHome(process.env);
    if (!fs.existsSync(path.join(home, STAMP_FILE))) {
      fail("no global ADD install at " + home + " (.add-version not found) — nothing to restore " +
           "from; run `init --global-data` on a source checkout first");
    }
  }
  // Project-scope lock (project-scope-install-lock): keyed on chosenTarget's FINAL value (after
  // any interactive redirect above) — acquired BEFORE the as_global sub-block, held through the
  // function's end. Independent of, and acquired BEFORE, the home-scoped acquireUpdateLock that
  // installGlobal() below nests inside (M11 — never the reverse nesting).
  const addDir = path.join(chosenTarget, ".add");
  acquireProjectLock(addDir);   // registers its own process.on("exit", release) — no explicit
                                 // release()/finally needed at the call site (mirrors
                                 // acquireUpdateLock's own usage at cmdUpdateGlobal)
  // OPT-IN global home, BEFORE the per-project drop (fail-closed if the home is unwritable
  // or its registry is corrupt — the package + the self-contained default stay usable).
  if (args.global) installGlobal(args, chosenTarget);
  dropFiles(args, chosenTarget, profile, intent);
  // OPT-IN data persist, AFTER the drop (one-way snapshot of existing user-data).
  if (args.globalData) installGlobalData(chosenTarget);
  // OPT-IN restore (consume), AFTER the drop: rehydrate user-data from the home into this clone.
  if (args.fromGlobalData) installGlobalDataRestore(chosenTarget, args.force);
}

// --- update: re-materialize the managed layer without a re-install -----------
// The managed trees (ship-controlled). `update` clean-replaces each, so a file removed
// upstream leaves no orphan — and never touches .add/state.json, PROJECT.md, milestones,
// tasks, or archive (user data). Pure file-copy (npm <-> pip parity with _installer.py).
const MANAGED = [
  ["skill/add", [".claude", "skills", "add"], false],
  ["agents", [".claude", "agents"], false],
  ["tooling", [".add", "tooling"], true],
  ["personas-teacher", [".add", "personas-teacher"], false],
];
// Optional managed trees: an ENHANCEMENT the persona phase reads, not core runtime. The real
// package always ships these (guarded by test_packaging); a malformed/older package missing one
// must NOT abort the install — the core lands and the optional tree is soft-skipped. Twin of
// _installer.py:OPTIONAL. Design-for-failure. `agents` joins here (roster-install-drift): the
// phase-agent roster is a spawn-acceleration enhancement, not core runtime.
const OPTIONAL = new Set(["personas-teacher", "agents"]);
// SHARED-namespace managed trees (installer-shared-namespace-guard): destinations OTHER
// TOOLS also write — `.claude/agents` holds the user's own Claude Code subagents. A
// whole-dir clean-replace there sweeps the user's files as "orphans" (the reported
// data-loss bug), so these trees route to sharedFileReplace: per-file atomic landings of
// the shipped files + removal of ONLY the explicit tombstones below. Twin of
// _installer.py:_SHARED / _RETIRED_AGENTS.
const SHARED = new Set(["agents"]);
// Roster names retired upstream — the ONLY names the shared lander may remove (never a
// pattern/prefix heuristic: a USER file named add-anything.md must survive).
// roster-distill (ADD 2.0 M1): the 5-agent roster collapsed into the ONE `add` agent.
// advisor-split: that ONE `add` agent split into `add-worker` + `add-advisor`, so `add.md`
// retires here and `add-advisor.md` leaves the list (it ships again; landing precedes removal).
const RETIRED_AGENTS = ["add-design.md", "add-build.md", "add-verify.md",
                        "add-persona.md", "add.md"];
const STAMP_FILE = ".add-version";
const LOCK_FILE = ".update.lock";   // the `update --global` home lock (never user-data)
const LOCK_STALE_DEFAULT = 600;     // seconds (10 min); ADD_LOCK_STALE_SECONDS env-overridable
const LOCK_POLL_INTERVAL_MS = 50;   // ms between polls while waiting out a --lock-timeout
const LOCK_TICKET_STALE_SECONDS = 5;   // a leaked per-generation reclaim ticket (its own holder
                                        // crashed between winning it and its own best-effort
                                        // cleanup) self-heals after this long — deliberately far
                                        // shorter than LOCK_STALE_DEFAULT's own 600s: a ticket's
                                        // own critical section is a small, fixed handful of
                                        // syscalls (close/stat/unlink), microseconds under normal
                                        // operation, so a multi-second margin is generous, not
                                        // tight (global-lock-followups' own leaked-ticket-livelock
                                        // fix — independent of, not shared with, acquireProjectLock's
                                        // own PROJECT_LOCK_TICKET_STALE_SECONDS below).
const PROJECT_LOCK_FILE = ".install.lock";   // the project-scope init()/update() lock (never user-data)
const PROJECT_LOCK_STALE_DEFAULT = 120;      // seconds (2 min); ADD_PROJECT_LOCK_STALE_SECONDS env-overridable —
                                              // deliberately SHORTER than LOCK_STALE_DEFAULT's own 600s (see
                                              // _installer.py's _PROJECT_LOCK_STALE_DEFAULT for the reasoning)
const PROJECT_LOCK_TICKET_STALE_SECONDS = 5;   // a leaked per-generation reclaim ticket self-heals
                                                // after this long — independent of, but numerically
                                                // identical to, acquireUpdateLock's own
                                                // LOCK_TICKET_STALE_SECONDS: a ticket's own critical
                                                // section is the same small, fixed handful of
                                                // syscalls regardless of which lock it guards
                                                // (project-scope-install-lock's own
                                                // leaked-ticket-wedge fix)

// A synchronous sleep via Atomics.wait on a throwaway SharedArrayBuffer — builtin, no new
// dependency; Node's MAIN thread (unlike a browser's) is allowed to block on Atomics.wait.
function sleepSync(ms) {
  const ia = new Int32Array(new SharedArrayBuffer(4));
  Atomics.wait(ia, 0, 0, ms);
}

// An async, event-loop-YIELDING sleep (unlike sleepSync's Atomics.wait, which blocks the very
// thread a setInterval-based heartbeat needs to fire on) — js-reclaim-lock-heartbeat.
function sleepAsync(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// js-reclaim-lock-heartbeat: the JS analog of the Python `_lock_heartbeat` fix
// (reclaim-ticket-race) — refreshes a held lock file's own mtime on a `.unref()`'d
// `setInterval` for as long as it is held, so a live-but-slow holder is never misjudged
// stale by a sibling racer purely because wall-clock age crosses `staleAfterMs`. `.unref()`
// means the timer never keeps the process alive on its own; `stop()` clears it explicitly on
// release (belt AND suspenders, mirrors the interval's own `max(50ms, min(staleAfterMs/4,
// 5000ms))` formula the frozen contract cites). A crash simply stops the interval firing — the
// file still ages out and self-heals via the existing reclaim-ticket mechanism, unchanged.
//
// This is a probabilistic mitigation, not a mathematical guarantee: a callback fires only
// between synchronous JS turns, so whole-event-loop starvation (a long synchronous operation
// blocking the process) can defeat it exactly as whole-process scheduling starvation once
// defeated the Python fix's own real OS thread on real CI (see TASK.md's least-sure flag) —
// accepted given production defaults (600s/120s) make that starvation window vanishingly
// unlikely in practice.
function startLockHeartbeat(lockPath, staleAfterMs) {
  const intervalMs = Math.max(50, Math.min(staleAfterMs / 4, 5000));
  const timer = setInterval(() => {
    const now = new Date();
    try { fs.utimesSync(lockPath, now, now); } catch (_e) {}   // released/reclaimed — best-effort
  }, intervalMs);
  timer.unref();
  return { stop: () => clearInterval(timer) };
}

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

// The set of FILE paths (recursive leaves) under root, RELATIVE to root. ∅ if absent.
// Directories are not counted — only files (the "manifest" the roll-up measures).
function treeFiles(root) {
  const out = new Set();
  if (!fs.existsSync(root)) return out;
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else out.add(path.relative(root, full));
    }
  };
  walk(root);
  return out;
}

// Crash-safe stage-then-swap: project-scope-atomic-reconcile (TASK.md v1). Replaces the
// old wipe-then-copy (rmSync(dest) then cpSync onto dest directly) with a stage-into-a-
// sibling + two-rename commit, so dest is NEVER observed half-old/half-new (a random
// partial mix) — the achievable guarantee is "never observed half-composed", not "never
// observed absent for an instant" (a single-syscall atomic replace of an EXISTING
// non-empty directory is not portable; the sub-instant window between the two commit
// renames is closed by the NEXT call's own self-heal, not this one).
//
// Returns a file-level roll-up of the heal: { restored, refreshed } where `restored` = a
// file in the FINAL tree whose relative path was ABSENT before the call (fresh or
// partially-gutted trees heal these), `refreshed` = a final file that was PRESENT before
// (re-materialized). Orphans (present before, gone after) are swept, counted as neither.
// Pure observation — copy semantics unchanged. Mirror of _installer.py:_clean_replace.
function cleanReplaceTree(src, dest, stripTests) {
  if (!fs.existsSync(src)) fail("missing packaged source: " + src);
  const destParent = path.dirname(dest);
  const destName = path.basename(dest);
  fs.mkdirSync(destParent, { recursive: true });

  // -- self-heal -- (before this call's own work): recover/discard whatever a PRIOR,
  // interrupted call left behind. A stale backup found while dest is absent is the last
  // known-good tree — restore it first (a cheap rename), minimizing how long dest stays
  // broken; any other stale sibling (a stage, or a backup found while dest is present) is
  // discarded outright — its content is never merged or reused.
  const siblings = fs.readdirSync(destParent);
  const tmpStales = siblings.filter((n) => n.startsWith(destName + ".add-tmp-"));
  const bakStales = siblings.filter((n) => n.startsWith(destName + ".add-bak-"))
    .map((n) => path.join(destParent, n))
    .sort((a, b) => fs.statSync(a).mtimeMs - fs.statSync(b).mtimeMs);
  let remainingBaks = bakStales;
  if (!fs.existsSync(dest) && bakStales.length > 0) {
    const winner = bakStales[bakStales.length - 1];      // most-recently-modified is authoritative
    fs.renameSync(winner, dest);
    remainingBaks = bakStales.slice(0, -1);
  }
  for (const stale of tmpStales.map((n) => path.join(destParent, n)).concat(remainingBaks)) {
    fs.rmSync(stale, { recursive: true, force: true });
  }

  const before = treeFiles(dest);                        // snapshot BEFORE this call's own work

  // -- stage -- : copy src into a fresh, uniquely-named sibling of dest, in dest's own
  // parent (same filesystem, so the commit renames below are a genuine atomic move). dest
  // itself is never opened for writing or deletion during this step.
  const staged = fs.mkdtempSync(path.join(destParent, destName + ".add-tmp-"));
  try {
    fs.cpSync(src, staged, { recursive: true });
    if (stripTests) {
      fs.rmSync(path.join(staged, "__pycache__"), { recursive: true, force: true });
      for (const entry of fs.readdirSync(staged)) {
        if (/^test_.*\.py$/.test(entry)) fs.rmSync(path.join(staged, entry), { force: true });
      }
    }
  } catch (e) {
    fs.rmSync(staged, { recursive: true, force: true });   // dest untouched — it was never opened
    throw e;
  }

  // -- commit -- : two same-parent renames, NEITHER targets an already-existing name.
  const token = path.basename(staged).slice((destName + ".add-tmp-").length);
  let bak = null;
  if (fs.existsSync(dest)) {
    bak = path.join(destParent, destName + ".add-bak-" + token);
    try {
      fs.renameSync(dest, bak);                            // (a) vacate dest, aside
    } catch (e) {
      fs.rmSync(staged, { recursive: true, force: true });  // dest untouched — the rename never happened
      throw e;
    }
  }
  try {
    fs.renameSync(staged, dest);                           // (b) land the new generation
  } catch (e) {
    if (bak !== null) fs.renameSync(bak, dest);             // roll back: restore the original
    fs.rmSync(staged, { recursive: true, force: true });
    throw e;
  }

  // -- sweep -- : remove the backup sibling — ONLY after (b) has landed the new dest.
  if (bak !== null) fs.rmSync(bak, { recursive: true, force: true });

  let restored = 0, refreshed = 0;
  for (const f of treeFiles(dest)) (before.has(f) ? refreshed++ : restored++);
  return { restored: restored, refreshed: refreshed };
}

const TREE_LABEL = { "skill/add": "skill", "agents": "agents", "tooling": "tooling", "personas-teacher": "personas" };

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

// installer-shared-namespace-guard: land a SHARED-namespace managed tree per FILE.
// `.claude/agents` belongs to the user as much as to ADD — only the shipped files are
// written (temp-sibling + atomic rename each, so a crash never leaves a torn file) and
// only the explicit RETIRED_AGENTS tombstones are removed; every other destination file
// is never opened. Returns the same { restored, refreshed } roll-up shape as
// cleanReplaceTree so the reconcile reporting is agnostic. Mirror of
// _installer.py:_shared_file_replace.
function sharedFileReplace(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  let restored = 0, refreshed = 0;
  const entries = fs.readdirSync(src).filter((n) => fs.statSync(path.join(src, n)).isFile()).sort();
  for (const name of entries) {
    const target = path.join(dest, name);
    const existed = fs.existsSync(target);
    const tmp = path.join(dest, name + ".add-tmp-" + Math.random().toString(36).slice(2, 10));
    try {
      fs.copyFileSync(path.join(src, name), tmp);
      fs.renameSync(tmp, target);   // atomic overwrite (same directory)
    } catch (e) {
      fs.rmSync(tmp, { force: true });   // dest entry untouched or already whole
      throw e;
    }
    if (existed) refreshed++; else restored++;
  }
  for (const name of RETIRED_AGENTS) {
    fs.rmSync(path.join(dest, name), { force: true });   // absent tombstone — never fatal
  }
  return { restored: restored, refreshed: refreshed };
}

// reconcile: restore-missing + refresh-present (sweep orphans) across the managed trees,
// reporting per-tree status. Honors --no-skill (the plugin provides the skill). Touches
// ONLY managed trees — never user data. Prechecks ALL sources first (design-for-failure:
// a corrupt package leaves the target untouched).
function reconcile(args, target, srcRoot) {
  srcRoot = srcRoot || PKG_ROOT;   // default: the package; the global home feeds propagation
  const trees = MANAGED
    .filter(([sub]) => !(sub === "skill/add" && args.noSkill))
    .filter(([sub]) => !(OPTIONAL.has(sub) && !fs.existsSync(path.join(srcRoot, sub))));  // soft-skip absent optional
  for (const [sub] of trees) {
    if (!fs.existsSync(path.join(srcRoot, sub))) {
      fail("missing packaged source: " + path.join(srcRoot, sub));
    }
  }
  const status = managedStatus(target);
  let restored = 0, refreshed = 0;
  for (const [sub, destParts, stripTests] of trees) {
    const roll = SHARED.has(sub)
      ? sharedFileReplace(path.join(srcRoot, sub), path.join(target, ...destParts))
      : cleanReplaceTree(path.join(srcRoot, sub), path.join(target, ...destParts), stripTests);
    restored += roll.restored;
    refreshed += roll.refreshed;
    const dest = destParts.join("/");
    if (status[sub] === "missing") {
      log("  ✓ restored  " + TREE_LABEL[sub].padEnd(8) + "-> " + dest + "  (was missing)");
    } else {
      log("  ✓ refreshed " + TREE_LABEL[sub].padEnd(8) + "-> " + dest);
    }
  }
  log("  → " + restored + " restored · " + refreshed + " refreshed");
  return { restored: restored, refreshed: refreshed, trees: status };
}

// --- global home: an OPT-IN shared install (engine+skill) updated for all projects ----
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

// The home mirrors the bundled layout (skill/add + tooling at the SAME relative paths
// the package ships) so reconcile(args, project, home) reuses MANAGED unchanged.
const GLOBAL_TREES = [
  ["skill/add", ["skill", "add"], false],
  // roster-drift fix: absent here, `update --global` propagation (sourced FROM the home)
  // soft-skipped the roster forever — no refresh, no retired-agent tombstones.
  ["agents", ["agents"], false],
  ["tooling", ["tooling"], true],
  ["personas-teacher", ["personas-teacher"], false],
];

// Clean-replace the bundled managed layer INTO <home> (canonical mirror), then DEPLOY the
// skill to ~/.claude/skills/add. Throws if a dir can't be written (caller -> home_unwritable).
// Prechecks ALL sources first (design-for-failure: a corrupt package leaves the home as-is).
function reconcileGlobal(home, claudeDir, noSkill) {
  const trees = GLOBAL_TREES.filter(([sub]) => !(OPTIONAL.has(sub) && !fs.existsSync(path.join(PKG_ROOT, sub))));
  for (const [sub] of trees) {
    if (!fs.existsSync(path.join(PKG_ROOT, sub))) {
      fail("missing packaged source: " + path.join(PKG_ROOT, sub));
    }
  }
  for (const [sub, destParts, stripTests] of trees) {
    cleanReplaceTree(path.join(PKG_ROOT, sub), path.join(home, ...destParts), stripTests);
  }
  if (!noSkill) cleanReplaceTree(path.join(home, "skill", "add"), claudeDir, false);
}

// --- global DATA: an OPT-IN per-project user-data snapshot under <home>/data/<key> ----------
// Strictly additive; copies ONLY user-data (managed trees + transient excluded), clean-replaced,
// one-way (project->home). Mirror of _installer.py (identical key + include/exclude rule).
const DATA_EXCLUDE = ["tooling", "docs", ".update-cache", STAMP_FILE, LOCK_FILE, PROJECT_LOCK_FILE];   // managed trees + meta + both locks ("docs" = legacy 1.x tree: still never user-data)

// data_key twin: <sanitized-basename>-<sha1(abspath_utf8)[:12]>. Pure · total · separator-free.
function dataKey(projectAbspath) {
  const p = String(projectAbspath);
  const digest = crypto.createHash("sha1").update(p, "utf8").digest("hex").slice(0, 12);
  const base = (path.basename(p) || "root").replace(/[^A-Za-z0-9._-]/g, "_");
  return base + "-" + digest;
}

// A top-level .add/ entry is user-data unless it is a managed tree, a transient artifact, a
// scratch-staging sibling left by an interrupted persist/restore/clean-replace call (the shared
// .add-tmp-/.add-bak- infix convention — crash-safe-persist-restore v1 §3 M11), or a
// per-generation reclaim-ticket sibling a lock's own stale-reclaim mechanism may transiently (or,
// if leaked by a crash, semi-persistently) leave next to it (the .reclaim-<inode> infix
// convention — project-scope-install-lock / global-lock-followups' leaked-ticket self-heal fix).
function isUserData(name) {
  if (DATA_EXCLUDE.includes(name)) return false;
  if (name.startsWith("scope-snapshot")) return false;
  if (name.includes("pre-archive-bak")) return false;
  if (name.endsWith(".bak.json")) return false;
  if (name.includes(".add-tmp-") || name.includes(".add-bak-")) return false;
  if (name.includes(".reclaim-")) return false;
  return true;
}

// Best-effort removal of a scratch sibling (staging dir/file, or a whole-tree backup dir);
// tolerates it already being gone. A sweep failure here is hygiene, not a correctness gap —
// self-heal simply retries it on the next call touching this target.
function sweepScratch(p) {
  try { fs.rmSync(p, { recursive: true, force: true }); } catch (_e) { /* best-effort */ }
}

// Crash-safe clean-replace of a project's USER-DATA into <home>/data/<key>: self-heal any
// scratch sibling left by an earlier interrupted call, then a WHOLE-TREE stage-then-commit
// (mirrors cleanReplaceTree's own pattern) — dest is never opened for writing or deletion until
// its replacement has FULLY landed. true=persisted, false=skipped (no .add or no user-data — an
// honest skip, dest — including any EXISTING stale snapshot — left completely untouched).
// Throws if the data dir can't be written.
function persistData(home, projectAbspath) {
  const key = dataKey(projectAbspath);
  const dataRoot = path.join(home, "data");
  const dest = path.join(dataRoot, key);

  // step 0 -- self-heal: a stale backup found while dest is currently ABSENT means a PRIOR call
  // crashed between its two commit renames -- restore it first (the newest wins a >1 tie-break,
  // a defensive case, not an expected path). Then sweep every remaining scratch sibling for this
  // key unconditionally (never merged/reused).
  if (fs.existsSync(dataRoot)) {
    const siblings = fs.readdirSync(dataRoot);
    const tmpStale = siblings.filter((n) => n.startsWith(key + ".add-tmp-"));
    let bakStale = siblings.filter((n) => n.startsWith(key + ".add-bak-"));
    if (!fs.existsSync(dest) && bakStale.length > 0) {
      let newest = bakStale[0];
      let newestMtime = fs.statSync(path.join(dataRoot, newest)).mtimeMs;
      for (const n of bakStale.slice(1)) {
        const t = fs.statSync(path.join(dataRoot, n)).mtimeMs;
        if (t > newestMtime) { newest = n; newestMtime = t; }
      }
      fs.renameSync(path.join(dataRoot, newest), dest);
      bakStale = bakStale.filter((n) => n !== newest);
    }
    for (const n of bakStale) sweepScratch(path.join(dataRoot, n));
    for (const n of tmpStale) sweepScratch(path.join(dataRoot, n));
  }

  const addDir = path.join(projectAbspath, ".add");
  if (!fs.existsSync(addDir)) return false;
  const entries = fs.readdirSync(addDir).filter(isUserData);
  if (entries.length === 0) return false;        // UNCHANGED: an existing stale snapshot is left as-is

  // step 1 -- stage: copy every filtered entry into a fresh, uniquely-named sibling of dest, IN
  // home/data/. dest itself is never opened for writing during this step.
  fs.mkdirSync(dataRoot, { recursive: true });
  const staged = fs.mkdtempSync(path.join(dataRoot, key + ".add-tmp-"));
  try {
    for (const e of entries) {
      fs.cpSync(path.join(addDir, e), path.join(staged, e), { recursive: true });
    }
  } catch (e) {
    sweepScratch(staged);
    throw e;
  }

  // step 2 -- commit: two same-parent renames, neither ever targets an already-existing name.
  const backup = path.join(dataRoot, key + ".add-bak-" + crypto.randomBytes(6).toString("hex"));
  let asideLanded = false;
  if (fs.existsSync(dest)) {
    try {
      fs.renameSync(dest, backup);
      asideLanded = true;
    } catch (e) {
      sweepScratch(staged);
      throw e;
    }
  }
  try {
    fs.renameSync(staged, dest);
  } catch (e) {
    if (asideLanded) fs.renameSync(backup, dest);   // roll back: dest ends where it started
    sweepScratch(staged);
    throw e;
  }

  // step 3 -- sweep: the old backup is removed only now that the new dest has landed.
  if (asideLanded) sweepScratch(backup);
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

function isSymlink(p) {
  try { return fs.lstatSync(p).isSymbolicLink(); } catch (_e) { return false; }
}

// Restore USER-DATA from <home>/data/<key> into <project>/.add — the NON-DESTRUCTIVE inverse of
// persistData, crash-safe via a PER-ENTRY stage-then-commit (.add/ is a SHARED directory most of
// which this function must leave alone, so — unlike persistData's self-owned whole-tree dest —
// only ONE entry stages/commits at a time). FILL-GAPS by default (write only ABSENT entries);
// force overwrites a present entry, writing a <name>.bak sidecar of the original FIRST (the SAME
// permanent, already-contracted sidecar name as before this task — never the new transient
// staging marker). Copies only isUserData entries; DEREFERENCES symlinks to content (cpSync
// dereference). true if >=1 restored, false if nothing to restore. Throws on an unwritable dest
// -> restore_failed. Mirror of _installer.py:_restore_data.
function restoreData(home, projectAbspath, force) {
  const addDir = path.join(projectAbspath, ".add");
  const src = path.join(home, "data", dataKey(projectAbspath));

  // step 0 -- self-heal: sweep any stale per-entry staging sibling left by an earlier
  // INTERRUPTED call, unconditionally (never merged/reused/completed) -- the untouched snapshot
  // at src lets THIS call's own ordinary fill-gaps-or-force logic re-derive the correct end
  // state; no backup-recovery step is needed here (unlike persistData's step 0).
  if (fs.existsSync(addDir)) {
    for (const n of fs.readdirSync(addDir)) {
      if (n.includes(".add-tmp-")) sweepScratch(path.join(addDir, n));
    }
  }

  if (!fs.existsSync(src)) return false;
  const entries = fs.readdirSync(src).filter(isUserData).sort();
  if (entries.length === 0) return false;
  fs.mkdirSync(addDir, { recursive: true });
  let restored = false;
  for (const e of entries) {
    const dest = path.join(addDir, e);
    const existed = fs.existsSync(dest) || isSymlink(dest);
    if (existed && !force) continue;                        // fill-gaps: never clobber; no staging begins

    // step 1b -- stage: copy this ONE entry into a fresh, uniquely-named sibling of dest, IN
    // .add/ -- dest's own name is not opened for writing during this step. A reserved unique
    // name is claimed via mkdtempSync, then either kept as a dir (cpSync merges into the empty
    // dir) or freed via rmdirSync for a plain-file copy.
    const staged = fs.mkdtempSync(path.join(addDir, e + ".add-tmp-"));
    try {
      const srcEntry = path.join(src, e);
      if (fs.statSync(srcEntry).isDirectory()) {
        fs.cpSync(srcEntry, staged, { recursive: true, dereference: true });
      } else {
        fs.rmdirSync(staged);
        fs.cpSync(srcEntry, staged, { dereference: true });   // deref a symlink source
      }
    } catch (err) {
      sweepScratch(staged);
      throw err;
    }

    // step 1c -- commit:
    if (existed) {
      const bak = dest + ".bak";
      if (fs.existsSync(bak) || isSymlink(bak)) sweepScratch(bak);   // a stale .bak: replace, don't merge
      fs.renameSync(dest, bak);                               // back up the original BEFORE replacing
      try {
        fs.renameSync(staged, dest);
      } catch (err) {
        fs.renameSync(bak, dest);                             // roll back: this entry ends where it started
        sweepScratch(staged);
        throw err;
      }
    } else {
      fs.renameSync(staged, dest);                            // fill-gaps: single rename, no backup needed
    }
    restored = true;
  }
  return restored;
}

// init --from-global-data: rehydrate user-data after the per-project drop. Resolves the SAME
// realpath the snapshot key uses. The home is verified BEFORE the drop (no_global_home fails fast,
// in cmdInit). An unwritable dest -> restore_failed; a missing snapshot is an honest skip.
function installGlobalDataRestore(chosenTarget, force) {
  const home = resolveGlobalHome(process.env);
  let resolved = chosenTarget;
  try { resolved = fs.realpathSync(chosenTarget); } catch (_e) { /* fall back to the abspath */ }
  const snap = path.join(home, "data", dataKey(resolved));
  let restored;
  try { restored = restoreData(home, resolved, force); }
  catch (e) {
    fail("restore_failed: cannot write restored data into " + path.join(resolved, ".add") +
         " — " + (e && e.message ? e.message : e));
  }
  if (restored) log("  ✓ restored data <- " + snap);
  else log("  (no snapshot for this project at " + snap + " — nothing restored)");
}

// Every "<lockFileName>.reclaim-*" directly under dir aged past staleAfterSeconds — a LEAKED
// per-generation reclaim ticket (its own holder crashed between winning it and its own
// best-effort cleanup; a live, currently-in-flight ticket is never this old). Returns full
// paths, sorted; [] if dir does not exist. Mirror of _installer.py:_aged_reclaim_tickets.
function agedReclaimTickets(dir, lockFileName, staleAfterSeconds, nowMs) {
  if (!fs.existsSync(dir)) return [];
  const prefix = lockFileName + ".reclaim-";
  return fs.readdirSync(dir).filter((name) => name.startsWith(prefix)).map((name) => path.join(dir, name))
    .filter((p) => {
      try { return (nowMs - fs.statSync(p).mtimeMs) / 1000 > staleAfterSeconds; }
      catch (_e) { return false; }               // vanished mid-sweep — nothing to report
    }).sort();
}

// True iff `p` is STILL the exact stale generation identified by `observedIno` AND still stale —
// the guard that gates a reclaim UNLINK. Mirror of _installer.py:_still_stale_generation.
//
// Inode NUMBER alone is NOT a stable identity across a delete+recreate: Linux (ext4/tmpfs)
// aggressively REUSES freed inode numbers, so a live holder's fresh replacement lock can reuse the
// crashed file's inode. A reclaimer that trusts inode identity alone then unlinks a LIVE lock whose
// inode merely coincides with the crashed generation it observed — two holders end up inside the
// critical section at once (the peak=2 double-hold; reproduced on Linux CI, never on macOS APFS,
// which does not reuse inodes in a short window).
//
// Re-verifying that the CURRENT file is itself still stale (mtime age > `staleAfterSeconds`)
// distinguishes a live reused-inode holder (age ~0, or heartbeat-refreshed) from the crashed
// generation we meant to reclaim. The "wx" create remains the SOLE mutual-exclusion primitive;
// this only prevents a live file being mistaken for a dead one.
function stillStaleGeneration(p, observedIno, staleAfterSeconds, nowMs) {
  const now = nowMs === undefined ? Date.now() : nowMs;
  let cur = null;
  try { cur = fs.statSync(p); }
  catch (_e) { return false; }                  // vanished — nothing to reclaim
  return cur.ino === observedIno && (now - cur.mtimeMs) / 1000 > staleAfterSeconds;
}

// prune-data: reclaim ORPHANED snapshots under <home>/data. An orphan is a <home>/data/<key>
// whose key is owned by NO LIVE registry entry (LIVE = a registered path that still EXISTS on
// disk) — so unregistered AND registered-but-vanished are BOTH orphans (the explicit reclaim;
// DIVERGES from update --global's keep-vanished). Reads the registry FIRST (corrupt throws,
// before any removal).
//
// sweep-orphan-reclaim-tickets: ALSO sweeps LEAKED per-generation reclaim tickets — a
// "<LOCK_FILE>.reclaim-*" under home (home-scope) and a "<PROJECT_LOCK_FILE>.reclaim-*" under
// every LIVE registered project's own .add/ (project-scope) — each aged past its OWN kind's
// existing staleness constant (LOCK_TICKET_STALE_SECONDS / PROJECT_LOCK_TICKET_STALE_SECONDS,
// reused verbatim; no new threshold). Reuses the registry already read for the data-orphan
// sweep — no new read.
//
// Returns {orphans, removed, ticketOrphans, ticketsRemoved} — extends the prior {orphans,
// removed} object non-breakingly (existing dot-access callers are unaffected). ticketOrphans/
// ticketsRemoved are full paths; ticketsRemoved == [] on a dry-run, == ticketOrphans under
// force (each unlinked best-effort, matching the existing reclaim code's own swallow-errors
// convention). Mirror of _installer.py:_prune_data.
function pruneData(home, force) {
  const reg = readRegistry(home);                           // corrupt -> throw (LOUD, zero removal)
  const livePaths = reg.filter((p) => fs.existsSync(p));
  const live = new Set(livePaths.map(dataKey));
  const dataDir = path.join(home, "data");
  const orphans = !fs.existsSync(dataDir) ? [] : fs.readdirSync(dataDir).filter((name) => {
    try { return fs.statSync(path.join(dataDir, name)).isDirectory() && !live.has(name); }
    catch (_e) { return false; }
  }).sort();
  const removed = [];
  if (force) {
    for (const key of orphans) {
      fs.rmSync(path.join(dataDir, key), { recursive: true, force: true });
      removed.push(key);
    }
  }

  const now = Date.now();
  let ticketCandidates = agedReclaimTickets(home, LOCK_FILE, LOCK_TICKET_STALE_SECONDS, now)
    .map((p) => ({ path: p, staleAfter: LOCK_TICKET_STALE_SECONDS }));
  for (const project of livePaths) {
    ticketCandidates = ticketCandidates.concat(
      agedReclaimTickets(path.join(project, ".add"), PROJECT_LOCK_FILE, PROJECT_LOCK_TICKET_STALE_SECONDS, now)
        .map((p) => ({ path: p, staleAfter: PROJECT_LOCK_TICKET_STALE_SECONDS }))
    );
  }
  const ticketOrphans = ticketCandidates.map((c) => c.path);
  const ticketsRemoved = [];
  if (force) {
    for (const { path: ticket, staleAfter } of ticketCandidates) {
      try {
        if ((Date.now() - fs.statSync(ticket).mtimeMs) / 1000 <= staleAfter) continue;  // no longer stale at unlink time — §5 safety rule
        fs.unlinkSync(ticket);
        ticketsRemoved.push(ticket);
      } catch (_e) { /* already gone — harmless, matches reclaim's own convention */ }
    }
  }

  return { orphans: orphans, removed: removed, ticketOrphans: ticketOrphans, ticketsRemoved: ticketsRemoved };
}

// prune-data command: dry-run lists orphans (removes nothing); --force deletes. no_global_home /
// registry_corrupt = fail-closed (LOUD, nothing removed). Mirror of pip _installer.prune_data.
//
// prune-data-update-lock: the registry-read + orphan-computation + removal critical section now
// holds the SAME home lock (acquireUpdateLock) `update --global` already holds during its own
// reconcile (which refreshes an existing project's <home>/data/<key> snapshot) — so the two can
// never interleave. Reuses the existing, proven primitive verbatim (fail-fast, no poll — the
// primitive's own fail() call handles a contended lock, no extra catch needed here).
//
// sweep-orphan-reclaim-tickets: ALSO reports (and, with --force, removes) leaked reclaim
// tickets found by pruneData — see its own comment; a separate, additive count from the
// data-orphan sweep above.
function cmdPruneData(args) {
  const home = resolveGlobalHome(process.env);
  if (!fs.existsSync(path.join(home, STAMP_FILE))) {
    fail("no global ADD install at " + home + " (.add-version not found) — nothing to prune");
  }
  acquireUpdateLock(home, { timeout: null }, process.env);
  let result;
  try { result = pruneData(home, args.force); }
  catch (_e) { fail("global registry " + registryPath(home) + " is corrupt — fix or delete it; not pruning"); }
  if (result.orphans.length === 0 && result.ticketOrphans.length === 0) {
    log("  no orphaned snapshots — nothing to prune");
    return;
  }
  if (args.force) {
    if (result.orphans.length > 0) log("  ✓ " + result.removed.length + " removed");
    if (result.ticketOrphans.length > 0) log("  ✓ " + result.ticketsRemoved.length + " reclaim ticket(s) removed");
    return;
  }
  for (const key of result.orphans) log("  orphan: " + key);
  if (result.orphans.length > 0) log("  " + result.orphans.length + " orphan(s); re-run with --force to remove");
  for (const ticket of result.ticketOrphans) log("  ticket orphan: " + ticket);
  if (result.ticketOrphans.length > 0) {
    log("  " + result.ticketOrphans.length + " reclaim ticket orphan(s); re-run with --force to remove");
  }
}

// init --global: install the managed layer ONCE to the shared home + register this project,
// fail-closed BEFORE the per-project drop. Returns the resolved target for the normal drop.
// Serialized under the SAME home lock update --global uses (global-lock-followups M3) — a lock
// failure aborts BEFORE any home/registry write and BEFORE the per-project drop (dropFiles,
// called by cmdInit right after this returns), matching the all-or-nothing precedent every
// other as_global-path failure already has.
function installGlobal(args, chosenTarget) {
  const home = resolveGlobalHome(process.env);
  const claudeDir = claudeSkillsDir(process.env);
  acquireUpdateLock(home, { timeout: args.lockTimeout }, process.env);
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
// True iff path.normalize(p) is an EXISTING ADD project (a dir containing .add/). The is-.add/
// backstop: a managed-file reconcile NEVER lands in a dir without a .add/ marker. Absoluteness is
// the SEPARATE LOUD gate in cmdUpdateGlobal (a relative path is the traversal vector). pip twin:
// _installer.py:_valid_registry_path.
function validRegistryPath(p) {
  const np = path.normalize(String(p));
  try { return fs.statSync(np).isDirectory() && fs.statSync(path.join(np, ".add")).isDirectory(); }
  catch (_e) { return false; }
}

// Serialize `update --global` (and, since global-lock-followups, `init --global`) with an
// EXCLUSIVE lockfile (O_CREAT|O_EXCL via the "wx" flag) — the SAME mechanism as the pip twin
// (_installer.py:_update_lock's os.open(O_EXCL)), so a pip-held lock blocks an npm run and
// vice-versa.
//
// Held AND fresh (age <= ADD_LOCK_STALE_SECONDS, env-overridable, default 600s) -> today's
// byte-identical behavior: `timeout` null/0 fails "update_in_progress" immediately; timeout=N>0
// polls up to N seconds before failing.
//
// Held AND stale (age > threshold) -> self-heals: unlinks the stale lockfile and retries the
// create. The "wx" create remains the SOLE mutual-exclusion primitive — staleness only ever
// decides whether to retry, never bypasses exclusivity. A clock-skewed FUTURE mtime is a
// negative age, so it is NEVER treated as stale.
//
// A successful acquire (fresh or reclaimed) stamps the file "<PID> <ISO ts>\n" — informational
// ONLY, never read to decide staleness; a stamp-write failure is swallowed.
//
// KNOWN PROBLEM this shape works around: fail() calls process.exit(1) DIRECTLY (skips any
// pending finally/loop state) — so this retry/self-heal loop uses `continue`/`break` for its
// OWN internal control flow and calls fail() **at most once**, only AFTER the loop has
// genuinely exhausted every retry/self-heal/wait attempt — never from inside the loop body.
//
// Released on process exit (normal completion OR fail()'s process.exit), so it never outlives
// the run; a hard crash may leave a stale lock — the NEXT acquire self-heals it automatically.
function acquireUpdateLock(home, { timeout = null } = {}, env = process.env) {
  fs.mkdirSync(home, { recursive: true });
  const lockPath = path.join(home, LOCK_FILE);
  const staleAfterMs = Number(env.ADD_LOCK_STALE_SECONDS || LOCK_STALE_DEFAULT) * 1000;
  const deadline = timeout ? (Date.now() + timeout * 1000) : null;   // null/0 = byte-identical fail-fast

  let fd = null;
  let timedOut = false;
  while (fd === null) {
    try {
      fd = fs.openSync(lockPath, "wx");
      break;
    } catch (e) {
      if (!e || e.code !== "EEXIST") throw e;
    }
    let st;
    try { st = fs.statSync(lockPath); }
    catch (_e) { continue; }   // vanished between the failed open and the stat — retry the create
    let reclaimed = false;
    if (Date.now() - st.mtimeMs > staleAfterMs) {
      // Identity-verified reclaim (fixes a TOCTOU race: an unconditional unlink-by-path let a
      // second racer delete a FIRST racer's already-recreated, live lock). A NAIVE "rename to a
      // quarantine name" does NOT fix this — a rename is JUST as identity-blind as an unlink: it
      // operates on whatever currently sits at `lockPath`, so a delayed racer's rename can just
      // as easily steal a WINNER's brand-new fresh file (empirically reproduced while building
      // this fix; that attempt made the race MEASURABLY WORSE, not better, by adding an extra
      // syscall to the vulnerable window). The actual fix: gate entry to the reclaim itself
      // behind a SEPARATE, per-GENERATION exclusive ticket, keyed to the CURRENT stale file's
      // own inode number (`st.ino` — stable for this file's lifetime, and a FRESH replacement
      // file always gets a NEW inode). Two racers that observe the SAME stale file compute the
      // IDENTICAL ticket name and race an exclusive create on IT — only one wins; every loser
      // backs off WITHOUT ever touching `lockPath` itself, so nobody can ever unlink/steal a
      // generation they didn't win the ticket for.
      const ticketPath = lockPath + ".reclaim-" + st.ino;
      let ticketFd = null;
      try {
        ticketFd = fs.openSync(ticketPath, "wx");
      } catch (_e) { /* LOST the ticket outright — checked below before giving up on it */ }
      if (ticketFd === null) {
        // LOST the per-generation reclaim ticket outright. Before treating this as "someone
        // else legitimately owns reclaiming THIS stale file right now," check whether THAT
        // ticket is itself orphaned — leaked by a process that crashed between winning it and
        // its own best-effort cleanup below. Left unchecked, a leaked ticket wedges this
        // generation's reclaim FOREVER: the ticket's name is deterministically keyed to
        // `lockPath`'s own (unchanging) inode, so every future contender recomputes the
        // IDENTICAL ticket path, loses the identical EEXIST race, and — pre-fix — `continue`d
        // straight back to the top of this loop without ever reaching the `deadline` check
        // below: an unbounded livelock no `--lock-timeout` could ever interrupt (found by a
        // fresh adversarial verify pass; independently reproduced here against the unmodified
        // code via both a direct call and a real `node cli.js` subprocess, both still spinning
        // well past their own declared timeout budget).
        let tst = null;
        try { tst = fs.statSync(ticketPath); } catch (_e) { /* vanished — retry the create below */ }
        if (tst === null) {
          try { ticketFd = fs.openSync(ticketPath, "wx"); } catch (_e) {}
        } else if (Date.now() - tst.mtimeMs > LOCK_TICKET_STALE_SECONDS * 1000) {
          // The ticket ITSELF is orphaned — reclaim it with the IDENTICAL identity-verified
          // discipline already used for the main lock just above, one level down: re-stat
          // immediately before unlinking and compare inode, so a ticket some THIRD, still-
          // legitimately-in-flight reclaimer freshly (re)created in the gap between our stat
          // and our unlink is never destroyed. A plain unconditional unlink-by-path here would
          // reopen the IDENTICAL TOCTOU hole this whole ticket mechanism exists to close, one
          // level down (e.g. a naive "just unlink if old" would let racer A destroy racer C's
          // brand-new, not-yet-stale ticket for the SAME generation, so A and C would BOTH
          // believe they are the sole reclaimer — the exact double-hold bug this ticket
          // mechanism was built to prevent, reintroduced one level down).
          // Same reuse guard as the main lock: only unlink a ticket STILL at its observed inode
          // AND still aged past the ticket-stale threshold (a freed inode number can be reused
          // by a fresh, live ticket for a new generation).
          if (stillStaleGeneration(ticketPath, tst.ino, LOCK_TICKET_STALE_SECONDS)) {
            try { fs.unlinkSync(ticketPath); } catch (_e) {}   // already gone — harmless
          }
          try { ticketFd = fs.openSync(ticketPath, "wx"); } catch (_e) {}   // someone else won it
        }
        // else: the ticket is live and fresh — a genuine, currently-in-flight reclaimer;
        // ticketFd stays null and falls through to the shared deadline check below (previously
        // an unconditional `continue` back to the top of this same branch — now routed the same
        // as any other non-progress iteration, never a special case that could spin unboundedly
        // on its own).
      }
      if (ticketFd !== null) {
        try {
          fs.closeSync(ticketFd);
          // Winning the ticket proves we are the SOLE reclaimer for the generation we observed
          // (`st.ino`) — it does NOT prove `lockPath` is STILL that generation right now. An
          // arbitrarily long scheduling gap can separate "we judged st.ino stale" from "we act on
          // it," and in that gap this SAME path can already have cycled through a full, unrelated
          // reclaim by someone else (that old inode gone, a fresh one created and now actively
          // held — empirically observed while building this fix: a late-scheduled racer's ticket
          // for a long-superseded inode still "won" trivially, since nothing else was contesting
          // that specific stale ticket name any more, and its UNCONDITIONAL unlink then blindly
          // destroyed the CURRENT live holder's fresh file). Re-stat immediately before mutating
          // and compare inodes: only remove the file if it is STILL, right now, the exact
          // generation we ticketed for; otherwise our ticket is moot — leave the (unrelated,
          // currently live) file completely alone and let the loop's own open/EEXIST/age logic
          // re-evaluate reality fresh on the next iteration.
          // Re-verify STALENESS, not just inode identity: a freed inode number is REUSED by
          // Linux (ext4/tmpfs), so a live holder's fresh reused-inode lock must never be
          // unlinked on a bare inode match. Only remove it if it is STILL the observed inode
          // AND still stale — a live/heartbeated file (age < staleAfterMs) is spared, closing
          // the peak=2 double-hold.
          if (stillStaleGeneration(lockPath, st.ino, staleAfterMs / 1000)) {
            try { fs.unlinkSync(lockPath); } catch (_e) {}   // already gone — harmless
          }
        } finally {
          try { fs.unlinkSync(ticketPath); } catch (_e) {}   // best-effort cleanup of our own ticket
        }
        reclaimed = true;
      }
    }
    if (reclaimed) {
      continue;                                          // retry the create immediately (self-heal)
    }
    if (deadline !== null && Date.now() < deadline) {
      sleepSync(LOCK_POLL_INTERVAL_MS);
      continue;   // keep polling a LIVE holder — or a still-contested ticket — until the deadline.
                  // This check is now ALWAYS reachable on every non-reclaiming iteration (the
                  // fix's other half): a wedged/leaked ticket can no longer bypass it by looping
                  // back to the top of the `while` unconditionally, so an explicit --lock-timeout
                  // is honored even while a stale ticket is being self-healed above.
    }
    timedOut = true;
    break;
  }
  if (timedOut) {
    fail("update_in_progress: another `update --global` is already running — retry shortly " +
         "(remove " + lockPath + " if it is stale)");
    return () => {};   // unreachable once fail() exits — keeps the function's return shape honest
  }
  try { fs.writeSync(fd, process.pid + " " + new Date().toISOString() + "\n"); }
  catch (_e) {}   // diagnostics are best-effort — never fail an acquired lock over this
  const heartbeat = startLockHeartbeat(lockPath, staleAfterMs);   // js-reclaim-lock-heartbeat
  const release = () => {
    heartbeat.stop();   // cleared FIRST — never outlives the fd/lockPath it refreshes
    try { fs.closeSync(fd); } catch (_e) {}
    try { fs.unlinkSync(lockPath); } catch (_e) {}
  };
  process.on("exit", release);   // covers normal completion AND fail()'s process.exit
  return release;
}

// project-scope lock (project-scope-install-lock) — serializes cmdInit()/cmdUpdate() (non-
// `--global` path) against the SAME target's own .add/ tree. A NEW, INDEPENDENT primitive that
// mirrors (but never calls into or shares code with) acquireUpdateLock's own proven shape:
// different function, different file, different default threshold, zero shared code (the two
// locks guard genuinely different-shaped resources — see _installer.py:_project_lock).
//
// Held AND fresh -> fails IMMEDIATELY with "install_in_progress". UNLIKE acquireUpdateLock,
// there is NO bounded-wait/poll mode (a live contention never waits, never polls — M7).
//
// Held AND stale (age > ADD_PROJECT_LOCK_STALE_SECONDS, default 120s) -> self-heals: unlinks
// the stale lockfile and retries the create EXACTLY once before falling through to fail-fast.
// A clock-skewed FUTURE mtime is NEVER treated as stale.
//
// KNOWN PROBLEM this shape works around: fail() calls process.exit(1) DIRECTLY (skips any
// pending finally) — release is wired via process.on("exit", release), never a plain
// try/finally at the call site (mirrors acquireUpdateLock's own already-solved precedent).
//
// If addDir did not exist yet (a virgin target — the lock file needs somewhere to live), it is
// created here; on release, an addDir THIS call created is removed again iff it is still
// completely empty (the lock file was its only occupant) — e.g. an --global failure (a held
// home lock, an unwritable home) that aborts before the per-project drop leaves NOTHING behind,
// exactly as before this lock existed. A non-empty addDir (the real drop landed, or it
// pre-existed) is never touched.
function acquireProjectLock(addDir, env = process.env) {
  const createdDir = !fs.existsSync(addDir);
  fs.mkdirSync(addDir, { recursive: true });
  const lockPath = path.join(addDir, PROJECT_LOCK_FILE);
  const staleAfterMs = Number(env.ADD_PROJECT_LOCK_STALE_SECONDS || PROJECT_LOCK_STALE_DEFAULT) * 1000;

  let fd = null;
  try {
    fd = fs.openSync(lockPath, "wx");
  } catch (e) {
    if (!e || e.code !== "EEXIST") throw e;
    let st = null;
    try { st = fs.statSync(lockPath); } catch (_e) { /* vanished — treat as reclaimable now */ }
    if (st === null) {
      // vanished between the failed open and the stat — nothing to quarantine; retry a plain
      // create directly (safe unconditionally: O_EXCL is still the sole arbiter — this can
      // never clobber a legitimate concurrent holder's fresh file, it can only succeed if the
      // path is genuinely vacant right now).
      try {
        fd = fs.openSync(lockPath, "wx");
      } catch (e2) {
        if (!e2 || e2.code !== "EEXIST") throw e2;
      }
    } else if (Date.now() - st.mtimeMs > staleAfterMs) {
      // Identity-verified reclaim (fixes a TOCTOU race: an unconditional unlink-by-path let a
      // second racer delete a FIRST racer's already-recreated, live lock). A NAIVE "rename to a
      // quarantine name" does NOT fix this — a rename is JUST as identity-blind as an unlink: it
      // operates on whatever currently sits at `lockPath`, so a delayed racer's rename can just
      // as easily steal a WINNER's brand-new fresh file (empirically reproduced while building
      // this fix; that attempt made the race MEASURABLY WORSE, not better, by adding an extra
      // syscall to the vulnerable window). The actual fix: gate entry to the reclaim itself
      // behind a SEPARATE, per-GENERATION exclusive ticket, keyed to the CURRENT stale file's
      // own inode number (`st.ino` — stable for this file's lifetime, and a FRESH replacement
      // file always gets a NEW inode). Two racers that observe the SAME stale file compute the
      // IDENTICAL ticket name and race an exclusive create on IT — only one wins; every loser
      // backs off WITHOUT ever touching `lockPath` itself, so nobody can ever unlink/steal a
      // generation they didn't win the ticket for.
      const ticketPath = lockPath + ".reclaim-" + st.ino;
      let ticketFd = null;
      try {
        ticketFd = fs.openSync(ticketPath, "wx");
      } catch (_e) {
        // LOST the per-generation reclaim ticket outright -- checked below before treating this
        // as "someone else legitimately owns reclaiming THIS stale file right now."
      }
      if (ticketFd === null) {
        // LOST the ticket outright. A leaked ticket -- its own holder crashed between winning
        // it and its own best-effort cleanup below -- would otherwise wedge this generation's
        // reclaim PERMANENTLY: the ticket's name is deterministically keyed to `lockPath`'s own
        // (unchanging) inode, so every future contender recomputes the IDENTICAL ticket path and
        // loses the identical EEXIST race forever (found by a fresh adversarial verify pass;
        // independently reproduced here against the unmodified code).
        let tst = null;
        try { tst = fs.statSync(ticketPath); } catch (_e) { /* vanished — retry the create below */ }
        if (tst === null) {
          try { ticketFd = fs.openSync(ticketPath, "wx"); } catch (_e) {}
        } else if (Date.now() - tst.mtimeMs > PROJECT_LOCK_TICKET_STALE_SECONDS * 1000) {
          // The ticket ITSELF is orphaned — reclaim it with the IDENTICAL identity-verified
          // discipline already used for the main lock just above, one level down: re-stat
          // immediately before unlinking and compare inode, so a ticket some THIRD, still-
          // legitimately-in-flight reclaimer freshly (re)created in the gap between our stat and
          // our unlink is never destroyed. A plain unconditional unlink-by-path here would
          // reopen the IDENTICAL TOCTOU hole this whole ticket mechanism exists to close, one
          // level down (e.g. a naive "just unlink if old" would let racer A destroy racer C's
          // brand-new, not-yet-stale ticket for the SAME generation, so A and C would BOTH
          // believe they are the sole reclaimer — the exact double-hold bug this ticket
          // mechanism was built to prevent, reintroduced one level down). Exactly one extra
          // self-heal attempt — never a second, matching M7's own "no poll, ever" discipline
          // already governing the main lock's own reclaim above.
          // Same reuse guard as the main lock: only unlink a ticket STILL at its observed inode
          // AND still aged past the ticket-stale threshold (a freed inode number can be reused
          // by a fresh, live ticket for a new generation).
          if (stillStaleGeneration(ticketPath, tst.ino, PROJECT_LOCK_TICKET_STALE_SECONDS)) {
            try { fs.unlinkSync(ticketPath); } catch (_e) {}   // already gone — harmless
          }
          try { ticketFd = fs.openSync(ticketPath, "wx"); } catch (_e) {}   // someone else won it
        }
        // else: the ticket is live and fresh — a genuine, currently-in-flight reclaimer;
        // ticketFd stays null, falls through to the SAME fail-fast below (M7 — this lock never
        // polls a live holder, whether it is the main lock or a contested ticket).
      }
      if (ticketFd !== null) {
        try {
          fs.closeSync(ticketFd);
          // Winning the ticket proves we are the SOLE reclaimer for the generation we observed
          // (`st.ino`) — it does NOT prove `lockPath` is STILL that generation right now. An
          // arbitrarily long scheduling gap can separate "we judged st.ino stale" from "we act
          // on it," and in that gap this SAME path can already have cycled through a full,
          // unrelated reclaim by someone else (that old inode gone, a fresh one created and now
          // actively held — empirically observed while building this fix: a late-scheduled
          // racer's ticket for a long-superseded inode still "won" trivially, since nothing else
          // was contesting that specific stale ticket name any more, and its UNCONDITIONAL
          // unlink then blindly destroyed the CURRENT live holder's fresh file). Re-stat
          // immediately before mutating and compare inodes: only remove the file if it is
          // STILL, right now, the exact generation we ticketed for; otherwise our ticket is
          // moot — leave the (unrelated, currently live) file completely alone and let the
          // single retry below observe reality fresh (EEXIST -> fail-fast, per M7 — this lock
          // never polls a live holder).
          // Re-verify STALENESS, not just inode identity: a freed inode number is REUSED by
          // Linux (ext4/tmpfs), so a live holder's fresh reused-inode lock must never be
          // unlinked on a bare inode match. Only remove it if it is STILL the observed inode
          // AND still stale — a live/heartbeated file (age < staleAfterMs) is spared, closing
          // the peak=2 double-hold.
          if (stillStaleGeneration(lockPath, st.ino, staleAfterMs / 1000)) {
            try { fs.unlinkSync(lockPath); } catch (_e) {}   // already gone — harmless
          }
        } finally {
          try { fs.unlinkSync(ticketPath); } catch (_e) {}   // best-effort cleanup of our own ticket
        }
        try {
          fd = fs.openSync(lockPath, "wx");
        } catch (e2) {
          if (!e2 || e2.code !== "EEXIST") throw e2;
          // someone else created a fresh file at the just-vacated path before we did (e.g. a
          // brand-new, never-raced contender's own first attempt landed in the gap) -> fail-fast,
          // exactly once — never a second reclaim attempt, never a poll/wait (M7).
        }
      }
    }
    if (fd === null) {
      fail("install_in_progress: another install/update is already running against " +
           path.dirname(addDir) + " — retry shortly (remove " + lockPath + " if stale)");
      return () => {};   // unreachable once fail() exits — keeps the function's return shape honest
    }
  }
  try { fs.writeSync(fd, process.pid + " " + new Date().toISOString() + "\n"); }
  catch (_e) {}   // diagnostics are best-effort — never fail an acquired lock over this
  const heartbeat = startLockHeartbeat(lockPath, staleAfterMs);   // js-reclaim-lock-heartbeat
  const release = () => {
    heartbeat.stop();   // cleared FIRST — never outlives the fd/lockPath it refreshes
    try { fs.closeSync(fd); } catch (_e) {}
    try { fs.unlinkSync(lockPath); } catch (_e) {}
    if (createdDir) {
      try { if (fs.readdirSync(addDir).length === 0) fs.rmdirSync(addDir); } catch (_e) {}
      // non-empty (the real drop landed) or already gone — leave it alone either way
    }
  };
  process.on("exit", release);   // covers normal completion AND fail()'s process.exit
  return release;
}

function cmdUpdateGlobal(args) {
  const home = resolveGlobalHome(process.env);
  const claudeDir = claudeSkillsDir(process.env);
  if (!fs.existsSync(path.join(home, STAMP_FILE))) {
    fail("no_global_home: no global ADD install at " + home + " (.add-version not found) — run `init --global` first");
  }
  // exclusive; self-heals a stale lock; a LIVE lock -> update_in_progress (immediate, or after
  // waiting up to --lock-timeout seconds); released on process exit
  acquireUpdateLock(home, { timeout: args.lockTimeout }, process.env);
  // Read the registry BEFORE refreshing the home — a corrupt registry fails closed with ZERO
  // writes (never a silent empty-list no-op), leaving the file for the user to fix or delete.
  let reg;
  try { reg = readRegistry(home); }
  catch (_e) { fail("registry_corrupt: global registry " + registryPath(home) + " is corrupt — fix or delete it; not propagating"); }
  // PRE-SCAN (security): a NON-ABSOLUTE entry is the traversal vector -> abort with zero mutations.
  for (const p of reg) {
    if (!path.isAbsolute(p)) {
      fail("unsafe_registry_path: registered project '" + p + "' is not an absolute path — fix or remove it in " + registryPath(home) + "; not propagating");
    }
  }
  try { reconcileGlobal(home, claudeDir, args.noSkill); }
  catch (e) { fail("cannot write global home " + home + " — " + (e && e.message ? e.message : e)); }
  const version = pkgVersion();
  writeStamp(home, version, "global");
  const kept = [];
  let pruned = 0, dropped = 0;
  for (const p of reg) {
    const np = path.normalize(p);   // absolute (pre-scan) -> lexically normalized
    if (!fs.existsSync(np)) { log("  ⚠ registered project " + np + " not found — pruning"); pruned++; continue; }
    if (!validRegistryPath(np)) {   // exists but no .add/ -> NEVER reconcile managed files into it
      log("  ⚠ registered path " + np + " is not an ADD project (no .add/) — dropping"); dropped++; continue;
    }
    reconcile(args, np, home);      // standard MANAGED map, sourced from the home mirror
    seedGitignore(np);               // keep .add/.gitignore current too (parity: _installer.py)
    // re-persist an opted-in project (one that already has a snapshot); a vanished
    // project's snapshot is KEPT above (the backup outlives the dir).
    if (fs.existsSync(path.join(home, "data", dataKey(np)))) persistData(home, np);
    kept.push(np);                  // store the NORMALIZED path (heals a bent legit entry)
  }
  writeRegistry(home, kept);
  const bits = [];
  if (pruned) bits.push(pruned + " pruned");
  if (dropped) bits.push(dropped + " dropped");
  log("ADD " + version + " · global home + " + kept.length + " project(s) reconciled" +
      (bits.length ? " (" + bits.join(", ") + ")" : "") + ".");
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
  // Project-scope lock (project-scope-install-lock): acquired AFTER the read-only --check
  // report (a JS-only carve-out — see TASK.md §0/M3), held from here through the function's
  // end — INCLUDING the same-version no-op check below, so a retried call re-evaluates it fresh.
  acquireProjectLock(addDir);
  // same-version no-op ONLY when nothing is missing — a missing managed tree HEALS
  // even at the current version (heal-reconcile).
  const status = managedStatus(target);
  // An optional tree absent from BOTH the package and the project can't be healed, so it
  // never counts as "missing" — otherwise a same-version update would never reach the no-op.
  const missing = MANAGED.some(([sub]) => status[sub] === "missing"
    && !(OPTIONAL.has(sub) && !fs.existsSync(path.join(PKG_ROOT, sub))));
  if (cur === version && !args.force && !missing) {
    log("ADD already at " + version + " — nothing to update (use --force to re-materialize).");
    return;
  }
  // design-for-failure: back up state BEFORE touching anything.
  const stateFile = path.join(addDir, "state.json");
  if (fs.existsSync(stateFile)) {
    fs.copyFileSync(stateFile, path.join(addDir, "pre-update-state.bak.json"));
  }
  const roll = reconcile(args, target);
  seedSoulMd(target);   // pip parity: re-seed a missing user-owned SOUL.md (never clobber)
  seedGitignore(target);   // pip parity: seed/append-if-absent the engine-transient ignore lines
  writeStamp(addDir, version);
  log("ADD updated " + (cur || "(unstamped)") + " -> " + version +
      " · managed layer reconciled (" + roll.restored + " restored · " + roll.refreshed +
      " refreshed) · your project state untouched.");
  // crossing nudge — an engine-owned follow-up the updater NAMES, never runs (python3 may be
  // absent on this PATH; the command is idempotent). After a version change, verify the vendored
  // engine + bundle still conform, using a REAL verb — the flat 3.0 engine has no OKF
  // `sync-guidelines`/`migrate` verbs (both retired), so there is nothing else to name here.
  if (cur !== version) {
    log("next: python3 .add/tooling/cli.py status --check   # verify the engine + bundle conform to this version");
  }
}

// js-reclaim-lock-heartbeat: a test-only entrypoint so the Python subprocess suite can drive
// real multi-process contention against acquireUpdateLock/acquireProjectLock without duplicating
// their acquire/release logic in the test itself. Intercepted BEFORE the `cmd`/switch dispatch
// below, guarded behind an undocumented flag — never listed in --help, never reachable via any
// documented public command, so it carries zero surface on the real CLI path.
async function cmdInternalAcquireLock(argv) {
  const kind = argv[0];
  const targetPath = argv[1];
  const holdMs = Number(argv[2]);
  let release;
  if (kind === "update") {
    release = acquireUpdateLock(targetPath, { timeout: null }, process.env);
  } else if (kind === "project") {
    release = acquireProjectLock(targetPath, process.env);
  } else {
    fail("internal_acquire_lock_bad_kind: expected 'update' or 'project', got '" + kind + "'");
    return;
  }
  log("HELD " + Date.now());
  await sleepAsync(holdMs);   // event-loop-yielding — lets the heartbeat's setInterval fire
  log("RELEASED " + Date.now());
  release();
  process.exit(0);
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === "--internal-acquire-lock") {
    await cmdInternalAcquireLock(argv.slice(1));
    return;
  }
  const cmd = argv[0] && !argv[0].startsWith("--") ? argv.shift() : "init";
  const args = parseArgs(argv);
  switch (cmd) {
    case "init":
      await cmdInit(args);
      break;
    case "update":
      cmdUpdate(args);
      break;
    case "prune-data":
      cmdPruneData(args);
      break;
    case "help":
    case "--help":
      log("usage: npx @pilotspace/add <init|update|prune-data> [targetDir] [--force] [--check] [--no-skill] [--global] [--yes|--non-interactive]");
      log("  init    install the ADD skill + tooling into a project");
      log("          (--no-skill drops the engine only — used by the Claude Code plugin)");
      log("          (--global ALSO installs to a shared home [ADD_HOME|XDG_DATA_HOME/add|~/.add] + registers the project)");
      log("          (--global-data implies --global + persists this project's user-data under <home>/data/<key>)");
      log("          (--from-global-data rehydrates this project's user-data FROM the shared home on a fresh clone)");
      log("          (interactive in a real terminal; --yes / --non-interactive force the plain path)");
      log("  update  re-materialize skill/tooling to this package version (preserves your state)");
      log("          (--global refreshes the shared home + propagates to every registered project)");
      log("  prune-data  remove orphaned per-project snapshots from the shared home (dry-run; --force deletes)");
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
  stillStaleGeneration: stillStaleGeneration,
  detectAgent: detectAgent,
  detectAgentEnriched: detectAgentEnriched,
  readinessLine: readinessLine,
  whichSync: whichSync,
  scopeOptions: scopeOptions,
  writeIntentNote: writeIntentNote,
  writeGeminiSettings: writeGeminiSettings,
};
