"""add_engine.constants — engine constants (moved verbatim from add.py).

Pure module-level constants. add.py re-exports these so `import add; add.STAGES`
(and the 6 _-prefixed names) still resolve. `__all__` lists the public names so
`from add_engine.constants import *` brings exactly them (not the Path import).
"""
import re
from pathlib import Path

__all__ = [
    "ROOT_DIRNAME",
    "STATE_FILE",
    "MILESTONE_FILE",
    "GOAL_UNSET",
    "STAGES",
    "GRADUATION_CUE",
    "RELEASABLE_CUE",
    "RELEASES_FILE",
    "PHASES",
    "GATES",
    "HEAL_CAP",
    "PHASE_GUIDE",
    "PHASE_OWNER",
    "PHASE_GROUPS",
    "PHASE_AGENT",
    "SETUP_FILES",
    "PERSONA_FRONTMATTER_KEYS",
    "PERSONA_REQUIRED_SECTIONS",
    "PERSONA_FLOW_VALUES",
    "PERSONA_HINT",
    "PERSONA_FIT_HINT_TEMPLATE",
    "GUIDELINE_FILES",
    "RULES_FILE_REL",
    "WORKFLOW_HEADINGS",
    "_GATE_MODES",
    "_SKIPPABLE_PHASES",
    "_DIALECT_CLASSES",
]

ROOT_DIRNAME = ".add"
STATE_FILE = "state.json"
MILESTONE_FILE = "MILESTONE.md"
# The project GOAL (v20) is read live from PROJECT.md — never copied into state.json
# (single-source; the foundation is the truth). A missing/blank source degrades to
# this sentinel so the read-only orientation surfaces never blank or crash.
GOAL_UNSET = "(unset — add a 'goal:' line to PROJECT.md)"
STAGES = ("prototype", "poc", "mvp", "production")
# v22 stage-graduation: the read-only cue `status` shows when the MVP is covered.
# Worded as the ACTION (never a file) so it stands before graduate.md exists.
GRADUATION_CUE = "MVP covered → propose graduation"
# release-altitude: the read-only cue `status` shows when ≥1 closed milestone is
# unreleased. The 5th scope level (release.md). `{n}` is filled at print time; the
# wording matches SKILL.md's "Beyond the bundle" cross-ref byte-for-byte.
RELEASABLE_CUE = "releasable: {n} milestone(s) closed since last release"
# the append-only release ledger lives at the PROJECT ROOT (the dir containing .add/),
# a sibling of CHANGELOG.md — NOT inside .add/. The ledger IS the attribution source:
# a milestone is "released" iff its slug appears on a `milestones:` row.
RELEASES_FILE = "RELEASES.md"
PHASES = ("specify", "scenarios", "plan", "tests", "build", "verify", "observe", "done")
GATES = ("none", "PASS", "RISK-ACCEPTED", "HARD-STOP")
# heal-then-escalate (verify-integrity): the bounded self-heal loop cap. A CONFIRMED cheat
# (mechanical tripwire divergence, or an agent-reported semantic refute-read finding) returns
# the task to BUILD for an honest redo; after HEAL_CAP such attempts the next confirmed cheat
# forces a HARD-STOP escalation to the human. MONOTONIC — attempts never auto-resets (a gamed
# green is never auto-passed; the loop is never unbounded).
HEAL_CAP = 3



# `add.py guide` copy: per-phase (concrete next action, book chapter to read).
# Keep the action wording aligned with each phase's EXIT line in the TASK template.
PHASE_GUIDE = {
    "specify":   ("state every rule — Must / Reject (+ named code) / After, projected from the milestone Ground + the request; rank assumptions lowest-confidence first and flag the biggest risk",
                  "03-step-1-specify.md"),
    "scenarios": ("write one Given/When/Then per Must AND per Reject; every result observable",
                  "04-step-2-scenarios.md"),
    "plan":      ("build the change plan — ground the real code the contract will cite, freeze the contract shape (names match the glossary), and set the build strategy; this is the one human approval",
                  "05-step-3-contract.md"),
    "tests":     ("write one failing test per scenario; run them RED for the right reason",
                  "06-step-4-tests.md"),
    "build":     ("write the minimum code to pass the tests; change no test and no contract",
                  "07-step-5-build.md"),
    "verify":    ("run the suite + non-functional checks, then record the gate",
                  "08-step-6-verify.md"),
    "observe":   ("note what to watch + the spec delta for the next loop",
                  "09-the-loop.md"),
    "done":      ("this task is done — pick the next feature",
                  "02-the-flow.md"),
}
# Phase -> who owns it, for the `--json` autonomy signal. An autonomous harness may run a
# phase only when owner=="ai" (stop is false); every other phase is a checkpoint. The map
# follows the book's who-does-what table (Verify is "human only"); `tests`/`build`/`observe`
# are AI-led. A phase missing here is `unmapped_phase` (fail closed) — never defaulted.
PHASE_OWNER = {
    "specify": "human", "scenarios": "human", "plan": "seam",
    "tests": "ai", "build": "ai", "verify": "human", "observe": "ai", "done": "human",
}
# phase-bundles: the 7 work phases (PHASES minus the terminal "done") group into 3
# agent-owned bundles surfaced at `status`/`guide` — DIRECTION fixes the shape (through
# the frozen change plan — grounding + contract + build-strategy — AND the red suite; the
# method thesis is "fix spec/scenarios/plan/failing-tests BEFORE the build"), BUILD makes
# it green, VERIFY earns trust and feeds the next loop. A grouping OVER PHASES, never a
# reorder; "done" (terminal, human-led) deliberately has no bundle — see PHASE_AGENT/
# _phase_bundle below. Union == set(PHASES) - {"done"}, pairwise disjoint (test_phase_bundles.py).
PHASE_GROUPS = {
    "DIRECTION": ("specify", "scenarios", "plan", "tests"),
    "BUILD": ("build",),
    "VERIFY": ("verify", "observe"),
}
# phase-bundles: the roster agent PREFERRED for each phase (per-PHASE, not per-bundle —
# `tests` bundles into DIRECTION above yet its preferred agent is still add-build, the
# shipped roster's own boundary: add-design owns specify/scenarios/plan, add-build owns
# tests/build, add-verify owns verify/observe). A phase missing here is a bug (PHASE_GROUPS'
# own union covers every key); `_phase_bundle` is the fail-closed resolver for an
# unmapped/corrupted phase token, not this map directly.
PHASE_AGENT = {
    "specify": "add-design", "scenarios": "add-design", "plan": "add-design",
    "tests": "add-build", "build": "add-build",
    "verify": "add-verify", "observe": "add-verify",
}
SETUP_FILES = ("PROJECT.md", "CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md", "dependencies.allowlist", "DESIGN.md", "SOUL.md", "personas/_template.md")

# persona-setup: a PERSONA living doc (`.add/personas/<slug>.md`) is a frozen-schema file
# distilled from the vendored teacher library to its critical-rules + default-requirement +
# measurable success-metrics. The schema is presence-based (these keys/sections must exist);
# content quality is the AI's authoring concern, not the engine gate. NO-EXEC: validation is pure.
PERSONA_FRONTMATTER_KEYS = ("name", "vibe")
PERSONA_REQUIRED_SECTIONS = ("## Identity", "## Critical Rules", "## Default Requirement", "## Success Metrics")
# persona-schema-hardening: the closed set of apply-surfaces a `flow:` value may name — the
# single source the quality predicate reads (a value outside this set is loaded by NO surface,
# so a typo would otherwise fail silently). Findings are WARN-only (measure-not-block).
PERSONA_FLOW_VALUES = ("design", "build", "advisor", "verify")

# persona-seed-nudge v2: ONE hint, single-sourced — `new-milestone`/`check`/`status` all print
# THIS constant (not their own copy) so the wording can never drift across the three surfaces.
# Project-scoped (not "this milestone's domain") per the confirmed v2 amendment: the AI should
# catch up ALL of a project's missing personas, not draft a single milestone-fit one.
PERSONA_HINT = ("no project-fit persona seeded yet under .add/personas/ — spawn the add-persona "
                "agent (or read docs/18-personas.md) to seed the project's persona(s) from "
                "PROJECT.md's domain")

# persona-fit-nudge: the OPPOSITE-branch, mutually-exclusive sibling of PERSONA_HINT — fires only
# when ≥1 real persona ALREADY exists, so a brand-new milestone doesn't silently assume one of
# them fits its domain. Existence-only (names the persona slugs already seeded); the AI still
# owns the actual fit judgment via add-persona — the engine never scores content similarity.
# {slugs} is filled at call time from `.add/personas/*.md` (excluding `_template`).
PERSONA_FIT_HINT_TEMPLATE = (
    "existing persona(s) seeded — {slugs} — confirm one fits this milestone's domain, or spawn "
    "the add-persona agent (or read docs/18-personas.md) to draft a better-fit one"
)

# Scaffolded into .add/.gitignore at init so the engine's transient LOCAL artifacts
# never reach git. Bare-filename patterns match at any depth under .add/ (tasks/,
# milestones/, archive/). These are working state, not records: scope-snapshot.json
# is the tests->build touch baseline the verify scope-gate reads from disk (the
# durable scope declaration is the state.json anchor); pre-archive-state.bak.json is
# archive-milestone's pre-delete recovery net — needed on disk, never in history;
# pre-update-state.bak.json is the installer update's pre-write state backup (cli.js
# cmdUpdate / pip _installer.update) — same "on disk, never in git" need; .update-cache.json
# is the update-nudge's once-a-day registry throttle. All stay on disk; git-ignoring them
# is hygiene, never deletion. SINGLE-SOURCED: this constant is kept byte-identical to
# tooling/templates/gitignore.tmpl (test_gitignore_bak_seed parity) so the installers,
# which seed/refresh .add/.gitignore from that template on update, never drift from init.
_GITIGNORE_BODY = """\
# ADD engine transient artifacts — local working state, never committed.
# (Scaffolded by `add.py init`; refreshed additively by the installer on update.)
scope-snapshot.json
pre-archive-state.bak.json
pre-update-state.bak.json
.update-cache.json

# ADD-managed vendor trees: regenerable/vendored copies the installer drops in,
# never project-authored — mirrors the .add/docs/ rationale above, generalized
# to every consumer project (not just this repo). Patterns are BARE, not repo-
# root style: this file lives INSIDE .add/, so git resolves its patterns
# relative to .add/ itself — a ".add/"-prefixed pattern here would look for
# the non-existent .add/.add/tooling/ and never match anything. (one further
# managed tree is NOT listed here — the engine's own _GITIGNORE_BODY constant
# must stay hands-off of it by name; the installer twins seed that pattern
# themselves, also bare.)
tooling/
docs/
"""

# Guideline-injection targets + version-stable markers. NEVER change these marker
# strings: a re-run finds the old block by exact match, so changing them would
# orphan every block written by a prior version (see TASK guideline-inject).
GUIDELINE_FILES = ("AGENTS.md", "CLAUDE.md", ".clinerules")
_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"

# Rule-file mode (ccsk-style projects): instead of inlining the block into CLAUDE.md,
# write it to a dedicated rule file under .claude/rules/ and leave a one-line reference
# in CLAUDE.md's Workflows section. .claude/rules/ is a CLAUDE-only convention, so this
# mode only ever relocates CLAUDE.md — AGENTS.md/.clinerules keep the inline block.
RULES_FILE_REL = Path(".claude") / "rules" / "add-workflows.md"
# Headings (most→least specific) a project may already use to group rule/workflow links.
# Match is case-insensitive on the heading TEXT, at any `#` level.
WORKFLOW_HEADINGS = ("Rules & Workflows", "Workflows", "Rules")
_RULE_REF_LINE = "- ADD (AI-Driven Development) Workflows rules: ./.claude/rules/add-workflows.md"

# Minimal embedded fallback so the tool still works if templates/ is missing
# (circuit breaker: never hard-fail just because a template file was deleted).
_FALLBACK_TASK = """# TASK: {title}

slug: {slug} · created: {date} · stage: {stage}
autonomy: auto
phase: specify

## 1 · SPECIFY
Feature:
Framings weighed:
Must:
Reject:
After:
Assumptions — lowest-confidence first:
  ⚠ <most likely wrong> — lowest confidence because <why>; if wrong: <cost>

## 2 · SCENARIOS
## 3 · PLAN
### Grounding
Touches (files · symbols · signatures):
Honors (patterns / conventions):
Anchors the contract cites:
### Contract
Status: DRAFT
### Build-strategy
Scope (may touch):
## 4 · TESTS
## 5 · BUILD
## 6 · VERIFY
### GATE RECORD
Outcome:
## 7 · OBSERVE
### Spec delta
### Competency deltas
"""


# Fast-lane fallback: the minimal TASK.md variant (sections {0,1,3,4,5,6}; §2 + §7 dropped).
# Mirrors templates/TASK.fast.md.tmpl's section set (circuit-breaker parity); a deleted
# templates/ never hard-fails the fast lane. Keeps the trust floor: §3 freeze-flag + Status,
# §6 GATE RECORD/Outcome, §0 Anchors, §4 red-before-build, §5 Scope.
_FALLBACK_TASK_FAST = """# TASK: {title}

slug: {slug} · created: {date} · stage: {stage}
autonomy: auto
phase: specify
fast: true

## 1 · SPECIFY
Feature:
Must:
Reject:
Accept:
Assumptions: ⚠ <most likely wrong> — why; if wrong: <cost>

## 3 · PLAN
### Grounding
Touches (files · symbols):
Anchors the contract cites:
Ground SHA:
### Contract
Least-sure flag surfaced at freeze:
Status: DRAFT
### Build-strategy
Scope (may touch): `./src/`

## 4 · TESTS
Plan:
Tests live in: `./tests/` · MUST run red before Build.

## 5 · BUILD
Strategy actually used:
Code lives in: `./src/`

## 6 · VERIFY
Build expectations (from §1 Accept + §3 CONTRACT):
### GATE RECORD
Outcome:
Reviewed by:
"""

_DEFAULT_WIDTH = 72       # fixed width for the persisted/canonical render (RETRO.md)


# --- shared delta-parsing regexes (used by taskdoc readers AND the deltas-web lint) ---
# Groups stay (1) competency, (2) status, (3) text — every caller relies on that. A competency
# lesson MAY carry an OPTIONAL persona target + section hint between status and `]`
# (persona-self-improve): `[<comp> · <status> · persona:<slug> · <critical-rule|success-metric>] …`.
# That clause is NON-capturing here (group numbering unchanged); _PERSONA_TAG_RE below pulls the
# slug + hint out when a route needs them — permissively, so an unroutable hint still PARSES (and is
# rejected by code) rather than silently failing to match.
_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(DDD|SDD|UDD|TDD|ADD)\s*·\s*(open|folded|rejected)"
    r"(?:\s*·\s*persona:[^\s·\]]+\s*·\s*[^·\]]+?)?\s*\]\s*(.+)$"
)
# Pull the OPTIONAL persona target + section hint out of a delta tag line (persona-self-improve).
_PERSONA_TAG_RE = re.compile(r"persona:([^\s·\]]+)\s*·\s*([^·\]]+?)\s*\]")
_EVIDENCE_RE = re.compile(r"^(.*?)\s*\(evidence:\s*(.*?)\)\s*$")
_SPEC_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(SPEC)\s*·\s*(open|seeded|dropped|carried)\s*\]\s*(.+)$"
)

# delta-task-backlink: reads the `[→ <slug>]` seed stamp `_resolve_spec_delta` appends, so the
# delta→task lineage can be walked back (check WARNs when a seeded pointer no longer resolves).
_SEED_POINTER_RE = re.compile(r"\[→\s*([A-Za-z0-9_-]+)\s*\]")

# rule-id-coverage: §1 Must-ID / Reject-code lines, plus the §2 scenario tag and §4 `covers:`
# back-reference a task uses to claim coverage of a rule. A Reject's ID is its literal error_code
# string (from `-> "<error_code>"`), never a positional R1/R2 sequence number.
_MUST_ID_RE = re.compile(r"^\s*-\s*(M\d+)\s*:", re.MULTILINE)
_REJECT_CODE_RE = re.compile(r'^\s*-\s.*->\s*"([^"]+)"\s*$', re.MULTILINE)
_SCENARIO_TAG_RE = re.compile(r"^\s*Scenario:.*#\s*(.+?)\s*$", re.MULTILINE)
_COVERS_LINE_RE = re.compile(r"covers:\s*(.+?)\s*$", re.MULTILINE)
_TAG_TOKEN_RE = re.compile(r"(M\d+|R:[A-Za-z0-9_]+)")


# --- autonomy levels (shared: autonomy resolvers + _AUTONOMY_ORDER/cmd_autonomy) ---
_AUTONOMY_LEVELS = ("manual", "conservative", "auto")

# --- streams posture (shared: streams resolvers + cmd_streams) — the parallel-vs-sequential
#     half of the run mode (persist-run-mode); project-scoped, persisted in PROJECT.md beside autonomy ---
_STREAMS_POSTURES = ("parallel", "sequential")

# --- sensitivity taxonomy (shared: _task_sensitivity reader + cmd_freeze/status/audit) — the
#     risk-CLASS the human declares in the TASK header at freeze (risk-sensitivity-taxonomy). The
#     engine validates + surfaces a HUMAN-declared token; it NEVER classifies. A closed enum, sibling
#     of _AUTONOMY_LEVELS/_STREAMS_POSTURES. Consumed downstream by advisor-gate-relax (mechanical). ---
_SENSITIVITY_VALUES = ("security", "data", "architecture", "mechanical")

# --- gate mode (shared: _task_gate_mode reader + cmd_freeze's --ai-plan-verify path) — the
#     two-way DIRECTION-freeze declaration (ai-plan-verify-gate): human (default) | ai-plan-verify.
#     A closed 2-tuple, sibling of _AUTONOMY_LEVELS/_STREAMS_POSTURES/_SENSITIVITY_VALUES — but,
#     unlike them, listed in __all__: a NEW trust-loosening capability is deliberately surfaced via
#     `from add_engine.constants import *`, not tucked into the _-prefixed sibling import list.
#     Absent header line -> None from the resolver, treated as "human" by every caller (fail-closed
#     default — never silently upgrades to the loosened path). ---
_GATE_MODES = ("human", "ai-plan-verify")

# --- skippable phases (shared: _task_skip_set reader + cmd_advance's skip pre-pass) — the
#     fast-lane-skips closed 2-tuple: the ONLY set cmd_advance's skip pre-pass ever tests `nxt`
#     against. specify/plan/tests/build/verify can NEVER be skipped — a structural
#     exclusion (this tuple never names them), not a runtime-checked policy. Same relative order
#     as PHASES. Listed in __all__ (mirrors _GATE_MODES): a new trust-loosening capability is
#     deliberately surfaced via `from add_engine.constants import *`, not tucked away. ---
_SKIPPABLE_PHASES = ("scenarios", "observe")

# --- format-dialect registry (shared: _dialect_gaps + the tests->build crossing warning +
#     cmd_check's dialect_gap lint) — quality-floors floor 1. Closed (name, regex) pairs: a
#     class matches only its FULL value shape, never prose fragments (a bare `2026-07-10`
#     date must not match — the aware class requires the T separator + a zone suffix). Born
#     from benchmark WV1 wm2: an arm's own suite stayed green on naive timestamps while the
#     spec's own examples were Z-suffixed; the aware/naive crash shipped green. Listed in
#     __all__ (mirrors _GATE_MODES): a new trust surface is deliberately surfaced. ---
_DIALECT_CLASSES = (
    ("aware-iso-timestamp",
     r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})"),
)
